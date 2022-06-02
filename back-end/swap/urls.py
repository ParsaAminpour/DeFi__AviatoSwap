from django.urls import path
from .views import Home, Signup, Profile, Swap, Info, Login, AddUserApiView, testPage,\
    user_api_view
from django.contrib.auth.views import LogoutView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('home/', Home.as_view()),
    path('signup/', Signup),
    path('profile/', Profile),
    path('swap/', Swap.as_view()),
    path('info/', Info.as_view()),
    path('login/', Login),
    path('logout/', LogoutView.as_view()),
    path('api/user/<int:user_id>/', user_api_view),
    path('api/user/add/', AddUserApiView.as_view()),
    path('api/', obtain_auth_token),
    path('test/', testPage)
]
