from django.urls import path


from accounts.views import (
    GroupListView,
    InviteUserView,
    LoginView,
    LogoutView,
    SalesEngineerListView,
    UsersListView,
)
from accounts.views_refresh import TokenRefreshWithUserView


urlpatterns = [
    path(
        f"get-new-access-token/",
        TokenRefreshWithUserView.as_view(),
        name="token_refresh",
    ),
    path(f"login/", LoginView.as_view(), name="login"),
    path(f"logout/", LogoutView.as_view(), name="logout"),
    path(f"groups/", GroupListView.as_view(), name="groups"),
    path(f"invite/user/", InviteUserView.as_view(), name="invite_user"),
    path("users/", UsersListView.as_view(), name="users_list"),  # ← add
    path("sales-engineers/", SalesEngineerListView.as_view(), name="sales-engineers"),
]
