from django.http.response import HttpResponseForbidden
from .models import User

class IncludesBlackList:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if not request.user.is_anonymous:
            if request.user.blocked_user is not None or\
                request.user.blocked_user:
                return HttpResponseForbidden('This user has been blocked for security matter')
            
        response = self.get_response(request)
        return response

