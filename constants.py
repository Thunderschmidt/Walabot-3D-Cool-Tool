WINDOWSIZE = (1200, 640)
MAX_FPS = 40

"""Initial Walabot settings"""
WALA_MINRANGE_CM = 15  # minimal range threshold in cm (1...1000)
WALA_MAXRANGE_CM = 400  # maximal range threshold in cm (1...1000)
WALA_RANGESTEPSIZE_CM = 5.0  # Resolution in cm (0.1...10)
WALA_HORIZONTALANGLE = 20  # ?...90 Degrees (90 means 180)
WALA_HORIZONTALSTEPSIZE_DEG = 4  # Resolution in degrees (1.0...10)
WALA_VERTICALANGLE_DEG = 10  # ?...90 Degrees (90 means 180)
WALA_VERTICALSTEPSIZE_DEG = 4  # Resolution in degrees (1.0...10) (smaller means finer)
WALA_MOVINGTARGETFILTER = False  # if true, the Walabot is supposed to only deliver blibs from moving targets
WALA_SIGNALTHRESHOLD = 2  # 0.1...100 Walabot won't send blibs with an intensity below this threshold

"""display parameters"""
STARTROT = [20, 180, 0]
STARTPOS = [0, 0, -WALA_MAXRANGE_CM / 50]
GRIDCOLOR = (100, 100, 120, 255)
WALABOTCOLOR = (30, 200, 10, 255)
BACKGROUNDCOLOR = (0.09, 0.09, 0.10, 1.0)
SENSORTARGETSCOLOR = (255, 0, 255, 255)
FLOORDISTANCE = 0.0  # how many meters above ground is the walabot located?
CYLINDRICALPROJECTION = False # switches projection from spherical to cylindrical (mathematically wrong, but more comfortable to watch)
SHOW_SENSOR_TARGETS = False
STANDARDLINEWIDTH = 1.0
POINTSIZE = 7.0
HOTSPOT_POINTSIZE = 12.0

"""camera movement options"""
CAMROTSPEED = 90  # camera rotates at 90° per second
CAMTRANSSPEED = WALA_MAXRANGE_CM / 100  # camera speed depends on initial max range
MOUSEROTSPEED = 0.4  # how fast the mouse rotates the camera
MOUSETRANSSPEED = 0.015  # how fast the mouse translates the camera

"""clustering parameters"""
CLUSTERING_THRESHOLD = 130 # from which intensity on a point becomes a hotspot?
CLUSTER_HISTORY_STACK_SIZE = 100  # how many frames to look into the past for identifying clusters?
CLUSTER_SPATIAL_THRESHOLD = 1  # how close together must clusters be to get merged? recommended: 1 - 3
CLUSTER_NOSTALGIA = 4 # how many frames to look back in the past for drawable clusters? For noise reduction
MINCLUSTERSIZE = 4  # how many hotspots make a cluster?
CLUSTER_SHADOW_OFFSET = 6 # influences the erasure of cluster shadows
BOXOFFSET = 0.05 # size of boxes drawn around clusters
ERASE_RADAR_SHADOWS = False # A radar echo can produce shadows behind it. If True, they get deleted
