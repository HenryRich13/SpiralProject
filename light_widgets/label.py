from light_widgets.image import *


class Font(PropertyManager):
    type_manager = TypeManager(name=TypeGroup(str, conversion_func=TypeGroup.AUTO),
                               size=TypeGroup(int, conversion_func=TypeGroup.AUTO),
                               bold=TypeGroup(bool, conversion_func=TypeGroup.AUTO),
                               italic=TypeGroup(bool, conversion_func=TypeGroup.AUTO),
                               antialias=TypeGroup(bool, conversion_func=TypeGroup.AUTO),
                               color=TypeGroup(pg.Color, conversion_func=TypeGroup.AUTO),
                               highlight=TypeGroup(pg.Color, types.NoneType, conversion_func=TypeGroup.AUTO))

    def __init__(self, **properties):
        super().__init__()
        if not pg.font.get_init():
            pg.font.init()
        self.config(name="verdana",
                    size=16,
                    bold=False,
                    italic=False,
                    antialias=True,
                    color=BLACK,
                    highlight=None)
        self._font_obj: typing.Optional[pg.font.Font] = None
        if type(self) == Font:
            self.config(**properties)

    def __copy__(self):
        return type(self)(**self._properties)

    def copy(self):
        return self.__copy__()

    def size(self, text: str):
        self.build()
        return self._font_obj.size(text)

    @buildmethod
    def build(self):
        self._font_obj = pg.font.SysFont(self.get_property("name"),
                                         self.get_property("size"),
                                         self.get_property("bold"),
                                         self.get_property("italic"))

    def get_render(self, text: str):
        self.build()
        return self._font_obj.render(text,
                                     self.get_property("antialias"),
                                     self.get_property("color"),
                                     self.get_property("highlight"))


class Label(Widget):
    type_manager = TypeManager(seed=Widget.type_manager,
                               text=TypeGroup(str, conversion_func=TypeGroup.AUTO),
                               font=TypeGroup(Font),
                               txt_align=TypeGroup(str),
                               txt_padding=TypeGroup(Padding),
                               clip_text=TypeGroup(bool, conversion_func=TypeGroup.AUTO))

    def __init__(self, **properties):
        Widget.__init__(self)
        self.config(text="",
                    font=Font(),
                    txt_align=Alignment.TOPLEFT,
                    txt_padding=Padding(0, 0),
                    clip_text=False)
        if type(self) == Label:
            self.config(**properties)

    @buildmethod
    def build(self):
        Widget.build(self)
        txt_obj: pg.Surface = self.get_property("font").get_render(self.get_property("text"))
        txt_rect = txt_obj.get_rect()
        setattr(txt_rect, self.get_property("txt_align"),
                getattr(self._surf.get_rect(), self.get_property("txt_align")))
        sides = ("left", "right", "top", "bottom")
        for i, side in enumerate(sides):
            if side in self.get_property("txt_align"):
                setattr(txt_rect, side, getattr(txt_rect, side) + ((-1 * (i % 2)) *
                        getattr(self.get_property("txt_padding"), "horizontal" if i < 2 else "vertical")))
        self._surf.blit(txt_obj, txt_rect)
        if self.get_property("clip_text"):
            if self.get_property("texture") is None:
                raise LightWidgetsError("Cannot clip text if texture is none")
            clipping_surf = self.get_property("texture").get_mask().to_surface(unsetcolor=CLEAR)
            self._surf.blit(clipping_surf, (0, 0), special_flags=pg.BLEND_RGBA_MIN)


class ImageLabel(Image, Label):
    type_manager = TypeManager(seed=(Image.type_manager, Label.type_manager))

    def __init__(self, **properties):
        Label.__init__(self)
        self.config(img=None,
                    img_align=Alignment.TOPLEFT,
                    img_padding=Padding(0, 0))
        if type(self) == ImageLabel:
            self.config(**properties)

    @buildmethod
    def build(self):
        Image.build(self)
        Label.build(self)
