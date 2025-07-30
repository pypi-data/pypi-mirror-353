import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from aiohttp import web

from src.pybootstrapgui import Page
from src.pybootstrapgui.utils import copy_bootstrap_static_to
from src.pybootstrapgui.components import Body, Head, Paragraph, Script, Icon

copy_bootstrap_static_to("./static/")

class TestPage(Page):
    def __init__(self):
        super().__init__()
        self.tree = self.doc.xml_html

    def compose(self):
        with Head("MyApp", bootstrap_css="static/css/bootstrap.min.css", bootstrap_icons_css="static/css/bootstrap-icons.min.css"):
            internal_script_js = """console.log('Hello World');"""
            yield Script(js=internal_script_js)
        # https://getbootstrap.com/docs/5.3/customize/color-modes/#enable-dark-mode
        with Body(style="font-size: 14px; background-color: #f0f0f0", bootstrap_js="static/js/bootstrap.bundle.min.js"):  # Change Theme: **{"data-bs-theme": "dark"}
            yield Paragraph("App name", style="word-break: break-word;")
            yield Icon("circle")


test_page = TestPage()

web_app = web.Application()
routes = web.RouteTableDef()


@routes.get("/")
async def index(request: web.Request):
    html = test_page.build()
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
