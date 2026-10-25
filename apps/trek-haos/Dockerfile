ARG BUILD_FROM
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
