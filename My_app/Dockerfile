FROM python:3.8-alpine
WORKDIR /ret-invc
ADD . /ret-invc

RUN set -e; \
        apk add --no-cache --virtual .build-deps \
                gcc \
                libc-dev \
                linux-headers \
                mariadb-dev \
                python3-dev \
                postgresql-dev \
        ;
COPY requirements.txt /ret-invc
RUN pip install -r requirements.txt
CMD ["python","my_app.py"]