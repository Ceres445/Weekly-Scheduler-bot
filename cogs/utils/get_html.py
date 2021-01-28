import os
import subprocess
from io import BytesIO

import imgkit
from PIL import Image
from jinja2 import Template

if 'DYNO' in os.environ:
    print('loading wkhtmltopdf path on heroku')
    WKHTMLTOPDF_CMD = subprocess.Popen(
        ['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf-pack')],
        # Note we default to 'wkhtmltopdf' as the binary name
        stdout=subprocess.PIPE).communicate()[0].strip()
else:
    print('loading wkhtmltopdf path on localhost')
    MYDIR = os.path.dirname(__file__)
    WKHTMLTOPDF_CMD = os.path.join(MYDIR + "/static/executables/bin/", "wkhtmltoimage.exe")


def get_string(elements):
    with open('cogs/utils/index.html', 'r') as f:
        string = f.read()
    template = Template(string)
    config = imgkit.config(wkhtmltoimage=WKHTMLTOPDF_CMD)
    img = imgkit.from_string(template.render(a=elements, r=range(len(elements)),
                                             k=[range(i['span']) for i in elements.values()]), False, config=config)
    print(img[:20])
    buffer = BytesIO(img)
    buffer.seek(0)
    image = Image.open(buffer)
    buff = BytesIO()
    size = image.size
    image1 = image.crop((1, 2, 350, size[1]-1))
    image1.save(buff, 'png')
    buff.seek(0)
    return buff
