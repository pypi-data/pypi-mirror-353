import uuid

from .base import Component, Doc


class JsExtension:
    """
    ! EXPEREMENTAL: Currently in the testing
    """

    def __init__(self, *args, **kwargs) -> None:
        self.listeners = []

    def _render_listeners(self, doc: Doc):
        if not self.listeners:
            return

        id = getattr(self, "id") or getattr(self, "kwargs", {}).get("id")

        if not id:
            raise AttributeError("id is required for listeners to work")

        for listener in self.listeners:
            js = """document.querySelector('#%s').addEventListener('%s', %s);"""
            js = js.replace("%s", id, 1)
            js = js.replace("%s", listener["event"], 1)
            js = js.replace("%s", listener["func"], 1)
            Script(js=js).render(doc)

    def listener(self, event: str, func: str):
        """
        It does not matter where you call this method
        event: click, submit, ...
        func: async function(event) { console.log("Hello World"); };
        """
        self.listeners.append({"event": event, "func": func})


class ComponentTemplate(Component):
    """USE THIS TO ADD NEW ELEMENTS"""

    def __init__(self, text="Title", **kwargs) -> None:
        """
        _summary_

        Args:
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", text=text, params={}, **kwargs)

        default_class = ["template"]

        self.class_ = default_class + self.class_
        pass

    def render(self, doc: Doc):
        id = {"id": self.id} if self.id else {}
        class_ = {"class": " ".join(self.class_)} if self.class_ else {}
        with doc.tag(self.tag, {**id, **class_, **self.params, **self.kwargs}) as div:
            self.tag = div
            if self.text:
                div.text = self.text
            component: Component
            for component in self.children:
                component.render(doc)

        """
        * You can use other elements here like this:

        ```
        self.button = Button(
            self.label,
            icon=self.icon,
            color=self.color,
            outline=self.outline,
            class_=button_class,
            **{
                "data-bs-toggle": "offcanvas",
                "data-bs-target": f"#{self.toggler}",
                "aria-controls": self.toggler,
                **self.kwargs,
            },
        )
        self.button.render(doc)
        ```
        """


class Script(Component):

    def __init__(self, src="", js="", **kwargs) -> None:
        super().__init__(tag="script", **kwargs)
        self.src = src
        self.js = js
        assert all([src, js]) != True, "One param allowed"

    def render(self, doc: Doc):
        if self.src:
            with doc.tag("script", {"src": self.src}) as script:
                self.tag = script
        elif self.js:
            with doc.tag("script", {"type": "text/javascript"}) as script:
                self.tag = script
                script.text = self.js


class Style(Component):

    def __init__(self, href="", css="", **kwargs) -> None:
        super().__init__(tag="style" if css else "link", **kwargs)
        self.style = None
        self.href = href
        self.css = css
        assert all([href, css]) != True, "One param allowed"

    def render(self, doc: Doc):
        if self.href:
            with doc.tag("link", {"rel": "stylesheet", "href": self.href}) as style:
                self.style = style
        elif self.css:
            with doc.tag("style") as style:
                self.style = style
                style.text = self.css


class Head(Component):

    def __init__(
        self,
        title="Title",
        bootstrap_css="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
        bootstrap_icons_css="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
        **kwargs,
    ) -> None:
        super().__init__(tag="head", **kwargs)
        self.title = title
        self.bootstrap_css = bootstrap_css
        self.bootstrap_icons_css = bootstrap_icons_css

    def render(self, doc: Doc):
        with doc.tag("head") as head:
            self.tag = head
            doc.tag("meta", {"charset": "utf-8"})()
            doc.tag(
                "meta",
                {
                    "name": "viewport",
                    "content": "width=device-width, initial-scale=1.0",
                },
            )()
            doc.tag("title")(self.title)
            # bootstrap_css = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
            # doc.tag("link", {"rel": "stylesheet", "href": bootstrap_css})()
            # bootstrap_icons_css = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css"
            # doc.tag("link", {"rel": "stylesheet", "href": bootstrap_icons_css})()

            styles = [
                Style(href=self.bootstrap_css),
                Style(href=self.bootstrap_icons_css),
            ]
            component: Component
            for component in styles + self.children:
                component.render(doc)


class Body(Component):
    """
    Dark Mode:
        https://getbootstrap.com/docs/5.3/customize/color-modes/#enable-dark-mode
        **{"data-bs-theme": "dark"}
    """

    def __init__(
        self,
        bootstrap_js="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        **kwargs,
    ) -> None:
        super().__init__(tag="body", **kwargs)
        self.body = None
        self.bootstrap_js = bootstrap_js

    def render(self, doc: Doc):
        id = {"id": self.id} if self.id else {}
        class_ = {"class": " ".join(self.class_)} if self.class_ else {}
        with doc.tag("body", {**id, **class_, **self.params, **self.kwargs}) as body:
            self.body = body
            scripts = [Script(src=self.bootstrap_js)]
            component: Component
            for component in self.children + scripts:
                component.render(doc)
            # doc.tag("script", {"src": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"})()


class Header(Component):
    def __init__(self, **kwargs) -> None:
        """
        _summary_

        Args:
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="header", **kwargs)
        pass


