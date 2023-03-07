FROM python

WORKDIR /app

COPY ./pyproject.toml .
COPY ./README.md .
COPY ./fastclam /app/fastclam

RUN pip install . uvicorn


CMD [ "uvicorn", "fastclam.app:app", "--host", "0.0.0.0" ]
