import tkinter as tk
from tkinter import ttk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.pyplot import Normalize
from ..astronomy import find_index
matplotlib.use("TkAgg")
from ..parameters import *
from ..localization import get_locale
from ..parameters import SCALE_FLOATING_POINT_FORMAT

from ..common_GUI.modified_base import EntryWithEnterKey

LOWER_EDGES = np.arange(HALF_PIXELS)*PIXEL_SIZE+HALF_GAP_SIZE
LOWER_EDGES = np.concatenate([-np.flip(LOWER_EDGES)-PIXEL_SIZE, LOWER_EDGES])




class Plotter(ttk.Frame):
    def __init__(self, master, polar=False, *args, **kwargs):
        super(Plotter, self).__init__(master, *args, **kwargs)
        self.figure: Figure
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.axes: Axes
        self.axes = self.figure.add_subplot(1, 1, 1, polar=polar)

        self.mpl_canvas = FigureCanvasTkAgg(self.figure, self)
        self.mpl_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(self.mpl_canvas, self)
        self.toolbar.update()


    def allow_callbacks(self):
        return not self.figure.canvas.toolbar.mode

    def draw(self):
        #self.figure.canvas.draw()
        #self.figure.canvas.flush_events()
        self.mpl_canvas.draw()

class GridView(object):
    def __init__(self, axes, initcolor="blue"):
        self._grid_axes = axes
        span = HALF_PIXELS*PIXEL_SIZE+HALF_GAP_SIZE
        self._grid_axes.set_xlim(-span, span)
        self._grid_axes.set_ylim(-span, span)
        self._grid_axes.set_box_aspect(1)

        self.patches = []
        for y in LOWER_EDGES:
            row = []
            for x in LOWER_EDGES:
                rect = Rectangle((x, y), PIXEL_SIZE, PIXEL_SIZE, color=initcolor)
                self._grid_axes.add_patch(rect)
                row.append(rect)
            self.patches.append(row)
        self._grid_axes.vlines(LOWER_EDGES, -span, -HALF_GAP_SIZE, colors="black")
        self._grid_axes.vlines(LOWER_EDGES, span, HALF_GAP_SIZE, colors="black")
        self._grid_axes.vlines([-HALF_GAP_SIZE, span], -span, -HALF_GAP_SIZE, colors="black")
        self._grid_axes.vlines([-HALF_GAP_SIZE, span], span, HALF_GAP_SIZE, colors="black")
        self._grid_axes.hlines(LOWER_EDGES, -span, -HALF_GAP_SIZE, colors="black")
        self._grid_axes.hlines(LOWER_EDGES, span, HALF_GAP_SIZE, colors="black")
        self._grid_axes.hlines([-HALF_GAP_SIZE, span], -span, -HALF_GAP_SIZE, colors="black")
        self._grid_axes.hlines([-HALF_GAP_SIZE, span], span, HALF_GAP_SIZE, colors="black")

    def set_colors(self, color_mat):
        for j in range(2 * HALF_PIXELS):
            for i in range(2 * HALF_PIXELS):
                self.set_pixel_color(j,i,color_mat[i,j])

    def set_pixel_color(self,j,i, color):
        self.patches[j][i].set_color(color)


