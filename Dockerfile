FROM python:3-slim AS builder

COPY requirements.txt /requirements.txt
COPY main.py /main.py
COPY diglett.py /diglett.py

RUN pip install -r /requirements.txt

ENTRYPOINT ["python", "/main.py"]
