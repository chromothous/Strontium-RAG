FROM python:3-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN groupadd --system --gid 10001 strontium \
    && useradd --system --uid 10001 --gid strontium \
        --home-dir /nonexistent \
        --shell /usr/sbin/nologin \
        strontium \
    && mkdir -p /container/app \
        /container/config \
        /container/data \
        /container/tmp \
    && chown 10001:10001 /container/data /container/tmp \
    && chmod 0555 /container/config \
    && chmod 0750 /container/data /container/tmp

WORKDIR /container/app

COPY --chown=root:root classes/ ./classes/
COPY --chown=root:root constants/ ./constants/
COPY --chown=root:root testing/ ./testing/
COPY --chown=root:root services/ ./services/
COPY --chown=root:root api/ ./api/
COPY --chown=root:root security/ ./security/
COPY --chown=root:root configuration/ ./configuration/
COPY --chown=root:root main.py ./main.py

RUN chmod -R a-w /container/app \
    && chmod 0555 /container

USER 10001:10001

CMD ["python", "main.py"]