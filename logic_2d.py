import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from config import *
from utils import clamp
from graphics import (
    draw_cube_common,
    setup_lights,
    setup_point_light,
    draw_planar_floor,
    draw_pulsating_apple,
)


class PlanarGame:
    def __init__(self):
        """Initializes the planar game mode state."""
        self.GRID_X = (-10, 10)
        self.GRID_Y = (-8, 8)
        self.reset()

    def reset(self):
        """Resets the snake, food, and camera to default starting values."""
        self.snake = [(0, 0), (-1, 0), (-2, 0)]
        self.direction = (1, 0)
        self.next_turn = None
        self.food = self.get_safe_food()
        self.cam_pitch = 0
        self.cam_yaw = 0
        self.cam_zoom = -30
        self.score = 0

    def get_safe_food(self):
        """Finds a random grid position for food that is not occupied by the snake."""
        while True:
            x = random.randint(self.GRID_X[0], self.GRID_X[1])
            y = random.randint(self.GRID_Y[0], self.GRID_Y[1])
            if (x, y) not in self.snake:
                return (x, y)

    def handle_camera_input(self, keys):
        """Updates camera rotation angles based on keyboard input."""
        if keys[K_w]:
            self.cam_pitch = clamp(self.cam_pitch + 1.5, -90, 90)
        if keys[K_s]:
            self.cam_pitch = clamp(self.cam_pitch - 1.5, -90, 90)
        if keys[K_a]:
            self.cam_yaw = clamp(self.cam_yaw - 1.5, -90, 90)
        if keys[K_d]:
            self.cam_yaw = clamp(self.cam_yaw + 1.5, -90, 90)

    def update(self):
        """Updates game logic for one tick: moves snake, checks collisions."""
        if self.next_turn == "LEFT":
            self.direction = (-self.direction[1], self.direction[0])
        elif self.next_turn == "RIGHT":
            self.direction = (self.direction[1], -self.direction[0])
        self.next_turn = None

        nx = self.snake[0][0] + self.direction[0]
        ny = self.snake[0][1] + self.direction[1]
        new_head = (nx, ny)

        if (
            nx < self.GRID_X[0]
            or nx > self.GRID_X[1]
            or ny < self.GRID_Y[0]
            or ny > self.GRID_Y[1]
            or new_head in self.snake
        ):
            return False

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.food = self.get_safe_food()
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
        """Renders the entire planar game scene including lights, floor, and objects."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, DISPLAY_SIZE[0] / DISPLAY_SIZE[1], 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, self.cam_zoom)
        glRotatef(self.cam_pitch, 1, 0, 0)
        glRotatef(self.cam_yaw, 0, 1, 0)

        setup_lights((0, 0, 20, 1))

        setup_point_light(
            0, (self.snake[0][0], self.snake[0][1], 2.0, 1.0), (0.1, 0.6, 0.1, 1.0)
        )
        setup_point_light(
            1, (self.food[0], self.food[1], 2.0, 1.0), (0.6, 0.1, 0.1, 1.0)
        )

        draw_planar_floor(self.GRID_X, self.GRID_Y, floor_tex_id)

        glDisable(GL_LIGHTING)
        glColor3fv(COLOR_GRID)
        glLineWidth(1.0)
        glBegin(GL_LINES)
        z = -0.54
        for x in range(self.GRID_X[0] - 1, self.GRID_X[1] + 2):
            glVertex3f(x - 0.5, self.GRID_Y[0] - 0.5, z)
            glVertex3f(x - 0.5, self.GRID_Y[1] + 0.5, z)
        for y in range(self.GRID_Y[0] - 1, self.GRID_Y[1] + 2):
            glVertex3f(self.GRID_X[0] - 0.5, y - 0.5, z)
            glVertex3f(self.GRID_X[1] + 0.5, y - 0.5, z)
        glEnd()

        glLineWidth(3.0)
        glColor3fv(COLOR_BORDER)
        glBegin(GL_LINE_LOOP)
        glVertex3f(self.GRID_X[0] - 0.5, self.GRID_Y[0] - 0.5, 0)
        glVertex3f(self.GRID_X[1] + 0.5, self.GRID_Y[0] - 0.5, 0)
        glVertex3f(self.GRID_X[1] + 0.5, self.GRID_Y[1] + 0.5, 0)
        glVertex3f(self.GRID_X[0] - 0.5, self.GRID_Y[1] + 0.5, 0)
        glEnd()
        glEnable(GL_LIGHTING)

        glPushMatrix()
        glTranslatef(self.food[0], self.food[1], 0)
        if shader_program and apple_tex_id:
            draw_pulsating_apple(
                0.6 * CELL_SCALE_FACTOR, apple_tex_id, shader_program, time
            )
        else:
            draw_cube_common(COLOR_FOOD, 0.6 * CELL_SCALE_FACTOR, 0.5, apple_tex_id)
        glPopMatrix()

        for i, (sx, sy) in enumerate(self.snake):
            glPushMatrix()
            glTranslatef(sx, sy, 0)
            if i == 0:
                draw_cube_common(COLOR_HEAD, 0.9 * CELL_SCALE_FACTOR, 0.5, snake_tex_id)
            else:
                draw_cube_common(
                    COLOR_BODY, 0.85 * CELL_SCALE_FACTOR, 0.2, snake_tex_id
                )
            glPopMatrix()
