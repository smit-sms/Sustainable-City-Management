from datetime import datetime, timedelta
from sensors.models import Sensor, Air, Noise
import pytz
import csv
import random


def run():
    print("Adding sensors and their data to database from CSV files... ", end="")
    f_sensor = open('sensors/data/sensors.csv')
    reader_sensor = csv.reader(f_sensor)
    next(reader_sensor)

    # Empty the tables to repopulate them.
    Air.objects.all().delete()
    Noise.objects.all().delete()
    Sensor.objects.all().delete()

    timezone = pytz.timezone('GMT')

    for row in reader_sensor:
        sensor = Sensor(serial_number=row[0], latitude=float(
            row[1]), longitude=float(row[2]), sensor_type=row[3])
        sensor.save()

        timezone_aware_datetime = timezone.localize(datetime.now(
        )-timedelta(hours=random.randint(0, 3), minutes=random.randint(0, 59)))

        if (sensor.sensor_type == "air"):
            Air.objects.create(pm2_5=round(random.uniform(
                0, 10), 3), datetime=timezone_aware_datetime, sensor=sensor)
        else:
            Noise.objects.create(
                datetime=timezone_aware_datetime, sensor=sensor, laeq=round(random.uniform(30, 65), 2))
    f_sensor.close()
    print("Done")
