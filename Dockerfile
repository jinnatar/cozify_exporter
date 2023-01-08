FROM python:3.11.0a3-bullseye AS poetry_builder
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python -

FROM poetry_builder as builder
RUN mkdir /build
WORKDIR /build
COPY cozify_exporter ./cozify_exporter
COPY poetry.lock pyproject.toml ./
RUN poetry build -f wheel

FROM python:3.12.0a3-slim-bullseye
WORKDIR /srv
COPY --from=builder /build/dist/*.whl ./
RUN pip install *.whl

ENTRYPOINT ["cozify_exporter"]
