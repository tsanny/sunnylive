from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns = [
    # Authentication
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.CreateTokenView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", views.LogoutView.as_view(), name="token"),
    # User Details
    path("user/", views.CurrentUserView.as_view(), name="user"),
    path("user/<str:pk>/", views.RetrieveUserView.as_view(), name="user"),
    # Streams
    path("streams/", views.CreateStreamView.as_view(), name="create-stream"),
    path(
        "streams/auth/",
        views.StreamAuthView.as_view(),
        name="authenticate-stream",
    ),
    path(
        "streams/done/",
        views.StreamDoneView.as_view(),
        name="end-stream",
    ),
    path(
        "streams/<str:pk>/",
        views.RetrieveStreamView.as_view(),
        name="stream-detail",
    ),
    path(
        "streams/<str:pk>/key/",
        views.RetrieveStreamKeyView.as_view(),
        name="stream-key",
    ),
    path(
        "streams/<str:pk>/<str:action>/",
        views.UpdateStreamView.as_view(),
        name="update-stream",
    ),
    # Donations
    path(
        "donations/charge/",
        views.ChargeDonationView.as_view(),
        name="charge-donation",
    ),
    path(
        "donations/create/",
        views.CreateDonationView.as_view(),
        name="create-donation",
    ),
    path(
        "donations/<str:pk>/",
        views.RetrieveDonationView.as_view(),
        name="donation-detail",
    ),
    path(
        "donations/",
        views.ListDonationView.as_view(),
        name="list-donation",
    ),
    # Comments
    path(
        "comments/create/",
        views.CreateCommentView.as_view(),
        name="create-comment",
    ),
    path(
        "comments/<str:stream_id>/",
        views.ListCommentView.as_view(),
        name="list-stream-comments",
    ),
]
