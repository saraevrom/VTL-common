import tkinter as tk
from tkinter.simpledialog import Dialog
from ...localization import get_locale


def fine_line(axes, label):
    for line in axes.get_lines():
        if line.get_label() == label:
            return line

class StyleDialog(Dialog):
    def __init__(self,master, line_artist, axes):
        self.line_artist = line_artist
        self.axes = axes
        self._grid_index = 0
        self._colorvar = None
        self._stylevar = None
        super().__init__(master)

    def add_entry(self, parent, key, initial_var):
        tk.Label(parent,text=get_locale(key)).grid(row=self._grid_index,column=0, sticky="nsew")
        var = tk.StringVar(parent)
        var.set(initial_var)
        tk.Entry(parent,textvariable=var).grid(row=self._grid_index,column=1, sticky="nsew")
        self._grid_index += 1
        return var

    def body(self, master: tk.Frame) -> tk.Misc | None:
        self._colorvar = self.add_entry(master, "app.popup_plot.dialog.color", self.line_artist.get_color())
        self._stylevar = self.add_entry(master, "app.popup_plot.dialog.color", self.line_artist.get_linestyle())

    def apply(self) -> None:
        line = fine_line(self.axes, self.line_artist.get_label())
        if line:
            line.set_color(self._colorvar.get())
            line.set_linestyle(self._stylevar.get())