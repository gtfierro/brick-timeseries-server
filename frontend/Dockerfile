FROM python:3.10

RUN mkdir -p /opt/frontend
ADD pyproject.toml /opt/frontend
ADD poetry.lock /opt/frontend
WORKDIR /opt/frontend

RUN pip install poetry==1.4.0
RUN poetry install --no-dev
ADD app.py /opt/frontend
ENTRYPOINT poetry run uvicorn app:app --host 0.0.0.0
