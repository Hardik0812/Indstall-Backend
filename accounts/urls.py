from django.urls import path
from accounts.group_and_permissions import GroupListView
from accounts.views import InviteUserView, LoginView, LogoutView
from accounts.views_refresh import TokenRefreshWithUserView
import os
from dotenv import load_dotenv

load_dotenv()

ROUTE_PREFIX = os.getenv("ROUTE_PREFIX")

urlpatterns = [
    path(f"{ROUTE_PREFIX}get-new-access-token/", TokenRefreshWithUserView.as_view(), name="token_refresh"),
    path(f"{ROUTE_PREFIX}login/", LoginView.as_view(), name="login"),
    path(f"{ROUTE_PREFIX}logout/", LogoutView.as_view(), name="logout"),
    path(f"{ROUTE_PREFIX}groups/", GroupListView.as_view(), name="groups"),
    path(f"{ROUTE_PREFIX}invite/user/", InviteUserView.as_view(), name="invite_user"),
]
