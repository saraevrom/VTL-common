import tkinter as tk

try:
    from tkinter.ttk import Spinbox
except ImportError:
    from vtl_common.py36xspinbox import Spinbox
    print("Spinbox compat is loaded")


class EntryWithEnterKey(tk.Entry):
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<Return>", self.on_keypress_enter)
        self.bind("<FocusOut>", self.on_focus_out)
        self.on_commit = None

    def on_focus_out(self, *args):
        if self.on_commit:
            self.on_commit()

    def on_keypress_enter(self, *args):
        self.winfo_toplevel().focus()
        # if self.on_commit:
        #     self.on_commit()


class SpinboxWithEnterKey(Spinbox):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.bind("<Return>", self.on_keypress_enter)

    def on_keypress_enter(self, *args):
        self.winfo_toplevel().focus()

