from .preset_base_class import PresetBaseClass


class DefaultPreset(PresetBaseClass):

    def get_delimiter(self) -> str:
        return ','

    def get_decimal(self) -> str:
        return '.'

    def get_index_col(self) -> int:
        return 0

    def get_quotechar(self) -> str:
        return '"'
