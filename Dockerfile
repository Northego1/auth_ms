FROM python:3.12.3-slim

COPY reqs.txt reqs.txt

RUN pip install --no-cache-dir -r reqs.txt

COPY . .

