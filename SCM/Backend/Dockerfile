FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.in /app/requirements.in

RUN pip install pip-tools
# generating requirements.txt from requirements.in file
RUN pip-compile
# installing requirements inside container
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Make sure the scripts are executable
RUN chmod +x /app/run_services.sh
RUN chmod +x /app/scripts/dublin_bikes_pipeline.py

EXPOSE 8000 8003

CMD ["./run_services.sh"]
