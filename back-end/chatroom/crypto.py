from cryptography.fernet import Fernet
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

class Crypto:
	def __init__(self):
		self.key = Fernet.generate_key()

	def encrypting(self, data:str):
		data = data.encode()
		fernet = Fernet(self.key)
		_ = fernet.encrypt(data)
		return _

	def decrypting(self, data):
		if type(data) != bytes:
			data = data.decode()
		fernet = Fernet(self.key)
		decrypted = fernet.decrypt(data)

		return decrypted.decode()