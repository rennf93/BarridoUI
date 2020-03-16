from abc import ABCMeta, abstractmethod


class ComponentBaseClass(metaclass=ABCMeta):
    """ ComponentsBaseClass
        Attributes:
             template (str): Ubicación del template
    """
    def __init__(self, template):
        self.template = template

    def get_template(self) -> str:
        """
        Returns:
            String con el nombre del template
        """
        return self.template


class KeyValueBaseClass(ComponentBaseClass):
    @abstractmethod
    def __init__(self, clave, valor, template):
        self.clave = clave
        self.valor = valor
        super().__init__(template)


class ActionButton:
    """ Action Button
        Attributes:
            title (str): Nombre que se mostrará
            method (str): Action hacia donde dirigirá el botón
            icon (str): Nombre de fa-icons ejemplo: "fa-edit"
                (default is "")
    """
    def __init__(self, title, method, icon="", params=""):
        self.title = title
        self.method = method
        self.icon = icon
        self.params = params


# Editable Button
# Modelo del componente EditableButton
# name: String = Nombre del elemento que se volverá key del request
# value: String/Number = Valor inicial del elemnto
# action: Url hacia donde enviará el request
# id: Id del elemento a editar
class EditableSpan:
    def __init__(self, name, value, action, element_id):
        self.name = name
        self.value = value
        self.action = action
        self.id = element_id


class Tabber:
    """ Constructor de tabs
    Attributes:
        tabber_tabs (TabberTabs[]): Array de tabs
    """
    def __init__(self, tabber_tabs):
        self.tabber_tabs = tabber_tabs


class TabberTab:
    """ Stepper step
    Attributes:
        name (str): Texto a mostrar en tab
        enabled (Boolean): Si está o no habilitado el tab
        active (bool): Si es o no el tab activo
        link (str): Hacia donde dirige el tab
    """
    def __init__(self, name, enabled, active, link):
        self.name = name
        self.enabled = enabled
        self.active = active
        self.link = link


class ProgressBar:
    """ ProgressBar
    Attributes:
        value (int): [0 - 100] Qué tan avanzada está la barra de progreso, del 0 al 100
        enabled (bool): Si está o no habilitada
    """
    def __init__(self, value, enabled):
        self.value = value
        self.enabled = enabled


class StepperHeader:
    """ StepperHeader (AKA wizard)
    Attributes:
        steps (TabberTab[]): Array de TabberTabs, se usan para definir los pasos del stepper.
        progress_bar (ProgressBar): Barra de progreso.
    """
    def __init__(self, steps, progress_bar):
        self.steps = steps
        self.progress_bar = progress_bar


class AccordionListItem(ComponentBaseClass):
    """ ActionNav Ítem para usar dentro de un nav
    Attributes:
        items (list(ListItem)): Lista de ListItems, los elementos que contiene el acordeón.
        title (str): Título del acordeón.
    """
    def __init__(self, items, title, icon):
        self.items = items
        self.title = title
        self.icon = icon
        super().__init__('components/accordion_list_item.html')


class AccordionSecondLevelListItem(ComponentBaseClass):
    """ ListItem: ul con link
    Attributes:
        title (str): Texto a mostrar
        link (str): Url hacia donde ir
    """
    def __init__(self, title, link, args):
        self.title = title
        self.link = link
        self.args = args
        super().__init__('components/accordion_second_level_list_item.html')


class DataBlock(ComponentBaseClass):
    def __init__(self, size, items):
        self.size = size
        self.items = items
        super().__init__('components/data_block.html')


class DataItem(KeyValueBaseClass):
    def __init__(self, clave, valor):
        super().__init__(clave, valor, 'components/data_item.html')
