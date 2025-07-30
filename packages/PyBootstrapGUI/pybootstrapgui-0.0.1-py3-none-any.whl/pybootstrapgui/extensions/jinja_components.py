import io
import xml.etree.ElementTree as ET
from copy import deepcopy

try:
    from jinja2 import Template
    from pyquery import PyQuery as pq
except ImportError:
    print("pip install jinja2 pyquery")

from ..base import Component, Doc


def is_imported(module: str) -> bool:
    return module in globals()


class JinjaCondition(Component):
    def __init__(self, condition: str, **kwargs) -> None:
        """
        !IMPORTANT: Use render_template() method from extension
        Component used to create jinja template condition.

        Args:
            condition (str, required): Condition to be checked. E.g. "{% if title %}"
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", **kwargs)
        self.condition = condition

        self.class_ = ["jinja-condition"] + self.class_
        pass

    def render(self, doc: Doc):
        id = {"id": self.id} if self.id else {}
        class_ = {"class": " ".join([c for c in self.class_ if c])} if self.class_ else {}
        with doc.tag("div", {**id, **class_, **self.params, **self.kwargs}) as div:
            self.tag = div
            div.text = self.condition  # "{% if title %}"
            component: Component
            for component in self.children:
                component.render(doc)
            div[-1].tail = "{% endif %}"


class JinjaLoop(Component):
    def __init__(self, loop: str, **kwargs) -> None:
        """
        !IMPORTANT: Use render_template() method from extension
        Component used to create jinja template condition.

        Args:
            condition (str, required): Condition to be checked. E.g. "{% if title %}"
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", **kwargs)
        self.loop = loop

        self.class_ = ["jinja-loop"] + self.class_
        pass

    def render(self, doc: Doc):
        id = {"id": self.id} if self.id else {}
        class_ = {"class": " ".join([c for c in self.class_ if c])} if self.class_ else {}
        with doc.tag("div", {**id, **class_, **self.params, **self.kwargs}) as div:
            self.tag = div
            div.text = self.loop  # "{% for i in range(10) %}"
            component: Component
            for component in self.children:
                component.render(doc)
            div[-1].tail = "{% endfor %}"


def __pyquery_replace_elements(html: str, classes: list) -> str:
    doc = pq(html)
    elements_to_remove = []
    for class_ in classes:
        elements_to_remove += list(doc(class_))
    for el in elements_to_remove:
        parent = el.getparent()
        index = parent.index(el)
        for kid in reversed(el.getchildren()):
            parent.insert(index, kid)
        parent.remove(el)

    html = str(doc)
    return html


def html_pyquery_postprocessing(html: str):
    bytes = io.BytesIO()
    bytes.write(html.encode(encoding="utf-8"))
    bytes.seek(0)
    tree = ET.parse(bytes)

    string = io.StringIO()
    ET.indent(tree)
    # root = tree.getroot()
    tree.write(
        string,
        encoding="unicode",
        method="html",
        short_empty_elements=True,
    )
    string.seek(0)
    html = string.read()
    html = "<!DOCTYPE html>\n" + html
    return html


def render_template(html: str, *args, **kwargs) -> str:
    """
    TODO: I should able to save generated html and use standard Template later
    """
    if not is_imported("Template") and not is_imported("pq"):
        raise ImportError("pip install jinja2 pyquery")
    template = Template(html)
    html = template.render(*args, **kwargs)

    html = __pyquery_replace_elements(html, [".jinja-condition", ".jinja-loop"])
    html = html_pyquery_postprocessing(html)

    return html


def remove_element_keep_children(tree, el):
    # el = tree.find(".//div[@class='jinja-condition']")
    for parent in tree.iter():
        for child in parent:
            if child == el:
                index = list(parent).index(el)
                kids = deepcopy(list(child))
                parent.remove(child)
                for kid in reversed(kids):
                    parent.insert(index, kid)
            break
