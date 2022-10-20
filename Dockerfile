FROM python:3.9.14

WORKDIR /srv

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

CMD "./start.sh"