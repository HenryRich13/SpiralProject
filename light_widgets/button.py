from light_widgets.label import *


class Button(Label):
    type_manager = TypeManager(seed=Label.type_manager,
                               cmd=TypeGroup(types.FunctionType, types.LambdaType, types.MethodType))

    def __init__(self, **properties):
        Label.__init__(self)
        self.config(cmd=lambda *args: None)
        self.set_event_listener(pg.MOUSEBUTTONUP, lambda btn, e: btn.click(e))
        if type(self) == Button:
            self.config(**properties)

    def click(self, event: pg.event.Event = None, collision_type: int = CollisionType.ABS_VISIBILITY):
        if event is None or self.collide_pos(event.pos, collision_type):
            self.get_property("cmd")(self, event)
