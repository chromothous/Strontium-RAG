FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY . /build/

RUN mkdir -p /install \
    && if [ -f requirements.txt ]; then pip install --prefix=/install -r requirements.txt; fi

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TMPDIR=/container/tmp

WORKDIR /container/app

RUN groupadd --gid 10001 strontium \
    && useradd --uid 10001 --gid 10001 --create-home --home-dir /home/strontium --shell /usr/sbin/nologin strontium \
    && mkdir -p /container/config /container/data /container/tmp \
    && chown -R 10001:10001 /container/data /container/tmp /home/strontium \
    && chmod 700 /container/tmp

COPY --from=builder /install/ /usr/local/

COPY --from=builder --chown=10001:10001 /build/main.py /container/app/main.py
COPY --from=builder --chown=10001:10001 /build/classes/ /container/app/classes/
COPY --from=builder --chown=10001:10001 /build/constants/ /container/app/constants/
COPY --from=builder --chown=10001:10001 /build/testing/ /container/app/testing/
COPY --from=builder --chown=10001:10001 /build/services/ /container/app/services/
COPY --from=builder --chown=10001:10001 /build/api/ /container/app/api/
COPY --from=builder --chown=10001:10001 /build/security/ /container/app/security/
COPY --from=builder --chown=10001:10001 /build/configuration/ /container/app/configuration/

RUN chmod -R a-w /container/app

USER 10001:10001

CMD ["python", "main.py"]