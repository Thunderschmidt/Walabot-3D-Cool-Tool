# import pygame
# from pygame.locals import *
# from OpenGL.GL import *
# from OpenGL.GLU import *
# import math
# import numpy
# from constants import *
import threading
import winsound
import WalabotAPI as WB
import clustering
from heat_map_colors import HeatMapColors
from gfx import *


def play_beep(frequency, duration):
    thread = threading.Thread(target=winsound.Beep, args=[frequency, duration])
    thread.start()


class GridDrawer:
    """Draws the static 3D stuff, like the wireframe grid, the walabot and the arches."""

    def __init__(self, min_dist_cm, max_dist_cm, angle_deg):
        self.angle_rad = deg_2_rad(angle_deg)
        self.min_dist_m = min_dist_cm / 100
        self.max_dist_m = max_dist_cm / 100
        self.width_m = math.sin(self.angle_rad) * self.max_dist_m
        line_count_z = math.trunc(self.max_dist_m) + 1
        line_count_x = math.trunc(self.width_m) + 1
        lines = [[(-self.width_m, 0, self.max_dist_m), (self.width_m, 0, self.max_dist_m)],
                 [(-self.width_m, 0, 0), (-self.width_m, 0, self.max_dist_m)],
                 [(self.width_m, 0, 0), (self.width_m, 0, self.max_dist_m)]]

        for i in range(0, line_count_z):
            lines.append([(-self.width_m, 0, i), (self.width_m, 0, i)])

        for i in range(0, line_count_x):
            lines.append([(i, 0, 0), (i, 0, self.max_dist_m)])
            lines.append([(-i, 0, 0), (-i, 0, self.max_dist_m)])

        vertices = []
        for line in lines:
            vertices.append([line[0][0], line[0][1], line[0][2], line[1][0], line[1][1], line[1][2]])
        verts = numpy.array(vertices, dtype='float32')
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, verts, GL_STATIC_DRAW)
        self.number_of_lines = len(verts) * 2
        self.min_arc = ArcXZ(-angle_deg, angle_deg, 1, self.min_dist_m)
        self.max_arc = ArcXZ(-angle_deg, angle_deg, 1, self.max_dist_m)

    def draw_numbers(self):
        i = 1
        while i <= self.width_m:
            draw_text_3D(f"{-i}", True, (0, -20), (i, 0, 0), GRIDCOLOR)
            draw_text_3D(f"{i}", True, (0, -20), (-i, 0, 0), GRIDCOLOR)
            i += 1
        i = 1
        while i <= self.max_dist_m:
            draw_text_3D(f"{i}", True, (0, -20), (self.width_m, 0, i), GRIDCOLOR)
            i += 1
    @staticmethod
    def draw_walabot():
        cube.draw_stretched((0, 0, -0.01), (0.14, 0.072, 0.02))
        glBegin(GL_LINES)
        glVertex3fv((0, 0, 0))
        glVertex3fv((0, - FLOORDISTANCE, 0))
        glVertex3fv((-0.07, 0.02, 0))
        glVertex3fv((-0.11, 0.02, 0))
        glEnd()
        draw_text_3D("Walabot", True, (0, -12), (0, -0.1, 0))

    def draw(self):
        glTranslatef(0, 0, -self.max_dist_m / 2)
        glColor4ub(*GRIDCOLOR)
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glDrawArrays(GL_LINES, 0, self.number_of_lines)
        glTranslatef(0, FLOORDISTANCE, 0)
        self.min_arc.draw()
        self.max_arc.draw()
        glColor4ub(*WALABOTCOLOR)
        self.draw_walabot()
        self.draw_numbers()