class GridPlotter(Plotter, GridView):
    def __init__(self, master, norm=None, enable_scale_configuration=True, bright=False, enable_pixel_dclick=True, *args, **kwargs):
        Plotter.__init__(self,master, *args, **kwargs)
        GridView.__init__(self, self.axes)
        self.use_autoscale_var = tk.IntVar(self)
        self.use_autoscale_var.set(1)
        self.use_autoscale_var.trace("w", self.on_scale_change_commit)

        self.min_norm_entry = tk.StringVar(self)
        self.max_norm_entry = tk.StringVar(self)

        self.on_left_click_callback = None
        self.on_right_click_callback = None
        self.on_right_click_callback_outofbounds = None

        self.colorbar = None
        self.buffer_matrix = np.zeros((2*HALF_PIXELS, 2*HALF_PIXELS))
        self.alive_pixels_matrix = np.ones([2 * HALF_PIXELS, 2 * HALF_PIXELS]).astype(bool)
        self.highlight_pixels_matrix = np.zeros([2 * HALF_PIXELS, 2 * HALF_PIXELS]).astype(bool)

        self.enable_scale_configuration = enable_scale_configuration
        self.bright = bright
        self.norm = norm
        self.use_autoscale_var = tk.IntVar(self)
        self.use_autoscale_var.set(1)
        self.use_autoscale_var.trace("w", self.on_scale_change_commit)

        self.min_norm_entry = tk.StringVar(self)
        self.max_norm_entry = tk.StringVar(self)

        self.enable_scale_configuration = enable_scale_configuration
        self.on_left_click_callback = None
        self.on_right_click_callback = None
        self.on_right_click_callback_outofbounds = None
        self.bright = bright

        self.colorbar = None

        self.buffer_matrix = np.zeros((16, 16))
        self.alive_pixels_matrix = np.ones([2*HALF_PIXELS, 2*HALF_PIXELS]).astype(bool)
        self.highlight_pixels_matrix = np.zeros([2*HALF_PIXELS, 2*HALF_PIXELS]).astype(bool)


        self.figure.canvas.mpl_connect("button_press_event", self.on_plot_click)
        self.figure.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.figure.canvas.mpl_connect("axes_leave_event", self.on_leave)

        tk_control_panel = tk.Frame(self)
        tk_control_panel.pack(side=tk.BOTTOM, fill=tk.X)
        for i in range(4):
            tk_control_panel.columnconfigure(i, weight=1)
        if enable_scale_configuration:
            autoscale_check = tk.Checkbutton(tk_control_panel, text=get_locale("app.widgets.gridplotter.use_autoscale"),
                                             variable=self.use_autoscale_var)
            autoscale_check.grid(row=0, column=0, columnspan=4, sticky="w")
            tk.Label(tk_control_panel, text=get_locale("app.widgets.gridplotter.scale")).grid(row=0, column=1, sticky="ew")
            tk.Label(tk_control_panel, text="—").grid(row=0, column=3, sticky="ew")
            min_ = EntryWithEnterKey(tk_control_panel, textvariable=self.min_norm_entry)
            min_.grid(row=0, column=2, sticky="ew")
            min_.on_commit = self.on_scale_change_commit
            max_ = EntryWithEnterKey(tk_control_panel, textvariable=self.max_norm_entry)
            max_.grid(row=0, column=4, sticky="ew")
            max_.on_commit = self.on_scale_change_commit
            tk.Button(tk_control_panel, text="C", command=self.clear_broken).grid(row=0, column=5, sticky="e")


        self.annotation = self.axes.annotate("", xy=(0, 0), xytext=(-25, 20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        self.annotation.set_visible(False)
        self._last_alive = None
        self.enable_pixel_dclick = enable_pixel_dclick
        self.update_matrix_plot(True)

    def on_scale_change_commit(self, *args):
        self.update_matrix_plot(True)
        self.draw()

    def get_broken(self):
        return np.logical_not(self.alive_pixels_matrix)

    def clear_broken(self):
        self.alive_pixels_matrix = np.ones([2*HALF_PIXELS, 2*HALF_PIXELS]).astype(bool)
        self.update_matrix_plot(True)
        self.draw()

    def update_norm(self, low_fallback=None, high_fallback=None):
        if low_fallback is None:
            if self.norm is None:
                return
            low_fallback = self.norm.vmin

        if high_fallback is None:
            if self.norm is None:
                return
            high_fallback = self.norm.vmax
        if low_fallback >= high_fallback:
            if self.bright:
                high_fallback = low_fallback - 1e-6
            else:
                high_fallback = low_fallback + 1e-6

        if not self.enable_scale_configuration or self.use_autoscale_var.get():
            low = low_fallback
            high = high_fallback
            self.max_norm_entry.set(SCALE_FLOATING_POINT_FORMAT.format(high_fallback))
            self.min_norm_entry.set(SCALE_FLOATING_POINT_FORMAT.format(low_fallback))
        else:
            try:
                low = float(self.min_norm_entry.get())
            except ValueError:
                self.min_norm_entry.set(SCALE_FLOATING_POINT_FORMAT.format(low_fallback))
                low = low_fallback
            try:
                high = float(self.max_norm_entry.get())
            except ValueError:
                self.max_norm_entry.set(SCALE_FLOATING_POINT_FORMAT.format(high_fallback))
                high = high_fallback

        if low > high:
            low, high = high, low

        if self.norm is None:
            self.norm = Normalize(low, high)
        else:
            # Magic: pyplot requires to assign twice
            self.norm.vmin = low
            self.norm.vmin = low
            self.norm.vmax = high
            self.norm.vmax = high

    def update_matrix_plot(self, update_norm=False):
        # start_time = time.time()
        # print("Draw START")
        if update_norm or (self.norm is None):
            alive_data = self.buffer_matrix[self.alive_pixels_matrix]
            if len(alive_data)>0:
                low_auto = np.min(alive_data)
                high_auto = np.max(alive_data)
            else:
                low_auto = -1
                high_auto = 0

            self.update_norm(low_auto, high_auto)

            if self.colorbar is None:
                self.colorbar = self.figure.colorbar(plt.cm.ScalarMappable(norm=self.norm, cmap=PLOT_COLORMAP),
                                                     ax=self.axes)
        # print("Normalized:", time.time()-start_time)
        if self.norm is not None:
            for j in range(2*HALF_PIXELS):
                for i in range(2*HALF_PIXELS):
                    if self.highlight_pixels_matrix[i, j]:
                        self.set_pixel_color(j,i,PLOT_HIGHLIGHT_COLOR)
                    elif self.alive_pixels_matrix[i, j]:
                        self.set_pixel_color(j,i,PLOT_COLORMAP(self.norm(self.buffer_matrix[i, j])))
                    else:
                        self.set_pixel_color(j, i, PLOT_BROKEN_COLOR)
        # print("Draw end:", time.time()-start_time)

    def set_broken(self, broken):
        self.alive_pixels_matrix = np.ones([2*HALF_PIXELS, 2*HALF_PIXELS]).astype(bool)
        for i, j in broken:
            self.alive_pixels_matrix[i, j] = False

    def toggle_broken(self, i, j):
        self.alive_pixels_matrix[i, j] = not self.alive_pixels_matrix[i, j]
        self._last_alive = self.alive_pixels_matrix[i, j]

    def mark_broken(self,i,j):
        self.alive_pixels_matrix[i, j] = False

    def clear_highlight(self):
        self.highlight_pixels_matrix = np.zeros([2*HALF_PIXELS, 2*HALF_PIXELS]).astype(bool)

    def highlight_pixel(self, i, j):
        self.highlight_pixels_matrix[i, j] = True

    def highlighted_pixels_query(self):
        return np.array(np.where(self.highlight_pixels_matrix)).T



    def on_plot_click(self, event):
        if (event.xdata is not None) and (event.ydata is not None) and self.allow_callbacks():
            i = find_index(event.xdata)
            j = find_index(event.ydata)
            if i >= 0 and j >= 0:
                if event.button == 1:  #LMB
                    self.toggle_broken(i, j)
                    self.update_matrix_plot(True)
                    self.draw()
                    if self.on_left_click_callback:
                        self.on_left_click_callback(i, j)
                elif event.button == 3:  #RMB
                    if self.on_right_click_callback:
                        self.on_right_click_callback(i, j)
                if self.enable_pixel_dclick and event.dblclick and self._last_alive is not None:
                    if i<8 and j<8:
                        self.alive_pixels_matrix[:8,:8] = np.logical_not(self.alive_pixels_matrix[:8,:8])
                    elif i>=8 and j<8:
                        self.alive_pixels_matrix[8:,:8] = np.logical_not(self.alive_pixels_matrix[8:,:8])
                    elif i<8 and j>=8:
                        self.alive_pixels_matrix[:8,8:] = np.logical_not(self.alive_pixels_matrix[:8,8:])
                    elif i>=8 and j>=8:
                        self.alive_pixels_matrix[8:,8:] = np.logical_not(self.alive_pixels_matrix[8:,8:])

                    self.update_matrix_plot(True)
                    self.draw()
                    if self.on_left_click_callback:
                        self.on_left_click_callback(i, j)
            elif event.button == 3:
                if self.on_right_click_callback_outofbounds:
                    self.on_right_click_callback_outofbounds()
            elif event.button == 1:  # LMB OOB
                self._last_alive = None

            if (i<0 or j<0) and event.dblclick:
                self.alive_pixels_matrix = np.logical_not(self.alive_pixels_matrix)
                self.update_matrix_plot(True)
                self.draw()
                if self.on_left_click_callback:
                    self.on_left_click_callback(i, j)

    def on_leave(self, event):
        self.annotation.set_visible(False)
        self.figure.canvas.draw_idle()

    def pointer_additional_text(self,x,y):
        return ""

    def on_hover(self, event):
        if event.xdata and event.ydata:
            i = find_index(event.xdata)
            j = find_index(event.ydata)
            if i >= 0 and j >= 0:
                v = self.buffer_matrix[i, j]
                self.annotation.xy = (event.xdata, event.ydata)
                self.annotation.set_visible(True)
                add_text = self.pointer_additional_text(event.xdata, event.ydata)
                if add_text:
                    add_text = "\n" + add_text
                self.annotation.set_text(f"[{i+1}, {j+1}]\n({round(v,2)})"+add_text)
                #print(f"HOVERING over {i},{j}")

                if event.button == 1 and self._last_alive is not None:
                    if self.alive_pixels_matrix[i,j] != self._last_alive:
                        self.alive_pixels_matrix[i,j] = self._last_alive
                        self.update_matrix_plot(True)
                        if self.on_left_click_callback:
                            self.on_left_click_callback(i, j)
                self.draw()
                return
        self.annotation.set_visible(False)
        self.draw()

