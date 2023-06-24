from ..common_GUI.tk_forms_assist import IntNode, FloatNode, StringNode, BoolNode
from multiprocessing import cpu_count
from .form_parts import LocaleSelection, ColormapSetting

PARAMETERS_DEFINITION = [
    ["MAIN_LATITUDE", FloatNode, 68.607279],
    ["MAIN_LONGITUDE", FloatNode, 31.803085],

    ["PIXEL_SIZE", FloatNode, 2.85],
    ["HALF_GAP_SIZE", FloatNode, 2.0],
    ["HALF_PIXELS", IntNode, 8],
    ["APERTURE", FloatNode, 19.6e2],

    ["PLOT_COLORMAP", ColormapSetting, "viridis"],
    ["PLOT_BROKEN_COLOR", StringNode, "black"],
    ["PLOT_HIGHLIGHT_COLOR", StringNode, "red"],

    ["NPROC", IntNode, cpu_count()],

    ["LOCALE", LocaleSelection, "en"],

    ["SCALE_FLOATING_POINT_FORMAT", StringNode, "{:.2f}"],
    ["DATETIME_FORMAT", StringNode, "%Y-%m-%d %H:%M:%S"],
]

def add_parameters(*args):
    for arg in args:
        PARAMETERS_DEFINITION.append(arg)

def get_defaults():
    return {item[0]: item[2] for item in PARAMETERS_DEFINITION}