class PointCanvas:
    """
    Calculates positions and draws all those colorful little points,
    using the point cloud data from the Walabot.
    """

    def __init__(self):
        self.raw_image = None
        self.raw_image = None
        self.verts = None
        self.z_count = None
        self.y_count = None
        self.x_count = None
        self.colors = None
        self.coordinates = None
        self.vbo = glGenBuffers(1)
        self.cbo = glGenBuffers(1)
        self.hotspots_are_set = False
        self.colors_are_set = False
        self.raw_image_has_been_updated = False
        self.clustering_threshold = CLUSTERING_THRESHOLD

    def create(self, x_count, y_count, z_count, range2, phi, theta):
        self.coordinates = numpy.empty((x_count, y_count, z_count), dtype=object)
        self.colors = numpy.empty(x_count * y_count * z_count * 4, dtype='ubyte')
        vertices = []
        self.x_count = x_count
        self.y_count = y_count
        self.z_count = z_count
        for i in range(x_count):
            if x_count == 1:
                angle_x = 0
            else:
                angle_x = phi[0] + (2 * phi[1]) / (x_count - 1) * i
            sin_x = math.sin(deg_2_rad(angle_x))
            cos_x = math.cos(deg_2_rad(angle_x))
            for j in range(y_count):
                if y_count == 1:
                    angle_y = 0
                else:
                    angle_y = theta[0] + (2 * theta[1]) / (y_count - 1) * j
                sin_y = math.sin(deg_2_rad(angle_y))
                cos_y = math.cos(deg_2_rad(angle_y))
                for k in range(z_count):
                    dist = (range2[0] + (range2[1] - range2[0]) / (z_count - 1) * k) / 100
                    y = sin_y * dist
                    if CYLINDRICALPROJECTION:
                        x = sin_x * dist
                        z = cos_x * dist
                    else:
                        x = cos_y * sin_x * dist
                        z = cos_y * cos_x * dist
                    self.coordinates[i, j, k] = (x, y, z)
                    vertices.append([(x, y, z)])

        self.verts = numpy.array(vertices, dtype='float32')
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.verts, GL_STATIC_DRAW)
        self.hotspots_are_set = True

    def add_value_to_threshold(self, adder):
        self.clustering_threshold += adder
        if self.clustering_threshold < 0:
            self.clustering_threshold = 0
        elif self.clustering_threshold > 255:
            self.clustering_threshold = 255

    def extract_hotspots_from_raw_image(self, raw_image):
        self.raw_image = raw_image
        if self.hotspots_are_set is False: return
        hotspots = []
        intensity = numpy.array([0], dtype=numpy.uint8)  # this is necessary, because the intensity sometimes exceeds 255!
        for i in range(self.x_count):
            for j in range(self.y_count):
                for k in range(self.z_count):
                    intensity[0] = self.raw_image[0][j][i][k]
                    if intensity[0] > self.clustering_threshold:
                        hotspot = clustering.Hotspot(self.get_cartesian_point_coordinates((i, j, k)), intensity[0], (i, j, k))
                        hotspots.append(hotspot)
        for i in range(len(hotspots)): hotspots[i].index = i
        self.raw_image_has_been_updated = True
        return hotspots

    def process_raw_image(self, raw_image):
        self.raw_image = raw_image
        if self.hotspots_are_set is False: return
        color_index = 0
        intensity = numpy.array([0], dtype=numpy.uint8)
        for i in range(self.x_count):
            for j in range(self.y_count):
                for k in range(self.z_count):
                    intensity[0] = self.raw_image[0][j][i][k]
                    color = heat_map_colors.get(intensity[0])
                    self.colors[color_index] = color[0]
                    self.colors[color_index + 1] = color[1]
                    self.colors[color_index + 2] = color[2]
                    self.colors[color_index + 3] = color[3]
                    color_index += 4
        self.raw_image_has_been_updated = True

    def upload_colors_to_gpu(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.cbo)
        glBufferData(GL_ARRAY_BUFFER, self.colors, GL_STATIC_DRAW)
        self.colors_are_set = True
        self.raw_image_has_been_updated = False

    def get_cartesian_point_coordinates(self, loc):
        return self.coordinates[loc]

    def draw(self):
        if self.colors_are_set is False: return
        glPointSize(POINTSIZE)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, self.cbo)
        glColorPointer(4, GL_UNSIGNED_BYTE, 0, None)

        glDrawArrays(GL_POINTS, 0, len(self.verts))
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)


