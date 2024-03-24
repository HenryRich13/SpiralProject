from light_widgets.widget import *

_DEFAULT_TEXTURE: dict[str, GridTexture]


def _setup_default_texture():
    global _DEFAULT_TEXTURE
    radius = 3
    _DEFAULT_TEXTURE = {"DEFAULT":
                        GridTexture(resize_method=ResizeMethod.STRETCH, grid_offsets=GridOffsets(all_sides=radius))}
    surf = pg.Surface((7, 7), pg.SRCALPHA)
    surf.fill(CLEAR)
    pg.draw.rect(surf, WHITE, surf.get_rect(), 0, radius)
    _DEFAULT_TEXTURE["DEFAULT"].add_layer("bg", Layer(surf, pg.Color(200, 200, 255)))
    surf.fill(CLEAR)
    pg.draw.rect(surf, WHITE, surf.get_rect(), 2, radius)
    _DEFAULT_TEXTURE["DEFAULT"].add_layer("outline", Layer(surf, pg.Color(225, 225, 255)))


class Slider(Widget):
    type_manager = TypeManager(seed=Widget.type_manager,
                               value=TypeGroup(float, int, conversion_func=TypeGroup.AUTO),
                               range=TypeGroup(tuple, list, Cartesian, conversion_func=TypeGroup.AUTO),
                               top_size=TypeGroup(Size, conversion_func=TypeGroup.AUTO),
                               top_texture=TypeGroup(Texture, alternate_types=str,
                                                     conversion_func=lambda val: _DEFAULT_TEXTURE[val].copy()))

    def __init__(self, **properties):
        if "_DEFAULT_TEXTURE" not in globals().keys():
            _setup_default_texture()
        Widget.__init__(self)
        self.config(value=0,
                    range=(0, 1),
                    top_size=Size(25, 25),
                    top_texture="DEFAULT")
        self._top_surf: typing.Optional[pg.Surface] = None
        self._top_rect: typing.Optional[pg.Rect] = None
        self._focused = False
        self._value_changed_callback: typing.Optional[typing.Callable] = None
        self._previous_value = None
        self.set_event_listener(pg.MOUSEBUTTONDOWN, self.on_mouse_down)
        self.set_event_listener(pg.MOUSEMOTION, self.on_mouse_move)
        self.set_event_listener(pg.MOUSEBUTTONUP, self.on_mouse_up)
        if type(self) == Slider:
            self.config(**properties)

    def config(self, **properties):
        old_value = None
        if "value" in self._properties.keys() and self._value_changed_callback is not None:
            old_value = self.get_property("value")
        super().config(**properties)
        if old_value is not None and old_value != self.get_property("value"):
            self.build()
            self._value_changed_callback(self)

    def on_mouse_down(self, _, event: pg.event.Event):
        self.build()
        event_pos = Pos(event.pos)
        top_mask = pg.mask.from_surface(self._top_surf, MASK_THRESHOLD)
        temp_rect = self._top_rect.copy()
        temp_rect.topleft = self.get_abs_pos() - self.get_property("pos") + self._top_rect.topleft
        if self.collide_pos(event_pos, CollisionType.ABS_VISIBILITY) or \
                (temp_rect.collidepoint(event.pos) and top_mask.get_at(event_pos - temp_rect.topleft)):
            self._focused = True

    def on_mouse_move(self, _, event: pg.event.Event):
        if not self._focused:
            return
        ratio = (event.pos[0] - self.get_abs_pos().x) / (self.get_property("size")[0])
        self.config(value=ratio * (self.get_property("range")[1] - self.get_property("range")[0]))

    def on_mouse_up(self, _, event: pg.event.Event):
        if self._focused:
            self._focused = False
            ratio = (event.pos[0] - self.get_abs_pos().x) / (self.get_property("size")[0])
            self.config(value=ratio * (self.get_property("range")[1] - self.get_property("range")[0]))

    def set_value_changed_callback(self, callback: typing.Callable):
        self._value_changed_callback = callback

    @buildmethod
    def build(self):
        Widget.build(self)

        if self._top_surf is None or self.get_property("top_size") != self._top_surf.get_size():
            self._top_surf = convert_surface(pg.Surface(self.get_property("top_size"), pg.SRCALPHA), True)
        self.get_property("top_texture").set_size(self.get_property("top_size"))
        self.get_property("top_texture").render(self._top_surf)
        self._top_rect = self._top_surf.get_rect()

        if self.get_property("value") < self.get_property("range")[0]:
            self.config(value=self.get_property("range")[0])
        if self.get_property("range")[1] < self.get_property("value"):
            self.config(value=self.get_property("range")[1])

        ratio = self.get_property("value") / (self.get_property("range")[1] - self.get_property("range")[0])

        self._top_rect.center = (self.get_property("pos").x + (ratio * self.get_property("size").w),
                                 self.get_property("pos").y + self._surf.get_rect().centery)

    @rendermethod
    def render(self, display: pg.Surface):
        super().render(display)
        display.blit(self._top_surf, self._top_rect)
