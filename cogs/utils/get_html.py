import jinja2
from jinja2 import Template


def get_string(elements):
    with open('cogs/utils/index.html', 'r') as f:
        string = f.read()
    template = Template(string)

    return template.render(a=elements, r=range(len(elements)))