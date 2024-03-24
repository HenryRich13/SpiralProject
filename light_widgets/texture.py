from light_widgets.utils import *


# <editor-fold desc="Base Texture">
class Layer(PropertyManager):
    type_manager = TypeManager(alpha_map=TypeGroup(pg.Surface),
                               color=TypeGroup(pg.Color, conversion_func=TypeGroup.AUTO),
                               visible=TypeGroup(bool, conversion_func=TypeGroup.AUTO))

    def __init__(self, alpha_map: pg.Surface, color: pg.Color, visible=True):
        PropertyManager.__init__(self)
        self._surf: typing.Optional[pg.Surface] = None
        self.config(alpha_map=alpha_map.copy(), color=pg.Color(color), visible=visible)

    def __copy__(self):
        return type(self)(**self._properties).set_parent(self.get_parent())

    def copy(self):
        return self.__copy__()

    def get_size(self) -> Size:
        return Size(self.get_property("alpha_map").get_size())

    def get_property(self, name: str):
        output = super().get_property(name)
        if name in ("alpha_map", "color"):
            self.queue_build()
        return output

    @buildmethod
    def build(self):
        self._surf = convert_surface(self.get_property("alpha_map"), True)
        self._surf.fill(self.get_property("color"), special_flags=pg.BLEND_RGBA_MULT)

    @rendermethod
    def render(self, disp: pg.Surface):
        self.build()
        disp.blit(self._surf, (0, 0))


class Texture(BuildManager):
    def __init__(self, layers: dict[typing.Any, Layer] = None, size: SizeType = Size(0, 0)):
        self._layers: dict[typing.Any, Layer] = {}
        self._mask: typing.Optional[pg.Mask] = None
        self._surf: typing.Optional[pg.Surface] = None
        self._size = size if isinstance(size, Size) else Size(size)
        self._parent = None
        if layers is not None:
            for key, value in layers.items():
                self.add_layer(key, value)

    def __copy__(self):
        new_layers = {}
        for key, layer in self._layers.items():
            new_layers[key] = layer.copy()
        return type(self)(new_layers, self._size.copy()).set_parent(self._parent)

    def copy(self):
        return self.__copy__()

    @staticmethod
    def create_layers(surf: pg.Surface):
        size = Size(surf.get_size())
        layers: dict[tuple[int | float, int | float, int | float], list[tuple[int, int]] | Layer] = {}
        for y in range(size.h):
            for x in range(size.w):
                color = tuple(surf.get_at((x, y)))
                if color in layers.keys():
                    layers[color].append((x, y))
                else:
                    layers[color] = [(x, y)]
        layer_surf = convert_surface(pg.Surface(size, pg.SRCALPHA), True)
        for color, positions in layers.items():
            layer_surf.fill(CLEAR)
            for pos in positions:
                layer_surf.set_at(pos, WHITE)
            layers[color] = Layer(layer_surf, pg.Color(color))
        return layers, size

    @classmethod
    def from_surf(cls, surf: pg.Surface):
        return cls(*cls.create_layers(surf))

    def get_parent(self):
        return self._parent

    def set_parent(self, new_parent: object):
        self._parent = new_parent
        return self

    def get_parent_attr(self, attr: str):
        if self._parent is not None and hasattr(self._parent, attr):
            return getattr(self._parent, attr)
        return None

    def queue_build(self):
        super().queue_build()
        if self._parent is not None and hasattr(self._parent, "queue_build"):
            self._parent.queue_build()

    def get_layer(self, name: str):
        return self._layers[name]

    def add_layer(self, name: str, layer: Layer):
        if name in self._layers.keys():
            raise LightWidgetsError(f"Texture already contains a layer with the name '{name}'")
        self._layers[name] = layer
        if layer.get_size() != tuple(self._layers.values())[0].get_size():
            raise LightWidgetsError("All layers in texture must be the same size")
        layer.set_parent(self)
        self.queue_build()

    def get_mask(self):
        if self._mask is None:
            self.queue_build()
            self.build()
        return self._mask

    def get_size(self):
        return self._size

    def set_size(self, new_size: SizeType):
        self._size = Size(new_size)
        self.queue_build()

    @buildmethod
    def build(self) -> pg.Surface | None:
        surface = convert_surface(pg.Surface(tuple(self._layers.values())[0].get_size(), pg.SRCALPHA), True)
        for layer in self._layers.values():
            layer.render(surface)
        if self._surf is None or self._size != self._surf.get_size():
            self._surf = convert_surface(pg.Surface(self._size, pg.SRCALPHA), True)
        self._surf.fill(CLEAR)
        if type(self) != Texture:
            return surface
        self._surf.blit(surface, (0, 0))
        self._mask = pg.mask.from_surface(self._surf, MASK_THRESHOLD)

    def render(self, display: pg.Surface):
        self.build()
        display.blit(self._surf, (0, 0))
