import standard_lib as std
import light_widgets.lib as lw
import pygame as pg
import math


pg.init()
display_size = lw.Size(1300, 800)  # lw.Size(800, 600)
display = pg.display.set_mode(display_size)
display.fill(lw.WHITE)
degree_symbol = u"\N{DEGREE SIGN}"


surf2_size = display_size * 10
surf2 = pg.Surface(surf2_size)
surf2.fill(lw.GREEN)


DEGREES = 0
RADIANS = 1


container_texture = lw.GridTexture(resize_method=lw.ResizeMethod.STRETCH, grid_offsets=lw.GridOffsets(all_sides=2))
img_surf = pg.Surface((80, 80))
sdr_texture = lw.ResizableTexture(resize_method=lw.ResizeMethod.STRETCH)


def create_textures():
    # <editor-fold desc="Container">
    container_surf = pg.Surface((5, 5), pg.SRCALPHA)
    container_surf.fill(lw.WHITE)
    container_texture.add_layer("bg", lw.Layer(container_surf, pg.Color(10, 100, 56)))
    container_surf.fill(lw.CLEAR)
    pg.draw.rect(container_surf, lw.WHITE, container_surf.get_rect(), 2)
    container_texture.add_layer("outline", lw.Layer(container_surf, pg.Color(0, 0, 100)))
    # </editor-fold>

    sdr_surf = pg.Surface((255, 1))
    for x in range(255):
        sdr_surf.set_at((x, 0), pg.Color(x, x, x))
    sdr_texture.add_layer("bg", lw.Layer(sdr_surf, lw.RED))


create_textures()


class InstructionSet(object):
    def __init__(self, pos: lw.Pos):
        self.container = lw.Container(pos=pos, size=(600, 100), texture=container_texture.copy())
        self.container.set_widget("img_color", lw.Image(pos=(10, 10), size=(80, 80), img=img_surf))

        slider_len = 200
        sdr_texture.get_layer("bg").config(color=lw.RED)
        self.container.set_widget("sdr_r", lw.Slider(pos=(110, 15), size=(slider_len, 10), texture=sdr_texture.copy(),
                                                     range=(0, 255)))
        sdr_texture.get_layer("bg").config(color=lw.GREEN)
        self.container.set_widget("sdr_g", lw.Slider(pos=(110, 45), size=(slider_len, 10), texture=sdr_texture.copy(),
                                                     range=(0, 255)))
        sdr_texture.get_layer("bg").config(color=lw.BLUE)
        self.container.set_widget("sdr_b", lw.Slider(pos=(110, 75), size=(slider_len, 10), texture=sdr_texture.copy(),
                                                     range=(0, 255)))
        self.container.get_widget("sdr_r").set_value_changed_callback(self.sdr_changed)
        self.container.get_widget("sdr_g").set_value_changed_callback(self.sdr_changed)
        self.container.get_widget("sdr_b").set_value_changed_callback(self.sdr_changed)

        new_start_x = slider_len + 130
        self.container.set_widget("txt_r", lw.Textbox(pos=(new_start_x, 5), size=(50, 30), text=0))
        self.container.set_widget("txt_g", lw.Textbox(pos=(new_start_x, 35), size=(50, 30), text=0))
        self.container.set_widget("txt_b", lw.Textbox(pos=(new_start_x, 65), size=(50, 30), text=0))
        self.container.get_widget("txt_r").bind_key(pg.K_RETURN, self.txt_return)
        self.container.get_widget("txt_g").bind_key(pg.K_RETURN, self.txt_return)
        self.container.get_widget("txt_b").bind_key(pg.K_RETURN, self.txt_return)

        new_start_x += 60
        self.container.set_widget("lbl_mag", lw.Label(pos=(new_start_x, 5), size=(100, 30), text="Magnitude:",
                                                      txt_align=lw.Alignment.MIDRIGHT, font=lw.Font(color=lw.WHITE)))
        self.container.set_widget("lbl_thick", lw.Label(pos=(new_start_x, 35), size=(100, 30), text="Thickness:",
                                                        txt_align=lw.Alignment.MIDRIGHT, font=lw.Font(color=lw.WHITE)))
        self.container.set_widget("lbl_angle", lw.Label(pos=(new_start_x, 65), size=(100, 30),
                                                        text=f"Angle{degree_symbol}:", font=lw.Font(color=lw.WHITE),
                                                        txt_align=lw.Alignment.MIDRIGHT))
        new_start_x += 105
        self.container.set_widget("txt_mag", lw.Textbox(pos=(new_start_x, 5), size=(100, 30), text=.25))
        self.container.set_widget("txt_thick", lw.Textbox(pos=(new_start_x, 35), size=(100, 30), text=.025))
        self.container.set_widget("txt_angle", lw.Textbox(pos=(new_start_x, 65), size=(100, 30), text=45))

    def sdr_changed(self, slider):
        txt, c = std.functions.switch(slider,
                                      {self.container.get_widget("sdr_r"): (self.container.get_widget("txt_r"), 0),
                                       self.container.get_widget("sdr_g"): (self.container.get_widget("txt_g"), 1),
                                       self.container.get_widget("sdr_b"): (self.container.get_widget("txt_b"), 2)})
        new_color = int(slider.get_property("value"))
        txt.config(text=new_color)
        if len(txt.get_property("text")) < txt.current_index:
            txt.current_index = len(txt.get_property("text"))
        slider.get_property("top_texture").get_layer("bg").config(color=pg.Color(new_color if c == 0 else 0,
                                                                                 new_color if c == 1 else 0,
                                                                                 new_color if c == 2 else 0))
        img = pg.Surface((80, 80), pg.SRCALPHA)
        try:
            r = int(self.container.get_widget("txt_r").get_property("text"))
        except ValueError:
            r = 0
            self.container.get_widget("sdr_r").config(value=0)
        try:
            g = int(self.container.get_widget("txt_g").get_property("text"))
        except ValueError:
            g = 0
            self.container.get_widget("sdr_g").config(value=0)
        try:
            b = int(self.container.get_widget("txt_b").get_property("text"))
        except ValueError:
            b = 0
            self.container.get_widget("sdr_b").config(value=0)
        img.fill(pg.Color(r, g, b))
        self.container.get_widget("img_color").config(img=img)

    def txt_return(self, txt: lw.Textbox, _):
        sdr = std.functions.switch(txt,
                                   {self.container.get_widget("txt_r"): self.container.get_widget("sdr_r"),
                                    self.container.get_widget("txt_g"): self.container.get_widget("sdr_g"),
                                    self.container.get_widget("txt_b"): self.container.get_widget("sdr_b")})
        sdr.config(value=int(txt.get_property("text")))

    def reset(self):
        self.container.get_widget("sdr_r").config(value=0)
        self.container.get_widget("sdr_g").config(value=0)
        self.container.get_widget("sdr_b").config(value=0)

        self.container.get_widget("txt_mag").config(text=0)
        self.container.get_widget("txt_mag").current_index = 1
        self.container.get_widget("txt_thick").config(text=0)
        self.container.get_widget("txt_thick").current_index = 1
        self.container.get_widget("txt_angle").config(text=0)
        self.container.get_widget("txt_angle").current_index = 1


