# assert __name__ != "__main__", "It's not main!!!"

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.absolute()))

from src.pybootstrapgui import tag
from src.pybootstrapgui.base import CustomComponent
from src.pybootstrapgui import Page
from src.pybootstrapgui.components import (
    Body,
    Button,
    Card,
    CardGroup,
    Collapsable,
    Column,
    Container,
    Head,
    Header,
    Heading,
    NavbarOld,
    NavbarBrand,
    NavbarLink,
    NavbarNav,
    NavbarToggler,
    OffcanvasOld,
    OffcanvasToggler,
    Paragraph,
    Row,
    Script,
    Style,
)
from src.pybootstrapgui.html_builder import Doc
from src.pybootstrapgui.tag import Div  # Most popular tag
from src.pybootstrapgui.utils import B, C, D, H, R, V, copy_bootstrap_static_to

# ============================================================================================
#                                           CUSTOM EXAMPLES
# ============================================================================================
"""
You can't use doc.tag() in CustomComponent but you can use tag.Div() or other tag component
"""


class CustomOffcanvasSideBar(CustomComponent):

    def __init__(self, toggler="customOffcanvasToggler1", **kwargs):
        self.toggler = toggler
        self.kwargs = kwargs
        super().__init__()

    def compose(self):
        yield OffcanvasToggler(toggler=self.toggler, style="width: 50px; height: 40px")
        with OffcanvasOld(possition="start", toggler=self.toggler):
            yield Heading(3, "This is sidear", v_align="center", h_align="center")
            yield Button("Some button", color="warning", v_align="center")


class CustomResponsiveOffcanvasSideBar(CustomComponent):

    def __init__(self, toggler="customOffcanvasToggler2", collapse_at="md", **kwargs):
        self.toggler = toggler
        self.collapse_at = collapse_at
        self.kwargs = kwargs
        super().__init__()

    def compose(self):
        # with Container(v_align="end"):
        yield OffcanvasToggler(size="lg", toggler=self.toggler, show_at=self.collapse_at)
        with OffcanvasOld(position="end", toggler=self.toggler, collapse_at=self.collapse_at):
            yield Heading(1, "This is responsive sidear", v_align="center", h_align="center")


class CustomNavBarTopBrand(CustomComponent):

    def __init__(self, toggler="CustomNavBarTopBrand1", **kwargs):
        self.toggler = toggler
        self.kwargs = kwargs
        super().__init__()

    def compose(self):
        with NavbarOld(position="sticky-top", expand="md", container="lg", **self.kwargs):
            """container "lg" means that content will use "container-flex" for screns lower then lg and "container" for screens bigger than lg"""
            yield NavbarBrand(width="30", height="30")  # style="margin: 0px 8px;"
            yield NavbarToggler(target=self.toggler)
            with Collapsable(toggler=self.toggler):
                with NavbarNav():

                    # with Div(class_="nav-item"):
                    #     yield Button(
                    #         "",
                    #         icon="list",
                    #         color="dark",
                    #         outline=True,
                    #         style="margin-top: 5px;",
                    #         class_="btn-lg",
                    #     )

                    yield NavbarLink("Active", "", class_="active")
                    yield NavbarLink("Cart", "cart")
                    yield NavbarLink("Profile", "person")
                    yield NavbarLink("Disabled", "table", class_="disabled")

                with NavbarNav(class_="ms-md-auto"):
                    with Div(class_="nav-item"):
                        with Div(class_="d-inline-block"):
                            yield Button("Login", color="dark", outline=True)
                            yield Button("SignUp", color="dark", style="margin-left: 5px;")


class CustomNavBarBottomButtons(CustomComponent):

    def __init__(self, toggler="CustomNavBarBottomButtons1", **kwargs):
        self.toggler = toggler
        self.kwargs = kwargs
        super().__init__()

    def compose(self):
        with NavbarOld(position="fixed-bottom", expand=True, container="fluid", **self.kwargs):
            with NavbarNav(type="pills", fill=True):
                yield NavbarLink("Active", "", class_="active bg-warning text-dark")
                yield NavbarLink("Cart", "cart")
                yield NavbarLink("Profile", "person")
                yield NavbarLink("Disabled", "table", class_="disabled")


