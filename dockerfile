FROM tiangolo/uwsgi-nginx-flask:flask

COPY requirements.txt /tmp/

COPY . /tmp/Primers/

COPY resources/primers.db /resources/

RUN pip install -U pip
RUN pip install -r /tmp/requirements.txt

COPY ./app /app

WORKDIR /tmp/Primers

RUN python setup.py install

WORKDIR /app

ENV MESSAGE "Primers is running..."
