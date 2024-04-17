import csv
from sensors.models import Sensor

def run():
    print("Adding sensors to database from CSV file...", end="")
    fhand = open('sensors/data/sensors.csv')
    reader = csv.reader(fhand)
    next(reader) # skip the 1st row

    # Empty the tables to repopulate them.
    Sensor.objects.all().delete()

    # monitor
    # DCC-AQ2
    # DCC-AQ3
    # DCC-AQ4
    # ...

    for row in reader:
        # print(row)
        m = Sensor(serial_number=row[0], latitude=float(row[1]), longitude=float(row[2]), sensor_type=row[3])
        m.save()
    print("Done")
