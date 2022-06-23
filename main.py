# =====================
# UNIT CIRCLE SIMULATOR
# =====================
# Author: ctrl-empress
# Date: June 23, 2022
# Version: 1.0
# ====================

import math

import pygame as pg


# Color struct
class Color:
    BLACK = pg.Color(0, 0, 0)
    GRAY = pg.Color(180, 180, 180)
    WHITE = pg.Color(255, 255, 255)
    RED = pg.Color(255, 0, 0)
    GREEN = pg.Color(0, 204, 0)
    BLUE = pg.Color(0, 102, 255)
    ORANGE = pg.Color(255, 102, 0)
    PINK = pg.Color(255, 0, 102)


class UnitCircle:
    VERSION = '1.0'
    AUTHOR = 'ctrl-empress'

    # Window props
    WIDTH = 1000
    HEIGHT = 600
    TITLE = 'Unit Circle'
    DIM = (WIDTH, HEIGHT)
    ICON_NAME = 'icon.bmp'

    FONT_NAME = 'monospace'
    FONT_SIZES = (15, 18, 22)

    # Unit circle snap points
    SNAP_POINTS = (
        (1, 0), (-1, 0),
        (0, 1), (0, -1)
    )

    # Main special angles in radians
    SPEC_ANGLES = (
        math.pi / 2,
        math.pi,
        3 * math.pi / 2,
        math.tau
    )

    # Value to reach before snapping (degrees)
    SNAP_THRESHOLD = 6

    UNIT_CIRC_RAD = 200  # Default radius
    MIN_RAD = 100
    MAX_RAD = 300

    def __init__(self):
        pg.init()
        self.canvas = pg.display.set_mode(self.DIM, pg.HWSURFACE)
        pg.display.set_caption(self.TITLE)

        icon = pg.image.load(self.ICON_NAME)
        if icon is not None:
            pg.display.set_icon(icon)

        self.fonts = {}
        self.__load_fonts()

        self.is_running = False
        self.enable_snap = True
        self.rad_mode = False
        self.unit_circ_rad = self.UNIT_CIRC_RAD

    def __del__(self):
        pg.quit()

    def start(self):
        self.is_running = True

        # Main loop
        while self.is_running:
            self.handle_events()
            self.render()

    def handle_events(self):
        event = pg.event.wait()
        # Python >=3.10
        match event.type:
            case pg.QUIT:
                self.is_running = False
            case pg.KEYUP:
                match event.key:
                    case pg.K_s:
                        self.enable_snap = self.toggle(self.enable_snap)
                    case pg.K_r:
                        self.rad_mode = self.toggle(self.rad_mode)
                    case pg.K_LEFT:
                        if self.unit_circ_rad > self.MIN_RAD:
                            self.unit_circ_rad -= 5
                    case pg.K_RIGHT:
                        if self.unit_circ_rad < self.MAX_RAD:
                            self.unit_circ_rad += 5

    def render(self):
        self.canvas.fill(Color.WHITE)
        canvas_center = pg.Vector2(self.canvas.get_size()) // 2
        cursor = pg.Vector2(pg.mouse.get_pos())

        # =======================
        # UNIT CIRCLE
        # =======================
        UNIT_CIRC_OUT = 2

        pg.draw.circle(
            self.canvas,
            Color.GRAY,
            canvas_center,
            self.unit_circ_rad,
            UNIT_CIRC_OUT
        )

        # =======================
        # X & Y AXES
        # =======================
        # x-axis
        pg.draw.line(
            self.canvas, Color.GRAY,
            (0, canvas_center.y),
            (self.canvas.get_width(), canvas_center.y)
        )

        # y-axis
        pg.draw.line(
            self.canvas, Color.GRAY,
            (canvas_center.x, 0),
            (canvas_center.x, self.canvas.get_height())
        )

        # Calculate the unit values
        unit = (cursor - canvas_center).normalize()
        unit.y *= -1  # Invert y-axis

        # Calculate the angle
        test_angle = self.calc_angle(unit)

        # =======================
        # SNAPPING FEATURE
        # =======================
        tresh = math.radians(self.SNAP_THRESHOLD)
        from_up = True if unit.y >= 0 else False
        from_left = True if unit.x < 0 else False

        if self.enable_snap:
            if self.SPEC_ANGLES[0] - tresh <= test_angle <= self.SPEC_ANGLES[0] + tresh:
                unit = pg.Vector2(self.SNAP_POINTS[2])
            elif self.SPEC_ANGLES[1] - tresh <= test_angle <= self.SPEC_ANGLES[1] + tresh:
                unit = pg.Vector2(self.SNAP_POINTS[1])
            elif self.SPEC_ANGLES[2] - tresh <= test_angle <= self.SPEC_ANGLES[2] + tresh:
                unit = pg.Vector2(self.SNAP_POINTS[3])
            # from 4th quad
            elif test_angle >= self.SPEC_ANGLES[3] - tresh or test_angle <= tresh:
                unit = pg.Vector2(self.SNAP_POINTS[0])

        # Apply the snap and recalculate the angle
        angle = self.calc_angle(unit)

        if unit == self.SNAP_POINTS[0]:
            angle = 0 if from_up else math.tau

        point_on_circle = pg.Vector2(
            canvas_center.x + self.unit_circ_rad * math.cos(angle),
            canvas_center.y + self.unit_circ_rad * -math.sin(angle)
        )

        # =======================
        # RADIUS
        # =======================
        pg.draw.line(
            self.canvas, Color.BLACK,
            (canvas_center.x, canvas_center.y),
            point_on_circle,
            width=2
        )

        # =======================
        # 90° angle
        # =======================
        # Only draw this if the point snaps to (0, 1),
        # otherwise draw the anlge arc
        ARC_DIA = 80
        if angle == self.SPEC_ANGLES[0]:
            ninety_deg = pg.Rect(0, 0, ARC_DIA / 2, ARC_DIA / 2)
            ninety_deg.bottomleft = canvas_center
            pg.draw.rect(
                self.canvas,
                Color.BLACK,
                ninety_deg,
                width=1
            )
        else:
            # =======================
            # ANGLE ARC
            # =======================
            # I won't be using gfxdraw here
            arc_rect = pg.Rect(0, 0, ARC_DIA, ARC_DIA)
            arc_rect.center = canvas_center
            pg.draw.arc(
                self.canvas,
                Color.BLACK,
                arc_rect,
                0, angle
            )

        # =======================
        # COS(θ) LINE
        # =======================
        cos_line = pg.draw.line(
            self.canvas,
            Color.ORANGE,
            point_on_circle,
            (canvas_center.x, point_on_circle.y),
            width=2
        )

        # =======================
        # SIN(θ) LINE
        # =======================
        sine_line = pg.draw.line(
            self.canvas, Color.ORANGE,
            (point_on_circle.x, canvas_center.y),
            point_on_circle,
            width=2
        )

        # =======================
        # SEC(θ) LINE
        # =======================
        # Calculate the width of the other portion of sec(θ) line
        direction = math.copysign(1, unit.x)
        sec2_len = sine_line.height * math.tan(angle)
        # Add the 1st portion of the line to the other
        sec_len = canvas_center.x + cos_line.width * direction

        # Correct the direction
        if angle <= self.SPEC_ANGLES[1]:
            sec_len += sec2_len
        else:
            sec_len -= sec2_len

        # Prevent the line from getting infinitely long
        if angle == self.SPEC_ANGLES[0] or angle == self.SPEC_ANGLES[2]:
            sec_len = 0 if from_left else self.canvas.get_width()

        sec_line = pg.draw.line(
            self.canvas,
            Color.BLUE,
            canvas_center,
            (sec_len, canvas_center.y),
            width=2
        )

        # =======================
        # TAN(θ) LINE
        # =======================
        tan_end = pg.Vector2(sec_len, canvas_center.y)

        if angle == self.SPEC_ANGLES[0] or angle == self.SPEC_ANGLES[2]:
            tan_end.x = 0 if from_left else self.canvas.get_width()
            tan_end.y = point_on_circle.y

        tan_line = pg.draw.line(
            self.canvas,
            Color.PINK,
            point_on_circle,
            tan_end, width=2
        )

        # =======================
        # CSC(θ) LINE
        # =======================
        # Correct the angle
        direction = math.copysign(1, -unit.y)
        new_angle = math.tau if angle == 0 else angle
        csc2_len = cos_line.width * 1 / math.tan(new_angle)

        # Add the 1st portion of the line to the other
        csc_len = canvas_center.y + sine_line.height * direction

        # Correct the direction
        if angle <= self.SPEC_ANGLES[0] or angle > self.SPEC_ANGLES[2]:
            csc_len -= csc2_len
        else:
            csc_len += csc2_len

        if angle == 0 or angle == self.SPEC_ANGLES[1] or angle == self.SPEC_ANGLES[3]:
            csc_len = 0 if from_up else self.canvas.get_height()

        csc_line = pg.draw.line(
            self.canvas,
            Color.RED,
            canvas_center,
            (canvas_center.x, csc_len),
            width=2
        )

        # =======================
        # COT(θ) LINE
        # =======================
        cot_end = pg.Vector2(canvas_center.x, csc_len)

        if angle == 0 or angle == self.SPEC_ANGLES[1] or angle == self.SPEC_ANGLES[3]:
            cot_end.y = 0 if from_up else self.canvas.get_height()
            cot_end.x = point_on_circle.x

        cot_line = pg.draw.line(
            self.canvas,
            Color.GREEN,
            point_on_circle,
            cot_end, width=2
        )

        # =======================
        # UPDATE VALUES
        # =======================
        lbl_angle_text = round(angle, 2) if self.rad_mode else round(math.degrees(angle), 2)
        lbl_unit_text = 'rad' if self.rad_mode else '°'
        lbl_sin_text = round(math.sin(angle), 2)
        lbl_cos_text = round(math.cos(angle), 2)

        lbl_tan_text = 0
        lbl_sec_text = 0
        lbl_csc_text = 0
        lbl_cot_text = 0

        if angle == 0 or angle == self.SPEC_ANGLES[0] or angle == self.SPEC_ANGLES[2]:
            lbl_tan_text = 'undefined'
            lbl_sec_text = 'undefined'
        elif angle == 0 or angle == self.SPEC_ANGLES[1] or angle == self.SPEC_ANGLES[3]:
            lbl_csc_text = 'undefined'
            lbl_cot_text = 'undefined'
        else:
            lbl_tan_text = round(math.tan(angle), 2)
            lbl_csc_text = round(1 / math.sin(angle), 2)
            lbl_sec_text = round(1 / math.cos(angle), 2)
            lbl_cot_text = round(1 / math.tan(angle), 2)

        lbl_snap = self.fonts['label'].render(f'Snap(S): {"ON" if self.enable_snap else "OFF"}', True,
                                     Color.BLACK if self.enable_snap else Color.GRAY)
        lbl_rad = self.fonts['label'].render(f'Radians(R): {"ON" if self.rad_mode else "OFF"}', True,
                                    Color.BLACK if self.rad_mode else Color.GRAY)

        lbl_sep = self.fonts['label'].render('-' * 20, False, Color.BLACK)

        lbl_unit = self.fonts['label'].render(f'Unit: {unit}', True, Color.BLACK)
        lbl_angle = self.fonts['label'].render(f'Angle {lbl_angle_text} {lbl_unit_text}', True, Color.BLACK)

        lbl_sin = self.fonts['label'].render(f'Sin(θ) = {lbl_sin_text}', True, Color.ORANGE)
        lbl_cos = self.fonts['label'].render(f'Cos(θ) = {lbl_cos_text}', True, Color.ORANGE)
        lbl_tan = self.fonts['label'].render(f'Tan(θ) = {lbl_tan_text}', True, Color.PINK)

        lbl_csc = self.fonts['label'].render(f'Csc(θ) = {lbl_csc_text}', True, Color.RED)
        lbl_sec = self.fonts['label'].render(f'Sec(θ) = {lbl_sec_text}', True, Color.BLUE)
        lbl_cot = self.fonts['label'].render(f'Cot(θ) = {lbl_cot_text}', True, Color.GREEN)

        lbl_angl = self.fonts['values'].render(f'θ = {lbl_angle_text} {lbl_unit_text}', True, Color.BLACK)
        lbl_cos_l = self.fonts['values'].render(f'x = {round(unit.x, 2)}', True, Color.ORANGE)
        lbl_sin_l = self.fonts['values'].render(f'y = {round(unit.y, 2)}', True, Color.ORANGE)

        # Unit coordinates
        lbl_right = self.fonts['values'].render('(1, 0)', True, Color.ORANGE)
        lbl_left = self.fonts['values'].render('(-1, 0)', True, Color.ORANGE)
        lbl_top = self.fonts['values'].render('(0, 1)', True, Color.ORANGE)
        lbl_bottom = self.fonts['values'].render('(0, -1)', True, Color.ORANGE)

        # Quadrants
        lbl_first_quad = self.fonts['quadrants'].render('I', True, Color.RED)
        lbl_second_quad = self.fonts['quadrants'].render('II', True, Color.RED)
        lbl_third_quad = self.fonts['quadrants'].render('III', True, Color.RED)
        lbl_fourth_quad = self.fonts['quadrants'].render('IV', True, Color.RED)

        lbl_ver = self.fonts['label'].render(f'v {self.VERSION}', True, Color.BLACK)
        lbl_auth = self.fonts['label'].render(f'by {self.AUTHOR}', True, Color.BLACK)

        # =======================
        # RENDER GUI
        # =======================
        self.canvas.blit(lbl_snap, (20, 20))
        self.canvas.blit(lbl_rad, (20, 40))

        self.canvas.blit(lbl_sep, (20, 60))

        self.canvas.blit(lbl_unit, (20, 80))
        self.canvas.blit(lbl_angle, (20, 100))
        self.canvas.blit(lbl_sin, (20, 120))
        self.canvas.blit(lbl_cos, (20, 140))
        self.canvas.blit(lbl_tan, (20, 160))
        self.canvas.blit(lbl_csc, (20, 180))
        self.canvas.blit(lbl_sec, (20, 200))
        self.canvas.blit(lbl_cot, (20, 220))

        self.canvas.blit(lbl_angl, (canvas_center.x + 25, canvas_center.y - 20))
        self.canvas.blit(lbl_cos_l, (
            point_on_circle.x - lbl_cos_l.get_width() / 2,
            canvas_center.y + 20
        ))
        self.canvas.blit(lbl_sin_l, (
            canvas_center.x - lbl_sin_l.get_width() / 2,
            point_on_circle.y + 20
        ))
        self.canvas.blit(lbl_right, (
            canvas_center.x + self.unit_circ_rad + 40,
            canvas_center.y - lbl_right.get_height() / 2
        ))
        self.canvas.blit(lbl_left, (
            canvas_center.x - lbl_left.get_width() - self.unit_circ_rad - 40,
            canvas_center.y - lbl_left.get_height() / 2
        ))
        self.canvas.blit(lbl_top, (
            canvas_center.x - lbl_top.get_width() / 2,
            canvas_center.y - lbl_top.get_height() - self.unit_circ_rad - 40
        ))
        self.canvas.blit(lbl_bottom, (
            canvas_center.x - lbl_bottom.get_width() / 2,
            canvas_center.y + self.unit_circ_rad + 40
        ))
        self.canvas.blit(lbl_first_quad, (
            canvas_center.x + self.unit_circ_rad / 2 - lbl_first_quad.get_width() / 2,
            canvas_center.y - self.unit_circ_rad / 2 - lbl_first_quad.get_height() / 2
        ))
        self.canvas.blit(lbl_second_quad, (
            canvas_center.x - self.unit_circ_rad / 2 - lbl_second_quad.get_width() / 2,
            canvas_center.y - self.unit_circ_rad / 2 - lbl_second_quad.get_height() / 2
        ))
        self.canvas.blit(lbl_third_quad, (
            canvas_center.x - self.unit_circ_rad / 2 - lbl_third_quad.get_width() / 2,
            canvas_center.y + self.unit_circ_rad / 2 - lbl_third_quad.get_height() / 2
        ))
        self.canvas.blit(lbl_fourth_quad, (
            canvas_center.x + self.unit_circ_rad / 2 - lbl_fourth_quad.get_width() / 2,
            canvas_center.y + self.unit_circ_rad / 2 - lbl_fourth_quad.get_height() / 2
        ))
        self.canvas.blit(lbl_ver, (20, self.canvas.get_height() - 40))
        self.canvas.blit(lbl_auth, (self.canvas.get_width() - lbl_auth.get_width() - 20,
                               self.canvas.get_height() - lbl_auth.get_height() - 20))

        pg.display.flip()

    def __load_fonts(self):
        self.fonts['label'] = pg.font.SysFont(self.FONT_NAME, self.FONT_SIZES[0])
        self.fonts['values'] = pg.font.SysFont(self.FONT_NAME, self.FONT_SIZES[1])
        self.fonts['quadrants'] = pg.font.SysFont(self.FONT_NAME, self.FONT_SIZES[2])

    @staticmethod
    def toggle(value: bool):
        return False if value else True

    @staticmethod
    def calc_angle(vect):
        angle = math.atan2(vect.y, vect.x)
        # The value becomes negative as the angle moves past
        # ~179 degrees. Correct it by adding a full revolution
        if angle < 0:
            angle += math.tau

        return angle


if __name__ == '__main__':
    simulator = UnitCircle()
    simulator.start()
