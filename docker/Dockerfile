FROM docker:27-cli

RUN apk add --no-cache python3 py3-pip
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x /app/docker/entrypoint.sh

EXPOSE 8000

CMD ["/app/docker/entrypoint.sh"]
