FROM python:3.9-bullseye
RUN apt-get update && apt-get install -y wkhtmltopdf fonts-thai-tlwg
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD gunicorn -b 0.0.0.0:$PORT main:app