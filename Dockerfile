FROM python:3.9-buster

RUN apt update
RUN apt install procinfo

WORKDIR /podda

ADD ./requirements.txt /podda/requirements.txt
RUN pip install -r requirements.txt

ADD . /podda

ENTRYPOINT ["python", "bot.py"]