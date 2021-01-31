FROM python:3.9-buster

RUN apt update
RUN apt install procinfo

WORKDIR /podda

COPY . .
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]