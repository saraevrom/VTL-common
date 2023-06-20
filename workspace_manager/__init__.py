import json
import os.path as ospath
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from ..localization import get_locale
import os, re


cwd = ospath.abspath(__file__)
CONF_PATH = ospath.join(ospath.dirname(cwd), "workspace.json")


def get_extensions(file_types):
    res = []
    for item in file_types:
        res += re.findall(r"\.\w+", item[1])
    print("ACCEPTED EXTENSIONS", res)
    return res
    #return [re.findall(r"\.\w+", item[1]) for item in file_types]

def add_extension(filename:str, extensions):
    if not filename:
        return filename
    check_passed = False
    candidate = ""
    for ext in extensions:
        if ext:
            if not candidate:
                candidate = ext
            if filename.endswith(ext):
                check_passed = True
                print("Extension check passed")
                break
    if not check_passed and candidate:
        print("Automatically added extension", candidate)
        filename = filename + candidate
    return filename


class Workspace(object):
    WORKSPACE_DIR = None

    def __init__(self, subspace):
        self.subspace = subspace

    def ensure_directory(self):
        if self.WORKSPACE_DIR:
            os.makedirs(ospath.join(self.WORKSPACE_DIR, self.subspace),exist_ok=True)
            return ospath.join(self.WORKSPACE_DIR, self.subspace)
        return None

    def _modify_kwargs(self, kwargs):
        cwd = self.ensure_directory()
        if cwd:
            kwargs["initialdir"] = cwd
            filetypes = []
            if "auto_formats" in kwargs.keys():
                for key in kwargs["auto_formats"]:
                    subdata = " ".join([f"*.{subkey}" for subkey in key.split(" ")])
                    locale_title = "_".join([subkey for subkey in key.split(" ")])
                    filetypes.append((get_locale(f'app.filedialog_formats.{locale_title}'),subdata))
                kwargs["filetypes"] = filetypes
                del kwargs["auto_formats"]

    def askopenfilename(self, *args, **kwargs):
        self._modify_kwargs(kwargs)
        return filedialog.askopenfilename(*args, **kwargs)

    def get_file(self, filename):
        cwd = self.ensure_directory()
        if cwd:
            filepath = os.path.join(cwd, filename)
            return filepath

    def askdirectory(self, *args, **kwargs):
        self._modify_kwargs(kwargs)
        return filedialog.askdirectory(*args, **kwargs)

    def asksaveasfilename(self, *args, **kwargs):
        self._modify_kwargs(kwargs)
        filename = filedialog.asksaveasfilename(*args, **kwargs)
        extensions = get_extensions(kwargs["filetypes"])
        filename = add_extension(filename, extensions)
        return filename

    def askopenfilenames(self, *args, **kwargs):
        self._modify_kwargs(kwargs)
        return filedialog.askopenfilenames(*args, **kwargs)

    @classmethod
    def initialize_workspace(cls, force=False):
        if ospath.isfile(CONF_PATH) and not force:
            with open(CONF_PATH, "r") as fp:
                cls.WORKSPACE_DIR = json.load(fp)["workspace"]
        else:
            messagebox.showinfo(
                title=get_locale("app.workspace_manager.greeter.title"),
                message=get_locale("app.workspace_manager.greeter.message")
            )
            workspace_dir = filedialog.askdirectory(initialdir=".",
                                                    title=get_locale("app.workspace_manager.askdir"))
            if not workspace_dir:
                workspace_dir = None
            with open(CONF_PATH, "w") as fp:
                json.dump({"workspace": workspace_dir}, fp)
            cls.WORKSPACE_DIR = workspace_dir