class Footer(Component):
    def __init__(self, **kwargs) -> None:
        """
        _summary_

        Args:
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="footer", **kwargs)
        pass


class Container(Component):

    def __init__(self, br="", display="", v_align="", h_align="", **kwargs) -> None:
        """
        <div class="container[-fluid | xs-xxl] [d-flex] [justify-content-] [align-items-]"></div>

        Args:
            br (str, optional): Can be: "", "fluid"(Full width), "xs"-"xxl"(Full width at the breakpoint)
            display (str, optional): Can be: "", "flex", "grid", "table", "inline", "none"(hide) etc see Display. Defaults to "block" inherited from default css.
            v_align (str, optional): Veritical: start,end,center,between,around,evenly.
            h_align (str, optional): Horizontal: start,end,center,baseline,stretch.
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", **kwargs)
        if (v_align or h_align) and not display:
            raise AttributeError("display is required for v_align or h_align")

        default_class = []
        (
            default_class.append(f"container-{br}")
            if br
            else default_class.append("container")
        )
        default_class.append(f"d-{display}") if display else None
        default_class.append(f"justify-content-{v_align}") if v_align else None
        default_class.append(f"align-items-{h_align}") if h_align else None

        self.class_ = default_class + self.class_
        pass

    def render(self, doc: Doc):
        return super().render(doc)


class Row(Component):
    def __init__(self, display="", v_align="", h_align="", **kwargs) -> None:
        """
        _summary_

        Args:
            display (str, optional): Can be: "", "flex", "grid", "table", "inline", "none"(hide) etc see Display. Defaults to "block" inherited from default css.            v_align (str, optional): Veritical: start,end,center,between,around,evenly.
            h_align (str, optional): Horizontal: start,end,center,baseline,stretch.
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", **kwargs)
        if (v_align or h_align) and not display:
            raise AttributeError("display is required for v_align or h_align")

        default_class = ["row"]
        default_class.append(f"d-{display}") if display else None
        default_class.append(f"justify-content-{v_align}") if v_align else None
        default_class.append(f"align-items-{h_align}") if h_align else None

        self.class_ = default_class + self.class_
        pass


class Column(Component):
    def __init__(self, col="", display="", v_align="", h_align="", **kwargs) -> None:
        """
        <div class="col[-xs-12] [d-flex] [justify-content-center] [align-items-center]"></div>

        Args:
            col (str, optional): Column size: 1-12. Screen breakpoints: "xs"-"xxl".
            display (str, optional): Can be: "", "flex", "grid", "table", "inline", "none"(hide) etc see Display. Defaults to "block" inherited from default css.
            v_align (str, optional): Veritical: start,end,center,between,around,evenly.
            h_align (str, optional): Horizontal: start,end,center,baseline,stretch.
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", **kwargs)
        if (v_align or h_align) and not display:
            raise AttributeError("display is required for v_align or h_align")

        default_class = []
        default_class.append(f"col-{col}") if col else default_class.append("col")
        default_class.append(f"d-{display}") if display else None
        default_class.append(f"justify-content-{v_align}") if v_align else None
        default_class.append(f"align-items-{h_align}") if h_align else None

        self.class_ = default_class + self.class_


