from .html_builder import Doc


class Base:
    COMPOSE_STACKS: list[list["ComponentBase"]] = []
    COMPOSE_STACK: list["ComponentBase"] = []
    COMPOSED: list[list["ComponentBase"]] = []


class ComponentBase(Base):
    def __init__(self, *args, **kwargs) -> None:
        self.children = []

    def render(self, doc: Doc):
        raise NotImplementedError()

    def compose_add_child(self, child: "ComponentBase"):
        self.children.append(child)

    def __enter__(self):
        """Use as context manager when composing."""
        self.COMPOSE_STACKS[-1].append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit compose context manager."""
        compose_stack: list["ComponentBase"] = self.COMPOSE_STACKS[-1]
        composed = compose_stack.pop()
        if compose_stack:
            compose_stack[-1].compose_add_child(composed)
        else:
            self.COMPOSED[-1].append(composed)


class Component(ComponentBase):
    def __init__(self, tag: str = None, text="", params={}, *args, **kwargs) -> None:
        """
        Attr: "tag", "text", "params", "id", "class_", "kwargs"
        """
        super().__init__()
        self.tag = tag
        self.text = text
        self.params = params # Service attribute
        self.id = kwargs.pop("id", None)
        self.class_: list = kwargs.pop("class_", "").split()
        for key, value in kwargs.items():
            if isinstance(value, bool):
                value = str(value).lower()
            kwargs[key] = str(value)
        self.kwargs = kwargs

    def render(self, doc: Doc):
        if self.tag == None:
            raise NotImplementedError("Should be overriden")
        id = {"id": self.id} if self.id else {}  # Readability purpuse
        class_ = {"class": " ".join([c for c in self.class_ if c])} if self.class_ else {}
        with doc.tag(self.tag, {**id, **class_, **self.params, **self.kwargs}) as tag:
            self.tag = tag
            if self.text:
                tag.text = self.text
            component: Component
            for component in self.children:
                component.render(doc)


class OverrideClass__init__(type):
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        # Here, you can customize the behavior as needed
        return instance.value


class CustomComponent(metaclass=OverrideClass__init__):
    """
    ! IT IS REDUNDANT. THE SAME CAN BE ACHIVED BY SIMPLE FUNCTION
    You can't use doc.tag() in CustomComponent but you can use tag.Div() or other tag component
    usage: yield from CustomComponent
    """

    def __init__(self):
        self.value = self.compose()

    def compose(self):
        raise NotImplementedError()