class SensorTargets:
    """draws the 'targets' that come out of the Walabot API"""

    def __init__(self):
        self.sensor_targets = []

    def update(self, targets):
        self.sensor_targets = targets

    def draw(self):
        glColor4ub(*SENSORTARGETSCOLOR)
        glClear(GL_DEPTH_BUFFER_BIT)
        glPointSize(HOTSPOT_POINTSIZE)
        for target in self.sensor_targets:
            x = target.yPosCm / 100
            y = target.xPosCm / 100
            z = target.zPosCm / 100
            glBegin(GL_POINTS)
            glVertex3fv((x, y, z))
            glEnd()
            glBegin(GL_LINES)
            glVertex3fv((x, y, z))
            glVertex3fv((x, -FLOORDISTANCE, z))
            glEnd()
            amplitude = str(target.amplitude * 10000)[:5]
            draw_text_3D(f"target ({amplitude:.3})", True, (0, -20), (x, y, z))

def fetch_walabot_data_loop():
    """Thread that continuously fetches data from the Walabot API."""
    global sensor_targets, point_canvas, walabot
    while thread_terminator is False:
        walabot.trigger()
        raw_image = walabot.get_raw_image()
        if walabot.image_energy > walabot.dynamic_image_energy_threshold and cluster_search_is_active:
            hotspots = point_canvas.extract_hotspots_from_raw_image(raw_image)
            cluster_maker.submit_new_hotspots(hotspots)
        else:
            point_canvas.process_raw_image(raw_image)
            cluster_maker.push_empty_cluster()
        clock_walabot_loop.tick()

class Walabot:
    """Class that manages everything that has to do with the walabot API"""

    def __init__(self):
        self.raw_image = None
        self.is_connected = False
        self.status = "unknown"
        self.params_are_set = False
        self.image_energy = 0.0
        self.sensor_targets = []
        self.range = [0, 0, 0]
        self.phi = [0, 0, 0]
        self.theta = [0, 0, 0]
        self.raw_image_size = [0, 0, 0]
        self.observed_area = 0
        self.point_count = 0
        self.dynamic_image_energy_threshold = 0.05
        self.terminator = False
        self.sensor_targets_are_shown = SHOW_SENSOR_TARGETS

    def trigger(self):
        try:
            WB.Trigger()
            if self.sensor_targets_are_shown: self.sensor_targets = WB.GetSensorTargets()
            self.image_energy = WB.GetImageEnergy()

        except WB.WalabotError:
            self.status = "disconnected!"

    def calc_observed_area(self):
        """Calculates the size of the space the Walabot is scanning"""
        self.observed_area = ((self.range[1] * self.range[1] * math.pi * ((self.phi[1] - self.phi[0]) / 360) -
                               (self.range[0] * self.range[0] * math.pi * ((self.phi[1] - self.phi[0]) / 360))) / 10000)

    def get_raw_image(self):
        self.raw_image = WB.GetRawImage()
        y_count, x_count, z_count = self.raw_image[1:4]
        self.point_count = y_count * x_count * z_count
        self.dynamic_image_energy_threshold = self.point_count / 45000 + 0.025
        self.raw_image_size = (y_count, x_count, z_count)
        return self.raw_image

    def connect(self):
        self.status = "trying to connect ..."
        walabot_connect_thread = threading.Thread(target=self.walabot_connect_loop)
        walabot_connect_thread.start()

    def walabot_connect_loop(self):
        """Loop that constantly checks if a Walabot is present. If so, it connects to it"""
        clock_walabot_connect_loop = pygame.time.Clock()
        pygame.time.wait(1000)
        connection_failed = False
        connecting_attempt_number = 0
        while self.is_connected is False or self.terminator == True:
            WB.Init()
            WB.SetSettingsFolder()
            connecting_attempt_number += 1
            #            print(wb.GetInstrumentsList())
            try:
                WB.ConnectAny()
            except WB.WalabotError as err:
                connection_failed = True
                self.status = str(err) + " (" + str(err.code) + ") ... attempting to reconnect (" + str(
                    connecting_attempt_number) + ") ... try changing USB port?"
                WB.Clean()
            if connection_failed is not True:
                self.is_connected = True
                self.status = "\"" + str(WB.GetInstrumentsList()) + "\" connected!"
                play_beep(800, 100)
                return
            connection_failed = False
            clock_walabot_connect_loop.tick(2)

    def set_range(self, min, max, step_size):
        if min < 0 or min >= max or max > 1000 or step_size < 0.1 or step_size > 10.0: return
        WB.SetArenaR(min, max, step_size)
        self.range = (min, max, step_size)
        self.calc_observed_area()

    def set_phi(self, min, max, step_size):
        if min < -90: min = -90
        if max > 90: max = 90
        if step_size < 1: step_size = 1
        if step_size > 10: step_size = 10
        if min >= max: min, max = -0.5, 0.5
        WB.SetArenaPhi(min, max, step_size)
        self.phi = (min, max, step_size)
        self.calc_observed_area()

    def set_theta(self, min, max, step_size):
        if min < -90: min = -90
        if max > 90: max = 90
        if step_size < 1: step_size = 1
        if step_size > 10: step_size = 10
        if min >= max: min, max = -0.5, 0.5
        WB.SetArenaTheta(min, max, step_size)
        self.theta = (min, max, step_size)
        self.calc_observed_area()

    def get_theta_resolution_from_steps(self, steps):
        if steps < 2: steps = 2
        return (self.theta[1] - self.theta[0]) / (steps - 1)

    def get_phi_resolution_from_steps(self, steps):
        if steps < 2: steps = 2
        return (self.phi[1] - self.phi[0]) / (steps - 1)

    def get_range_resolution_from_steps(self, steps):
        if steps < 2: steps = 2
        return (self.range[1] - self.range[0]) / (steps - 1)

    @staticmethod
    def start():
        WB.Start()

    def send_params(self, r, theta, phi, threshold, mti):
        self.range = r
        self.theta = theta
        self.phi = phi
        WB.SetProfile(WB.PROF_SENSOR)
        WB.SetArenaR(*r)
        WB.SetArenaTheta(*theta)
        WB.SetArenaPhi(*phi)
        WB.SetThreshold(threshold)
        WB.SetDynamicImageFilter(mti)

        self.params_are_set = True

    def show_calibration_status(self):
        play_beep(600, 200)
        while WB.GetStatus()[0] == 4:
            pygame.time.wait(10)
        while WB.GetStatus()[0] != 4:
            self.status = "calibrating (" + str(WB.GetStatus()[1]) + "%)"
            WB.Trigger()
        self.status = "Connected!"
        play_beep(1200, 200)

    def calibrate(self):
        if not self.is_connected: return
        if self.status.startswith("calibrating"): return
        walabot_calibration_thread = threading.Thread(target=self.show_calibration_status)
        walabot_calibration_thread.start()
        WB.StartCalibration()