class Heading(Component):
    def __init__(self, h=1, text="Label", v_align="", h_align="", **kwargs) -> None:
        """
        HTML Heading element

        Args:
            h (str, optional): Can be 1-6(h1-h6). Defaults to "1".
            text (str, optional): Text. Defaults to "Label".
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag=f"h{h}", text=text, **kwargs)

        default_class = []
        default_class.append("d-flex") if (v_align or h_align) else None
        default_class.append(f"justify-content-{v_align}") if v_align else None
        default_class.append(f"align-items-{h_align}") if h_align else None

        self.class_ = default_class + self.class_
        pass


class Paragraph(Component):
    def __init__(self, text="Text", v_align="", h_align="", **kwargs) -> None:
        """
        HTML Paragraph element

        Args:
            text (str, optional): Text. Defaults to "Label".
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="p", text=text, **kwargs)

        default_class = []
        default_class.append("d-flex") if (v_align or h_align) else None
        default_class.append(f"justify-content-{v_align}") if v_align else None
        default_class.append(f"align-items-{h_align}") if h_align else None

        self.class_ = default_class + self.class_
        pass


class Button(Component, JsExtension):
    def __init__(
        self, text="Button", color="primary", outline=False, size="", icon="", **kwargs
    ):
        """
        <button type="button" class="btn btn-primary">Button</button>
        Icons: https://icons.getbootstrap.com/

        Args:
            text (str, optional): _description_. Defaults to "Button".
            icon (str, optional): Bootstrap icons like "circle".
            color (str, optional): Button style: primary,secondary,success,info,warning,danger,light,dark,link. Defaults to "primary".
            outline (str, optional): Outline button.
            size (str, optional): Button size: "sm", "lg".
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="button", text=text, params={"type": "button"}, **kwargs)
        JsExtension.__init__(self)
        self.icon = icon

        default_class = ["btn"]
        if outline and color:
            default_class.append(f"btn-outline-{color}")
        elif outline:
            default_class.append(f"btn-outline")
        elif color:
            default_class.append(f"btn-{color}")

        default_class.append(f"btn-{size}") if size else None

        self.class_ = default_class + self.class_
        pass

    def render(self, doc: Doc):
        id = {"id": self.id} if self.id else {}
        class_ = {"class": " ".join(self.class_)} if self.class_ else {}
        with doc.tag(
            "button", {**id, **class_, **self.params, **self.kwargs}
        ) as button:
            self.tag = button
            if self.icon:
                with doc.tag("i", {"class": f"bi-{self.icon}"}) as i:
                    pass
                if self.text:
                    i.tail = self.text
            elif self.text:
                button.text = self.text
            component: Component
            for component in self.children:
                component.render(doc)

        self._render_listeners(doc)

        # def inner():
        #     with doc.tag("button", {"class": button_class, "type": "button", **self.kwargs}) as button:
        #         self.button = button
        #         if self.icon:
        #             with doc.tag("i", {"class": f"bi-{self.icon}"}) as i:
        #                 self.i = i
        #             if self.label:
        #                 i.tail = self.label
        #         elif self.label:
        #             button.text = self.label

        # if self.align == False:
        #     inner()
        # else:
        #     with doc.tag("div", {"class": div_class}) as div:
        #         self.div = div
        #         inner()


class ButtonGroup(Component):

    def __init__(self, **kwargs) -> None:

        super().__init__(tag="div", params={"role": "group"}, **kwargs)
        self.class_ = ["btn-group"] + self.class_
        pass


class RadioButton(Component):
    """MY OWN CUSTOMIZATION"""

    def __init__(
        self,
        id: str,
        text="Button",
        color="primary",
        outline=False,
        size="",
        icon="",
        checked=False,
        **kwargs,
    ) -> None:
        """
        _summary_

        Args:
            text (str, optional): _description_. Defaults to "Button".
            icon (str, optional): Bootstrap icons like "circle".
            color (str, optional): Button style: primary,secondary,success,info,warning,danger,light,dark,link. Defaults to "primary".
            outline (str, optional): Outline button.
            size (str, optional): Button size: "sm", "lg".
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="label", text=text, params={"for": id}, id=id, **kwargs)

        self.icon = icon
        self.checked = checked

        default_class = ["btn"]
        btn = f"btn-outline" if outline else "btn"
        btn = f"{btn}-{color}" if color else btn
        default_class.append(btn)
        default_class.append(f"btn-{size}") if size else None

        self.class_ = default_class + self.class_
        pass

    def render(self, doc: Doc):
        id = {"id": self.id} if self.id else {}
        class_ = {"class": "btn-check"}
        params = {"type": "radio", "name": "btnradio", "autocomplete": "off"}
        if self.checked:
            params.update({"checked": "true"})
        with doc.tag("input", {**id, **class_, **params}) as input:
            pass

        class_ = {"class": " ".join(self.class_)} if self.class_ else {}
        with doc.tag(self.tag, {**class_, **self.params, **self.kwargs}) as label:
            self.tag = label
            if self.icon:
                with doc.tag("i", {"class": f"bi-{self.icon}"}) as i:
                    pass
                if self.text:
                    i.tail = self.text
            elif self.text:
                label.text = self.text
            component: Component
            for component in self.children:
                component.render(doc)


