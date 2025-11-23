import random
import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from config import *
from utils import rot_x, rot_y, mat_mul
from graphics import (
    draw_cube_common,
    setup_lights,
    setup_point_light,
    draw_cube_face_background,
    draw_pulsating_apple,
)


class CubeGame:
    def __init__(self):
        """Initializes the cube game mode state."""
        self.N = 8
        self.CELL_SPAN = 2.0 / self.N
        self.SCALE = self.CELL_SPAN * 0.85
        self.reset()

    def reset(self):
        """Resets the snake, food, and camera to default starting values."""
        c = self.N // 2
        self.snake = [(0, c, c), (0, c - 1, c), (0, c - 2, c)]
        self.dir_idx = 1
        self.next_turn = None
        self.food = self.get_food()
        self.cam_pitch = 25.0
        self.cam_yaw = 30.0
        self.cam_zoom = -5.5
        self.score = 0

    def get_food(self):
        """Finds a random face and grid position for food, avoiding the snake."""
        while True:
            pos = (
                random.randint(0, 5),
                random.randint(0, self.N - 1),
                random.randint(0, self.N - 1),
            )
            if pos not in self.snake:
                return pos

    def handle_camera_input(self, keys):
        """Updates camera rotation and zoom based on keyboard input."""
        if keys[K_w]:
            self.cam_pitch += 1.5
        if keys[K_s]:
            self.cam_pitch -= 1.5
        if keys[K_a]:
            self.cam_yaw -= 1.5
        if keys[K_d]:
            self.cam_yaw += 1.5
        if keys[K_q]:
            self.cam_zoom += 0.2
        if keys[K_e]:
            self.cam_zoom -= 0.2

    def local_to_world(self, f, x, y):
        """Converts face index and grid coordinates to 3D world coordinates."""
        u = -1 + (x + 0.5) * self.CELL_SPAN
        v = 1 - (y + 0.5) * self.CELL_SPAN
        rots = {
            0: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            1: rot_y(90),
            2: rot_y(180),
            3: rot_y(-90),
            4: rot_x(-90),
            5: rot_x(90),
        }
        return mat_mul(rots[f], (u, v, 1.0))

    def get_face_normal(self, f):
        """Returns the normal vector for a given face index."""
        if f == 0:
            return (0, 0, 1)
        if f == 1:
            return (1, 0, 0)
        if f == 2:
            return (0, 0, -1)
        if f == 3:
            return (-1, 0, 0)
        if f == 4:
            return (0, 1, 0)
        if f == 5:
            return (0, -1, 0)
        return (0, 1, 0)

    def update(self):
        """Updates game logic for one tick: moves snake across faces, checks collisions."""
        if self.next_turn == "LEFT":
            self.dir_idx = (self.dir_idx - 1) % 4
        elif self.next_turn == "RIGHT":
            self.dir_idx = (self.dir_idx + 1) % 4
        self.next_turn = None

        f, x, y = self.snake[0]
        dx, dy = 0, 0
        if self.dir_idx == 0:
            dy = -1
        elif self.dir_idx == 1:
            dx = 1
        elif self.dir_idx == 2:
            dy = 1
        elif self.dir_idx == 3:
            dx = -1

        nx, ny = x + dx, y + dy
        nf, nd = f, self.dir_idx

        if not (0 <= nx < self.N and 0 <= ny < self.N):
            nf, nd, inv = CUBE_TRANSITIONS[f][self.dir_idx]
            p = x if self.dir_idx in (0, 2) else y
            if inv:
                p = self.N - 1 - p
            if nd == 0:
                nx, ny = p, self.N - 1
            elif nd == 1:
                nx, ny = 0, p
            elif nd == 2:
                nx, ny = p, 0
            else:
                nx, ny = self.N - 1, p

        new_head = (nf, nx, ny)
        if new_head in self.snake:
            return False

        self.snake.insert(0, new_head)
        self.dir_idx = nd
        if new_head == self.food:
            self.score += 1
            self.food = self.get_food()
        else:
            self.snake.pop()

        return True

    def render(
        self,
        snake_tex_id=None,
        floor_tex_id=None,
        apple_tex_id=None,
        shader_program=None,
        time=0,
    ):
        """Renders the entire cube game scene including lights, cube faces, and objects."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, DISPLAY_SIZE[0] / DISPLAY_SIZE[1], 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, self.cam_zoom)
        glRotatef(self.cam_pitch, 1, 0, 0)
        glRotatef(self.cam_yaw, 0, 1, 0)

        head_face = self.snake[0][0]
        food_face = self.food[0]

        hw = self.local_to_world(*self.snake[0])
        fw = self.local_to_world(*self.food)

        hn = self.get_face_normal(head_face)
        fn = self.get_face_normal(food_face)

        offset_dist = 0.5
        l_hw = (
            hw[0] + hn[0] * offset_dist,
            hw[1] + hn[1] * offset_dist,
            hw[2] + hn[2] * offset_dist,
            1.0,
        )
        l_fw = (
            fw[0] + fn[0] * offset_dist,
            fw[1] + fn[1] * offset_dist,
            fw[2] + fn[2] * offset_dist,
            1.0,
        )

        setup_lights((0, 0, 30, 1))

        setup_point_light(0, l_hw, (0.1, 0.6, 0.1, 1.0))
        setup_point_light(1, l_fw, (0.6, 0.1, 0.1, 1.0))

        for f in range(6):
            glPushMatrix()
            if f == 1:
                glRotatef(90, 0, 1, 0)
            elif f == 2:
                glRotatef(180, 0, 1, 0)
            elif f == 3:
                glRotatef(-90, 0, 1, 0)
            elif f == 4:
                glRotatef(-90, 1, 0, 0)
            elif f == 5:
                glRotatef(90, 1, 0, 0)
            glTranslatef(0, 0, 1.0)

            draw_cube_face_background(floor_tex_id, self.N)

            glDisable(GL_LIGHTING)
            glColor3f(0.2, 0.2, 0.2)
            glLineWidth(1.0)
            glBegin(GL_LINES)
            for i in range(self.N + 1):
                p = -1 + i * self.CELL_SPAN
                glVertex3f(p, -1, 0)
                glVertex3f(p, 1, 0)
                glVertex3f(-1, p, 0)
                glVertex3f(1, p, 0)
            glEnd()
            glEnable(GL_LIGHTING)
            glPopMatrix()

        glDisable(GL_LIGHTING)
        glLineWidth(2.0)
        glColor3fv(COLOR_BORDER)
        s = 1.01
        for a, b in [(-s, -s), (s, -s), (s, s), (-s, s)]:
            glBegin(GL_LINES)
            glVertex3f(a, b, s)
            glVertex3f(a, b, -s)
            glEnd()
        for z in [-s, s]:
            glBegin(GL_LINE_LOOP)
            glVertex3f(-s, -s, z)
            glVertex3f(s, -s, z)
            glVertex3f(s, s, z)
            glVertex3f(-s, s, z)
            glEnd()
        glEnable(GL_LIGHTING)

        glPushMatrix()
        glTranslatef(*fw)
        if shader_program and apple_tex_id:
            # Smaller apple in cube mode
            draw_pulsating_apple(self.SCALE * 0.7, apple_tex_id, shader_program, time)
        else:
            draw_cube_common(COLOR_FOOD, self.SCALE * 0.7, 0.5, apple_tex_id)
        glPopMatrix()

        for i, seg in enumerate(self.snake):
            wx, wy, wz = self.local_to_world(*seg)
            glPushMatrix()
            glTranslatef(wx, wy, wz)
            if i == 0:
                draw_cube_common(COLOR_HEAD, self.SCALE * 0.98, 0.5, snake_tex_id)
            else:
                draw_cube_common(COLOR_BODY, self.SCALE * 0.9, 0.2, snake_tex_id)
            glPopMatrix()
