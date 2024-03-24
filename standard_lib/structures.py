class __MROFirstPriorityMeta(type):
    def mro(self) -> list[type]:
        mro_list = super().mro()
        for index, cls in enumerate(mro_list):
            if cls.__name__ == "Initializer":
                mro_list.append(mro_list.pop(index))
                return mro_list
        return mro_list


class Initializer(metaclass=__MROFirstPriorityMeta):
    INITIALIZED = 1

    @classmethod
    def get_init_str(cls, obj):
        return f"_{type(obj).__name__}__initialized"

    def initialize(self):
        setattr(self, Initializer.get_init_str(self), Initializer.INITIALIZED)

    def get_initialized(self):
        return Initializer.get_init_str(self) in object.__getattribute__(self, "__dict__").keys()

    def _post_init_getattribute(self, name: str):
        return object.__getattribute__(self, name)

    def _post_init_setattr(self, name: str, value):
        object.__setattr__(self, name, value)

    def __getattribute__(self, name: str):
        if Initializer.get_init_str(self) in object.__getattribute__(self, "__dict__").keys():
            return object.__getattribute__(self, "_post_init_getattribute")(name)
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value):
        if Initializer.get_init_str(self) in object.__getattribute__(self, "__dict__").keys():
            object.__getattribute__(self, "_post_init_setattr")(name, value)
        object.__setattr__(self, name, value)
