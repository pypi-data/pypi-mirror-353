from typing import Iterable, List
from xml.etree import ElementTree as ET

from .base import Base, ComponentBase
from .components import *
from .html_builder import Doc

# TODO: markdown to html, html into xml, append xml
# TODO: Wish: do everithing in python without raw js. Move element in python and it is moved inside DOM. Complete blend of bootstrap_builder and pywebview


class Page(Base):
    """
    """

    def __init__(self):
        """Actual build happens here"""
        self.doc = Doc()
        self._compose()
        self.tree = self.doc.xml_html

    def _compose(self) -> List["Component"]:
        components: List["Component"] = []
        compose_stack: List["Component"] = []
        composed: List["Component"] = []
        self.COMPOSE_STACKS.append(compose_stack)
        self.COMPOSED.append(composed)
        iter_compose = iter(self.compose())
        is_generator = hasattr(iter_compose, "throw")
        try:
            while True:
                try:
                    child = next(iter_compose)
                except StopIteration:
                    break

                if composed:
                    components.extend(composed)
                    composed.clear()
                if compose_stack:
                    try:
                        compose_stack[-1].compose_add_child(child)
                    except Exception as error:
                        if is_generator:
                            # So the error is raised inside the generator
                            # This will generate a more sensible traceback for the dev
                            iter_compose.throw(error)  # type: ignore
                        else:
                            raise
                else:
                    components.append(child)
            if composed:
                components.extend(composed)
                composed.clear()
        except Exception as e:
            raise e
        finally:
            self.COMPOSE_STACKS.pop()
            self.COMPOSED.pop()

        for component in components:
            component.render(self.doc)

        return components

    def open(self):
        self.doc.open()

    def build(self, indent=False, short_empty_elements=True) -> str:
        return self.doc.build(indent=indent, short_empty_elements=short_empty_elements)

    def save(self, path="index.html", indent=False, short_empty_elements=True):
        self.doc.save(path=path, indent=indent, short_empty_elements=short_empty_elements)

    def find(self, path: str, namespaces: dict = None) -> ET.Element:
        """
        _summary_

        Args:
            path (str): xpath to get element. E.g. ".//input[@id='PasswordFormInput']"
            namespaces (dict, optional): _description_. Defaults to None.

        Returns:
            ET.Element: _description_
        """
        return self.doc.xml_html.find(path=path, namespaces=namespaces)

    def findall(self, path: str, namespaces: dict = None) -> List[ET.Element]:
        return self.doc.xml_html.findall(path=path, namespaces=namespaces)

    def iter(self) -> Iterable[ET.Element]:
        return self.doc.xml_html.iter()

    def compose(self):
        raise NotImplementedError()
