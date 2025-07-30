import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import base64

from aiohttp import web
from jinja2 import Template
from examples.locker_bootstrap_app.locker_bootstrap_page import LockerPage

from src.pybootstrapgui.extensions.jinja_components import render_template

locker_page = LockerPage()

web_app = web.Application()
routes = web.RouteTableDef()


@routes.get("/")
async def index(request: web.Request):
    html = locker_page.build(indent=True)

    with open("static/images/favicon.ico", "rb") as f:
        favicon_data = f.read()

    html = render_template(html, title="Zebra", icon=base64.b64encode(favicon_data).decode(), cancel=True)

    # el = bootstrap_app.find(".//input[@id='PasswordFormInput']")

    # template = Template(html)
    # bootstrap_app.save(indent=True) # Before postprocessing

    # html = template.render(title="Zebra", icon=base64.b64encode(favicon_data).decode(), cancel=True)

    # doc = pq(html)

    # elements_to_remove = doc("div[@class='jinja-condition']")
    # for el in elements_to_remove:
    #     # el = doc("div[@class='container-flex d-flex gap-3 justify-content-center']")[0]
    #     parent = el.getparent()
    #     index = parent.index(el)
    #     for kid in reversed(el.getchildren()):
    #         parent.insert(index, kid)
    #     parent.remove(el)

    # # html = "<!DOCTYPE html>\n" + str(doc)
    # html = str(doc)

    # import io

    # bytes = io.BytesIO()
    # bytes.write(html.encode())
    # bytes.seek(0)
    # tree = ET.parse(bytes)

    # root = tree.getroot()
    # list(list(root)[1]).insert(2, ET.Comment("{{ bebra }}"))

    # html = ET.tostring(
    #     root,
    #     encoding="unicode",
    #     method="html",
    #     short_empty_elements=True,
    # )

    # # root.insert(1, comment)  # 1 is the index where comment is inserted

    # bootstrap_app.doc.xml_html = tree.getroot()

    # html = bootstrap_app.build(indent=True)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    return web.Response(text=html, content_type="text/html")


@routes.get("/favicon.ico")
async def faviocon(request: web.Request):
    with open("static/images/favicon.ico", "rb") as f:
        favicon_data = f.read()
    return web.Response(body=favicon_data, content_type="image/x-icon")


if __name__ == "__main__":
    routes.static("/static/", "static", append_version=True)  # append_version responsable for cache busting
    web_app.add_routes(routes)
    web.run_app(web_app, host="localhost", port=8080)
