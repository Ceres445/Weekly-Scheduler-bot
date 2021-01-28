from jinja2 import Template
import imgkit

def get_string(elements):
    with open('cogs/utils/index.html', 'r') as f:
        string = f.read()
    template = Template(string)

    imgkit.from_string(template.render(a=elements, r=range(len(elements))), 'out.jpg')