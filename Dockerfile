FROM python:3.9-slim
RUN apt-get update && apt-get install -y wkhtmltopdf
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 10000
CMD ["gunicorn", "-b", "0.0.0.0:10000", "main:app"]