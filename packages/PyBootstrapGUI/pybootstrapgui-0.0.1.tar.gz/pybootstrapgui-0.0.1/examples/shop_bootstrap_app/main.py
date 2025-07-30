import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from aiohttp import web
from examples.shop_bootstrap_app.shop_bootstrap_page import ShopPage

shop_page = ShopPage()

web_app = web.Application()
routes = web.RouteTableDef()


@routes.get("/")
async def index(request: web.Request):
    html = shop_page.build()
    return web.Response(text=html, content_type="text/html")


@routes.get("/favicon.ico")
async def faviocon(request: web.Request):
    with open("static/images/favicon.ico", "rb") as f:
        favicon_data = f.read()
    return web.Response(body=favicon_data, content_type="image/x-icon")


if __name__ == "__main__":
    # routes.static("/static/", "static", append_version=True)  # append_version responsable for cache busting
    web_app.add_routes(routes)
    web.run_app(web_app, host="localhost", port=8080)
