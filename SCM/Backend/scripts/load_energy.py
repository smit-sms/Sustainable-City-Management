import csv
from cityservices.models import SA_energy_consumption

def run():
    fhand = open('cityservices/data/Dublin_Energy_dataset.csv')
    reader = csv.reader(fhand)
    next(reader) # skip the 1st row

    # Empty the tables to repopulate them.
    SA_energy_consumption.objects.all().delete()

    for row in reader:
        data_row = SA_energy_consumption(SA_code=row[1], Energy_use=row[2], Energy_cost=row[3], Total_Floor_Area=row[4], Small_Area_Name=row[5])
        data_row.save()
    print("Successfully loaded the energy data.")
