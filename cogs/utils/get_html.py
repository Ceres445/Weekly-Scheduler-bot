import subprocess

from jinja2 import Template
import imgkit
from io import BytesIO
import os

if 'DYNO' in os.environ:
    print('loading wkhtmltopdf path on heroku')
    WKHTMLTOPDF_CMD = subprocess.Popen(
        ['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf-pack')],
        # Note we default to 'wkhtmltopdf' as the binary name
        stdout=subprocess.PIPE).communicate()[0].strip()
else:
    print('loading wkhtmltopdf path on localhost')
    MYDIR = os.path.dirname(__file__)
    WKHTMLTOPDF_CMD = os.path.join(MYDIR + "/static/executables/bin/", "wkhtmltopdf.exe")


def get_string(elements):
    with open('cogs/utils/index.html', 'r') as f:
        string = f.read()
    template = Template(string)

    config = imgkit.config(wkhtmltoimage=WKHTMLTOPDF_CMD)
    options = {'format': 'png', 'width': '640', 'height': '480'}
    img = imgkit.from_string(template.render(a=elements, r=range(len(elements))), False, config=config, options=options)
    buffer = BytesIO(img)
    buffer.seek(0)
    return buffer
