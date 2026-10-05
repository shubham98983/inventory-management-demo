FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
# gunicorn 20.x imports pkg_resources, which Python 3.12 images no longer ship
RUN pip install --no-cache-dir "setuptools<81" -r requirements.txt

COPY . .

ENV INVENTORY_DB=/data/inventory.db \
    INVENTORY_BACKUP_DIR=/data/backups
RUN mkdir -p /data
VOLUME /data
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["sh", "-c", "python -m scripts.init_db && gunicorn --bind 0.0.0.0:5000 --workers 2 run:app"]
