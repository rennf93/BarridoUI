##  Quickstart ##

### Install VirtualEnv
> sudo apg-get install virtualenv

### Create enviroment
> virtualenv --python=/usr/bin/python3.6 ENV

### Install recquired libreries
> sudo apt install mysql-client

> sudo apt-get install libmysqlclient-dev

> sudo apt-get install python3.6-dev

> sudo apt-get install gcc

### Activate enviroment
> source ENV/bin/activate

### Install dependencies
> barrido-ui/pip install --upgrade -r requirements.txt

### Edit /barrido-ui/barridoUI/local_settings.py.example
Remove ".example" from the extention.
Edit DB pass.



```python

import os                      

# Possible values (random, car)
APP_COMPANY = "random"

# Remove tag if neccesary.
# DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database                                            
DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.sqlite3',
       'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
   }
}

MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = "3306"
MYSQL_USER = "root"
MYSQL_PASSWORD = "" # password correspondiente a la DB local


# celery
# CELERY_TASK_ALWAYS_EAGER = True

# Mambu
MAMBU_API_ENDPOINT_BACKUP = "https://wenance.sandbox.mambu.com/api/database/backup/LATEST"
MAMBU_API_GENERATE_SNAPSHOT = "https://wenance.sandbox.mambu.com/api/database/backup"
MAMBU_API_AUTHORIZATION = "AUTH_TOKEN_HERE"

# Core-Barrido
CORE_BARRIDO_URL = "http://localhost:8082/core-barrido/api/v1"
CORE_BARRIDO_API_TOKEN = "AAA"

COMPANY_CUIT = "30123456789"
COMPANY_NAME = "Wenance SA"

# Cadet
CADETE_URL = "http://inframambu-251935327.us-east-2.elb.amazonaws.com/cadete/api/v1"

# Core-Middleware
CORE_MIDDLEWARE_URL = "http://localhost:8080/core-mw/api/v2"
CORE_MIDDLEWARE_API_AUTH_TOKEN = "A"

# Core-Middleware CashIn
CORE_MIDDLEWARE_CASHIN_URL = "http://localhost:8080/core-mw/api/v2"
CORE_MIDDLEWARE_CASHIN_API_AUTH_TOKEN = "A"

# Notification
NOTIFICATION_URL = "http://notifications-dev.fintechpeople.io"
NOTIFICATION_GENERIC_TO = "e******.z****@w******.com"

```
### Environment config

|Key|Value|Environment|
|---|---|---|
|CORE_MIDDLEWARE_URL|http://inframambu-251935327.us-east-2.elb.amazonaws.com/core-mw/api/v2/|DEV|
|CORE_MIDDLEWARE_API_AUTH_TOKEN|MjAxODA3MzFfZW52PXN0YWdpbmc=|DEV|
|CORE_BARRIDO_URL|http://anyHTTPurl/|DEV|

### Migrate Django data
./manage.py migrate

### Django Superuser
python manage.py createsuperuser
password: asdasdasd (default)

### Iniciate the server
./manage.py runserver

