from .base import ComponentBase, Doc


class Tag(ComponentBase):
    """
    Can be used for any html tag
    yield Tag("div", "Hello world", class_="text-center")
    """

    def __init__(self, tag: str, text: str = None, **kwargs) -> None:
        super().__init__()
        self.tag = tag
        self.text = text
        if kwargs.get("class_"):
            kwargs["class"] = kwargs.pop("class_", "")
        for key, value in kwargs.items():
            if isinstance(value, bool):
                value = str(value).lower()
            kwargs[key] = str(value)
        self.kwargs = kwargs

    def render(self, doc: Doc):
        with doc.tag(self.tag, {**self.kwargs}) as tag:
            self.tag = tag
            if self.text:
                self.tag.text = self.text
            component: ComponentBase
            for component in self.children:
                component.render(doc)


class Template(Tag):

    def __init__(self, **kwargs) -> None:
        super().__init__(tag="template", **kwargs)


class Div(Tag):

    def __init__(self, **kwargs) -> None:
        super().__init__(tag="div", **kwargs)


class Br(Tag):

    def __init__(self, text="", **kwargs) -> None:
        super().__init__(tag="p", **kwargs)


class P(Tag):

    def __init__(self, text: str = None, **kwargs) -> None:
        super().__init__(tag="p", text=text, **kwargs)


class Form(Tag):

    def __init__(self, **kwargs) -> None:
        super().__init__(tag="form", **kwargs)


class Input(Tag):

    def __init__(self, **kwargs) -> None:
        super().__init__(tag="input", **kwargs)