sensor_targets = SensorTargets()
heat_map_colors = HeatMapColors()

pygame.init()
pygame.display.set_caption('Walabot 3D CoolTool')
screen = pygame.display.set_mode(WINDOWSIZE, DOUBLEBUF | OPENGL)

"""initialize OpenGL"""
cam_rotation = STARTROT
cam_translation = STARTPOS
gluPerspective(45, WINDOWSIZE[0] / WINDOWSIZE[1], 0.1, 500.0)
glBlendFunc(GL_ONE, GL_ONE)  # blending method. RGB values get added
glEnable(GL_LINE_SMOOTH)  # enables line anti aliasing
glEnable(GL_POINT_SMOOTH)  # enables point anti aliasing
glEnable(GL_BLEND)  # turns on blend effects, important for (semi) transparency
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # turns on alpha channel
glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
glLineWidth(STANDARDLINEWIDTH)
glEnable(GL_DEPTH_TEST)  # turns on z buffering
glClearColor(*BACKGROUNDCOLOR)  # background color
glMatrixMode(GL_MODELVIEW)
camera_start_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)

clock_GFX = pygame.time.Clock()
clock_walabot_loop = pygame.time.Clock()

grid_drawer = GridDrawer(WALA_MINRANGE_CM, WALA_MAXRANGE_CM, WALA_HORIZONTALANGLE)
point_canvas = PointCanvas()
walabot = Walabot()
cluster_maker = clustering.ClusterMaker()

mouse_is_pressed = False
current_mouse_position = None
last_mouse_position = None
cluster_search_is_active = False

