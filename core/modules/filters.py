class RequestFilter:

    # Filtros
    # Recibe un proveeodr, usuario y caracter para concatenar y devuelve un string con el filtro adecuado
    # privider: String = Nombre del proveedor
    # user: Request.User = Usuario actual
    # concat_char: String = Caracter a usar para concatenar al request param ('?' o '&')
    @staticmethod
    def filtrar(provider, user, concat_char):
        getattr(RequestFilter, "filtro_{}".format(provider))(user, concat_char)

    @staticmethod
    def filtro_middleware(user, concat_char):
        if not user.is_superuser and user.has_perm('core.company_car'):
            return "{}companyCode=creditoalrio".format(concat_char)
        if not user.is_superuser and user.has_perm('core.company_wenance'):
            return "{}companyCode=welp".format(concat_char)
        return ""

    @staticmethod
    def filtro_cadete(user, concat_char):
        if user.is_superuser:
            return ""
        if user.has_perm('core.company_wenance'):
            return "{}company=wenance".format(concat_char)
        if user.has_perm('core.company_car'):
            return "{}company=creditos_al_rio".format(concat_char)
