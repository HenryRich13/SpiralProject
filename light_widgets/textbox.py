import types

from light_widgets.label import *


class TextboxTexture(object):
    DEFAULT = 0
    ROUNDED = 1


_DEFAULT_TEXTURES: dict[TextboxTexture, Texture]


def _setup_default_textures():
    global _DEFAULT_TEXTURES
    bg_color = pg.Color(200, 200, 200)
    outline_color = pg.Color(000, 000, 200)
    surf = pg.Surface((15, 15), pg.SRCALPHA)

    default_texture = GridTexture(resize_method=ResizeMethod.STRETCH, grid_offsets=GridOffsets(all_sides=3))
    surf.fill(WHITE)
    default_texture.add_layer("bg", Layer(surf, bg_color))

    surf.fill(CLEAR)
    pg.draw.rect(surf, outline_color, surf.get_rect(), 3)
    default_texture.add_layer("outline", Layer(surf, outline_color))

    rounded_texture = GridTexture(resize_method=ResizeMethod.STRETCH, grid_offsets=GridOffsets(all_sides=7))
    surf.fill(CLEAR)
    pg.draw.rect(surf, bg_color, surf.get_rect(), 0, 7)
    rounded_texture.add_layer("bg", Layer(surf, bg_color))

    surf.fill(CLEAR)
    pg.draw.rect(surf, outline_color, surf.get_rect(), 3, 7)
    rounded_texture.add_layer("outline", Layer(surf, outline_color))

    _DEFAULT_TEXTURES = {TextboxTexture.DEFAULT: default_texture,
                         TextboxTexture.ROUNDED: rounded_texture}


class Cursor(PropertyManager):
    type_manager = TypeManager(seed=None,
                               pos=TypeGroup(Pos, conversion_func=TypeGroup.AUTO),
                               size=TypeGroup(Size, conversion_func=TypeGroup.AUTO),
                               color=TypeGroup(pg.Color, conversion_func=TypeGroup.AUTO),
                               blinks_ps=TypeGroup(float, conversion_func=TypeGroup.AUTO),
                               visible=TypeGroup(bool, conversion_func=TypeGroup.AUTO))

    def __init__(self, **properties):
        super().__init__()
        self.config(pos=Pos(0, 0),
                    size=Size(1, 12),
                    color=BLACK,
                    blinks_ps=1.5,
                    visible=False)
        self._surf: typing.Optional[pg.Surface] = None
        self._clock = pg.time.Clock()
        self._current_time: float = 0.0
        if type(self) == Cursor:
            self.config(**properties)

    def get_abs_pos(self):
        abs_pos = self.get_property("pos").copy()
        parent_abs_pos = self.get_parent_attr("get_abs_pos")
        if parent_abs_pos is not None:
            abs_pos += parent_abs_pos()
        return abs_pos

    def update(self, *_):
        self._current_time += self._clock.tick()/1000
        if self._current_time >= 1/self.get_property("blinks_ps"):
            self._current_time = 0.0
            self.config(visible=not self.get_property("visible"))

    def reset(self):
        self._clock.tick()
        self._current_time = 0.0
        self.config(visible=True)

    @buildmethod
    def build(self):
        if self._surf is None or self.get_property("size") != self._surf.get_size():
            self._surf = convert_surface(pg.Surface(self.get_property("size")), False)
        self._surf.fill(self.get_property("color"))

    @rendermethod
    def render(self, display: pg.Surface):
        self.build()
        display.blit(self._surf, self.get_abs_pos())


_DEFAULT_KEYS = (pg.K_LEFT, pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_BACKSPACE, pg.K_DELETE, pg.K_HOME, pg.K_END)
_INNER_OFFSET = 7