class ButtonToolbar(Component):
    pass  # TODO


class Image(Component):
    def __init__(self, src: str, alt="", **kwargs) -> None:
        """
        __desc__

        Args:
            src (str, required): Image source.
            alt (str, optional): Image alt text.
            kwargs (dict, optional): Can be anything id, style, class_ ...

        Classes:
            Roundness: rounded, rounded-circle, rounded-0, rounded-1, rounded-2, rounded-3, rounded-4, rounded-5
            Thumbnail: img-thumbnail
            Responsive: img-fluid
        """
        super().__init__(tag="img", params={"src": src, "alt": alt}, **kwargs)

        default_class = []

        self.class_ = default_class + self.class_
        pass


class Icon(Component):
    def __init__(self, icon: str, text: str = "", **kwargs) -> None:
        """
        https://icons.getbootstrap.com/

        Args:
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="i", text=text, params={}, **kwargs)

        default_class = [f"bi-{icon}"]

        self.class_ = default_class + self.class_
        pass

    def render(self, doc: Doc):
        id = {"id": self.id} if self.id else {}
        class_ = {"class": " ".join(self.class_)} if self.class_ else {}
        with doc.tag("i", {**id, **class_, **self.params, **self.kwargs}) as i:
            self.tag = i
            # TODO: Check if here should be text or tail
            if self.text:
                i.tail = self.text
            component: Component
            for component in self.children:
                component.render(doc)


class NavbarOld(Component):
    def __init__(
        self,
        position="sticky-top",
        expand: bool = "sm",
        bg="body-tertiary",
        container="",
        **kwargs,
    ):
        """
        Button

        Args:
            position (str, required): Can be sticky-top, fixed-top, fixed-bottom.
            expand (str, optional): Can be True, False(""), "xs"-"xxl"
            bg (str, optional): Background
            container (str, optional): Can be "", "fluid", "xs"-"xxl"
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="header" if "top" in position else "footer", **kwargs)

        self.nav_class = "container" if not container else f"container-{container}"

        default_class = ["navbar", position]
        if expand:
            (
                default_class.append("navbar-expand")
                if expand == True
                else default_class.append(f"navbar-expand-{expand}")
            )
        default_class.append(f"bg-{bg}") if bg else None

        self.class_ = default_class + self.class_
        pass

    def render(self, doc: Doc):
        id = {"id": self.id} if self.id else {}
        class_ = (
            {"class": " ".join([c for c in self.class_ if c])} if self.class_ else {}
        )
        # tag: header or footer
        with doc.tag(self.tag, {**id, **class_, **self.params, **self.kwargs}) as h_f:
            self.tag = h_f
            with doc.tag("nav", {"class": self.nav_class}) as nav:
                component: Component
                for component in self.children:
                    component.render(doc)


class Navbar(Component):
    def __init__(self, position="", expand: bool = "", bg="body-tertiary", **kwargs):
        """
        Navbar

        Args:
            position (str, required): Can be sticky-top, fixed-top, sticky-bottom, fixed-bottom.
            expand (str, optional): Can be True, False(""), "xs"-"xxl"
            bg (str, optional): Background, "body-tertiary"
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="nav", **kwargs)

        default_class = ["navbar"]
        if position:
            default_class.append(position)
        if expand:
            (
                default_class.append("navbar-expand")
                if expand == True
                else default_class.append(f"navbar-expand-{expand}")
            )
        default_class.append(f"bg-{bg}") if bg else None

        self.class_ = default_class + self.class_
        pass


class NavbarCollapse(Component):
    def __init__(self, **kwargs):
        """
        ___

        Args:
            pass
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", **kwargs)

        default_class = ["collapse", "navbar-collapse"]

        self.class_ = default_class + self.class_
        pass


class NavbarCollapse(Component):
    def __init__(self, **kwargs):
        """
        ___

        Args:
            pass
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", **kwargs)

        default_class = ["collapse", "navbar-collapse"]

        self.class_ = default_class + self.class_
        pass


class NavItem(Component):
    def __init__(self, **kwargs):
        """
        ___

        Args:
            pass
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="li", **kwargs)

        default_class = ["nav-item"]

        self.class_ = default_class + self.class_
        pass


