def convert_columns_into_types_dict(tipo, columns):
    types_dict = dict()
    for column in columns:
        types_dict.update({column: tipo})
    return types_dict
