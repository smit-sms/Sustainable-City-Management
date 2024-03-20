import csv
from bikes.models import Station

def run():
    fhand = open('bikes/data/stations.csv')
    reader = csv.reader(fhand)
    next(reader) # skip the 1st row

    # Empty the tables to repopulate them.
    Station.objects.all().delete()

    for row in reader:
        print(row)
        m = Station(
            id=int(row[0]), 
            name=row[1],
            latitude=float(row[2]), 
            longitude=float(row[3])
        )
        m.save()