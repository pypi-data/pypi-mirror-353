import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.pybootstrapgui.html_builder import Doc

if __name__ == "__main__":
    doc = Doc()

    with doc.tag("head"):
        doc.tag("meta", {"charset": "utf-8"})()
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
        with doc.tag("div") as div:
            div.text = "{% if title %}"
            doc.tag("button", {"class": "btn btn-primary", "type": "button"})("Submit")
            div[-1].tail = "{% endif %}"
    # print(doc.build(indent=True, short_empty_elements=False))
    doc.save(indent=True, short_empty_elements=False)