class LineDrawer(object):
    def __init__(self, start: lw.PosType, angle: float, color: pg.Color, surface: pg.Surface, mode=DEGREES):
        self.original_vars = {"start": lw.Pos(start),
                              "angle": angle,
                              "color": color}
        self.start = lw.Pos(start)
        self.end = lw.Pos(0, 0)
        self.angle = angle
        self.color = color
        self.surf = surface
        self.mode = mode

    def reset(self):
        self.start = self.original_vars["start"].copy()
        self.end = lw.Pos(0, 0)
        self.angle = self.original_vars["angle"]
        self.color = pg.Color(self.original_vars["color"])

    def rotate(self, angle):
        self.angle += angle
        while self.angle < 0:
            self.angle += 360 if self.mode == DEGREES else 2 * math.pi
        while (360 if self.mode == DEGREES else 2 * math.pi) <= self.angle:
            self.angle -= 360 if self.mode == DEGREES else 2 * math.pi

    def forward(self, mag, thick):
        self.end = self.start + (mag * math.cos(math.radians(self.angle) if self.mode == DEGREES else self.angle),
                                 mag * math.sin(math.radians(self.angle) if self.mode == DEGREES else self.angle))
        pg.draw.line(self.surf, self.color, self.start, self.end, int(thick))
        self.start = self.end


line_drawer = LineDrawer(surf2_size/2, 0, lw.BLUE, surf2)
magnitude = 0
thickness = 1
colors = (pg.Color(200, 200, 200), pg.Color(175, 175, 175), pg.Color(150, 150, 150))
surf2_rect = surf2.get_rect()


start_x = 50
start_y = 50
instructions: list[InstructionSet] = [InstructionSet(lw.Pos(start_x, start_y)),
                                      InstructionSet(lw.Pos(start_x, start_y + 100)),
                                      InstructionSet(lw.Pos(start_x, start_y + 200)),
                                      InstructionSet(lw.Pos(start_x, start_y + 300)),
                                      InstructionSet(lw.Pos(start_x, start_y + 400)),
                                      InstructionSet(lw.Pos(start_x, start_y + 500)),
                                      InstructionSet(lw.Pos(start_x + 600, start_y)),
                                      InstructionSet(lw.Pos(start_x + 600, start_y + 100)),
                                      InstructionSet(lw.Pos(start_x + 600, start_y + 200)),
                                      InstructionSet(lw.Pos(start_x + 600, start_y + 300)),
                                      InstructionSet(lw.Pos(start_x + 600, start_y + 400)),
                                      InstructionSet(lw.Pos(start_x + 600, start_y + 500))]


