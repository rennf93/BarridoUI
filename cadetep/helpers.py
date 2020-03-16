from barridoUI import settings


def allowed_tenants():
    if settings.APP_COMPANY == 'wenance':
        return [
            ("wenance-ar", "wenance-ar"),
            ("wenance-es", "wenance-es")
        ]
    elif settings.APP_COMPANY == 'car':
        return [
            ("creditosalrio-ar", "creditosalrio-ar")
        ]
    else:
        return []
