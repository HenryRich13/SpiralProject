from light_widgets.widget import *


class Container(Widget):
    type_manager = TypeManager(seed=Widget.type_manager,
                               skip_invisible=TypeGroup(bool, conversion_func=TypeGroup.AUTO))

    def __init__(self, **properties):
        Widget.__init__(self)
        self.config(skip_invisible=True)
        self._widgets: dict[str, Widget] = {}
        if type(self) == Container:
            self.config(**properties)

    def get_widget(self, name: str):
        return self._widgets[name]

    def set_widget(self, name: str, wgt: Widget):
        self._widgets[name] = wgt
        wgt.set_parent(self)
        self.queue_build()

    @updatemethod
    def update(self, events: list[pg.event.Event]):
        Widget.update(self, events)
        self.build()
        for widget in self._widgets.values():
            if self.get_property("skip_invisible") and widget.get_visibility_mask() is not None and \
                    widget.get_visibility_mask().count() == 0:
                continue
            widget.update(events)

    @buildmethod
    def build(self):
        Widget.build(self)

        widget_surf = pg.Surface(self.get_property("size"), pg.SRCALPHA)
        widgets_list = list(filter(lambda wgt: wgt.get_property("visible"), self._widgets.values()))

        for i in range(len(widgets_list) - 1):
            widget_surf.fill(CLEAR)
            widgets_list[i].render(widget_surf)
            widget_mask = pg.mask.from_surface(widget_surf, MASK_THRESHOLD)

            widget_surf.fill(CLEAR)
            for j in range(i+1, len(widgets_list)):
                widgets_list[j].render(widget_surf)
            other_mask = pg.mask.from_surface(widget_surf, MASK_THRESHOLD)
            other_mask.invert()

            visibility_mask = pg.Mask(widgets_list[i].get_property("size"))
            visibility_mask.draw(widget_mask.overlap_mask(other_mask, (0, 0)), -widgets_list[i].get_property("pos"))
            widgets_list[i].set_visibility_mask(visibility_mask)

        if len(widgets_list) > 0:
            widgets_list[-1].set_visibility_mask(None)

        for widget in widgets_list:
            if self.get_property("skip_invisible") and widget.get_visibility_mask() is not None and \
                    widget.get_visibility_mask().count() == 0:
                continue
            widget.render(self._surf)
