import standard_lib as std
from light_widgets.error import LightWidgetsError
import types
import typing
from functools import wraps
import pygame as pg


class Cartesian(object):
    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        self.items = [*args]

    def __copy__(self):
        return type(self)(*self.items)

    def copy(self):
        return self.__copy__()

    def __len__(self):
        return len(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __setitem__(self, key, value):
        self.items[key] = value

    def __iter__(self):
        for val in self.items:
            yield val

    def __contains__(self, item):
        return item in self.items

    def __add__(self, other):
        if hasattr(other, "__getitem__") and len(self) <= len(other):
            return type(self)(self[i] + other[i] for i in range(len(self)))
        return type(self)(self[i] + other for i in range(len(self)))

    def __iadd__(self, other):
        if hasattr(other, "__getitem__") and len(self) <= len(other):
            for i in range(len(self)):
                self[i] += other[i]
        else:
            for i in range(len(self)):
                self[i] += other
        return self

    def __sub__(self, other):
        if hasattr(other, "__getitem__") and len(self) <= len(other):
            return type(self)(self[i] - other[i] for i in range(len(self)))
        return type(self)(self[i] - other for i in range(len(self)))

    def __rsub__(self, other):
        if hasattr(other, "__getitem__") and len(self) <= len(other):
            return type(self)(other[i] - self[i] for i in range(len(self)))
        return type(self)(other - self[i] for i in range(len(self)))

    def __isub__(self, other):
        if hasattr(other, "__getitem__") and len(self) <= len(other):
            for i in range(len(self)):
                self[i] -= other[i]
            return
        else:
            for i in range(len(self)):
                self[i] -= other
        return self

    def __mul__(self, other):
        if hasattr(other, "__getitem__") and len(self) <= len(other):
            return type(self)(self[i] * other[i] for i in range(len(self)))
        return type(self)(self[i] * other for i in range(len(self)))

    def __imul__(self, other):
        if hasattr(other, "__getitem__") and len(self) <= len(other):
            for i in range(len(self)):
                self[i] *= other[i]
        else:
            for i in range(len(self)):
                self[i] *= other
        return self

    def __truediv__(self, other):
        if hasattr(other, "__getitem__") and len(self) <= len(other):
            return type(self)(self[i] / other[i] for i in range(len(self)))
        return type(self)(self[i] / other for i in range(len(self)))

    def __rtruediv__(self, other):
        if hasattr(other, "__getitem__") and len(self) <= len(other):
            return type(self)(other[i] / self[i] for i in range(len(self)))
        return type(self)(other / self[i] for i in range(len(self)))

    def __itruediv__(self, other):
        if hasattr(other, "__getitem__") and len(self) <= len(other):
            for i in range(len(self)):
                self[i] /= other[i]
        else:
            for i in range(len(self)):
                self[i] /= other
        return self

    def __mod__(self, other):
        if hasattr(other, "__getitem__") and len(self) <= len(other):
            return type(self)(self[i] % other[i] for i in range(len(self)))
        return type(self)(self[i] % other for i in range(len(self)))

    def __rmod__(self, other):
        if hasattr(other, "__getitem__") and len(self) <= len(other):
            return type(self)(other[i] % self[i] for i in range(len(self)))
        return type(self)(other % self[i] for i in range(len(self)))

    def __imod__(self, other):
        if hasattr(other, "__getitem__") and len(self) <= len(other):
            for i in range(len(self)):
                self[i] %= other[i]
        else:
            for i in range(len(self)):
                self[i] %= other
        return self

    def __neg__(self):
        return type(self)(-value for value in self)

    def __eq__(self, other):
        if hasattr(other, "__getitem__"):
            return all(self[i] == other[i] for i in range(len(self)))
        return all(self[i] == other for i in range(len(self)))

    def __ne__(self, other):
        if hasattr(other, "__getitem__"):
            return any(self[i] != other[i] for i in range(len(self)))
        return any(self[i] != other for i in range(len(self)))


class Vector(Cartesian):
    @property
    def magnitude(self):
        return sum(val**2 for val in self)**0.5

    def normalize(self):
        self.__itruediv__(self.magnitude)

    def __str__(self):
        return f"Vector{tuple(self.items)}"


class Pos(Cartesian):
    @typing.overload
    def __init__(self, x, y):
        pass

    @typing.overload
    def __init__(self, pos):
        pass

    def __init__(self, *args):
        super().__init__(*args)

    @property
    def x(self):
        return self.items[0]

    @x.setter
    def x(self, value):
        self.items[0] = value

    @property
    def y(self):
        return self.items[1]

    @y.setter
    def y(self, value):
        self.items[1] = value

    def __str__(self):
        return f"Pos(x: {self.x}, y: {self.y})"


class Size(Cartesian):
    @typing.overload
    def __init__(self, width, height):
        pass

    @typing.overload
    def __init__(self, size):
        pass

    def __init__(self, *args):
        super().__init__(*args)

    @property
    def width(self):
        return self.items[0]

    @width.setter
    def width(self, value):
        self.items[0] = value

    @property
    def w(self):
        return self.items[0]

    @w.setter
    def w(self, value):
        self.items[0] = value

    @property
    def height(self):
        return self.items[1]

    @height.setter
    def height(self, value):
        self.items[1] = value

    @property
    def h(self):
        return self.items[1]

    @h.setter
    def h(self, value):
        self.items[1] = value

    def __str__(self):
        return f"Size(w: {self.w}, h: {self.h})"


class TypeGroup(object):
    AUTO = "<light_widgets.TypeGroup.Auto>"

    def __init__(self, *allowed_types: type, alternate_types: type | typing.Sequence[type] = None,
                 conversion_func: types.FunctionType | type(lambda val: val) | str = None):
        self.allowed = list(allowed_types)
        self.alternates = [alternate_types] if isinstance(alternate_types, type) else list(alternate_types) \
            if alternate_types is not None else []
        self.conversion = conversion_func
        if len(self.alternates) > 0 and self.conversion is None:
            raise LightWidgetsError("Cannot have alternate types if conversion func is None")

    def update(self, other: typing.Self):
        self.allowed.extend(other.allowed)
        self.alternates.extend(other.alternates)
        if self.conversion is None:
            self.conversion = other.conversion
        elif other.conversion is not None and self.conversion != other.conversion:
            raise LightWidgetsError("Conflicting conversion funcs for TypeGroup")

    def check(self, obj):
        for t in self.allowed:
            if isinstance(obj, t):
                return obj
        for t in self.alternates:
            if isinstance(obj, t):
                return self.conversion(obj)
        if len(self.alternates) == 0 and self.conversion is not None:
            if self.conversion == self.AUTO:
                return self.allowed[0](obj)
            return self.conversion(obj)
        allowed_types = (*self.allowed, *self.alternates)
        raise TypeError(f"Value of wrong type, expected: '{allowed_types}', got: {type(obj)}")


class TypeManager(object):
    def __init__(self, seed: typing.Self | dict | typing.Iterable[typing.Self | dict] = None,
                 **properties: TypeGroup):
        self.properties: dict[str, TypeGroup] = {}
        if not hasattr(seed, "__iter__"):
            seed = (seed,)
        if seed is not None:
            for s in seed:
                if s is None:
                    continue
                if isinstance(s, TypeManager):
                    s = s.properties
                self.properties.update(**s)
        self.update(**properties)

    def update(self, **properties):
        for key, value in properties.items():
            if key in self.properties.keys():
                self.properties[key].update(value)
            else:
                self.properties[key] = value

    def check(self, key: str, value):
        return self.properties[key].check(value)


class BuildStatus(object):
    NOT_BUILT = 0
    BUILT = 1


def buildmethod(method: types.MethodType):
    @wraps(method)
    def wrapper(*args, **kwargs):
        self: BuildManager = args[0]
        if not isinstance(self, BuildManager):
            raise LightWidgetsError("Can only create a buildmethod of an instance of a BuildManager")
        if not hasattr(self, "_BuildManager__builds"):
            object.__setattr__(self, "_BuildManager__builds", {"active": [], "complete": []})
        builds: dict[str, list[types.MethodType]] = object.__getattribute__(self, "_BuildManager__builds")

        output = None
        if object.__getattribute__(self, "_BuildManager__build_status") == BuildStatus.NOT_BUILT and \
                method not in builds["complete"]:
            builds["active"].append(method)
            output = method(*args, **kwargs)
            builds["active"].remove(method)
            builds["complete"].append(method)
            if len(builds["active"]) == 0:
                builds["complete"].clear()
                object.__setattr__(self, "_BuildManager__build_status", BuildStatus.BUILT)
        return output
    return wrapper


class BuildManager(object):
    __build_status: int = BuildStatus.NOT_BUILT
    __builds: dict[str, list[types.MethodType]]

    def queue_build(self):
        object.__setattr__(self, "_BuildManager__build_status", BuildStatus.NOT_BUILT)


class PropertyManager(BuildManager):
    type_manager = TypeManager()

    def __init__(self):
        self._properties: dict[str, typing.Any] = {}
        self._parent = None

    def get_parent(self):
        return self._parent

    def set_parent(self, new_parent: object):
        self._parent = new_parent
        return self

    def get_parent_attr(self, attr: str):
        if self._parent is not None and hasattr(self._parent, attr):
            return getattr(self._parent, attr)
        return None

    def get_property(self, name: str):
        return self._properties[name]

    def has_property(self, name: str):
        return name in self._properties.keys()

    def config(self, **properties):
        updated = False
        for key, value in properties.items():
            value = self.type_manager.check(key, value)
            if key in self._properties.keys() and value == self._properties[key]:
                continue

            updated = True
            self._properties[key] = value
            if hasattr(value, "set_parent"):
                value.set_parent(self)
        if updated:
            self.queue_build()

    def queue_build(self):
        super().queue_build()
        if self._parent is not None and hasattr(self._parent, "queue_build"):
            self._parent.queue_build()


def updatemethod(method: types.MethodType):
    @wraps(method)
    def wrapper(*args, **kwargs):
        self: PropertyManager = args[0]
        if not isinstance(self, PropertyManager):
            raise LightWidgetsError("Can only have an updatemethod in a subclass of PropertyManager")
        if self.has_property("enabled"):
            if self.get_property("enabled"):
                return method(*args, **kwargs)
        else:
            return method(*args, **kwargs)
    return wrapper


def rendermethod(method: types.MethodType):
    @wraps(method)
    def wrapper(*args, **kwargs):
        self: PropertyManager = args[0]
        if not isinstance(self, PropertyManager):
            raise LightWidgetsError("Can only have a rendermethod in a subclass of PropertyManager")
        if self.has_property("visible"):
            if self.get_property("visible"):
                return method(*args, **kwargs)
        else:
            return method(*args, **kwargs)
    return wrapper


# threshold for converting a surface to a mask, should be 0
MASK_THRESHOLD = 0


# <editor-fold desc="Default Surface Functions">
__DEFAULT_SURFACE: typing.Optional[pg.Surface] = None


def set_default_surface(surf: pg.Surface):
    global __DEFAULT_SURFACE
    if __DEFAULT_SURFACE is not None:
        raise LightWidgetsError("Cannot re-set the default surface")
    __DEFAULT_SURFACE = surf


def convert_surface(surf: pg.Surface, alpha: bool) -> pg.Surface:
    default_surf = __DEFAULT_SURFACE if __DEFAULT_SURFACE is not None else pg.display.get_surface()
    if alpha:
        return surf.convert_alpha(default_surf)
    return surf.convert(default_surf)
# </editor-fold>


# <editor-fold desc="Types">
PosType = Pos | list[int | float] | tuple[int | float, int | float]
SizeType = Size | list[int | float] | tuple[int | float, int | float]
Offset = Pos
OffsetType = Offset | list[int | float] | tuple[int | float, int | float]
# </editor-fold>


# <editor-fold desc="Standard Colors">
WHITE = pg.Color(255, 255, 255)
BLACK = pg.Color(000, 000, 000)
CLEAR = pg.Color(000, 000, 000, 000)
RED = pg.Color(255, 000, 000)
GREEN = pg.Color(000, 255, 000)
BLUE = pg.Color(000, 000, 255)
# </editor-fold>