class Textbox(Widget):
    type_manager = TypeManager(seed=Widget.type_manager,
                               texture=TypeGroup(alternate_types=int,
                                                 conversion_func=lambda name: _DEFAULT_TEXTURES[name]),
                               text=TypeGroup(str, conversion_func=TypeGroup.AUTO),
                               font=TypeGroup(Font),
                               password=TypeGroup(str, types.NoneType, conversion_func=TypeGroup.AUTO))

    def __init__(self, **properties):
        if "_DEFAULT_TEXTURES" not in globals().keys():
            _setup_default_textures()
        Widget.__init__(self)
        self.current_index = 0
        self.config(texture=TextboxTexture.DEFAULT,
                    text="",
                    font=Font(),
                    password=None)
        pg.key.set_repeat(500, 50)
        self._cursor = Cursor().set_parent(self)
        self.pass_render(self._cursor)
        self._focused = False
        self._key_binds: dict[int, dict[int, typing.Callable]] = {}
        self.set_event_listener(pg.MOUSEBUTTONUP, self.on_click)
        self.set_event_listener(pg.KEYDOWN, self.keybind_callback)
        for key in _DEFAULT_KEYS:
            self.bind_key(key, self._default_binds)
        if type(self) == Textbox:
            self.config(**properties)

    def config(self, **properties):
        super().config(**properties)

    def on_click(self, _, event: pg.event.Event):
        self._focused = self.collide_pos(event.pos, CollisionType.ABS_VISIBILITY)
        if self._focused:
            smallest = None
            for i in range(len(self.get_property("text")) + 1):
                txt_size = self.get_property("font").size(self.get_property("text")[:i])
                dist = abs((event.pos[0] - self.get_abs_pos().x) - (_INNER_OFFSET + txt_size[0]))
                if smallest is None:
                    smallest = (i, dist)
                elif dist < smallest[1]:
                    smallest = (i, dist)
            self.current_index = 0 if smallest is None else smallest[0]
            self._cursor.reset()
            self.queue_build()
        else:
            self._cursor.config(visible=False)

    def insert_text(self, text: str | int):
        if not self._focused:
            return
        if self.current_index == 0:
            if type(text) == int:
                if text == pg.K_DELETE:
                    self.config(text=self.get_property("text")[1:])
                return
            self.config(text=text + self.get_property("text"))
            self.current_index = len(text)
        elif self.current_index == len(self.get_property("text")):
            if type(text) == int:
                if text == pg.K_BACKSPACE:
                    self.config(text=self.get_property("text")[:-1])
                    self.current_index -= 1
                return
            self.config(text=self.get_property("text") + text)
            self.current_index += len(text)
        else:
            if type(text) == int:
                before = self.get_property("text")[:self.current_index - (1 if text == pg.K_BACKSPACE else 0)]
                after = self.get_property("text")[self.current_index + (0 if text == pg.K_BACKSPACE else 1):]
                self.config(text=before + after)
                if text == pg.K_BACKSPACE:
                    self.current_index -= 1
                return
            self.config(text=self.get_property("text")[:self.current_index] + text +
                             self.get_property("text")[self.current_index:])
            self.current_index += len(text)

    def _default_binds(self, _, event: pg.event.Event):
        if not self._focused:
            return
        new_index = std.functions.switch(event.key,
                                         {pg.K_LEFT: max(self.current_index - 1, 0),
                                          pg.K_UP: 0,
                                          pg.K_RIGHT: min(self.current_index + 1, len(self.get_property("text"))),
                                          pg.K_DOWN: len(self.get_property("text")),
                                          pg.K_HOME: 0,
                                          pg.K_END: len(self.get_property("text")),
                                          "DEFAULT": None})
        if new_index is not None:
            self.current_index = new_index
        elif event.key in (pg.K_BACKSPACE, pg.K_DELETE):
            self.insert_text(event.key)
        self._cursor.reset()
        self.queue_build()

    def get_key_bind(self, key: int, mod: int = pg.KMOD_NONE):
        if key not in self._key_binds.keys():
            return None
        possible_mods = []
        for set_mod in self._key_binds[key].keys():
            if mod & set_mod == set_mod:
                possible_mods.append(set_mod)

        max_bits = possible_mods[0]
        for num in possible_mods:
            if std.functions.count_bits(max_bits) < std.functions.count_bits(num):
                max_bits = num
        for num in possible_mods:
            if std.functions.count_bits(num) < std.functions.count_bits(max_bits):
                possible_mods.remove(num)
        if len(possible_mods) == 1:
            return self._key_binds[key][possible_mods[0]]
        return None

    def bind_key(self, key: int, callback: typing.Callable, mod: int = pg.KMOD_NONE):
        if key in self._key_binds.keys():
            self._key_binds[key][mod] = callback
        else:
            self._key_binds[key] = {mod: callback}

    def keybind_callback(self, _, event: pg.event.Event):
        func = self.get_key_bind(event.key, event.mod)
        if func is not None:
            func(self, event)

    @updatemethod
    def update(self, events: list[pg.event.Event]):
        Widget.update(self, events)
        if self._focused:
            self._cursor.update()
            for event in events:
                if event.type == pg.TEXTINPUT:
                    self.insert_text(event.text)

    @buildmethod
    def build(self):
        Widget.build(self)

        font: Font = self.get_property("font")
        if self.get_property("password") is not None:
            text: str = "".join(self.get_property("password") for _ in range(len(self.get_property("text"))))
        else:
            text: str = self.get_property("text")

        txt_obj: pg.Surface = font.get_render(text)
        txt_rect = txt_obj.get_rect()
        txt_rect.midleft = (_INNER_OFFSET, self._surf.get_rect().centery)

        if self.get_property("size").w - _INNER_OFFSET < txt_rect.right:
            txt_rect.right = self.get_property("size").w - _INNER_OFFSET

        self._surf.blit(txt_obj, txt_rect)

        if self.current_index == len(text):
            x_pos = txt_rect.x + font.size(text[:len(text)])[0]
        else:
            x_pos = txt_rect.x + font.size(text[:self.current_index + 1])[0] - font.size(text[self.current_index])[0]
        self._cursor.config(pos=(x_pos, txt_rect.y),
                            size=(1, txt_rect.h))
