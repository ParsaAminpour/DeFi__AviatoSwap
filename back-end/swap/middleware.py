from django.http.response import HttpResponseForbidden
from .models import User

class IncludesBlackList:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.blocked_user is None or\
            request.user.blocked_user:
            return HttpResponseForbidden('This user have blocked for security matter')
        
        response = self.get_response(request)
        return response
