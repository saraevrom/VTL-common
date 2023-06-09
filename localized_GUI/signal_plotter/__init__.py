import tkinter as tk
from tkinter.simpledialog import askinteger
from ..plotter import GridPlotter
import numpy as np
from ...common_GUI.settings_frame import SettingMenu
from .build_settings import build_menu
from ...localization import get_locale

from .time_plotter import MainPlotter


class ChoosablePlotter(tk.Toplevel):
    def __init__(self, master, x_plot, display_data):
        super().__init__(master)
        self.display_data = display_data
        self._close_callback_cp = None
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.plotter = MainPlotter(self, x_plot, display_data)
        self.plotter.pack(side="left", fill="both", expand=True)

        auxpanel = tk.Frame(self)
        auxpanel.pack(side="right", fill="y")
        self.selector = GridPlotter(auxpanel, enable_scale_configuration=False, bright=True, enable_pixel_dclick=False)
        self.selector.axes.set_title(get_locale("app.popup_plot.pixel_map"))
        self.selector.alive_pixels_matrix = np.full(fill_value=False, shape=(16, 16))
        self.selector.update_matrix_plot()
        self.selector.pack(side="top", anchor="ne",fill="x")
        self.selector.on_left_click_callback = self.on_lmb
        self.selector.draw()
        self.selector.toolbar.pack_forget()
        self.selector.on_right_click_callback_outofbounds = self.on_right_click_callback_oob_inside

        self.settings_menu = SettingMenu(auxpanel, autocommit=True)
        self.settings_menu.commit_action = self.on_settings_commit
        build_menu(self.settings_menu)
        self.settings_dict = dict()

        quickactive_btn = tk.Button(auxpanel, text=get_locale("app.popup_plot.detect_active"),
                                    command=self.on_active_select)

        xlim_btn = tk.Button(auxpanel, text=get_locale("app.popup_plot.xlim"),
                                    command=self.on_xlim)


        scale_panel = tk.Frame(auxpanel)

        self.xscale_var = tk.IntVar(self)
        self.xscale_var.set(0)
        self.yscale_var = tk.IntVar(self)
        self.yscale_var.set(0)

        tk.Label(scale_panel, text="X").grid(row=0,column=0)
        tk.Radiobutton(scale_panel,text="lin", variable=self.xscale_var, value=0).grid(row=0,column=1)
        tk.Radiobutton(scale_panel,text="log", variable=self.xscale_var, value=1).grid(row=0,column=2)
        self.xscale_var.trace("w", self.on_xscale_change)

        tk.Label(scale_panel, text="Y").grid(row=1,column=0)
        tk.Radiobutton(scale_panel, text="lin", variable=self.yscale_var, value=0).grid(row=1, column=1)
        tk.Radiobutton(scale_panel, text="log", variable=self.yscale_var, value=1).grid(row=1, column=2)
        self.yscale_var.trace("w", self.on_yscale_change)


        quickactive_btn.pack(side="bottom", fill="x")
        xlim_btn.pack(side="bottom", fill="x")
        scale_panel.pack(side="bottom",fill="x")
        self.settings_menu.pack(side="bottom",fill="x")

        self.settings_menu.push_settings_dict(self.settings_dict)

    def on_xscale_change(self,*args):
        if self.xscale_var.get():
            self.plotter.axes.set_xscale("log")
        else:
            self.plotter.axes.set_xscale("linear")
        self.plotter.draw()

    def on_yscale_change(self,*args):
        if self.yscale_var.get():
            self.plotter.axes.set_yscale("log")
        else:
            self.plotter.axes.set_yscale("linear")
        self.plotter.draw()

    def get_axes(self):
        return self.plotter.axes

    def on_settings_commit(self):
        self.settings_menu.push_settings_dict(self.settings_dict)
        self.plotter.switch_accumulation_mode(self.settings_dict["lightcurve"])
        self.plotter.use_mean = self.settings_dict["lightcurve_mean"]
        self.plotter.flatten_ma = self.settings_dict["lightcurve_ma"]
        self.on_lmb(-1,-1)
        self.plotter.draw()

    def on_active_select(self):
        dst_matrix = self.selector.alive_pixels_matrix[:]
        amplitudes = np.max(self.display_data, axis=0)
        src_matrix = amplitudes > self.settings_dict["threshold"]
        dst_matrix = np.logical_or(src_matrix, dst_matrix)
        self.selector.alive_pixels_matrix = dst_matrix
        self.selector.update_matrix_plot()
        self.selector.draw()
        self.on_lmb(-1, -1)

    def on_lmb(self,i,j):
        if self.settings_dict["show_pixels"]:
            self.plotter.set_visibility(self.selector.alive_pixels_matrix)
        else:
            self.plotter.set_visibility(np.full(fill_value=False, shape=(16, 16)))
            self.plotter.display_matrix = self.selector.alive_pixels_matrix # To accumulate data
            self.plotter.draw()
        self.plotter.update_accumulation_selected()

    def on_right_click_callback(self,i,j):
        self.selector.alive_pixels_matrix[i,j] = True
        self.selector.update_matrix_plot()
        self.selector.draw()
        self.on_lmb(i,j)

    def on_right_click_callback_oob(self):
        self.selector.alive_pixels_matrix = np.full(shape=(16, 16), fill_value=True)
        self.selector.update_matrix_plot()
        self.selector.draw()
        self.on_lmb(-1, -1)

    def on_right_click_callback_oob_inside(self):
        '''
        QOL improvement: clicking inside grid will reset selection.
        :return:
        '''
        if not self.selector.alive_pixels_matrix.any():
            self.selector.alive_pixels_matrix = np.full(shape=(16, 16), fill_value=True)
        else:
            self.selector.alive_pixels_matrix = np.full(shape=(16, 16), fill_value=False)
        self.selector.update_matrix_plot()
        self.selector.draw()
        self.on_lmb(-1, -1)

    def connect_close(self, callback):
        self._close_callback_cp = callback

    def on_closing(self):
        if self._close_callback_cp is not None:
            self._close_callback_cp()
        self.destroy()

    def on_xlim(self):
        low_x = askinteger("xlim","low=")
        high_x = askinteger("xlim","high=")
        self.get_axes().set_xlim(low_x,high_x)


class PopupPlotable(tk.Misc):
    def __init__(self, grid_plotter:GridPlotter):
        self._active_gridplotter = grid_plotter
        self._plotter_window = None
        self._active_gridplotter.on_right_click_callback = self.on_right_click_callback
        self._active_gridplotter.on_right_click_callback_outofbounds = self.on_right_click_callback_oob

    def get_plot_data(self):
        raise NotImplementedError("Unable to obtain plot data")

    def postprocess_plot(self, axes):
        pass

    def on_left_click(self, i, j):
        if self.ensure_plotter():
            self._plotter_window.on_lmb(i, j)

    def on_right_click_callback(self,i,j):
        if self.ensure_plotter():
            self._plotter_window.on_right_click_callback(i,j)

    def on_right_click_callback_oob(self):
        if self.ensure_plotter():
            self._plotter_window.on_right_click_callback_oob()

    def ensure_plotter(self):
        if self._plotter_window is None:
            self.create_plotter()
        return self._plotter_window is not None

    def _on_popup_close(self):
        self._plotter_window = None

    def create_plotter(self):
        draw_data = self.get_plot_data()
        if draw_data is not None:
            x_data, display_data = draw_data
            self._plotter_window = ChoosablePlotter(self, x_data, display_data)
            self.postprocess_plot(self._plotter_window.get_axes())
            self._plotter_window.connect_close(self._on_popup_close)
