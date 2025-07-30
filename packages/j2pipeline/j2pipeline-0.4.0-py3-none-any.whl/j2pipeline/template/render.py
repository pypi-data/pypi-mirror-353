from j2pipeline.template.vars import get_vars, substitute

def render(template: str, subs: dict[str, str]) -> str:
    vars: dict[str, str] = get_vars(j2=template)
    return substitute(j2=template, subs=subs, vars=vars)