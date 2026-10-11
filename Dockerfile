FROM python:3-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV TMPDIR=/container/tmp

WORKDIR /container/app

RUN groupadd --system --gid 10001 strontium \
    && useradd --system --uid 10001 --gid 10001 --create-home --home-dir /home/strontium --shell /usr/sbin/nologin strontium \
    && mkdir -p /container/config /container/data /container/tmp \
    && chown -R 10001:10001 /container/data /container/tmp /home/strontium \
    && chmod 700 /container/tmp

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY --chown=root:root main.py ./main.py
COPY --chown=root:root classes/ ./classes/
COPY --chown=root:root constants/ ./constants/
COPY --chown=root:root testing/ ./testing/
COPY --chown=root:root services/ ./services/
COPY --chown=root:root api/ ./api/
COPY --chown=root:root security/ ./security/
COPY --chown=root:root configuration/ ./configuration/

RUN chmod -R a-w /container/app

USER 10001:10001

CMD ["python", "main.py"]