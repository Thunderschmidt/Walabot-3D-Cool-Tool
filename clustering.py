"""
How Martin's Cluster Search works:

First, hotspots are identified, which are radar blibs with an intensity beyond a certain threshold.
The hotspots enter the algorithm sorted from left to right.

    3   5   8       9   10

  2       7

1       6                  11

      4

The algorithm starts with the leftmost hotspot (1) and checks if the next few
hotspots right to it are in range. If so, it connects these hotpots via a
recursive algorithm, building a tree structure.

    3---5---8       9   10
   /     |
  2       7
 /
1       6                  11

      4

When the tree has ended, the algorithm returns to the origin hotspot. From there,
it hops to the nearest hotspot to the right which does not belong to a tree.
In our example this hotspot is hotspot number 4. A new recursive tree building begins.


    3---5---8       9---10
   /     |
  2       7
 /       /
1       6                  11
       /
      4

When two tree structures meet, they get merged. After the cluster search has
ended, solitary hotspots and very small trees get deleted (noise removal).

    C---C---C
   /     |
  C       C
 /       /
C       C
       /
      C
"""
import math
#import math
#import pygame
#from pygame.locals import *
#from OpenGL.GL import *
#from OpenGL.GLU import *
import threading
from circular_array import *
#import numpy
#from constants import *
from gfx import *

cluster_colors = [
    (255, 0, 0, 200),  # red
    (255, 165, 0, 200),  # orange
    (255, 255, 0, 200),  # yellow
    (127, 255, 0, 200),  # chartreuse
    (0, 255, 0, 200),    # green
    (0, 255, 127, 200),  # spring green
    (0, 255, 255, 200),  # cyan
    (0, 127, 255, 200),  # azure
    (0, 0, 255, 200),    # blue
    (127, 0, 255, 200),  # violet
    (255, 0, 255, 200),  # magenta
    (255, 0, 127, 200),  # rose
    (204, 0, 0, 200),    # dark red
    (204, 102, 0, 200),  # brown
    (204, 204, 0, 200),  # olive
    (76, 153, 0, 200),   # dark green
]


class Hotspot:
    """Special Point with high intensity, used for clustering."""

    def __init__(self, cart_loc=(0, 0, 0), intensity=0, polar_loc=(0, 0, 0)):
        self.cart_loc = cart_loc
        self.polar_loc = polar_loc
        self.intensity = intensity
        self.belongs_to_cluster = None

    def __eq__(self, other):
        return self.index == other.index
    def draw(self):
        glBegin(GL_POINTS)
        glVertex3fv(self.cart_loc)
        glEnd()


class Cluster:
    """conglomerate of hotspots"""

    def __init__(self):
        self.id = 0
        self.color = None
        self.size = None
        self.c_pos = None
        self.p_pos = None
        self.hotspots = []
        self.c_min = [None, None, None]
        self.c_max = [None, None, None]
        self.p_min = [None, None, None]
        self.p_max = [None, None, None]

    def is_similar_to(self, cluster_2):
        pos_1 = self.get_polar_pos()
        pos_2 = cluster_2.get_polar_pos()
        min_dif = 2
        if abs(pos_1[0] - pos_2[0]) < min_dif and abs(pos_1[1] - pos_2[1]) < min_dif and abs(pos_1[2] - pos_2[2]) < min_dif:
            return True
        return False

    def add_hotspot(self, hotspot):
        """adds hotspot to cluster and resizes the cluster"""

        def choose_bigger(a, b):
            if a is None: return b
            if b is None: return a
            if a > b:
                return a
            else:
                return b

        def choose_smaller(a, b):
            if a is None: return b
            if b is None: return a
            if a < b: return a
            else: return b

        hotspot.belongs_to_cluster = self
        self.hotspots.append(hotspot)
        for i in range(3):
            self.c_min[i] = choose_smaller(hotspot.cart_loc[i], self.c_min[i])
            self.c_max[i] = choose_bigger(hotspot.cart_loc[i], self.c_max[i])
            self.p_min[i] = choose_smaller(hotspot.polar_loc[i], self.p_min[i])
            self.p_max[i] = choose_bigger(hotspot.polar_loc[i], self.p_max[i])

    def merge_with(self, cluster):
        for hotspot in cluster.hotspots:
            self.add_hotspot(hotspot)
        cluster.hotspots = None

    def is_in_front_of(self, cluster):
        if abs(cluster.p_pos[0] - self.p_pos[0]) < CLUSTER_SHADOW_OFFSET and abs(
                cluster.p_pos[1] - self.p_pos[1]) < CLUSTER_SHADOW_OFFSET: return True
        return False

    def get_cart_pos(self):
        if self.c_pos is not None: return self.c_pos
        self.c_pos = ((self.c_min[0] + self.c_max[0]) / 2, (self.c_min[1] + self.c_max[1]) / 2, (self.c_min[2] + self.c_max[2]) / 2)
        return self.c_pos

    def get_polar_pos(self):
        if self.p_pos is not None: return self.p_pos
        self.p_pos = (int((self.p_min[0] + self.p_max[0]) / 2), int((self.p_min[1] + self.p_max[1]) / 2),
                      int((self.p_min[2] + self.p_max[2]) / 2))
        return self.p_pos

    def get_size(self):
        if self.size is not None: return self.size
        self.size = (abs(self.c_min[0] - self.c_max[0]) + BOXOFFSET * 2,
                     abs(self.c_min[1] - self.c_max[1]) + BOXOFFSET * 2,
                     abs(self.c_min[2] - self.c_max[2]) + BOXOFFSET * 2)
        return self.size

    def draw_hotspots(self):
        glColor4ub(*self.color)
        glPointSize(HOTSPOT_POINTSIZE)
        glBegin(GL_POINTS)
        for hotspot in self.hotspots:
            glVertex3fv(hotspot.cart_loc)
        glEnd()

    def draw_call_out(self):
        pos = self.get_cart_pos()
        dist = math.hypot(*pos)
        draw_text_3D(f" {dist:.2f} ", True, (0, 20), (pos[0], self.c_max[1], pos[2]), (0,0,0,255), self.color)

    def draw_cube_around_cluster(self):
        glColor4ub(*self.color)
        cube.draw_stretched(self.get_cart_pos(), self.get_size())

    def overlaps_with(self, cluster_2):
        if any(element in self.hotspots for element in cluster_2.hotspots): return True
        return False

