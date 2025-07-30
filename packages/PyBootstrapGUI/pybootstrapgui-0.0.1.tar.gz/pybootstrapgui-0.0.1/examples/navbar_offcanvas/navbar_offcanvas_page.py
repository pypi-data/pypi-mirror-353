# assert __name__ != "__main__", "It's not main!!!"
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.absolute()))

from src.pybootstrapgui import Page
from src.pybootstrapgui.base import CustomComponent, Component, ComponentBase
from src.pybootstrapgui.components import (
    Body,
    Button,
    Card,
    CardGroup,
    Collapsable,
    Column,
    Container,
    Dropdown,
    DropdownItem,
    DropdownMenu,
    DropdownToggleButton,
    Form,
    FormControl,
    FormLabel,
    FormText,
    Head,
    Header,
    Heading,
    Image,
    Navbar,
    NavbarBrand,
    NavbarLink,
    NavbarNav,
    NavbarToggler,
    NavItem,
    NavbarCollapse,
    Offcanvas,
    OffcanvasBody,
    OffcanvasCloseButton,
    OffcanvasHeader,
    OffcanvasOpenButton,
    OffcanvasTitle,
    OffcanvasToggler,
    Paragraph,
    Row,
    Script,
    Style,
    ButtonGroup,
    RadioButton,
)
from src.pybootstrapgui.extensions.jinja_components import (
    JinjaCondition,
    JinjaLoop,
    render_template,
)
from src.pybootstrapgui.extensions.pywebview_utils import pywebvew_button_js
from src.pybootstrapgui.tag import Div, Template
from src.pybootstrapgui.utils import B, C, D, H, R, V, copy_bootstrap_static_to

ROOT_DIR = Path(__file__).parent.absolute()


def Node():
    # fmt:off
    with Div(class_="node-container border-start ps-3"):
        with Div(class_="node"):
            with Container(br="flex", class_=f"{D.FLEX}"):
                yield Button(text="+", size="sm", outline="True", color="dark", class_="btn-no-hover p-0 me-2", style="border: none;") # style="font-size: 0.5rem; border: none;"
                yield Div(class_=f"title-edit {D.NONE}", text="Zebra")
                yield Div(class_="title-render editable", text="Zebra", contenteditable=True, spellcheck=True, autocorrect=False)
            yield Div(class_=f"note-edit ms-4 {D.NONE}", text="Bebra")
            yield Div(class_="note-render ms-3", text="Bebra", style="font-size: 0.8rem;")
            yield Div(id="Roman", class_="node-container")
    # fmt:on


class Page(Page):
    def __init__(self):
        super().__init__()
        # copy_bootstrap_static_to(str(ROOT_DIR / "static"))

    def compose(self):
        import sourcetypes

        # fmt:off
        with Head(title="Title"):
            # with Head(title="Title"):
            js: sourcetypes.js = """

            console.log('Hello World');
            """
            yield Script(js=js)
            css: sourcetypes.css = """

            .dropdown-toggle::after { 
                content: none; 
            }
            
            .btn-no-hover:hover, .btn-no-hover:focus, .btn-no-hover:active {
                background-color: inherit !important;
                color: inherit !important;
                box-shadow: none !important;    
            }
            
            .editable {
                white-space: pre-wrap;
                word-wrap: break-word;
                user-select: text;
            }
            
            .editable[contenteditable]:focus {
                outline: none; /* Removes the orange border */
            }
            """
            yield Style(css=css)
        # with Body(style="font-size: 14px; background-color: #f0f0f0"):
        with Body():
            with Header(class_="app-header"): # style="font-size: 0.6rem;"
                with Navbar(position="fixed-top", class_="shadow py-1"):
                    with Container(br="fluid"):
                        yield OffcanvasOpenButton(offcanvas_id="offcanvasExample", text="", outline=True, icon="list", color=C.SECONDARY, class_="btn-no-hover py-0", style="font-size: 1.3rem; border: none;")
                        with Div(class_=f"{D.FLEX} ms-auto"):
                            with ButtonGroup(class_="pe-sm-3"):
                                yield RadioButton(id="radio1", icon="file-earmark-code", text="", color="secondary", outline=True, size="sm", checked=True)
                                yield RadioButton(id="radio2", icon="file-earmark-font", text="", color="secondary", outline=True, size="sm")
                                yield RadioButton(id="radio3", icon="file-earmark-richtext", text="", color="secondary", outline=True, size="sm")
                        with Div(class_=f"{D.FLEX} {H.CENTER}"):
                            yield Button(text="", icon="arrow-return-left", color="secondary", outline=True, class_="btn-no-hover py-0", style="border: none;")
                            yield Button(text="", icon="card-checklist", color="secondary", outline=True, class_="btn-no-hover py-0", style="border: none;")
                            yield Button(text="", icon="search", color="secondary", outline=True, class_="btn-no-hover py-0", style="border: none;")
                            yield Button(text="", icon="lock", color="secondary", outline=True, class_="btn-no-hover py-0", style="border: none;")
                            with Dropdown():
                                yield DropdownToggleButton(text="", icon="three-dots-vertical", color="secondary", outline=True, class_="btn-no-hover py-0", style="border: none;")
                                with DropdownMenu(class_="dropdown-menu-end"):
                                    yield DropdownItem("Zebra")
                                    yield DropdownItem("Account")
                                    yield DropdownItem("Settings")
                                
                        
            with Offcanvas(id="offcanvasExample", scroll=True, backdrop=False, labelledby="offcanvasExampleLabel", style="max-width: 250px;"):
                with OffcanvasHeader(class_="shadow py-0"):
                    yield OffcanvasTitle(h=3, id="offcanvasExampleLabel", text="TreeRo")
                    yield OffcanvasCloseButton(class_="py-3")
                with OffcanvasBody():
                    yield Paragraph("Hello world")
                    


            with Container(br="sm", class_="py-5 my-5"):
                with Container(br="sm", class_="px-sm-5 mx-sm-5"):
                    with Container(br="md", class_="px-md-5 mx-md-5"):
                        with Container(br="lg", class_="px-lg-5 mx-lg-5"):
                            # with Template():
                            #     pass
                            yield Heading(h=3, text="Zebra")
                            for i in range(100):
                                with Div(class_="node-container border-start ps-3"):
                                    with Div(class_="node"):
                                        with Container(br="flex", class_=f"{D.FLEX}"):
                                            yield Button(text="+", size="sm", outline="True", color="dark", class_="btn-no-hover p-0 me-2", style="border: none;") # style="font-size: 0.5rem; border: none;"
                                            yield Div(class_=f"title-edit {D.NONE}", text="Zebra")
                                            yield Div(class_="title-render editable", text="Zebra", contenteditable=True, spellcheck=True, autocorrect=False)
                                        yield Div(class_=f"note-edit ms-4 {D.NONE}", text="Bebra")
                                        yield Div(class_="note-render ms-3", text="Bebra", style="font-size: 0.8rem;")
                                        with Div(id="Roman", class_="node-container"):
                                            yield from Node()
                                    


if __name__ == "__main__":
    import webbrowser

    page = Page()
    html = page.build(indent=True)
    html = render_template(html, title="Zebra")
    html_file = ROOT_DIR / "index.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)

    webbrowser.open("file://" + str(html_file))
