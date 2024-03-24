from light_widgets.texture import *


class CollisionType(object):
    DEFAULT = 0
    ABS_POS = 1
    VISIBILITY = 2
    ABS_VISIBILITY = 3


class Widget(PropertyManager):
    type_manager = TypeManager(None,
                               pos=TypeGroup(Pos, conversion_func=TypeGroup.AUTO),
                               size=TypeGroup(Size, conversion_func=TypeGroup.AUTO),
                               texture=TypeGroup(Texture, types.NoneType),
                               enabled=TypeGroup(bool, conversion_func=TypeGroup.AUTO),
                               visible=TypeGroup(bool, conversion_func=TypeGroup.AUTO))

    def __init__(self, **properties):
        super().__init__()
        self.config(pos=Pos(0, 0),
                    size=Size(0, 0),
                    texture=None,
                    enabled=True,
                    visible=True)
        self._surf: typing.Optional[pg.Surface] = None
        self._visibility_mask: typing.Optional[pg.Mask] = None
        self._event_listeners: dict[int, typing.Callable] = {}
        self._passed_objects = []
        if type(self) == Widget:
            self.config(**properties)

    def __copy__(self):
        new_obj = type(self)(**self._properties).set_parent(self.get_parent())
        new_obj.set_visibility_mask(self._visibility_mask)
        for event_t, func in self._event_listeners.items():
            new_obj.set_event_listener(event_t, func)
        return new_obj

    def copy(self):
        return self.__copy__()

    def pass_render(self, obj):
        parent_pass_render = self.get_parent_attr("pass_render")
        if parent_pass_render is not None:
            parent_pass_render(obj)
        else:
            self._passed_objects.append(obj)

    def set_parent(self, new_parent: object):
        super().set_parent(new_parent)
        while len(self._passed_objects) > 0:
            self.pass_render(self._passed_objects.pop(0))
        return self

    def get_abs_pos(self) -> Pos:
        abs_pos = self.get_property("pos").copy()
        parent_abs_pos = self.get_parent_attr("get_abs_pos")
        if parent_abs_pos is not None:
            abs_pos += parent_abs_pos()
        return abs_pos

    def get_visibility_mask(self) -> pg.Mask | None:
        return self._visibility_mask

    def set_visibility_mask(self, new_mask: pg.Mask | None):
        self._visibility_mask = new_mask

    def get_current_mask(self, collision_type: int) -> pg.Mask:
        if self.get_property("texture") is not None:
            mask: pg.Mask = self.get_property("texture").get_mask()
            if collision_type in (2, 3) and self.get_visibility_mask() is not None:
                return mask.overlap_mask(self.get_visibility_mask(), (0, 0))
            return mask
        if collision_type in (2, 3) and self.get_visibility_mask() is not None:
            return self.get_visibility_mask()
        return pg.Mask(self.get_property("size"), True)

    def collide_pos(self, other: PosType, collision_type: int = CollisionType.DEFAULT):
        rel_pos = other - (self.get_abs_pos() if collision_type in (1, 3) else self.get_property("pos"))
        try:
            return self.get_current_mask(collision_type).get_at(rel_pos)
        except IndexError:
            return False

    def collide_mask(self, other: pg.Mask, offset: OffsetType, collision_type: int = CollisionType.DEFAULT):
        return self.get_current_mask(collision_type).overlap(other, offset)

    def collide_rect(self, other: pg.rect.RectType, collision_type: int = CollisionType.DEFAULT):
        self_pos = self.get_abs_pos() if collision_type in (1, 3) else self.get_property("pos")
        if self.get_property("texture") is None and \
                (collision_type not in (2, 3) or self.get_visibility_mask() is None):
            return other.colliderect(self_pos, self.get_property("size"))
        return self.collide_mask(pg.Mask(other, True), -self_pos + other.topleft, collision_type)

    def get_event_listener(self, event_t: int) -> typing.Optional[typing.Callable]:
        return None if event_t not in self._event_listeners.keys() else self._event_listeners[event_t]

    def set_event_listener(self, event_t: int, callback: typing.Callable):
        self._event_listeners[event_t] = callback

    @updatemethod
    def update(self, events: list[pg.event.Event]):
        if not set(event.type for event in events).isdisjoint(self._event_listeners.keys()):
            for event in events:
                if event.type in self._event_listeners.keys():
                    self._event_listeners[event.type](self, event)

    @buildmethod
    def build(self):
        if self._surf is None or self.get_property("size") != self._surf.get_size():
            self._surf = convert_surface(pg.Surface(self.get_property("size"), pg.SRCALPHA), True)
        self._surf.fill(CLEAR)
        texture: Texture | None = self.get_property("texture")
        if texture is not None:
            texture.set_size(self.get_property("size"))
            texture.render(self._surf)
        parent_queue_build = self.get_parent_attr("queue_build")
        if parent_queue_build is not None:
            parent_queue_build()

    @rendermethod
    def render(self, display: pg.Surface):
        self.build()
        display.blit(self._surf, self.get_property("pos"))
        for obj in self._passed_objects:
            obj.render(display)
