from os import stat
from django.urls import path
from .views import Home, Signup, Profile, Swap, Info, Login, AddUserApiView,\
    user_api_view, wallet_api_get, wallet_api_post, EditProfile
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings
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
    path('api/wallet/<int:wallet_id>/', wallet_api_get.as_view()),
    path('api/wallet/add/', wallet_api_post.as_view()),
    path('profile/edit/', EditProfile.as_view())
]
