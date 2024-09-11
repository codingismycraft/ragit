FROM python:3.10

WORKDIR /ragit

COPY ragit/backend /ragit/backend
COPY ragit/libs /ragit/libs
COPY requirements.txt /ragit

RUN pip3 install --no-cache-dir -r /ragit/requirements.txt

ENV PYTHONPATH="/"

CMD ["python3.10", "/ragit/backend/ragit_cmd.py"]
