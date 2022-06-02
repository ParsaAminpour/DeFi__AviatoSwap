from bs4 import BeautifulSoup as bs
from django.test import TestCase
from rest_framework import status
from swap.models import User
from rest_framework import status

class ViewTests(TestCase):
    def test_signup(self):
        response = self.client.get('/signup')
        soup = bs(response.content, 'html.parser')
        data = soup.select('#title')[0].string.strip()
        self.assertEqual(data, 'Registration')
    
    def test_signup2(self):
        new_user1 = {
            'username' : 'user4' , 'email' : 'user4@gmail.com',
            'password1' : 'thisistestpasswordforuser4', 'password2' : 'thisistestpasswordforuser4'
        }
        unconfirmation_password = {
            'username' : 'user5', 'password1' : 'password',
            'email' : 'user5@gmail.com', 'password2':'password'
        }
        test1 = self.client.post('/signup/', data=new_user1)
        test2 = self.client.post('/signup/', data=unconfirmation_password)
        
        self.assertEqual(test1.url, '/login/')
        self.assertEqual(test2.status_code, 200)



    def test_login(self):
        response = self.client.get('/login/')
        soup = bs(response.content, 'html.parser')
        logotxt = soup.select('#logotxt')[0].string.strip()
        self.assertEqual(logotxt, 'AVIATO')

    def test_login2(self):
        unregistered_user = {
            'username' : 'user', 'password' : 'password'
        }

        registered_data = {
            'username' : 'user3', 'password' : 'thisistestpasswrod'
        }

        test1 = self.client.post('/login/', data=unregistered_user)
        test2 = self.client.post('/login/', data=registered_data)

        self.assertEqual(test1.status_code, 403)
        self.assertEqual(test2.status_code, 200)
