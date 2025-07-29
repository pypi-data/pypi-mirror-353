from ntsim.viewer.viewer_base import viewerbase
import pyqtgraph.opengl as gl
import numpy as np
import pyqtgraph as pg

import ntsim.utils.pdg_colors as dict_colors

import logging
log = logging.getLogger('tracks_viewer')

class tracks_viewer(viewerbase):
    def configure(self,opts):
        self.options = opts
        self.widgets['geometry'].opts['distance'] = self.options.distance
        g = gl.GLGridItem()
        g.scale(*self.options.grid_scale)
        g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
        # check if this widget is not added already
        if not self.widgets['geometry'] in self.docks['geometry'].widgets:
            self.docks['geometry'].addWidget(self.widgets['geometry'])
        self.tracks_list_static = []
        self.tracks_list_animated = {}

    def track_lines(self):
        self.pos = {}
        self.t = {}
        self.particle_id = {}
        self.pdgid_colors = {}
        pg.setConfigOption('useOpenGL', True)
        for track in self.data:
            self.particle_id[track] = self.data[track]['pdgid']
            if self.particle_id[track][0] in dict_colors.pdg_colors:
                self.pdgid_colors[track] = dict_colors.pdg_colors[self.particle_id[track][0]]
                x = self.data[track]['x_m']
                y = self.data[track]['y_m']
                z = self.data[track]['z_m']
                self.t[track] = self.data[track]['t_ns']
                if np.absolute(self.particle_id[track][0]) in (12, 14, 16):
                    x_new = []
                    y_new = []
                    z_new = []
                    t_new = []
#                    diff_x = [abs(int(n)) for n in np.diff(x)]
#                    diff_y = [abs(int(n)) for n in np.diff(y)]
#                    diff_z = [abs(int(n)) for n in np.diff(z)]
                    for n in range(len(x) - 1):
                        distance = int(np.linalg.norm(np.array((x[n],y[n],z[n]))-np.array((x[n+1],y[n+1],z[n+1]))))
                        x_new = np.concatenate([x_new, np.linspace(x[n], x[n+1], distance)], axis = 0)
                        y_new = np.concatenate([y_new, np.linspace(y[n], y[n+1], distance)], axis = 0)
                        z_new = np.concatenate([z_new, np.linspace(z[n], z[n+1], distance)], axis = 0)
                        t_new = np.concatenate([t_new, np.linspace(self.t[track][n], self.t[track][n+1], distance)], axis = 0)
                    self.pos[track] = np.array([x_new[:], y_new[:], z_new[:]]).T
                    self.t[track] = t_new
                    points = gl.GLLinePlotItem(pos = self.pos[track], color=pg.mkColor(self.pdgid_colors[track]), width = 1, mode = 'lines')
                else:
                    if self.particle_id[track][0] == -12: print(self.particle_id[track][0])
                    self.pos[track] = np.array([x[:], y[:], z[:]]).T
                    points = gl.GLLinePlotItem(pos = self.pos[track], color=pg.mkColor(self.pdgid_colors[track]), width = 2)
                self.tracks_list_static.append(points)
                points.setVisible(False)
                self.widgets['geometry'].addItem(points)

    def build_animated_tracks(self):
        self.track_lines()
        for frame in range(len(self.frames)):
            self.tracks_list_animated[frame] = []
            for track in self.data:
                if self.particle_id[track][0] in dict_colors.pdg_colors:
                    multi_pos = zip(self.pos[track], self.t[track])
                    pos_t = np.array( [points[0] for points in multi_pos if (points[1] <= self.frames[frame] and points[1] >= self.frames[frame-1])])
                    if np.size(pos_t) != 0:
                        if (pos_t[0] != self.pos[track][0]).all():
                            pos_t = np.vstack([self.pos[track][np.where(self.pos[track] == pos_t[0])[0][0] - 1], pos_t])
                        graph_track = gl.GLLinePlotItem(pos = pos_t, color=pg.mkColor(self.pdgid_colors[track]), width = 2)
                        if abs(self.particle_id[track][0]) in (12, 14, 16):
                            graph_track = gl.GLLinePlotItem(pos = pos_t, color=pg.mkColor(self.pdgid_colors[track]), width = 1, mode = 'lines')
                        self.tracks_list_animated[frame].append(graph_track)
                        graph_track.setVisible(False)
                        self.widgets['geometry'].addItem(graph_track)

    def display_static(self, vis = False):
        self.setVisible_tracks_static(vis)

    def setVisible_tracks_static(self, vis):
        track_lines = [track.setVisible(vis) for track in self.tracks_list_static]

    def clean_static(self):
        for track in self.tracks_list_static:
            self.widgets['geometry'].removeItem(track)
            self.tracks_list_static = []

    def clean_animated(self):
        for frame in self.tracks_list_animated:
            for track in self.tracks_list_animated[frame]:
                self.widgets['geometry'].removeItem(track)
        self.tracks_list_animated = {}

    def clean_view(self):
        self.clean_static()
        self.clean_animated()

    def setVisible_tracks_animated(self, vis):
        for frame in self.tracks_list_animated:
            [ track.setVisible(vis) for track in self.tracks_list_animated[frame] ]

    def display_frame(self,frame, vis):
        if frame == 0:
            self.setVisible_tracks_animated(False)
        for f in range(frame):
            [ track.setVisible(vis) for track in self.tracks_list_animated[f] ]
        for track in self.tracks_list_animated[frame]:
            track.setVisible(vis)