class NavbarToggler(Component):
    def __init__(self, target="navbarSupportedContent", **kwargs):
        """
        NavbarToggler

        Args:
            target (str, optional): Target Collapsable items.
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        params = {
            "type": "button",
            "data-bs-toggle": "collapse",
            "data-bs-target": f"#{target}",
            "aria-controls": target,
            "aria-expanded": "false",
            "aria-label": "Toggle navigation",
        }
        super().__init__(tag="button", params=params, **kwargs)

        self.class_ = ["navbar-toggler"] + self.class_
        pass

    def render(self, doc: Doc):
        id = {"id": self.id} if self.id else {}
        class_ = (
            {"class": " ".join([c for c in self.class_ if c])} if self.class_ else {}
        )
        with doc.tag(
            "button", {**id, **class_, **self.params, **self.kwargs}
        ) as button:
            self.tag = button
            with doc.tag("span", {"class": "navbar-toggler-icon"}) as span:
                component: Component
                for component in self.children:
                    component.render(doc)


class Collapsable(Component):
    def __init__(self, toggler="navbarSupportedContent", **kwargs):
        """
        Collapsable

        Args:
            toggler (str, optional): NavbarToggler button.
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", id=toggler, **kwargs)

        self.class_ = ["collapse", "navbar-collapse"] + self.class_
        pass


class NavbarNav(Component):
    def __init__(self, type="", fill=False, **kwargs):
        """
        NavbarNav

        Args:
            type (str, optional): Can be "", "pills".
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="ul", **kwargs)

        default_class = ["navbar-nav"]
        default_class.append(f"nav-{type}") if type else None
        default_class += ["nav-fill", "w-100"] if fill else []

        self.class_ = default_class + self.class_
        pass


class NavbarLink(Component):
    def __init__(self, title="Link", icon="cart", href="#", **kwargs):
        """
        <a class="nav-item nav-link" href="#"><i class="bi bi-alarm"></i> Zebra</a>

        Args:
            title (str, optional): Title.
            icon (str, optional): icon.
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="a", params={"href": href}, **kwargs)
        self.title = title
        self.icon = icon

        self.class_ = ["nav-item", "nav-link"] + self.class_
        pass

    def render(self, doc: Doc):
        id = {"id": self.id} if self.id else {}
        class_ = (
            {"class": " ".join([c for c in self.class_ if c])} if self.class_ else {}
        )
        with doc.tag("a", {**id, **class_, **self.params, **self.kwargs}) as a:
            self.tag = a
            if self.icon:
                with doc.tag("i", {"class": f"bi-{self.icon}"}) as i:
                    i.text = " "  # To make space between icon and text
                    i.tail = self.title
            else:
                a.text = self.title


class NavbarBrand(Component):
    def __init__(
        self,
        name=" Brand",
        img="https://getbootstrap.com//docs/4.0/assets/brand/bootstrap-solid.svg",
        href="#",
        **kwargs,
    ):
        """
        NavbarBrand

        Args:
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="a", params={"href": href}, **kwargs)
        self.name = name
        self.img = img
        self.href = href

        self.class_ = ["navbar-brand"] + self.class_
        pass

    def render(self, doc: Doc):
        # TODO self.class_ should be used for img tag
        id = {"id": self.id} if self.id else {}
        class_ = (
            {"class": " ".join([c for c in self.class_ if c])} if self.class_ else {}
        )
        with doc.tag("a", {**id, **class_, **self.params, **self.kwargs}) as a:
            self.tag = a
            if self.img:
                with doc.tag("img", {"src": self.img, **self.kwargs}) as img:
                    self.img = img
                    img.tail = self.name
            else:
                a.text = self.name


class Offcanvas(Component):
    def __init__(
        self,
        br="",
        placement="start",
        scroll: bool = None,
        backdrop: bool = None,
        labelledby: str = None,
        **kwargs,
    ) -> None:
        """
        https://getbootstrap.com/docs/5.3/components/offcanvas/

        Args:
            br (str): Responsive breakpoint xs-xxl
            placement (str): start, end, top, bottom
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        params = {"tabindex": "-1"}
        if scroll != None:
            params.update({"data-bs-scroll": str(scroll).lower()})
        if backdrop != None:
            params.update({"data-bs-backdrop": str(backdrop).lower()})
        if labelledby:
            params.update({"aria-labelledby": labelledby})
        super().__init__(tag="div", params=params, **kwargs)

        br = f"-{br}" if br else ""
        default_class = ["offcanvas" + br, f"offcanvas-{placement}"]

        self.class_ = default_class + self.class_
        pass


