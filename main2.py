import pygame
import os
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from config import *
from graphics import draw_text_gl, draw_cube_common
from logic_2d import PlanarGame
from logic_cube import CubeGame
from utils import load_shader_program


def load_texture_from_file(filename):
    """
    Loads an image file as an OpenGL texture.

    Args:
        filename (str): The path to the image file.

    Returns:
        int: The OpenGL texture ID.
    """
    if not os.path.exists(filename):
        print(f"Warning: Texture {filename} not found. Using procedural fallback.")
        return create_checkerboard_texture()

    try:
        texture_surface = pygame.image.load(filename)
        texture_data = pygame.image.tostring(texture_surface, "RGBA", 1)
        width = texture_surface.get_width()
        height = texture_surface.get_height()

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            width,
            height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            texture_data,
        )
        return tex_id
    except Exception as e:
        print(f"Error loading texture {filename}: {e}")
        return create_checkerboard_texture()


def create_checkerboard_texture():
    """
    Creates a fallback procedural checkerboard texture.

    Returns:
        int: The OpenGL texture ID.
    """
    width, height = 64, 64
    checker_data = []
    for y in range(height):
        for x in range(width):
            if (x // 8 + y // 8) % 2 == 0:
                checker_data.extend([255, 255, 255, 255])
            else:
                checker_data.extend([150, 150, 150, 255])

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        width,
        height,
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        bytes(checker_data),
    )
    return tex_id


def main():
    """Main entry point of the application. Initializes Pygame, OpenGL, and runs the game loop."""
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
    pygame.display.set_mode(DISPLAY_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Ultimate OpenGL Snake")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)

    snake_tex_id = load_texture_from_file("textures/snake.jpg")
    floor_tex_id = load_texture_from_file("textures/floor.jpg")
    apple_tex_id = load_texture_from_file("textures/apple.jpg")

    try:
        shader_program = load_shader_program("pulse.vert", "pulse.frag")
        print("Shader loaded successfully.")
    except Exception as e:
        print(f"Shader compilation failed: {e}")
        shader_program = None

    font_large = pygame.font.SysFont("Arial", 50, bold=True)
    font_small = pygame.font.SysFont("Arial", 25)

    game_planar = PlanarGame()
    game_cube = CubeGame()

    state = "MENU"
    last_game_mode = None
    final_score = 0

    clock = pygame.time.Clock()
    move_timer = 0
    running = True

    while running:
        dt = clock.tick(60)
        move_timer += dt

        current_time = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == KEYDOWN:
                if state == "MENU":
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_1:
                        state = "PLANAR"
                        game_planar.reset()
                    if event.key == K_2:
                        state = "CUBE"
                        game_cube.reset()

                elif state in ["PLANAR", "CUBE"]:
                    target = game_planar if state == "PLANAR" else game_cube
                    if event.key == K_ESCAPE:
                        state = "MENU"
                    if event.key == K_LEFT:
                        target.next_turn = "LEFT"
                    if event.key == K_RIGHT:
                        target.next_turn = "RIGHT"

                elif state == "GAME_OVER":
                    if event.key == K_r:
                        state = last_game_mode
                        if state == "PLANAR":
                            game_planar.reset()
                        else:
                            game_cube.reset()
                    elif event.key == K_m or event.key == K_ESCAPE:
                        state = "MENU"

        if state in ["PLANAR", "CUBE"]:
            keys = pygame.key.get_pressed()
            if state == "PLANAR":
                game_planar.handle_camera_input(keys)
            elif state == "CUBE":
                game_cube.handle_camera_input(keys)

        if state in ["PLANAR", "CUBE"]:
            if move_timer >= MOVE_DELAY:
                move_timer = 0
                is_alive = True

                if state == "PLANAR":
                    is_alive = game_planar.update()
                    if not is_alive:
                        final_score = game_planar.score
                        last_game_mode = "PLANAR"
                elif state == "CUBE":
                    is_alive = game_cube.update()
                    if not is_alive:
                        final_score = game_cube.score
                        last_game_mode = "CUBE"

                if not is_alive:
                    state = "GAME_OVER"

        glClearColor(*COLOR_BG)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        if state == "MENU":
            gluPerspective(45, DISPLAY_SIZE[0] / DISPLAY_SIZE[1], 0.1, 100.0)
            glTranslatef(0, 0, -5)
            glRotatef(pygame.time.get_ticks() * 0.05, 1, 1, 0)
            draw_cube_common(
                (0.2, 0.2, 0.3), scale=1.5, emission_level=0.1, texture_id=snake_tex_id
            )

            cx, cy = DISPLAY_SIZE[0] // 2, DISPLAY_SIZE[1] // 2
            draw_text_gl(cx - 150, cy + 50, "SNAKE 3D", font_large, (0, 255, 255))
            draw_text_gl(cx - 120, cy - 20, "Press [1] Planar Mode", font_small)
            draw_text_gl(cx - 120, cy - 60, "Press [2] Cube Mode", font_small)
            draw_text_gl(
                cx - 120, cy - 100, "Press [ESC] to Quit", font_small, (150, 150, 150)
            )

        elif state == "PLANAR":
            game_planar.render(
                snake_tex_id=snake_tex_id,
                floor_tex_id=floor_tex_id,
                apple_tex_id=apple_tex_id,
                shader_program=shader_program,
                time=current_time,
            )
            draw_text_gl(
                10, 10, f"Score: {game_planar.score}", font_small, (200, 200, 200)
            )
            draw_text_gl(10, 30, "WASD to Rotate Camera", font_small, (150, 150, 150))

        elif state == "CUBE":
            game_cube.render(
                snake_tex_id=snake_tex_id,
                floor_tex_id=floor_tex_id,
                apple_tex_id=apple_tex_id,
                shader_program=shader_program,
                time=current_time,
            )
            draw_text_gl(
                10, 10, f"Score: {game_cube.score}", font_small, (200, 200, 200)
            )
            draw_text_gl(10, 30, "WASD to Rotate Camera", font_small, (150, 150, 150))

        elif state == "GAME_OVER":
            gluPerspective(45, DISPLAY_SIZE[0] / DISPLAY_SIZE[1], 0.1, 100.0)
            glTranslatef(0, 0, -5)
            glRotatef(pygame.time.get_ticks() * 0.02, 0, 1, 0)
            draw_cube_common(
                (0.5, 0.0, 0.0), scale=1.5, emission_level=0.2, texture_id=snake_tex_id
            )

            cx, cy = DISPLAY_SIZE[0] // 2, DISPLAY_SIZE[1] // 2
            draw_text_gl(cx - 160, cy + 60, "GAME OVER", font_large, (255, 50, 50))
            draw_text_gl(
                cx - 60, cy + 10, f"Score: {final_score}", font_small, (255, 255, 255)
            )
            draw_text_gl(cx - 100, cy - 50, "[R] Try Again", font_small, (0, 255, 0))
            draw_text_gl(
                cx - 100, cy - 90, "[M] Main Menu", font_small, (200, 200, 200)
            )

        pygame.display.flip()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()
