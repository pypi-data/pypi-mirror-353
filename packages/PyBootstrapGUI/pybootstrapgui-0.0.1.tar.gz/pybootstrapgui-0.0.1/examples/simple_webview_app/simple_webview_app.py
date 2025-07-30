import sys
from pathlib import Path

import webview

from pybootstrapgui import Page
from pybootstrapgui.components import (Body, Button, Container, Form,
                                       FormControl, FormLabel, FormText, Head,
                                       Script, Style)
from pybootstrapgui.utils import B, C, D, H, R, V, copy_bootstrap_static_to

ROOT_DIR = Path(__file__).parent.absolute()


class CalculatorPage(Page):
    def __init__(self):
        super().__init__()
        copy_bootstrap_static_to(str(ROOT_DIR / "static"))

    def compose(self):
        with Head(
            title="Calculator",
            bootstrap_css="static/css/bootstrap.min.css",
            bootstrap_icons_css="static/css/bootstrap-icons.min.css",
        ):
            pass
        with Body(
            style="font-size: 14px; background-color: #f0f0f0",
            bootstrap_js="static/js/bootstrap.bundle.min.js",
        ):
            with Container(display="flex", class_=f"{V.CENTER} {H.CENTER} vh-100"):
                with Container(
                    br="sm",
                    class_="rounded-3 p-4",
                    style="min-width: 200px; max-width: 350px; background-color: #fff;",
                ):
                    with Form(id="CalculatorForm") as form:
                        yield FormControl(
                            class_="my-4",
                            id="DataInput",
                            type="text",
                            name="data_input",
                            placeholder="10 + 12",
                            required="true",
                        )
                        with Container("flex", display="flex", class_=f"{V.CENTER} gap-3"):
                            btn = Button(id="CancelButton", text="Cancel", color="warning", icon="lock", class_="w-50")
                            btn.listener("click", "async (event) => { await window.pywebview.api.cancel(); }")
                            yield btn
                            yield Button(text=" Calculate", type="submit", icon="calculator", class_="w-50")
                        js = """
                        async function (event) {
                            event.preventDefault(); // Prevent the default form submission
                            input = document.querySelector('#DataInput');
                            const data = input.value.trim();
                            const result = await window.pywebview.api.calculate(data);
                            alert(result);
                        }
                        """
                        form.listener("submit", js)


class JsApi:
    def __init__(self):
        pass

    def calculate(self, data):
        return eval(data)

    def cancel(self):
        print("Cancel")
        sys.exit()  # Not working as it is in separate thread


class WebviewCalculatorApp:

    def __init__(self) -> None:
        CalculatorPage().save(ROOT_DIR / "index.html", indent=True)

        self.window = webview.create_window(
            title="WebviewCalculatorApp",
            url="index.html",
            js_api=JsApi(),
        )

    def run(self):
        webview.start(private_mode=True, debug=False)


if __name__ == "__main__":
    WebviewCalculatorApp().run()
