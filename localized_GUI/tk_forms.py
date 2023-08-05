import tkinter as tk
from ..common_GUI import TkDictForm
from .controls import TkFormControlPanel

class OptionFrame(tk.Frame):
    def __init__(self, master, initial_view=True):
        super().__init__(master)
        topbar = tk.Frame(self, borderwidth = 1)
        topbar.pack(side="top", fill="x")
        self.togglevar = tk.IntVar(self)
        self.togglevar.set(int(initial_view))
        self.togglevar.trace("w", self.update_view)
        toggle = tk.Checkbutton(topbar,variable=self.togglevar, text="")
        toggle.pack(side="left")
        self.contents = tk.Frame(self)
        if initial_view:
            self.contents.pack(side="bottom", fill="both", expand=True)

    def update_view(self,*args):
        if self.togglevar.get():
            self.contents.pack(side="bottom", fill="both", expand=True)
        else:
            self.contents.pack_forget()


class SaveableTkDictForm(tk.Frame):
    def __init__(self, master, tk_form_configuration, use_scrollview=True, color_index=0, file_asker=None,
                 save_label="app.filedialog.save_settings.title", load_label="app.filedialog.load_settings.title",
                 optional=False, option_default_visible=True):
        #super().__init__(master, tk_form_configuration, use_scrollview, color_index)
        super().__init__(master)
        if optional:
            opt = OptionFrame(self, option_default_visible)
            opt.pack(fill="both", expand=True)
            tgt = opt.contents
        else:
            tgt = self

        self.tkform = TkDictForm(tgt, tk_form_configuration, use_scrollview, color_index)
        self.tkform.pack(fill="both", expand=True)

        control_panel = TkFormControlPanel(self, file_asker=file_asker, save_label=save_label, load_label=load_label)
        control_panel.connect_form(self)
        control_panel.pack(side="bottom",fill="x")

    def __getattr__(self, item):
        return getattr(self.tkform,item)