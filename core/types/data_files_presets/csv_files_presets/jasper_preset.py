from ..csv_files_presets.default_preset import DefaultPreset


class JasperPreset(DefaultPreset):

    def get_delimiter(self):
        return '|'