class OffcanvasHeader(Component):
    def __init__(self, **kwargs) -> None:
        """
        https://getbootstrap.com/docs/5.3/components/offcanvas/

        Args:
        """
        super().__init__(tag="div", **kwargs)

        default_class = ["offcanvas-header"]

        self.class_ = default_class + self.class_
        pass


class OffcanvasTitle(Heading):
    """# ! NON USUAL INHERITANCE"""

    def __init__(self, h: int, id: str, text: str, **kwargs) -> None:
        """
        https://getbootstrap.com/docs/5.3/components/offcanvas/

        Args:
        """
        class_ = kwargs.get("class_", "")
        class_ += " offcanvas-title"
        kwargs["class_"] = class_
        super().__init__(h=h, id=id, text=text, **kwargs)


class OffcanvasCloseButton(Button):
    """# ! NON USUAL INHERITANCE"""

    def __init__(self, text="", **kwargs) -> None:
        """
        https://getbootstrap.com/docs/5.3/components/offcanvas/

        Args:
        """
        params = {
            "data-bs-dismiss": "offcanvas",
            "aria-label": "Close",
        }
        super().__init__(text=text, color="close", **params, **kwargs)


class OffcanvasOpenButton(Button):
    """# ! NON USUAL INHERITANCE"""

    def __init__(
        self,
        offcanvas_id: str,
        text="",
        color="primary",
        outline=False,
        size="",
        icon="list",
        **kwargs,
    ) -> None:
        """
        https://getbootstrap.com/docs/5.3/components/offcanvas/

        Args:
        """
        params = {
            "data-bs-toggle": "offcanvas",
            "data-bs-target": f"#{offcanvas_id}",
            "aria-controls": offcanvas_id,
        }
        super().__init__(
            text=text,
            color=color,
            outline=outline,
            size=size,
            icon=icon,
            **params,
            **kwargs,
        )


class OffcanvasBody(Component):
    def __init__(self, **kwargs) -> None:
        """
        https://getbootstrap.com/docs/5.3/components/offcanvas/

        Args:
        """
        super().__init__(tag="div", **kwargs)

        default_class = ["offcanvas-body"]

        self.class_ = default_class + self.class_
        pass


class OffcanvasOld(Component):
    # TODO: Create separate OffcanvasHeader, OffcanvasTitle, OffcanvasBody
    def __init__(
        self,
        title="Offcanvas",
        position="start",
        toggler="offcanvasToggler",
        collapse_at="",
        **kwargs,
    ):
        """
        Offcanvas

        Args:
            title (str, optional): Offcanvas title.
            position (str, required): Offcanvas position: "start", "end", "top", "bottom".
            toggler (str, optional): OffcanvasToggler button.
            collapse_at (str, optional): Collapse body text lower then: "", "xs"-"xxl".
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", id=toggler, **kwargs)

        self.title = title
        self.toggler = toggler

        default_class = []
        (
            default_class.append(f"offcanvas-{collapse_at}")
            if collapse_at
            else default_class.append("offcanvas")
        )
        default_class.append(f"offcanvas-{position}")

        self.class_ = default_class + self.class_
        pass

    def render(self, doc: Doc):
        id = {"id": self.id} if self.id else {}
        class_ = (
            {"class": " ".join([c for c in self.class_ if c])} if self.class_ else {}
        )
        aria_labelledby = self.title.replace(" ", "")
        with doc.tag(
            "div",
            {
                **id,
                **class_,
                "tabindex": "-1",
                # "aria-labelledby": aria_labelledby,
                **self.params,
                **self.kwargs,
            },
        ) as div_offcanvas:
            self.tag = div_offcanvas
            with doc.tag("div", {"class": "offcanvas-header"}) as div_header:
                with doc.tag(
                    "h5", {"class": "offcanvas-title", "id": aria_labelledby}
                ) as h_title:
                    self.h_title = h_title
                    h_title.text = self.title
                with doc.tag(
                    "button",
                    {
                        "class": "btn-close",
                        "data-bs-dismiss": "offcanvas",
                        "data-bs-target": f"#{self.toggler}",
                    },
                ) as button_close:
                    self.button_close = button_close
            with doc.tag("div", {"class": "offcanvas-body"}) as div_body:
                self.div_body = div_body
                component: Component
                for component in self.children:
                    component.render(doc)


class OffcanvasToggler(Component):
    def __init__(
        self,
        text="",
        icon="three-dots",
        color="dark",
        outline=True,
        size="",
        toggler="offcanvasToggler",
        show_at="",
        **kwargs,
    ):
        """
        OffcanvasToggler

        Args:
            label (str, optional): Button title.
            icon (str, optional): Can be: "list", "three-dots" ...
            toggler (str, optional): Offcanvas toggler.
            show_at (str, optional) Can be: "", "xs"-"xxl"
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="button", text=text, **kwargs)

        self.icon = icon
        self.color = color
        self.outline = outline
        self.size = (size,)
        self.toggler = toggler

        default_class = []
        default_class.append(f"d-{show_at}-none") if show_at else None

        self.class_ = default_class + self.class_

    def render(self, doc: Doc):
        # Bew aware of _ in class_
        class_ = (
            {"class_": " ".join([c for c in self.class_ if c])} if self.class_ else {}
        )
        self.button = Button(
            self.text,
            icon=self.icon,
            color=self.color,
            outline=self.outline,
            **class_,
            **{
                "data-bs-toggle": "offcanvas",
                "data-bs-target": f"#{self.toggler}",
                "aria-controls": self.toggler,
                **self.kwargs,
            },
        )
        self.tag = self.button.tag
        self.button.render(doc)


