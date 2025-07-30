COMPOSE_STACKS: list[list[object]] = []
COMPOSED: list[object] = []

COMPOSE_STACK: list[object] = []


class Component:
    def __init__(self):
        self.children = []

    def compose_add_child(self, child: "Component"):
        self.children.append(child)

    def __enter__(self):
        """Use as context manager when composing."""
        COMPOSE_STACKS[-1].append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit compose context manager."""
        compose_stack = COMPOSE_STACKS[-1]
        composed = compose_stack.pop()
        if compose_stack:
            compose_stack[-1].compose_add_child(composed)
        else:
            COMPOSED[-1].append(composed)

    def render(self):
        """Render the component."""
        raise NotImplementedError("Subclasses must implement render()")


class Head(Component):
    def render(self):
        print("Rendering Head")


class Body(Component):
    def render(self):
        print("Rendering Body")
        for child in self.children:
            child.render()


class Label(Component):
    def render(self):
        print("Rendering Label")


class Container(Component):
    def render(self):
        print("Rendering Container")
        for child in self.children:
            child.render()


class Input(Component):
    def render(self):
        print("Rendering Input")


class Button(Component):
    def render(self):
        print("Rendering Button")


class App:
    def __init__(self):
        self._compose_stacks = [[]]
        self._composed = [[]]

    def compose(self):
        yield Head()
        with Body() as body:
            yield Label()
            with Container():
                yield Input()
            yield Button()

    def run(self):
        nodes: list[object] = []
        compose_stack: list[object] = []
        composed: list[object] = []
        COMPOSE_STACKS.append(compose_stack)
        COMPOSED.append(composed)
        iter_compose = iter(self.compose())
        is_generator = hasattr(iter_compose, "throw")
        try:
            while True:
                try:
                    child = next(iter_compose)
                except StopIteration:
                    break

                if composed:
                    nodes.extend(composed)
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
                    nodes.append(child)
            if composed:
                nodes.extend(composed)
                composed.clear()
        finally:
            COMPOSE_STACKS.pop()
            COMPOSED.pop()
        for node in nodes:
            node.render()
        return nodes


App().run()
