ARG BUILD_FROM=mauriceboe/trek:5.2.0
FROM $BUILD_FROM

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 sqlite3 && \
    rm -rf /var/lib/apt/lists/*

COPY run.sh /run.sh
COPY sync.py /sync.py
RUN chmod a+x /run.sh

ENTRYPOINT ["dumb-init", "--"]
CMD ["/run.sh"]
