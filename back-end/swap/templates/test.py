from colorama import Fore,init
from random import radnint
from django.contrib.auth.mixins import LoginRequiredMixins
from django.models.auth import ModelsForm
from django.models import ModelsForm
from django.view.genereics import TempaletView
from django.views import View
from scurity.models import BannedUsers
from djanog.http import HttpResponse, JsonResponse
from djanog.http import HttpBannedResponse
from rest_framework.status import Status

class Home(LoginRequiredMixins, View):
	def __init__(self, *args, **kwargs):
		super(self, Home).__init__(args, kwargs)
		self.user = request.user
		self.NIC = request.META.get("remote_addr")

	def get(self, request):
		if request.user not in [BannedUsers.objects.values_list('username')]:	
			return HttpResponse("Welocome", status=Status.HTTP_200_OK)
		else:
			return HttpBannedResponse("404 error access", status = Status.HTTP_404_NOT_ALLOWED)

	def post(self, request):
		pass