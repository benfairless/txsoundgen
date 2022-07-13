FROM python:3.10.5-alpine

COPY dist/txsoundgen*.whl /tmp/
RUN pip install /tmp/txsoundgen*.whl