class CustomButtonsSet(CustomComponent):

    def __init__(self, **kwargs):
        super().__init__()

    def compose(self):
        with Container(id="CustomButtonsSet"):
            with Row():
                with Column(display="flex", v_align="center", h_align="center"):
                    """As you see it is not a good practice to use v_align and h_align on the button itelf. It is better to use on the column, container and etc"""
                    yield Button("", icon="info", style="font-size: 2rem; color: white;")
                with Column():
                    yield Button("Submit", v_align="center", h_align="center", style="margin: 10px")
                with Column(display="flex", v_align="center", h_align="center"):
                    """BUTTONS GROUP"""
                    with Div(class_="btn-group"):
                        yield Button("Light", color="dark", outline=True)
                        yield Button("Dark", color="dark")


class CustomCardsGroup(CustomComponent):

    def __init__(self, img: str, **kwargs):
        self.img = img
        self.kwargs = kwargs
        super().__init__()

    def compose(self):
        with Container(br="xs", display="flex", v_align="center"):
            card_group_css = "flex-flow: row wrap;"
            with CardGroup(style=card_group_css, class_="d-flex justify-content-center"):
                card_css = "min-width: 9rem; max-width: 15rem; flex: 1 0 0%; border-radius: 0; margin: 0;"
                for i in range(6):
                    with Card(header="Header", body="Body text", footer="Footer", img=self.img, style=card_css, class_="text-center"):  # style="width: 18rem;"
                        yield Heading(h=6, text="200 uah", v_align="end", style="font-weight: bold;")


class CustomCardsGrid(CustomComponent):

    def __init__(self, img: str, **kwargs):
        self.img = img
        self.kwargs = kwargs
        super().__init__()

    def compose(self):
        with Container():
            with Row(class_="row-cols-xs-2 row-cols-sm-3 row-cols-md-4 row-cols-lg-5 row-cols-xl-6 g-4"):  # row-cols-auto
                card_css = "min-width: 9rem; max-width: 15rem;"
                with Column(class_=""):
                    with Card(header="Header", body="hello World" * 20, footer="Footer", img=self.img, style=card_css, class_="h-100"):
                        yield Heading(h=6, text="200 uah", v_align="end", h_align="end", style="font-weight: bold;")
                for i in range(10):
                    with Column(class_=""):
                        with Card(header="Header", body="hello World", footer="Footer", img=self.img, style=card_css, class_="h-100"):
                            yield Heading(h=6, text="200 uah", v_align="end", h_align="end", style="font-weight: bold;")


# ============================================================================================
#                                          CUSTOM
# ============================================================================================


class ShopPage(Page):
    def __init__(self):
        super().__init__()

    def compose(self):
        with Head("MyApp"):
            internal_script_js = """console.log('Hello World');"""
            yield Script(js=internal_script_js)
        # https://getbootstrap.com/docs/5.3/customize/color-modes/#enable-dark-mode
        with Body(style="font-size: 14px;"):  # Change Theme: **{"data-bs-theme": "dark"}

            yield from CustomNavBarTopBrand()

            with Container():
                with Row():
                    with Column(display="flex", v_align="start"):
                        yield from CustomOffcanvasSideBar()
                    with Column(display="flex", v_align="end"):
                        yield from CustomResponsiveOffcanvasSideBar()

            yield Div(class_="mt-2")
            with Container():
                yield Heading(1, "This is bootstrap builder example!!!", v_align="center", h_align="center")
                yield Paragraph("Nice to see you", v_align="center", h_align="center")

            yield from CustomButtonsSet()

            img = "https://m.media-amazon.com/images/I/61bK6PMOC3L._AC_UF1000,1000_QL80_.jpg"

            yield from CustomCardsGroup(img=img)

            yield tag.Br()

            yield from CustomCardsGrid(img=img)

            """to see scrolling"""
            for i in range(20):
                yield Heading(1, "##############", v_align="center", h_align="center")
            yield Heading(1, "END", v_align="center", h_align="center", class_="mb-5")

            yield Div(style="margin-bottom: 5rem;")  # Important to see all content
            # yield Div(class_="mb-5") #
            yield from CustomNavBarBottomButtons()


if __name__ == "__main__":
    app = ShopPage()
    app.save(indent=True, short_empty_elements=False)
    app.open()