### URLs
[Admin Site](http://localhost:8000/admin)
[Site](http://localhost:8000)

### Query references

- [Update cartera activa](#update-cartera-activasql)
- [Update cartera activa columns](#update-cartera-activa-columnssql)
- [Update salary -> cartera activa](#update-cartera-salarysql)

#### update-cartera-activa.sql

1. {0} base de datos barrido
2. {1} base de datos barrido ui
3. {2} tabla cartera activa (cartera_activa_#)

#### update-cartera-activa-columns.sql

1. {0} tabla cartera activa (cartera_activa_#)

#### update-cartera-salary.sql

1. {0} base de datos
2. {1} tabla cartera activa (cartera_activa_#)
2. {2} tabla salary

#### update-cartera-activa-csv.sql

1. {0} tabla cartera activa (cartera_activa)

#### update-cartera-activa-cobranzas-csv.sql

1. {0} tabla cartera activa (cartera_activa)



### Components

- [Tabber](#tabber)
- [Stepper](#stepper)
- [Editable Span](#editable-span)
- [Actions Dropdown](#actions-dropdown)
- [Boolean Icon](#boolean-icon)

#### Tabber

This component allows you to create tabs dinamically: it gets an array from TabberTab and render them.

Tabber Tab:

    Attributes:
        name (str): Text in the tab
        enabled (Boolean): Whether it's enabled/disabled
        active (bool): Whether the tab is active or not
        link (str): Where the tab should lead us to

##### Example:

###### BACK

```python

context["tabs"] = tabs [TabberTab("Nombre", True, True, '#')]

```

###### FRONT

```djangotemplate

{% include "components/tabber.html" with tabs=tabs %}

```

[Volver a componentes](#componentes)

#### Stepper

Special Tabber including a progress bar as a Wizard. Takes 2 objects: an array from TabberTabs and a ProgressBar

    Attributes:
        value (int): [0 - 100] ProgressBar value from 0-100
        enabled (bool): Either if it's enabled or not


##### Example

###### BACK

```python
steps = [TabberTab("Banco", True, True, "#"),
         TabberTab("Datos", False, False, "#"),
         TabberTab("Finalizar", False, False, "#")]
context["stepper_header"] = StepperHeader(progress_Bar=ProgressBar(0, True), steps=steps)

```

###### FRONT

```djangotemplate

{% include "components/stepper_header.html" with data=stepper_header %}

```

[Volver a componentes](#componentes)

#### Editable Span

Span that converts into an  input sending a POST with JSON of the edited element.

El usuario puede hacer click en el span que se convertirá en un input. Then we could modify the input and accept clicking on the check or cancel clicking the cross.

When the request is sent, the screen will show the response: Green for positive, Red for negative.

##### Ejemplo

###### BACK

```python

# ViewModel / ViewClass
# Template must take these variables:

context["action"] = './../update' # Endpoint to the request
context["id"] = self.kwargs.get("configuration_id") # Object ID to be modified

```

###### FRONT

```djangotemplate

 The template is included from editable_span to wherever it's required + scripts to make the request.
 Include must receive the variables: name (of the parameter to be modified), value, action= destiny and the id of the element.


    {% include "components/editable_span.html" with value=config_detail.version name='version' action=action id=id %}

    <script src="{% static "js/components/templates.js" %}"></script>
    <script src="{% static "js/components/editable_span.js" %}"></script>

```

Implementations are at: /templates/cadete/configurations_detail/edit.html

##### Capture the object:

The object has 2 names/attributes: parameter and value. This way, both values can be captured to be sent by the backend to the desired service.

###### EXAMPLE

```python
    data = {
        request.POST['parameter']: value=request.POST['value']
    }
```

*Nda: EditableSpan if an external service is needed, Django will normalize the object to be sent.*

[Volver a componentes](#componentes)

#### Actions Dropdown

The button turns into a dropdown in case we need to include more actions.

##### Example

###### BACK
```python
# ViewModel
# Context is added to the element table_actions: an array of ActionButton
from core.modules.components import ActionButton
context["table_actions"] = []
context["table_actions"].append(ActionButton("Detalles", "operations_detail", ""))

# View
# ActionsDropdown is included in the template which the element_id is sent.
# dropdown_actions the array of ActtionButton previously loaded.

```

###### FRONT

```djangotemplate

{% include "components/actions_dropdown.html" with element_id=config.id dropdown_actions=table_actions %}

```

[Volver a componentes](#componentes)

#### Boolean Icon

Font Awesome icon for true/false.

##### Example

```djangotemplate
# value (To be interpreted)
{% include "components/boolean_icon.html" with value=bank.cashoutAvailable %}

```

[Volver a componentes](#componentes)
[Volver al inicio](#quickstart)
....
