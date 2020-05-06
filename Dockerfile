FROM alpine:3.10

COPY entrypoint.sh /entrypoint.sh
COPY main.py /main.py

ENTRYPOINT ["/entrypoint.sh"]
