from io import BytesIO
import cv2
import numpy as np
import imgkit
from PIL import Image
from jinja2 import Template


def get_string(elements):
    with open('cogs/utils/index.html', 'r') as f:
        string = f.read()
    template = Template(string)
    if elements.get('span', None) is not None:
        r = None
        day = 0
        k = range(elements['span'])
    else:
        r = range(len(elements))
        day = 1
        k = [range(i['span']) for i in elements.values()]
    config = imgkit.config(wkhtmltoimage="/app/bin/wkhtmltoimage")
    img = imgkit.from_string(template.render(a=elements, r=r,
                                             k=k, day=day), False, config=config)
    buffer = BytesIO(img)
    buffer.seek(0)
    image = Image.open(buffer)
    opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    blur = cv2.blur(opencvImage, (3, 3))
    canny = cv2.Canny(blur, 50, 200)
    pts = np.argwhere(canny > 0)
    y1, x1 = pts.min(axis=0)
    y2, x2 = pts.max(axis=0)
    cropped = opencvImage[y1 - 3:y2 + 3, x1 - 3:x2 + 3]
    is_success, buffer = cv2.imencode(".png", cropped)
    buff = BytesIO(buffer)

    buff.seek(0)
    return buff
