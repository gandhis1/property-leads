FROM python:3.10-slim

USER root
RUN apt-get update && apt-get -y upgrade

RUN useradd --create-home nonroot
USER nonroot

ENV VIRTUAL_ENV=/home/nonroot/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /home/nonroot/src/property-leads

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install wheel build

COPY --chown=nonroot ./ ./
RUN python -m build --wheel
RUN pip install dist/*

ENTRYPOINT [ "python", "-m", "property_leads" ]