class CardGroup(Component):
    def __init__(self, **kwargs) -> None:
        """
        CardGroup

        Args:
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", **kwargs)

        self.class_ = ["card-group"] + self.class_
        pass


class Card(Component):
    def __init__(
        self,
        title="Title",
        subtitle="",
        img="",
        body="",
        header="",
        footer="",
        **kwargs,
    ):
        super().__init__(tag="div", **kwargs)

        self.title = title
        self.subtitle = subtitle
        self.img = img
        self.body = body
        self.header = header
        self.footer = footer

        self.class_ = ["card"] + self.class_
        pass

    def render(self, doc: Doc):
        id = {"id": self.id} if self.id else {}
        class_ = (
            {"class": " ".join([c for c in self.class_ if c])} if self.class_ else {}
        )
        with doc.tag("div", {**id, **class_, **self.params, **self.kwargs}) as div_card:
            self.tag = div_card
            if self.header:
                with doc.tag("div", {"class": "card-header"}) as div_card_header:
                    div_card_header.text = self.header
            if self.img:
                with doc.tag(
                    "img",
                    {"src": self.img, "class": "card-img-top", "alt": "Card image cap"},
                ) as img:
                    pass
            with doc.tag("div", {"class": "card-body"}) as div_card_body:
                if self.title:
                    with doc.tag("h5", {"class": "card-title"}) as h_card_title:
                        h_card_title.text = self.title
                if self.subtitle:
                    with doc.tag("h6", {"class": "card-subtitle"}) as h_card_subtitle:
                        h_card_subtitle.text = self.subtitle
                if self.body:
                    with doc.tag("p", {"class": "card-text"}) as p_card_body:
                        p_card_body.text = self.body

                component: Component
                for component in self.children:
                    component.render(doc)

            if self.footer:
                with doc.tag("div", {"class": "card-footer"}) as div_card_footer:
                    div_card_footer.text = self.footer


class Form(Component, JsExtension):
    def __init__(self, id="", **kwargs) -> None:
        """
        _summary_

        Args:
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="form", id=id, **kwargs)
        JsExtension.__init__(self)
        pass

    def render(self, doc: Doc):
        super().render(doc)
        self._render_listeners(doc)


