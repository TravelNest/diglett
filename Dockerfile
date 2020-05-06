FROM python:3-slim AS builder

#COPY entrypoint.sh /entrypoint.sh
COPY main.py /main.py
COPY diglett.py /diglett.py

ENTRYPOINT ["python", "/main.py"]
