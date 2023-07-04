from ..common_GUI import TkDictForm
from .controls import TkFormControlPanel
class SaveableTkDictForm(TkDictForm):
    def __init__(self, master, tk_form_configuration, use_scrollview=True, color_index=0, file_asker=None,
                 save_label="app.filedialog.save_settings.title", load_label="app.filedialog.load_settings.title"
                 ):
        super().__init__(master, tk_form_configuration, use_scrollview, color_index)
        control_panel = TkFormControlPanel(self, file_asker=file_asker, save_label=save_label, load_label=load_label)
        control_panel.connect_form(self)
        control_panel.pack(side="bottom",fill="x")