class ClusterMaker:
    clusters = []
    is_performing_cluster_search = False
    hotspots_have_been_updated = False

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.hotspots = []
        self.hotspots_buffer = []
        self.current_cluster_id = 0
        self.cluster_history = CircularArray(CLUSTER_HISTORY_STACK_SIZE)

    def submit_new_hotspots(self, hotspots):
        self.hotspots_buffer = hotspots
        self.hotspots_have_been_updated = True
        if not self.is_performing_cluster_search:
            cluster_search_thread = threading.Thread(target=self.martins_cluster_search)
            cluster_search_thread.start()

    def find_cluster_identity_in_history(self, cluster_1):
        for i in range(self.cluster_history.stack_size):
            clusters_2 = self.cluster_history.get(i)
            if clusters_2 is None: continue
            for cluster_2 in clusters_2:
                if cluster_2.is_similar_to(cluster_1):
                    return cluster_2.id
        return None

    def martins_cluster_search(self):
        self.clock.tick()
        self.is_performing_cluster_search = True
        self.hotspots_have_been_updated = False
        self.hotspots = self.hotspots_buffer
        hotspots = self.hotspots
        clusters = []
        for hotspot in hotspots:
            if hotspot.belongs_to_cluster is None:
                cluster = Cluster()
                cluster.add_hotspot(hotspot)
                self.martins_cluster_search_recursor(cluster, hotspot, hotspots)
                clusters.append(cluster)
        self.filter_out_small_clusters(clusters)
        if ERASE_RADAR_SHADOWS:
            self.filter_out_cluster_shadows(clusters)
        for cluster in clusters:
            cluster.id = self.find_cluster_identity_in_history(cluster)
            if cluster.id is None:
                cluster.id = self.current_cluster_id
                self.current_cluster_id += 1
            cluster.color = cluster_colors[cluster.id % 16]
        self.cluster_history.push(clusters)
        if self.hotspots_have_been_updated: self.martins_cluster_search() # if there are new hotspots, restart this method
        self.is_performing_cluster_search = False

    def martins_cluster_search_recursor(self, cluster, hotspot, hotspots):
        offset = 0
        while True:
            offset += 1
            index = hotspot.index + offset
            if index >= len(hotspots): break
            new_hotspot = hotspots[index]
            if new_hotspot.polar_loc[0] - hotspot.polar_loc[0] > CLUSTER_SPATIAL_THRESHOLD: break
            if new_hotspot.belongs_to_cluster == cluster: continue
            if abs(new_hotspot.polar_loc[1] - hotspot.polar_loc[1]) > CLUSTER_SPATIAL_THRESHOLD: continue
            if abs(new_hotspot.polar_loc[2] - hotspot.polar_loc[2]) > CLUSTER_SPATIAL_THRESHOLD: continue
            if new_hotspot.belongs_to_cluster is not None: cluster.merge_with(new_hotspot.belongs_to_cluster)
            cluster.add_hotspot(new_hotspot)
            self.martins_cluster_search_recursor(cluster, new_hotspot, hotspots)

    def push_empty_cluster(self):
        self.cluster_history.push(None)

    @staticmethod
    def filter_out_small_clusters(clusters):
        i = 0
        while i < len(clusters):
            if clusters[i].hotspots is None or len(clusters[i].hotspots) < MINCLUSTERSIZE:
                del clusters[i]
            else:
                i += 1

#    def is_cluster_historic(self, cluster_1):
    @staticmethod
    def filter_out_cluster_shadows(clusters):
        """ This method detects if there is one cluster covering up another one, then it deletes the one with the greater distance"""
        for cluster in clusters: cluster.get_polar_pos()
        clusters = sorted(clusters, key=lambda cluster: cluster.p_pos[2])
        for id in range(0, len(clusters)): clusters[id].id = id
        i = 0
        while i < (len(clusters) - 1):
            j = i + 1
            while j < len(clusters):
                if clusters[i].is_in_front_of(clusters[j]):
                    clusters[j].id += 1000
                j += 1
            i += 1
        new_clusters = []
        for cluster in clusters:
            if cluster.id < 1000: new_clusters.append(cluster)
        return new_clusters

    def calc_drawable_clusters(self):
        drawable_clusters = []
        cluster_ids = []
        cluster_colors = []
        for i in range(CLUSTER_NOSTALGIA):
            clusters = self.cluster_history.get(i)
            if clusters is None: return
            for cluster in clusters:
                if cluster.id not in cluster_ids:
                    overlaps = False
                    for drw_clus in drawable_clusters:
                        if  cluster.overlaps_with(drw_clus):
                            overlaps = True
                            break
                    if overlaps: continue
                    drawable_clusters.append(cluster)
                    cluster_ids.append(cluster.id)
                    cluster_colors.append(cluster.color)
        return drawable_clusters;
