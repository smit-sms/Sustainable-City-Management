from django.views import View
from django.http import JsonResponse
from .models import SA_energy_consumption
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class SA_energy(View):
    
    response_message = ''
    response_status = 200
    response_data = []

    def get(self,request):
        small_area_code = request.GET.get('small_area_code')
        SA_db_obj = SA_energy_consumption.objects.filter(SA_code=small_area_code).first() # get requested small_area for the small_area table in the DB
        if (SA_db_obj != None): # if requested small area code does exist, then ...
            try: # try to fetch data from the database.
                self.response_data = list(SA_energy_consumption.objects.filter(id=SA_db_obj.id).values()) # return data of requested Small_area only
                self.response_message = f'Success. Data fetched from the DB for the small_area {small_area_code}.'
                self.response_status = 200
            except Exception as e: # if there was some error with fetching data then ...
                print(e)
                self.response_message= f'Failure. Could not fetch data from the DB for the small_area {small_area_code}.'
                self.response_status = 400
        else: # if requested small_area does not exist, then ...
            self.response_data = []
            self.response_status = 400
            self.response_message = f'Failure. Invalid small_area {small_area_code}.'
    
        #Return response.
        return JsonResponse({'message': self.response_message, 'data': self.response_data}, status=self.response_status, safe=True)
