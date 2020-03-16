# Cadete Helpers


def get_all_dates(operations):
    lista_loca = []
    for operation in operations:
        if operation["updated_at"] not in lista_loca:
            lista_loca.append(operation["updated_at"])
    return lista_loca


def fill_global(el):
    nuevo_dict = {"data": {}}
    for key, value in el.items():
        if key.find("data_") >= 0:
            nuevo_dict["data"].update({key[5:]: value})
        else:
            nuevo_dict.update({key: value})
    return nuevo_dict


def fill_mail(bank):
    bank["via"] = "mail"
    return bank


def fill_francos(bank, francos):
    bank["data"].update({"days_off": francos})
    return bank


def fill_bank(bank):
    bank["enabled"] = True
    bank["config_type"] = "bank_configuration"
    bank["masked"] = True
    return bank


def fill_pago_voluntario(bank):
    bank["data"].update({"query_params": ["distributionMail=pv_cashin.arg@wenance.com"]})
    return bank


def fill_web(bank):
    bank["via"] = "web"
    return bank


def fill_ftp(bank):
    bank["via"] = "ftp"
    return bank


def paises():
    return (("AR", "Argentina"),
            ("UR", "Uruguay"))


def dias_de_la_semana():
    return (("Monday", "Lunes"),
            ("Tuesday", "Martes"),
            ("Wednesday", "Miércoles"),
            ("Thursday", "Jueves"),
            ("Friday", "Viernes"),
            ("Saturday", "Sábado"),
            ("Sunday", "Domingo"))


def companies():
    return (("wenance", "Wenance"),
            ("creditos_al_rio", "Créditos al río"))

