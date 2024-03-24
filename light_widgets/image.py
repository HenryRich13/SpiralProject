import types

from light_widgets.widget import *


class Alignment(object):
    TOPLEFT = "topleft"
    MIDTOP = "midtop"
    TOPRIGHT = "topright"
    MIDLEFT = "midleft"
    CENTER = "center"
    MIDRIGHT = "midright"
    BOTTOMLEFT = "bottomleft"
    MIDBOTTOM = "midbottom"
    BOTTOMRIGHT = "bottomright"


class Padding(Cartesian):
    @typing.overload
    def __init__(self, horizontal: int | float, vertical: int | float):
        pass

    @typing.overload
    def __init__(self, padding: typing.Self | dict[str, int | float]):
        pass

    def __init__(self, *args):
        if len(args) == 1:
            if type(args[0]) == Padding:
                args = (args[0].horizontal, args[0].vertical)
            else:
                args = tuple(args[0].values())
        super().__init__(*args)

    @property
    def horizontal(self):
        return self[0]

    @horizontal.setter
    def horizontal(self, value):
        self[0] = value

    @property
    def vertical(self):
        return self[1]

    @vertical.setter
    def vertical(self, value):
        self[1] = value


class Image(Widget):
    type_manager = TypeManager(seed=Widget.type_manager,
                               img=TypeGroup(pg.Surface, types.NoneType),
                               img_align=TypeGroup(str),
                               img_padding=TypeGroup(Padding))

    def __init__(self, **properties):
        super().__init__()
        self.config(img=None,
                    img_align=Alignment.TOPLEFT,
                    img_padding=Padding(0, 0))
        if type(self) == Image:
            self.config(**properties)

    def config(self, **properties):
        super().config(**properties)

    @buildmethod
    def build(self):
        Widget.build(self)
        if self.get_property("img") is None:
            return

        img_rect: pg.Rect = self.get_property("img").get_rect()
        setattr(img_rect, self.get_property("img_align"),
                getattr(self._surf.get_rect(), self.get_property("img_align")))
        sides = ("left", "right", "top", "bottom")
        for i, side in enumerate(sides):
            if side in self.get_property("img_align"):
                setattr(img_rect, side, getattr(img_rect, side) + ((-1 * (i % 2)) *
                                                                   getattr(self.get_property("img_padding"),
                                                                           "horizontal" if i < 2 else "vertical")))
        self._surf.blit(self.get_property("img"), img_rect)
