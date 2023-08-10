from ...common_GUI.settings_frame import SettingMenu, DoubleValue, ComboboxValue, CheckboxValue, IntValue, EntryValue
from ...localization import get_locale

def build_menu(menu: SettingMenu):
    menu.add_setting(ComboboxValue, "lightcurve", get_locale("app.popup_plot.lightcurve"),"Off",
                     options=["Off", "All", "Selected"], sensitive=True)
    menu.add_setting(IntValue, "lightcurve_ma", get_locale("app.popup_plot.lightcurve_ma"), 1)
    menu.add_setting(CheckboxValue, "lightcurve_mean", get_locale("app.popup_plot.lightcurve_mean"), False, sensitive=True)
    menu.add_setting(CheckboxValue, "lightcurve_median_offset", get_locale("app.popup_plot.lightcurve_median_offset"), False, sensitive=True)
    menu.add_setting(CheckboxValue, "lightcurve_suppress_negative", get_locale("app.popup_plot.lightcurve_suppress_negative"), False, sensitive=True)
    menu.add_setting(CheckboxValue, "show_pixels", get_locale("app.popup_plot.show_pixels"), True, sensitive=True)
    menu.add_setting(IntValue, "tick_label_size", get_locale("app.popup_plot.tick_label_size"),10)
    menu.add_setting(EntryValue, "title", get_locale("app.popup_plot.title"),"")
    menu.add_setting(EntryValue, "x_label", get_locale("app.popup_plot.x_label"),"")
    menu.add_setting(EntryValue, "y_label", get_locale("app.popup_plot.y_label"),"")
    menu.add_setting(DoubleValue, "threshold", get_locale("app.popup_plot.threshold"), 3.5)