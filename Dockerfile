FROM python
RUN pip install -U pip uvicorn

WORKDIR /app

COPY pyproject.toml pdm.lock README.md ./
COPY fastclam fastclam

RUN pip install .


CMD [ "uvicorn", "fastclam.app:app", "--host", "0.0.0.0" ]
