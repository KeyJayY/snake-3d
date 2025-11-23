import math
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


def clamp(value, min_val, max_val):
    """Clamps a value between a minimum and maximum limit."""
    return max(min_val, min(value, max_val))


def rot_x(d):
    """Returns a rotation matrix for the X-axis given degrees d."""
    a = math.radians(d)
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def rot_y(d):
    """Returns a rotation matrix for the Y-axis given degrees d."""
    a = math.radians(d)
    c, s = math.cos(a), math.sin(a)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def mat_mul(m, v):
    """Multiplies a 3x3 matrix by a 3D vector."""
    return (
        m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
        m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
        m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2],
    )


def load_shader_program(vertex_path, fragment_path):
    """Reads shader source files and compiles them into a shader program."""
    with open(vertex_path, "r") as f:
        vertex_src = f.read()
    with open(fragment_path, "r") as f:
        fragment_src = f.read()

    shader = compileProgram(
        compileShader(vertex_src, GL_VERTEX_SHADER),
        compileShader(fragment_src, GL_FRAGMENT_SHADER),
    )
    return shader
