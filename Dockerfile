FROM wenance/python-nr-vault:latest


LABEL maintainer="orlando.jimenez@wenance.com"
LABEL collaborator="gustavo.ghioldi@wenance.com"

RUN apk --no-cache add python build-base python-dev \
        mariadb-dev linux-headers musl-dev \
        p7zip mysql-client
WORKDIR /srv/src/
ADD requirements.txt /srv/src/
# Se agrega esta línea por un downgrade de panda a la v0.22.0 por un problema desconocido...
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN pip install -r requirements.txt
COPY . /srv/src/
COPY entrypoint.sh /docker-entrypoint-init.d
VOLUME ["/srv/src/static", "/srv/src/media"]
EXPOSE :9090
CMD ["uwsgi", "--ini", "/srv/src/conf/uwsgi/uwsgi.ini"]
