FROM python:3.8-buster
RUN apt update && apt install -y \
    tor \
    tesseract-ocr \
    tesseract-ocr-rus \
    libarchive
COPY torrc.default /etc/tor/torrc.default
RUN pip install poetry
WORKDIR /opt/ocr-bot
COPY pyproject.toml poetry.lock ./
RUN cd /opt/ocr-bot && poetry install --no-root
COPY . . 
RUN poetry install
CMD service tor start && poetry run python ocr_bot/bot.py