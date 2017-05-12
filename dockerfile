FROM tiangolo/uwsgi-nginx-flask:flask

COPY requirements.txt /tmp/

COPY . /tmp/PerformanceSummary/

COPY resources/performance.db /resources/

RUN pip install -U pip
RUN pip install -r /tmp/requirements.txt

COPY ./app /app

WORKDIR /tmp/PerformanceSummary

RUN python setup.py install

WORKDIR /tmp

RUN apt-get install git

RUN git clone https://github.com/sch-sdgs/SDGSCommonLibs.git

WORKDIR /tmp/SDGSCommonLibs

RUN git checkout master

RUN pip install -r requirements.txt

RUN python setup.py install

WORKDIR /app

ENV MESSAGE "PerformanceSummary is running..."