class FormLabel(Component):

    def __init__(self, text: str, for_: str, **kwargs) -> None:
        """
        _summary_

        Args:
            for_ (str, optional): This is an "id" of the FormControl element.
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="label", text=text, params={"for": for_}, **kwargs)

        self.class_ = ["form-label"] + self.class_
        pass


class FormControl(Component):
    """
    TODO: class="col-form-label" https://getbootstrap.com/docs/5.3/forms/form-control/#form-text
    TODO: class="form-control-plaintext" https://getbootstrap.com/docs/5.3/forms/form-control/#readonly-plain-text
    TODO: datalists https://getbootstrap.com/docs/5.3/forms/form-control/#datalists
    """

    def __init__(
        self,
        name: str,
        type="textarea",
        size="",
        placeholder="",
        description="",
        **kwargs,
    ) -> None:
        """
        <input class="form-control" type="password" name="password" placeholder="Password" aria-describedby="EmailFieldDescription" id="PasswordFormInput" required="true">

        Args:
            type (str, required): Can be: "email", "password", "text", "file", "color"(For color picker). Defaults to "textarea" which is custom one. We could use "" instead but it is more clear.
            name (str, required): Name of the input filed, will be assosiated with value.
            size (str, optional): Can be: "sm", "lg". Defaults to "".
            placeholder (str, optional): Placeholder text.
            description (str, optional): This is an "id" of the FormText element.
            kwargs (dict, optional): Can be anything id, style, class_ ...

            Attributes that can be passed: required, disabled, readonly, multiple(To select multiple files), is-invalid
        """
        description = {"aria-describedby": description} if description else {}
        placeholder = {"placeholder": placeholder} if placeholder else {}
        params = {"name": name, "type": type, **description, **placeholder}
        super().__init__(
            tag="textarea" if type == "textarea" else "input", params=params, **kwargs
        )

        default_class = ["form-control"]
        default_class.append(f"form-control-{size}") if size else None

        self.class_ = default_class + self.class_
        pass


class FormText(Component):

    def __init__(self, id: str, text: str = None, **kwargs) -> None:
        """
        _summary_

        Args:
            id (str, required): This is an "id" used by the FormControl element.
            text (str, optional): Description text. You can nest other elemens with text instead.
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", text=text, id=id, **kwargs)

        self.class_ = ["form-text"] + self.class_
        pass


class FormSelect(Component):
    pass  # TODO https://getbootstrap.com/docs/5.3/forms/select/


class FormCheckInput(Component):
    pass  # TODO https://getbootstrap.com/docs/5.3/forms/checks-radios/


class InputGroup(Component):
    def __init__(self, **kwargs) -> None:
        """
        _summary_

        Args:
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", **kwargs)

        default_class = ["input-group"]

        self.class_ = default_class + self.class_
        pass


class InputGroupText(Component):
    def __init__(self, text: str, **kwargs) -> None:
        """
        _summary_

        Args:
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="span", text=text, **kwargs)

        default_class = ["input-group-text"]

        self.class_ = default_class + self.class_
        pass


class Dropdown(Component):
    def __init__(self, **kwargs):
        """
        ___

        Args:
            pass
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="div", **kwargs)

        default_class = ["dropdown"]

        self.class_ = default_class + self.class_
        pass


class DropdownMenu(Component):
    def __init__(self, **kwargs):
        """
        ___

        Args:
            pass
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="ul", **kwargs)

        default_class = ["dropdown-menu"]

        self.class_ = default_class + self.class_
        pass


class DropdownItem(Component):
    def __init__(self, text: str, href="#", **kwargs):
        """
        <li><a class="dropdown-item" href="#">Action</a></li>

        Args:
            pass
            kwargs (dict, optional): Can be anything id, style, class_ ...
        """
        super().__init__(tag="li", text=text, **kwargs)

        self.href = href

        default_class = ["dropdown-item"]

        self.class_ = default_class + self.class_
        pass

    def render(self, doc: Doc):
        id = {"id": self.id} if self.id else {}
        class_ = {"class": " ".join(self.class_)} if self.class_ else {}
        with doc.tag(self.tag, {}) as li:
            self.tag = li
            with doc.tag(
                "a", {**id, **class_, "href": self.href, **self.params, **self.kwargs}
            ) as a:
                if self.text:
                    a.text = self.text
                component: Component
                for component in self.children:
                    component.render(doc)


class DropdownToggleButton(Button):
    """# ! NON USUAL INHERITANCE"""

    def __init__(
        self, text="", color="primary", outline=False, size="", icon="", **kwargs
    ) -> None:
        """
        https://getbootstrap.com/docs/5.3/components/offcanvas/


        Args:
        """
        params = {
            "data-bs-toggle": "dropdown",
            "aria-expanded": f"false",
        }
        class_ = kwargs.get("class_", "")
        class_ += " dropdown-toggle"
        kwargs["class_"] = class_
        super().__init__(
            text=text,
            color=color,
            outline=outline,
            size=size,
            icon=icon,
            **params,
            **kwargs,
        )
