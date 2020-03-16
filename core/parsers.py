from dateutil import parser


def datetime_parser(dict_object):
    for key, value in dict_object.items():
        try:
            if len(str(value)) > 6:
                dict_object[key] = parser.parse(value)
        except Exception:
            pass
    return dict_object
