from typing import Union, Callable


def pywebvew_button_js(button_id: str, func: Union[str, Callable]) -> str:
    # func.__code__.co_varnames
    name = func
    if callable(func):
        name = func.__name__
    js = """
    document.querySelector('#%s').addEventListener('click', async function(event) {
        await window.pywebview.api.%s();
    });
    """
    js = js.replace("%s", button_id, 1)
    js = js.replace("%s", name, 1)
    return js.strip()
