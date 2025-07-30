import re

from ..base import Component


class Comment(Component):
    def __init__(self, **kwargs) -> None:
        """
        !IMPORTANT: Use comments_postprocessing() method from extension
        Component used to create jinja template condition.

        Args:
            condition (str, required): Condition to be checked. E.g. "{% if title %}"
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="html_comment", **kwargs)
        pass


def comments_postprocessing(html: str) -> str:
    html = html.replace("<html_comment>", "/*")
    html = html.replace("</html_comment>", "*/")
    return html
    # re.sub(r"<html_comment>", "/*", html)
    # re.sub(r"</html_comment>", "*/", html)
