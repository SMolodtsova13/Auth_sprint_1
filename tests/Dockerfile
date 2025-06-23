FROM python:3.11

WORKDIR /tests

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["pytest"]