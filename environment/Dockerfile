FROM python:3.11.5-bookworm
ENV HOST=0.0.0.0
ENV LISTEN_PORT 8000
EXPOSE 8000
COPY ./ /app
WORKDIR /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt
CMD ["chainlit", "run", "--port", "8000", "app.py"]