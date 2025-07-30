assert __name__ != "__main__", "It's not main!!!"
from pathlib import Path

from src.pybootstrapgui import Page
from src.pybootstrapgui.base import CustomComponent
from src.pybootstrapgui.components import (
    Body,
    Button,
    Card,
    CardGroup,
    Collapsable,
    Column,
    Container,
    Form,
    FormControl,
    FormLabel,
    FormText,
    Head,
    Header,
    Heading,
    Image,
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
from src.pybootstrapgui.extensions.jinja_components import JinjaCondition, JinjaLoop
from src.pybootstrapgui.extensions.pywebview_utils import pywebvew_button_js
from src.pybootstrapgui.tag import Div, Template
from src.pybootstrapgui.utils import B, C, D, H, R, V, copy_bootstrap_static_to


class LockerPage(Page):
    def __init__(self):
        super().__init__()
        copy_bootstrap_static_to(str(Path(__file__).parent.absolute() / "static"))

    def compose(self):
        with Head(title="Title", bootstrap_css="static/css/bootstrap.min.css", bootstrap_icons_css="static/css/bootstrap-icons.min.css"):
            # with Head(title="Title"):
            internal_script_js = """console.log('Hello World');"""
            yield Script(js=internal_script_js)
        # https://getbootstrap.com/docs/5.3/customize/color-modes/#enable-dark-mode
        with Body(style="font-size: 14px; background-color: #f0f0f0", bootstrap_js="static/js/bootstrap.bundle.min.js"):  # Change Theme: **{"data-bs-theme": "dark"}
            # with Body(style="font-size: 14px; background-color: #f0f0f0"):
            with Container(display="flex", class_=f"{V.CENTER} {H.CENTER} vh-100"):
                with Container(br="sm", class_="rounded-3 p-4", style="min-width: 200px; max-width: 350px; background-color: #fff;"):
                    with Container("flex", class_="text-center"):
                        with JinjaCondition("{% if icon %}"):
                            yield Image(src="data:image/png;base64,{{ icon }}", alt="image")
                        with JinjaCondition("{% if title %}"):
                            yield Paragraph("{{ title }}", style="word-break: break-word;")
                    with Form(id="LockerForm") as form:
                        yield FormControl(class_="my-4", id="PasswordFormInput", type="password", name="password", placeholder="Password", description="EmailFieldDescription", required="true")
                        # yield FormLabel("Email address", for_="EmailFormInput")
                        # yield FormControl(id="EmailFormInput", type="email", name="email", placeholder="zebra@gmail.com", description="EmailFieldDescription")
                        # yield FormText("EmailFieldDescription", "We'll never share your email with anyone else.", class_="form-text")
                        with Container("flex", display="flex", class_=f"{V.CENTER} gap-3"):
                            # with Container("flex", display="grid", class_="gap-3 col-6 mx-auto"): # col-12(Responsible for width)
                            with JinjaCondition("{% if cancel %}"):
                                btn = Button(id="CancelButton", text="Cancel", color="warning", icon="lock", class_="w-50")
                                # btn.listener("click", 'async function(event) { console.log("Hello World"); }')
                                btn.listener("click", "async function(event) { await window.pywebview.api.cancel(); }")
                                yield btn
                                # yield Script(js=pywebvew_button_js("CancelButton", "cancel"))
                            # with JinjaCondition("{% if title %}"):
                            #     with JinjaLoop("{% for i in range(5) %}"):
                            #         yield Heading(1, "{{ title }}", class_="text-center")

                            btn = Button(text=" Unlock", type="submit", icon="unlock", class_="w-50")
                            yield btn
                            js = """
                            console.log("love me");
                            """
                            yield Script(js=js)
                        js = """
                        async function (event) {
                            event.preventDefault(); // Prevent the default form submission
                            passwordInput = document.querySelector('#PasswordFormInput');
                            const enteredPassword = passwordInput.value.trim();
                            const result = await window.pywebview.api.unlock(enteredPassword);

                            if (result === false) {
                                // showError("Incorrect password. Please try again.");
                                alert("Incorrect password. Please try again.");
                                passwordInput.focus();
                            }
                        }
                        """
                        form.listener("submit", js)


if __name__ == "__main__":
    page = LockerPage()
    page.save(indent=True, short_empty_elements=False)
    page.open()
