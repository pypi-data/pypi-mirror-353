import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import base64
import time
import shutil

import webview
from examples.locker_bootstrap_app.locker_bootstrap_page import LockerPage

try:
    from winytils.windows import (
        Windows,
        set_window_fullscreen,
        set_window_overrideredirect,
        set_window_topmost,
    )
except Exception as e:
    pass

from src.pybootstrapgui.extensions.jinja_components import render_template

locker_page = LockerPage()


class JsApi:
    def __init__(self):
        self._window = None
        self._password = None
        self._result = False
        # self._window_title = ""
        # self._window_icon = ""

    def set_window(self, window: webview.Window):
        self._window = window

    def set_password(self, password: str):
        self._password = password

    def unlock(self, password):
        if password == self._password:
            self._result = True
            self._window.destroy()
        else:
            return False

    def cancel(self):
        self._window.destroy()

    # def get_window_title(self):
    #     return self._window_title

    # def get_window_icon(self):
    #     return self._window_icon


class AppLocker:
    PATH_FILE_HTML = Path(__file__).parent.absolute() / "index.html"
    # shutil.copytree("static", str(Path(__file__).parent.absolute() / "static"), dirs_exist_ok=True)

    def __init__(
        self,
        browser_title="AppLocker",
        jinja_title: str = None,
        jinja_base64_icon: str = None,
        password="0000",
        cancel_button=True,
        auto_destroy=-1,
    ) -> None:
        self.js_api = JsApi()

        self.browser_title = browser_title

        html = locker_page.build(indent=True)
        html = render_template(html, title=jinja_title, icon=jinja_base64_icon, cancel=cancel_button)
        with open(self.PATH_FILE_HTML, "w", encoding="utf-8") as f:
            f.write(html)

        self.js_api.set_password(password)
        self.auto_destroy = auto_destroy

        maximized = True
        fullscreen = True
        resizable = True
        on_top = True

        self.window = webview.create_window(
            title=self.browser_title,
            url="index.html",
            js_api=self.js_api,
            maximized=maximized,
            fullscreen=fullscreen,
            resizable=resizable,
            # on_top=on_top,
        )
        self.js_api.set_window(self.window)

    def run(self):

        self.window.events.loaded += self.onload
        self.window.events.closed += lambda: print("AppLocker window is closed")

        # Should be started in the proccess, not thread
        webview.start(private_mode=True, debug=False)

        return self.js_api._result

    def onload(self):
        stop = False
        while True:
            time.sleep(0.1)
            windows = Windows.filter(has_gui=True, opened=None, has_title=True)
            for w in windows:
                if w.title == self.browser_title:
                    time.sleep(0.01)
                    # try:
                    #     w.activate()
                    # except Exception as e:
                    #     pass
                    # time.sleep(0.01)
                    # w.maximize()
                    # time.sleep(0.01)
                    # set_window_fullscreen(w.hwnd)
                    time.sleep(0.01)
                    set_window_overrideredirect(w.hwnd)
                    # time.sleep(0.01)
                    # set_window_topmost(w.hwnd)
                    # time.sleep(0.01)
                    # try:
                    #     w.activate()
                    # except Exception as e:
                    #     pass
                    stop = True
                    break
            if stop:
                break
        if self.auto_destroy > 0:
            time.sleep(self.auto_destroy)
            self.window.destroy()


if __name__ == "__main__":
    with open(Path(__file__).parent / "static/images/favicon.ico", "rb") as f:
        favicon_data = f.read()
    base64_icon = base64.b64encode(favicon_data).decode()
    result = AppLocker(jinja_title="Zebra", jinja_base64_icon=base64_icon, auto_destroy=10).run()
    print(result)
