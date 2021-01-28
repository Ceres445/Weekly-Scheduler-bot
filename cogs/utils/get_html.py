from jinja2 import Template
import imgkit
from io import BytesIO

def get_string(elements):
    with open('cogs/utils/index.html', 'r') as f:
        string = f.read()
    template = Template(string)
    buffer = BytesIO()
    imgkit.from_string(template.render(a=elements, r=range(len(elements))), False).save(buffer, "png")
    buffer.seek(0)
    return buffer