def animation():
    global magnitude, thickness
    surf2_rect.center = lw.Size(display.get_size()) / 2
    magnitude, thickness = 0, 1
    for _ in range(int(min(display_size) * len(instructions))):
        for instruction_set in instructions:
            line_drawer.color = instruction_set.container.get_widget("img_color").get_property("img").get_at((0, 0))
            line_drawer.forward(magnitude, thickness)
            try:
                magnitude += float(instruction_set.container.get_widget("txt_mag").get_property("text"))
            except ValueError:
                instruction_set.container.get_widget("txt_mag").config(text=0)
                instruction_set.container.get_widget("txt_mag").current_index = 1
            try:
                thickness += float(instruction_set.container.get_widget("txt_thick").get_property("text"))
            except ValueError:
                instruction_set.container.get_widget("txt_thick").config(text=0)
                instruction_set.container.get_widget("txt_thick").current_index = 1
            try:
                line_drawer.rotate(float(instruction_set.container.get_widget("txt_angle").get_property("text")))
            except ValueError:
                instruction_set.container.get_widget("txt_angle").config(text=0)
                instruction_set.container.get_widget("txt_angle").current_index = 1
            (yield)


def main():
    btn_texture = lw.GridTexture(resize_method=lw.ResizeMethod.STRETCH, grid_offsets=lw.GridOffsets(all_sides=5))
    surf = pg.Surface((11, 11), pg.SRCALPHA)
    pg.draw.rect(surf, lw.WHITE, surf.get_rect(), 0, 5)
    btn_texture.add_layer("bg", lw.Layer(surf, pg.Color(200, 0, 0)))
    surf.fill(lw.CLEAR)
    pg.draw.rect(surf, lw.WHITE, surf.get_rect(), 2, 5)
    btn_texture.add_layer("outline", lw.Layer(surf, lw.BLACK))

    def btn_click(_, __):
        nonlocal coroutine
        coroutine = animation()
        line_drawer.reset()
        surf2.fill(lw.WHITE)

    def btn_reset_click(_, __):
        for instruct in instructions:
            instruct.reset()

    btn_run = lw.Button(pos=(display_size.w * 2 / 3 - 100, display_size.h - 75), size=(200, 50),
                        texture=btn_texture.copy(), text="Run", txt_align=lw.Alignment.CENTER, cmd=btn_click)
    btn_reset = lw.Button(pos=(display_size.w / 3 - 100, display_size.h - 75), size=(200, 50),
                          texture=btn_texture.copy(), text="Reset", txt_align=lw.Alignment.CENTER, cmd=btn_reset_click)
    lbl_warning_top = lw.Label(pos=(display_size.w / 2 - 300, 0), size=(600, 50), text="EPILEPSY WARNING",
                               txt_align=lw.Alignment.CENTER, font=lw.Font(name="helvetica", size=32, bold=True))
    lbl_warning_bottom = lbl_warning_top.copy()
    lbl_warning_bottom.config(pos=(display_size.w / 2 - 300, 650))

    for i in range(len(instructions)):
        instructions[i].reset()
        instructions[i].container.get_widget("txt_mag").config(text=.25)
        instructions[i].container.get_widget("txt_thick").config(text=.025)
        if i < 4:
            instructions[i].container.get_widget("sdr_r").config(value=255)
        elif i < 8:
            instructions[i].container.get_widget("sdr_g").config(value=255)
        else:
            instructions[i].container.get_widget("sdr_b").config(value=255)
        if i % 4 == 0:
            instructions[i].container.get_widget("txt_angle").config(text=118)
        elif i % 4 == 1:
            instructions[i].container.get_widget("txt_angle").config(text=-57)
        elif i % 4 == 2:
            instructions[i].container.get_widget("txt_angle").config(text=160)

    done_animating = False
    coroutine = None
    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                return
        display.fill(lw.WHITE)
        if coroutine is not None:
            if not done_animating:
                try:
                    next(coroutine)
                except StopIteration:
                    done_animating = True
            display.blit(surf2, surf2_rect)
            for event in events:
                if event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
                    done_animating = False
                    coroutine = None
        else:
            btn_run.update(events)
            btn_reset.update(events)
            for instruct_set in instructions:
                instruct_set.container.update(events)
                instruct_set.container.render(display)
            btn_reset.render(display)
            btn_run.render(display)
            lbl_warning_top.render(display)
            lbl_warning_bottom.render(display)
        pg.display.flip()


if __name__ == '__main__':
    main()
