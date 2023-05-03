import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy
from constants import *

pygame.init()
screen = pygame.display.set_mode(WINDOWSIZE, DOUBLEBUF | OPENGL)
pygame.font.init()
font = pygame.font.SysFont('dejavusansmono', 12)


def rad_2_deg(angle_rad): return angle_rad / math.pi * 180


def deg_2_rad(angle_deg): return angle_deg / 180 * math.pi


def draw_text_2D(x, y, text, color=(255, 255, 255, 255), bg_color = None):
    text_surface = font.render(text, True, color, bg_color).convert_alpha()
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)


def draw_text_3D(text, center=None, offset_2D=(0, 0), offset_3D=(0, 0, 0), color=(255, 255, 255, 255), bg_color = None):
    pos = gluProject(offset_3D[0], offset_3D[1], offset_3D[2])
    if bg_color is None:
        text_surface = font.render(text, True, color).convert_alpha()
    else:
        text_surface = font.render(text, True, color, bg_color).convert_alpha()
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    centerer = 0
    if center: centerer = - text_surface.get_width() / 2
    glWindowPos2d(pos[0] + offset_2D[0] + centerer, pos[1] + offset_2D[1])
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)


class Cube(object):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    Verts = numpy.array([
        (-0.5, 0.5, -0.5),  # left top rear
        (0.5, 0.5, -0.5),  # right top rear
        (0.5, -0.5, -0.5),  # right bottom rear
        (-0.5, -0.5, -0.5),  # left bottom rear
        (-0.5, 0.5, 0.5),  # left top front
        (0.5, 0.5, 0.5),  # right top front
        (0.5, -0.5, 0.5),  # right bottom front
        (-0.5, -0.5, 0.5),  # left bottom front
    ], dtype=numpy.float32)

    Faces = numpy.array([
        7, 6, 5, 4,  # front
        6, 2, 1, 5,  # right
        3, 7, 4, 0,  # left
        5, 1, 0, 4,  # top
        3, 2, 6, 7,  # bottom
        2, 3, 0, 1,  # rear
    ], dtype=numpy.int16)

    def __init__(self):
        self.vert = glGenBuffers(1)
        self.idx = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vert)
        glBufferData(GL_ARRAY_BUFFER, self.Verts, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.idx)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.Faces, GL_STATIC_DRAW)

    def draw_stretched(self, pos, scale):
        glPushMatrix()
        glTranslatef(*pos)
        glScalef(*scale)
        self.draw()
        glPopMatrix()

    def draw(self):
        # glDisable(GL_POLYGON_OFFSET_FILL);
        glEnableClientState(GL_VERTEX_ARRAY)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBindBuffer(GL_ARRAY_BUFFER, self.vert)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.idx)
        glDrawElements(GL_QUADS, len(self.Faces), GL_UNSIGNED_SHORT, None)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)


cube = Cube()


class ArcXZ:
    """creates and draws an arc on the XZ-Plane"""

    def __init__(self, start_angle_deg, end_angle_deg, step_angle_deg, radius):
        i = start_angle_deg
        vertices = [[(0, 0, 0)]]
        while i < end_angle_deg:
            vertices.append([(math.sin(deg_2_rad(i)) * radius, 0, math.cos(deg_2_rad(i)) * radius)])
            i = i + step_angle_deg
        vertices.append(([(math.sin(deg_2_rad(end_angle_deg)) * radius, 0, math.cos(deg_2_rad(end_angle_deg)) * radius)]))
        vertices.append([(0, 0, 0)])
        self.verts = numpy.array(vertices, dtype='float32')
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.verts, GL_STATIC_DRAW)

    def draw(self):
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glDrawArrays(GL_LINE_STRIP, 0, len(self.verts))
