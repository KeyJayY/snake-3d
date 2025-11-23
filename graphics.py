import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from config import *


def draw_cube_common(color, scale=0.85, emission_level=0.0, texture_id=None):
    """Draws a textured or colored cube with optional emission material settings."""
    glPushMatrix()
    glScalef(scale, scale, scale)

    if emission_level > 0:
        emission = [c * emission_level for c in color] + [1.0]
        glMaterialfv(GL_FRONT, GL_EMISSION, emission)
    else:
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])

    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 0.0)

    if texture_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor3f(1.0, 1.0, 1.0)
    else:
        glDisable(GL_TEXTURE_2D)
        glColor3fv(color)

    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(1.0, 1.0)

    glBegin(GL_QUADS)
    for i, face in enumerate(FACES_QUADS):
        glNormal3fv(NORMALS[i])

        glTexCoord2f(0.0, 0.0)
        glVertex3fv(VERTICES[face[0]])
        glTexCoord2f(1.0, 0.0)
        glVertex3fv(VERTICES[face[1]])
        glTexCoord2f(1.0, 1.0)
        glVertex3fv(VERTICES[face[2]])
        glTexCoord2f(0.0, 1.0)
        glVertex3fv(VERTICES[face[3]])
    glEnd()

    glDisable(GL_POLYGON_OFFSET_FILL)
    glDisable(GL_TEXTURE_2D)

    glDisable(GL_LIGHTING)
    glColor3f(0.0, 0.0, 0.0)
    glLineWidth(1.5)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glBegin(GL_QUADS)
    for face in FACES_QUADS:
        for vertex in face:
            glVertex3fv(VERTICES[vertex])
    glEnd()
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glEnable(GL_LIGHTING)

    glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
    glPopMatrix()


def draw_pulsating_apple(scale, texture_id, shader_program, time):
    """Draws the apple object using a custom vertex shader for animation."""
    glUseProgram(shader_program)

    time_loc = glGetUniformLocation(shader_program, "time")
    tex_loc = glGetUniformLocation(shader_program, "texture1")
    glUniform1f(time_loc, time)
    glUniform1i(tex_loc, 0)

    glEnable(GL_TEXTURE_2D)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glPushMatrix()
    glScalef(scale, scale, scale)

    glBegin(GL_QUADS)
    for i, face in enumerate(FACES_QUADS):
        glNormal3fv(NORMALS[i])
        glTexCoord2f(0.0, 0.0)
        glVertex3fv(VERTICES[face[0]])
        glTexCoord2f(1.0, 0.0)
        glVertex3fv(VERTICES[face[1]])
        glTexCoord2f(1.0, 1.0)
        glVertex3fv(VERTICES[face[2]])
        glTexCoord2f(0.0, 1.0)
        glVertex3fv(VERTICES[face[3]])
    glEnd()

    glPopMatrix()

    glUseProgram(0)
    glDisable(GL_TEXTURE_2D)


def draw_planar_floor(grid_x, grid_y, texture_id):
    """Renders the tiled floor for the planar game mode."""
    if texture_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor3f(1.0, 1.0, 1.0)
    else:
        glDisable(GL_TEXTURE_2D)
        glColor3f(0.2, 0.2, 0.2)

    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 0.0)

    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(2.0, 2.0)

    z = -0.55

    glBegin(GL_QUADS)
    glNormal3f(0, 0, 1)

    for x in range(grid_x[0], grid_x[1] + 1):
        for y in range(grid_y[0], grid_y[1] + 1):
            x0, y0 = x - 0.5, y - 0.5
            x1, y1 = x + 0.5, y + 0.5

            u0, v0 = x / 2.0, y / 2.0
            u1, v1 = (x + 1) / 2.0, (y + 1) / 2.0

            glTexCoord2f(u0, v0)
            glVertex3f(x0, y0, z)
            glTexCoord2f(u1, v0)
            glVertex3f(x1, y0, z)
            glTexCoord2f(u1, v1)
            glVertex3f(x1, y1, z)
            glTexCoord2f(u0, v1)
            glVertex3f(x0, y1, z)

    glEnd()

    glDisable(GL_POLYGON_OFFSET_FILL)
    glDisable(GL_TEXTURE_2D)


def draw_cube_face_background(texture_id, n):
    """Renders the background face for a side of the cube in cube mode."""
    if texture_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor3f(1.0, 1.0, 1.0)
    else:
        glDisable(GL_TEXTURE_2D)
        glColor3f(0.1, 0.1, 0.1)

    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 0.0)

    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(2.0, 2.0)

    step = 2.0 / n

    glBegin(GL_QUADS)
    glNormal3f(0, 0, 1)

    for i in range(n):
        for j in range(n):
            x0 = -1.0 + i * step
            y0 = -1.0 + j * step
            x1 = x0 + step
            y1 = y0 + step

            u0, v0 = i / float(n), j / float(n)
            u1, v1 = (i + 1) / float(n), (j + 1) / float(n)

            glTexCoord2f(u0, v0)
            glVertex3f(x0, y0, 0.0)
            glTexCoord2f(u1, v0)
            glVertex3f(x1, y0, 0.0)
            glTexCoord2f(u1, v1)
            glVertex3f(x1, y1, 0.0)
            glTexCoord2f(u0, v1)
            glVertex3f(x0, y1, 0.0)

    glEnd()

    glDisable(GL_POLYGON_OFFSET_FILL)
    glDisable(GL_TEXTURE_2D)


def setup_lights(pos):
    """Configures global ambient lighting and disables the default directional light."""
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)

    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.15, 0.15, 0.15, 1))

    glLightfv(GL_LIGHT0, GL_POSITION, pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.0, 0.0, 0.0, 1))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.0, 0.0, 0.0, 1))


def setup_point_light(index, pos, color):
    """Configures a specific point light source with color and attenuation."""
    light_id = GL_LIGHT1 + index
    if light_id > GL_LIGHT7:
        return
    glEnable(light_id)
    glLightfv(light_id, GL_POSITION, pos)

    glLightfv(light_id, GL_DIFFUSE, color)
    glLightfv(light_id, GL_SPECULAR, (0.0, 0.0, 0.0, 1))

    glLightfv(light_id, GL_CONSTANT_ATTENUATION, 0.5)
    glLightfv(light_id, GL_LINEAR_ATTENUATION, 0.2)
    glLightfv(light_id, GL_QUADRATIC_ATTENUATION, 0.05)


def draw_text_gl(x, y, text, font, color=(255, 255, 255)):
    """Renders text onto a 2D plane in the 3D world using orthographic projection."""
    text_surface = font.render(text, True, color).convert_alpha()
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    w, h = text_surface.get_width(), text_surface.get_height()

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, DISPLAY_SIZE[0], 0, DISPLAY_SIZE[1])
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data
    )

    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(x, y)
    glTexCoord2f(1, 0)
    glVertex2f(x + w, y)
    glTexCoord2f(1, 1)
    glVertex2f(x + w, y + h)
    glTexCoord2f(0, 1)
    glVertex2f(x, y + h)
    glEnd()

    glDeleteTextures([tex_id])
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
