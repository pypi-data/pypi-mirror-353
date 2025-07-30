import io
import os
import sys
import tempfile
import time
import webbrowser
from pathlib import Path
from xml.dom import minidom
from xml.etree import ElementTree as ET

"""
Known issues:
1) Self closing tags
    XML makes empty elemens(Without other element or text inside) - self closing like <i> tag
    But in html it is not self closing and this causes errors
    To fix this you can either add space as a text or append empty self closing tag or use ET.tostring(html, short_empty_elements=False)
2) Element text placed before embeded element
   When you use element.text = "Text" it places it before inner element like <div>Text<div></div></div>
   If you want text to be after inner element you should use div2.tail = "Text" for INNER element <div><div></div>Text</div>
"""


class Doc:
    def __init__(self) -> None:
        self.xml_html = ET.Element("html")
        self.elements_stack = [self.xml_html]

        class Tag:

            def __init__(selft, tag: str, attr={}) -> None:
                """
                Be aware of selfTTTT
                """
                selft.doc = self
                selft.tag = tag
                selft.attr = attr
                selft.element = None

                # Prevoiusly was inside __enter__
                selft.element = ET.Element(selft.tag, attrib=selft.attr)
                selft.doc.elements_stack[-1].append(selft.element)
                selft.doc.elements_stack.append(selft.element)

            def __enter__(selft) -> ET.Element:
                return selft.element

            def __exit__(selft, *args, **kwargs):
                selft.doc.elements_stack.pop()

            def __call__(selft, text: str = None, *args, **kwds) -> ET.Element:
                if text:
                    selft.element.text = text
                selft.__exit__()
                return selft.element

        self.tag = Tag

    def build(self, indent=False, short_empty_elements=True) -> str:
        if indent:
            string = io.StringIO()
            tree = ET.ElementTree(self.xml_html)
            ET.indent(tree)
            tree.write(
                string,
                encoding="unicode",
                method="html",
                short_empty_elements=short_empty_elements,
            )
            string.seek(0)
            html = string.read()
        else:
            html = ET.tostring(
                self.xml_html,
                encoding="unicode",
                method="html",
                short_empty_elements=short_empty_elements,
            )
        # if indent:
        #     html = minidom.parseString(html).toprettyxml(indent="  ")
        #     html = "\n".join(html.split("\n")[1:])
        html = "<!DOCTYPE html>" + ("\n" if indent else "") + html
        return html

    def save(self, path="index.html", indent=False, short_empty_elements=True):
        html = self.build(indent=indent, short_empty_elements=short_empty_elements)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    def open(self):
        path = Path() / "_index.html"
        html = self.build(indent=False, short_empty_elements=False)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        webbrowser.open("file://" + os.path.realpath(path))
        # temp = tempfile.NamedTemporaryFile(
        #     prefix="html_builder_", suffix=".html", delete=False
        # )
        # temp.write(self.build(short_empty_elements=False).encode("utf-8"))
        # # temp.seek(0)
        # temp.close()
        # webbrowser.open("file://" + os.path.realpath(temp.name))
        # time.sleep(3)
        # os.remove(os.path.realpath(temp.name))


if __name__ == "__main__":
    doc = Doc()

    with doc.tag("head"):
        doc.tag("meta", {"charset": "utf-8"})()
        doc.tag("title")("Title")
        with doc.tag("title") as e:
            e.text = "Title"
        doc.tag(
            "link",
            {"rel": "stylesheet", "href": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"},
        )()

        with doc.tag("script", {"type": "text/javascript"}) as script:
            inline_script_js = """console.log('Hello World');"""
            script.text = inline_script_js
    with doc.tag("body"):
        with doc.tag("div", {"class": "d-flex justify-content-center"}) as div:
            doc.tag("button", {"class": "btn btn-primary", "type": "button"})("Submit")
        doc.tag("br")()
        with doc.tag("div", {"class": "d-flex justify-content-center"}) as div:
            doc.tag("button", {"class": "btn btn-primary", "type": "button"})("Submit")
        doc.tag("script", {"src": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"})()

    print(doc.build(indent=True, short_empty_elements=False))
    doc.save()