# </editor-fold>


# <editor-fold desc="Resizable Texture">
class ResizeMethod(object):
    STRETCH = 0
    TILE = 1
    BOTH = 2


class ResizableTexture(Texture):
    def __init__(self, layers: dict[typing.Any, Layer] = None, size: SizeType = Size(0, 0),
                 resize_method: int = ResizeMethod.BOTH):
        super().__init__(layers, size)
        self._resize_method = resize_method

    def __copy__(self):
        new_layers = {}
        for key, layer in self._layers.items():
            new_layers[key] = layer.copy()
        return type(self)(new_layers, self._size.copy(), self._resize_method).set_parent(self._parent)

    @classmethod
    def from_surf(cls, surf: pg.Surface, resize_method: int = ResizeMethod.BOTH):
        return cls(*cls.create_layers(surf), resize_method=resize_method)

    @property
    def resize_method(self):
        return self._resize_method

    @resize_method.setter
    def resize_method(self, new_method: int):
        self._resize_method = new_method
        self.queue_build()

    @buildmethod
    def build(self) -> pg.Surface | None:
        surface: pg.Surface = super().build()
        if type(self) != ResizableTexture:
            return surface
        count_func = std.functions.switch(self.resize_method,
                                          {ResizeMethod.TILE: lambda val: int(val + 1) if val % 1 != 0 else int(val),
                                           ResizeMethod.STRETCH: lambda _: 1,
                                           ResizeMethod.BOTH: round})
        tile_counts = Offset(max(count_func(self._size.w/surface.get_size()[0]), 1),
                             max(count_func(self._size.h/surface.get_size()[1]), 1))
        sizable_surf = convert_surface(pg.Surface(tile_counts * surface.get_size(), pg.SRCALPHA), True)
        for x in range(tile_counts.x):
            for y in range(tile_counts.y):
                sizable_surf.blit(surface, (x * surface.get_size()[0], y * surface.get_size()[1]))
        if self.resize_method in (ResizeMethod.STRETCH, ResizeMethod.BOTH):
            pg.transform.scale(sizable_surf, self._size, self._surf)
        else:
            self._surf.blit(surface, (0, 0))
        self._mask = pg.mask.from_surface(self._surf, MASK_THRESHOLD)
# </editor-fold>


class GridOffsets(object):
    def __init__(self, all_sides: int = 0, horizontal: int = 0, vertical: int = 0,
                 left: int = 0, top: int = 0, right: int = 0, bottom: int = 0):
        self.left = self.top = self.right = self.bottom = all_sides
        if horizontal != 0:
            self.left = self.right = horizontal
        if vertical != 0:
            self.top = self.bottom = vertical
        if left != 0:
            self.left = left
        if top != 0:
            self.top = top
        if right != 0:
            self.right = right
        if bottom != 0:
            self.bottom = bottom

    @property
    def all(self):
        return self.left, self.top, self.right, self.bottom

    @all.setter
    def all(self, value: int):
        self.left = self.top = self.right = self.bottom = value

    @property
    def horizontal(self):
        return self.left, self.right

    @horizontal.setter
    def horizontal(self, value: int):
        self.left = self.right = value

    @property
    def vertical(self):
        return self.top, self.bottom

    @vertical.setter
    def vertical(self, value: int):
        self.top = self.bottom = value