walabot.connect()
thread_terminator = False
walabot_fetch_data_thread = threading.Thread(target=fetch_walabot_data_loop)
running = True

while running:
    """Calc the main loop frame rate."""
    fps = clock_GFX.get_fps()
    if fps == 0: fps = 40
    fmult = 1 / fps # multiplicator that makes camera movements independent from the frame rate

    """Get things going as soon Walabot is connected."""
    if walabot.is_connected and walabot.params_are_set is False:
        walabot.send_params((WALA_MINRANGE_CM, WALA_MAXRANGE_CM, WALA_RANGESTEPSIZE_CM),
                            (-WALA_VERTICALANGLE_DEG, WALA_VERTICALANGLE_DEG, WALA_VERTICALSTEPSIZE_DEG),
                            (-WALA_HORIZONTALANGLE, WALA_HORIZONTALANGLE, WALA_HORIZONTALSTEPSIZE_DEG),
                            WALA_SIGNALTHRESHOLD, WALA_MOVINGTARGETFILTER)

        walabot.start()
        y_count, x_count, z_count = walabot.get_raw_image()[1:4]
        point_canvas.create(x_count, y_count, z_count, (WALA_MINRANGE_CM, WALA_MAXRANGE_CM, WALA_RANGESTEPSIZE_CM),
                            (-WALA_HORIZONTALANGLE, WALA_HORIZONTALANGLE, WALA_HORIZONTALSTEPSIZE_DEG),
                            (-WALA_VERTICALANGLE_DEG, WALA_VERTICALANGLE_DEG, WALA_VERTICALSTEPSIZE_DEG))

        walabot_fetch_data_thread.start()

    """handle input"""
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_is_pressed = True
            last_mouse_position = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_is_pressed = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:
                walabot.sensor_targets_are_shown = 1 - walabot.sensor_targets_are_shown
            if event.key == pygame.K_SPACE:
                walabot.calibrate()
            if event.key == pygame.K_TAB:
                cluster_search_is_active = 1 - cluster_search_is_active
            if event.key == pygame.K_r or event.key == pygame.K_v or event.key == pygame.K_h:
                thread_terminator = True
                walabot_fetch_data_thread.join()
                thread_terminator = False
                WB.Stop()

                if event.key == pygame.K_r:
                    r = WB.GetArenaR()

                    if keys[K_LCTRL] or keys[K_RCTRL]:
                        steps = walabot.raw_image_size[2]
                        adder = math.ceil(steps / 10)
                        if keys[K_LSHIFT] or keys[K_RSHIFT]:
                            walabot.set_range(r[0], r[1], walabot.get_range_resolution_from_steps(steps - adder))
                        else:
                            walabot.set_range(r[0], r[1], walabot.get_range_resolution_from_steps(steps + adder))
                    else:
                        adder = 0
                        new_range = 0
                        if r[1] < 100:
                            adder = 5
                        elif r[1] < 300:
                            adder = 50
                        else:
                            adder = 100
                        if keys[K_LSHIFT] or keys[K_RSHIFT]:
                            new_range = r[1] - adder
                            if new_range <= r[0]: break
                        else:
                            new_range = r[1] + adder
                            if new_range > 1000: new_range = 1000
                        walabot.set_range(r[0], new_range, r[2])
                if event.key == pygame.K_h:
                    h = WB.GetArenaPhi()
                    if keys[K_LCTRL] or keys[K_RCTRL]:
                        if keys[K_LSHIFT] or keys[K_RSHIFT]:
                            walabot.set_phi(h[0], h[1], walabot.get_phi_resolution_from_steps(walabot.raw_image_size[1] - 1))
                        else:
                            walabot.set_phi(h[0], h[1], walabot.get_phi_resolution_from_steps(walabot.raw_image_size[1] + 1))
                    else:
                        if keys[K_LSHIFT] or keys[K_RSHIFT]:
                            walabot.set_phi(h[0] + h[2], h[1] - h[2], h[2])
                        else:
                            walabot.set_phi(h[0] - h[2], h[1] + h[2], h[2])

                if event.key == pygame.K_v:
                    v = WB.GetArenaTheta()
                    if keys[K_LCTRL] or keys[K_RCTRL]:
                        if keys[K_LSHIFT] or keys[K_RSHIFT]:
                            walabot.set_theta(v[0], v[1], walabot.get_theta_resolution_from_steps(walabot.raw_image_size[0] - 1))
                        else:
                            walabot.set_theta(v[0], v[1], walabot.get_theta_resolution_from_steps(walabot.raw_image_size[0] + 1))
                    else:
                        if keys[K_LSHIFT] or keys[K_RSHIFT]:
                            walabot.set_theta(v[0] + v[2], v[1] - v[2], v[2])
                        else:
                            walabot.set_theta(v[0] - v[2], v[1] + v[2], v[2])
                WB.Start()
                grid_drawer = GridDrawer(int(walabot.range[0]), int(walabot.range[1]), walabot.phi[1])
                y_count, x_count, z_count = walabot.get_raw_image()[1:4]
                point_canvas.create(x_count, y_count, z_count, walabot.range, walabot.phi, walabot.theta)
                walabot_fetch_data_thread = threading.Thread(target=fetch_walabot_data_loop)
                walabot_fetch_data_thread.start()

    if keys[K_c]:
        if keys[K_LSHIFT] or keys[K_RSHIFT]:
            point_canvas.add_value_to_threshold(-1)
        else:
            point_canvas.add_value_to_threshold(1)
    if keys[K_ESCAPE]:
        running = False
    """handle keyboard input for camera control"""
    if keys[K_DOWN]:      cam_rotation[0] += CAMROTSPEED * fmult
    if keys[K_UP]:        cam_rotation[0] -= CAMROTSPEED * fmult
    if keys[K_LEFT]:      cam_rotation[1] += CAMROTSPEED * fmult
    if keys[K_RIGHT]:     cam_rotation[1] -= CAMROTSPEED * fmult
    if keys[K_a]:         cam_translation[0] += CAMTRANSSPEED * fmult
    if keys[K_d]:         cam_translation[0] -= CAMTRANSSPEED * fmult
    if keys[K_s]:         cam_translation[1] += CAMTRANSSPEED * fmult
    if keys[K_w]:         cam_translation[1] -= CAMTRANSSPEED * fmult
    if keys[K_PAGEDOWN]:  cam_translation[2] += CAMTRANSSPEED * fmult
    if keys[K_PAGEUP]:    cam_translation[2] -= CAMTRANSSPEED * fmult

    """handle mouse input for camera control"""
    if mouse_is_pressed:
        current_mouse_position = pygame.mouse.get_pos()
        if current_mouse_position != last_mouse_position:
            delta = [current_mouse_position[0] - last_mouse_position[0],
                     current_mouse_position[1] - last_mouse_position[1]]
            if keys[K_LSHIFT] or keys[K_RSHIFT]:
                cam_translation[0] += delta[0] * MOUSETRANSSPEED
                cam_translation[1] -= delta[1] * MOUSETRANSSPEED
            else:
                cam_rotation[0] += delta[1] * MOUSEROTSPEED
                cam_rotation[1] += delta[0] * MOUSEROTSPEED
        last_mouse_position = current_mouse_position

    """Tell OpenGL where the camera is located"""
    glLoadIdentity()
    glMultMatrixf(camera_start_matrix)
    glTranslatef(cam_translation[0], cam_translation[1], cam_translation[2])
    glRotatef(cam_rotation[0], 1, 0, 0)
    glRotatef(cam_rotation[1], 0, 1, 0)
    glRotatef(cam_rotation[2], 0, 0, 1)

    """Draw stuff"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    grid_drawer.draw()
    if point_canvas.raw_image_has_been_updated is True:
        point_canvas.upload_colors_to_gpu()
    if not cluster_search_is_active:
        point_canvas.draw()

    glClear(GL_DEPTH_BUFFER_BIT)
    clusters = cluster_maker.cluster_history.get()
    if clusters is not None:
        for cluster in clusters:
            #cluster.draw_cube_around_cluster()
            cluster.draw_hotspots()
        for cluster in clusters:
            cluster.draw_call_out()
    clusters = cluster_maker.cluster_history.get(1)
    if clusters is not None:
        for cluster in clusters:
            cluster.draw_hotspots()

    glDisable(GL_DEPTH_TEST)
    if walabot.sensor_targets_are_shown:
        sensor_targets.update(walabot.sensor_targets)
        sensor_targets.draw()
    glEnable(GL_DEPTH_TEST)

    """draw Text to screen"""
    column = 0
    def col():
        global column
        column += 20
        return column

    draw_text_2D(10, WINDOWSIZE[1] - col(), f"Status: {walabot.status}", (255, 128, 255, 255))
    draw_text_2D(10, WINDOWSIZE[1] - col(), "[PgUp][PgDn][W][A][S][D][←][→][↑][↓] Control Camera")
    draw_text_2D(10, WINDOWSIZE[1] - col(), "[SPACE] Calibrate")
    if cluster_search_is_active:
        draw_text_2D(10, WINDOWSIZE[1] - col(), "[TAB] Stop Object Detection")
        draw_text_2D(10, WINDOWSIZE[1] - col(), f"[C] Clustering Cap: {str(point_canvas.clustering_threshold)}/255")

    else:
        draw_text_2D(10, WINDOWSIZE[1] - col(), "[TAB] Start Object Detection")
    if walabot.sensor_targets_are_shown:
        draw_text_2D(10, WINDOWSIZE[1] - col(), "[T] Hide Sensor Targets")
    else:
        draw_text_2D(10, WINDOWSIZE[1] - col(), "[T] Show Sensor Targets")
    draw_text_2D(10, WINDOWSIZE[1] - col(), f"[H] Hor. Spread   : {str(walabot.phi[0])[:4]}° → {str(walabot.phi[1])[:4]}°", (235, 200, 32, 255))
    draw_text_2D(10, WINDOWSIZE[1] - col(), f"[V] Vert. Spread  : {str(walabot.theta[0])[:4]}° → {str(walabot.theta[1])[:4]}°", (235, 200, 32, 255))
    draw_text_2D(10, WINDOWSIZE[1] - col(), f"[R] Range         : {str(math.trunc(walabot.range[0]))} cm → {str(math.trunc(walabot.range[1]))[:4]} cm", (235, 200, 32, 255))
    draw_text_2D(10, WINDOWSIZE[1] - col(), f"[CTRL]+[H] H-Res. : {str(walabot.phi[2])[:4]}° ({str(walabot.raw_image_size[1])} steps)", (235, 200, 32, 255))
    draw_text_2D(10, WINDOWSIZE[1] - col(), f"[CTRL]+[V] V-Res. : {str(walabot.theta[2])[:4]}° ({str(walabot.raw_image_size[0])} steps)", (235, 200, 32, 255))
    draw_text_2D(10, WINDOWSIZE[1] - col(), f"[CTRL]+[R] R-Res. : {str(walabot.range[2])[:4]} cm ({str(walabot.raw_image_size[2])})", (235, 200, 32, 255))
    draw_text_2D(10, WINDOWSIZE[1] - col(), f"Point Cloud Size  : {str(walabot.point_count)}")
    draw_text_2D(10, WINDOWSIZE[1] - col(), f"Image Energy      : {str(walabot.image_energy)[:5]}")
    draw_text_2D(10, WINDOWSIZE[1] - col(), f"GFX FPS           : {str(fps)[:4]}", (0, 255, 255, 255))
    draw_text_2D(10, WINDOWSIZE[1] - col(), f"Walabot FPS       : {str(clock_walabot_loop.get_fps())[:4]}", (0, 255, 255, 255))
    if cluster_search_is_active:
        draw_text_2D(10, WINDOWSIZE[1] - col(), f"Clustering FPS    : {str(cluster_maker.clock.get_fps())[:4]}", (0, 255, 255, 255))

    #    drawText2D(10, WINDOWSIZE[1] - col(), "Dyn. threshold   : " + str(walabot.dynamicImageEnergyThreshold)[:4])

    pygame.display.flip()
    clock_GFX.tick(MAX_FPS)

"""Code that is executed when the program gets closed"""
walabot.terminator = True
if walabot_fetch_data_thread.is_alive():
    thread_terminator = True
    walabot_fetch_data_thread.join()
    WB.Stop()
    WB.Disconnect()
pygame.quit()
quit()