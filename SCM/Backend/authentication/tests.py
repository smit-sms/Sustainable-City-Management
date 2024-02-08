from django.test import TestCase
from .models import User,Whitelist
from .views import *
from requests import get,post 


class UserTestCase(TestCase):
    test_use="sahil1"
    test_password="12345678"
    #need to change the test email after each test because the update test change the password and username associated to the email and so the get request won't get anything with the previous query
    test_email="sahil@te.ie"
    new_password="67891"
    new_username="Smarann"

    auth_test_use="JP"
    auth_test_password="mdp"
    auth_test_email="dragon123@tcd.ie"

    def test_signup(self):
        test_use=self.test_use
        test_password=self.test_password
        test_email=self.test_email
        
        whitelist_add=post('http://127.0.0.1:8000/authentication/whitelist',data={
            "email":test_email
        })
        signup_call=post('http://127.0.0.1:8000/authentication/signup',data={
            "username":test_use,
            "email":test_email,
            "password":test_password
        })
        user=post('http://127.0.0.1:8000/authentication/get',data={
            "username":test_use,
            "email":test_email,
            "password":test_password     
                  })
        dic=user.json()
        print(dic)
        print(signup_call.json())
        l=[dic["username"],dic["email"],dic["password"]]
        self.assertEqual([test_use,test_email,test_password],l)

    def test_authenticate(self):
        test_use=self.auth_test_use
        test_password=self.auth_test_password
        test_email=self.auth_test_email

        whitelist_add=post('http://127.0.0.1:8000/authentication/whitelist',data={
            "email":test_email
        })
        signup_call=post('http://127.0.0.1:8000/authentication/signup',data={
            "username":test_use,
            "email":test_email,
            "password":test_password
        })

        user=post('http://127.0.0.1:8000/authentication/authenticate',data={
        "username":test_use,
        "email":test_email,
        "password":test_password     
                })
        response=user.json()
        print(response)
        self.assertEqual("Successful login",response)

    def test_update(self):
        test_use=self.test_use
        test_password=self.test_password
        test_email=self.test_email

        update=post('http://127.0.0.1:8000/authentication/update',data={
        "username":test_use,
        "email":test_email,
        "password":test_password,
        "new_password":self.new_password,
        "new_username":self.new_username     
                })
        response=update.json()
        print(response)
        user=post('http://127.0.0.1:8000/authentication/get',data={
            "username":self.new_username,
            "email":test_email,
            "password":self.new_password     
                  })
        dic=user.json()
        print(dic)
        l=[dic["username"],dic["email"],dic["password"]]
        self.assertEqual([self.new_username,test_email,self.new_password],l)











        




