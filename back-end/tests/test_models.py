from django.test import TestCase
from swap.models import *
from security.models import *

class UserTest(TestCase):
    def setUp(self):
        user1 = User.objects.create(
            username='username1', first_name='fname1', last_name='lname1',
            ip_address = '127.0.0.1', user_agent='user_agent1', blocked_user=False
        )
        user2 = User.objects.create(
            username='username2', first_name='fname2', last_name='lanem2',
            ip_address = '127.0.0.1', user_agent='user_agent2', blocked_user=True
        )
    
    def test_block_status(self):
        user1 = User.objects.get(username='username1')
        user2 = User.objects.get(username='username2')
        self.assertTrue(user1.blocking_user())
        self.assertFalse(user2.unblocking_user())
    
    def test_str(self):
        user1 = User.objects.get(username='username1')
        user2 = User.objects.get(username='username2')
        self.assertEqual(user1.__str__(), 'username1')
        self.assertEqual(user2.__str__(), 'username2')
