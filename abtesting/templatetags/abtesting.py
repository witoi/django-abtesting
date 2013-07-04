import logging

from django import template

logger = logging.getLogger(__name__)

register = template.Library()


CTX_PREFIX = "__abtesting__experiment__"


class ExperimentNotDeclaredException(template.TemplateSyntaxError):
    MESSAGE = "Experiment %s has not yet been declared." \
              "Please declare it and supply variant names using an experiment tag before using hyp tags."

    def __init__(self, experiment, *args, **kwargs):
        logger.error(self.MESSAGE % experiment)
        super(ExperimentNotDeclaredException, self).__init__(self.MESSAGE % experiment)


class RequestRequiredException(template.TemplateSyntaxError):
    MESSAGE = "Use of abtestingtags requires the request context processor." \
              "Please add django.core.context_processors.request to your settings.TEMPLATE_CONTEXT_PROCESSORS."

    def __init__(self, *args, **kwargs):
        logger.error(self.MESSAGE)
        super(RequestRequiredException).__init__(self.MESSAGE)


class abtestingMiddlewareRequiredException(template.TemplateSyntaxError):
    TEMPLATE = "Use of abtestingtags requires the abtesting middleware." \
               "Please add abtesting.middleware.ExperimentsMiddleware to your settings.MIDDLEWARE_CLASSES."

    def __init__(self, *args, **kwargs):
        logger.error(self.MESSAGE)
        super(abtestingMiddlewareRequiredException).__init__(self.MESSAGE)


class ExperimentNode(template.Node):
    def __init__(self, exp_name, variants):
        self.exp_name = exp_name
        self.variants = variants

    def render(self, context):
        if "request" not in context:
            raise RequestRequiredException

        request = context["request"]
        experiments = request.experiments

        if not experiments:
            raise abtestingMiddlewareRequiredException

        expvariant = experiments.declare_and_enroll(self.exp_name, self.variants)
        context[CTX_PREFIX + self.exp_name] = expvariant
        logger.info('Experiment %s declared on %s with variant %s', self.exp_name, CTX_PREFIX + self.exp_name, expvariant)
        return ""

@register.tag('experiment')
def do_experiment(parser, token):
    try:
        tag_name, exp_name, variants_label, variantstring = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, '%r tag requires exactly three arguments, e.g. {% experiment "signuptext" variants "control,free,trial" %}' % token.contents.split()[0]

    variants = map(lambda s: s.strip('\'" '), variantstring.split(","))
    return ExperimentNode(exp_name.strip('\'" '), variants)


class HypNode(template.Node):
    def __init__(self, nodelist, exp_name, exp_variant):
        self.nodelist = nodelist
        self.exp_name = exp_name
        self.exp_variant = exp_variant

    def render(self, context):
        ctxvar = CTX_PREFIX + self.exp_name

        if ctxvar not in context:
            raise ExperimentNotDeclaredException(self.exp_name)

        if self.exp_variant == context[ctxvar]:
            return self.nodelist.render(context)

        return ""

@register.tag('hyp')
def do_hyp(parser, token):
    try:
        tag_name, exp_name, exp_variant = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly two arguments" % token.contents.split()[0]

    nodelist = parser.parse(('endhyp',))
    parser.delete_first_token()
    return HypNode(nodelist, exp_name.strip('\'" '), exp_variant.strip('\'"'))

