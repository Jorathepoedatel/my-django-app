from random import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView

from .forms import AvatarUpdateForm
from .models import Profile


class AboutMeView(UpdateView):
    model = Profile
    form_class = AvatarUpdateForm
    template_name = "myauth/about-me.html"
    success_url = reverse_lazy("myauth:about")

    def get_object(self, queryset=None):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user=user)
        return response


class MyLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('myauth:login')


def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie('fizz', 'buzz', max_age=3600)
    return response

@cache_page(60*2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default")
    return HttpResponse(f"Cookie value: {value!r} + {random()}")


def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set")


def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")

class FoobarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})


class UserListView(ListView):
    model = User
    template_name = "myauth/user_list.html"
    context_object_name = "users"

class UserDetailView(DetailView):
    model = User
    template_name = "myauth/user_detail.html"
    context_object_name = "profile_user"


class UserAvatarUpdateView(UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = AvatarUpdateForm
    template_name = "myauth/user_update.html"

    def test_func(self):
        return self.request.user.is_staff or self.get_object().user == self.request.user

    def get_object(self, queryset=None):
        user = User.objects.get(pk=self.kwargs["pk"])
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile

    def get_success_url(self):
        return reverse_lazy("myauth:user_detail", kwargs={"pk": self.kwargs["pk"]})