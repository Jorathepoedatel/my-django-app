from multiprocessing.resource_tracker import register

from django.contrib.auth.views import LoginView
from django.urls import path

from .views import get_cookie_view, set_cookie_view, set_session_view, get_session_view, MyLogoutView, AboutMeView, \
    RegisterView, FoobarView, UserListView, UserDetailView, UserAvatarUpdateView

app_name = "myauth"

urlpatterns = [
    # path('login/', login_view, name='login'),
    path(
        'login/',
        LoginView.as_view(
            template_name='myauth/login.html',
            redirect_authenticated_user=True,
        ),
        name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('about/', AboutMeView.as_view(), name='about'),
    path('register/', RegisterView.as_view(), name='register'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path("users/<int:pk>/update/", UserAvatarUpdateView.as_view(), name="user_update"),

    path('cookie/get/', get_cookie_view, name='cookie_get'),
    path('cookie/set/', set_cookie_view, name='cookie_set'),

    path('session/set/', set_session_view, name='session_set'),
    path('session/get/', get_session_view, name='session_get'),

    path('foobar/', FoobarView.as_view(), name='foo-bar'),
]