class GridTexture(ResizableTexture):
    def __init__(self, layers: dict[typing.Any, Layer] = None, size: SizeType = Size(0, 0),
                 resize_method: int = ResizeMethod.BOTH, grid_offsets: GridOffsets = GridOffsets()):
        super().__init__(layers, size, resize_method)
        self._grid_offsets = grid_offsets

    def __copy__(self):
        new_layers = {}
        for key, layer in self._layers.items():
            new_layers[key] = layer.copy()
        return type(self)(new_layers, self._size.copy(), self._resize_method,
                          self._grid_offsets).set_parent(self._parent)

    def get_grid_offsets(self):
        self.queue_build()
        return self._grid_offsets

    @buildmethod
    def build(self) -> pg.Surface | None:
        surface: pg.Surface = super().build()
        if type(self) != GridTexture:
            return surface

        outer_size = Size(sum(self._grid_offsets.horizontal), sum(self._grid_offsets.vertical))
        count_func = std.functions.switch(self.resize_method,
                                          {ResizeMethod.TILE: lambda val: int(val + 1) if val % 1 != 0 else int(val),
                                           ResizeMethod.STRETCH: lambda _: 1,
                                           ResizeMethod.BOTH: round})
        center_count = Offset(max(count_func((self._size.w - outer_size.w)/(surface.get_size()[0] - outer_size.w)), 1),
                              max(count_func((self._size.h - outer_size.h)/(surface.get_size()[1] - outer_size.h)), 1))
        center_size = Size(surface.get_size()) - outer_size
        temp_surfs = {"left": convert_surface(pg.Surface((self._grid_offsets.left, center_count.y * center_size.h),
                                                         pg.SRCALPHA), True),
                      "top": convert_surface(pg.Surface((center_count.x * center_size.w, self._grid_offsets.top),
                                                        pg.SRCALPHA), True),
                      "center": convert_surface(pg.Surface(center_count * center_size, pg.SRCALPHA), True),
                      "right": convert_surface(pg.Surface((self._grid_offsets.right, center_count.y * center_size.h),
                                                          pg.SRCALPHA), True),
                      "bottom": convert_surface(pg.Surface((center_count.x * center_size.w, self._grid_offsets.bottom),
                                                           pg.SRCALPHA), True)}

        for surf in temp_surfs.values():
            surf.fill(CLEAR)
        for i in range(center_count.x):
            size = [surface.get_size()[0] - outer_size.w, self._grid_offsets.top]
            temp_surfs["top"].blit(surface, (i * center_size.w, 0), ((self._grid_offsets.left, 0), size))
            size[1] = self._grid_offsets.bottom
            temp_surfs["bottom"].blit(surface, (i * center_size.w, 0), (
                (self._grid_offsets.left, surface.get_size()[0] - self._grid_offsets.bottom), size))
        for i in range(center_count.y):
            size = [self._grid_offsets.left, surface.get_size()[1] - outer_size.h]
            temp_surfs["left"].blit(surface, (0, i * center_size.h), ((0, self._grid_offsets.top), size))
            size[0] = self._grid_offsets.right
            temp_surfs["right"].blit(surface, (0, i * center_size.w), (
                (surface.get_size()[1] - self._grid_offsets.right, self._grid_offsets.top), size))
        for i in range(center_count.y):
            for j in range(center_count.x):
                temp_surfs["center"].blit(surface, (j * center_size.w, i * center_size.h),
                                          (self._grid_offsets.left, self._grid_offsets.top, *center_size))
        self._surf.blit(surface, (0, 0), (0, 0, self._grid_offsets.left, self._grid_offsets.top))
        self._surf.blit(surface, (self._size.w - self._grid_offsets.right, 0),
                        (surface.get_size()[0] - self._grid_offsets.right, 0,
                         self._grid_offsets.right, self._grid_offsets.top))
        self._surf.blit(surface, self._size - (self._grid_offsets.right, self._grid_offsets.bottom),
                        pg.Rect(Size(surface.get_size()) - (self._grid_offsets.right, self._grid_offsets.bottom),
                                (self._grid_offsets.right, self._grid_offsets.bottom)))
        self._surf.blit(surface, (0, self._size.h - self._grid_offsets.bottom),
                        (0, surface.get_size()[1] - self._grid_offsets.bottom,
                         self._grid_offsets.left, self._grid_offsets.bottom))
        if self._resize_method == ResizeMethod.TILE:
            self._surf.blit(temp_surfs["left"], (0, self._grid_offsets.top),
                            (0, 0, self._grid_offsets.left, self._size.h - outer_size.h))
            self._surf.blit(temp_surfs["top"], (self._grid_offsets.left, 0),
                            (0, 0, self._size.w - outer_size.w, self._grid_offsets.top))
            self._surf.blit(temp_surfs["center"], (self._grid_offsets.left, self._grid_offsets.top),
                            (self._size - outer_size))
            self._surf.blit(temp_surfs["right"], (self._size.w - self._grid_offsets.right, self._grid_offsets.top),
                            (0, 0, self._grid_offsets.right, self._size.h - outer_size.h))
            self._surf.blit(temp_surfs["bottom"], (self._grid_offsets.left, self._size.h - self._grid_offsets.bottom),
                            (0, 0, self._size.w - outer_size.w, self._grid_offsets.bottom))
        else:
            self._surf.blit(pg.transform.scale(temp_surfs["left"],
                                               (self._grid_offsets.left, self._size.h - outer_size.h)),
                            (0, self._grid_offsets.top))
            self._surf.blit(pg.transform.scale(temp_surfs["top"],
                                               (self._size.w - outer_size.w, self._grid_offsets.top)),
                            (self._grid_offsets.left, 0))
            self._surf.blit(pg.transform.scale(temp_surfs["center"], self._size - outer_size),
                            (self._grid_offsets.left, self._grid_offsets.top))
            self._surf.blit(pg.transform.scale(temp_surfs["right"],
                                               (self._grid_offsets.right, self._size.h - outer_size.h)),
                            (self._size.w - self._grid_offsets.right, self._grid_offsets.top))
            self._surf.blit(pg.transform.scale(temp_surfs["bottom"],
                                               (self._size.w - outer_size.w, self._grid_offsets.bottom)),
                            (self._grid_offsets.left, self._size.h - self._grid_offsets.bottom))
        self._mask = pg.mask.from_surface(self._surf)
