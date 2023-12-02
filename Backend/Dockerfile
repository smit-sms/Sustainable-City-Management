FROM python:3.9

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

EXPOSE 8080
CMD python manage.py makemigrations; python manage.py migrate; python manage.py runserver 0.0.0.0:8080
