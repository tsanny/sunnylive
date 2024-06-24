from django.urls import path

from . import views


urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.CreateTokenView.as_view(), name="token"),
    path("logout/", views.LogoutView.as_view(), name="token"),
    path("streams/", views.CreateRetrieveStreamView.as_view(), name="new-stream"),
    path(
        "streams/auth/",
        views.StreamAuthView.as_view(),
        name="start-stream",
    ),
    path(
        "streams/done/",
        views.StreamDoneView.as_view(),
        name="end-stream",
    ),
    path(
        "streams/<str:pk>/",
        views.CreateRetrieveStreamView.as_view(),
        name="stream-detail",
    ),
    path(
        "streams/<str:pk>/<str:action>/",
        views.UpdateStreamView.as_view(),
        name="update-stream",
    ),
    path(
        "donations/create/",
        views.CreateRetrieveDonationView.as_view(),
        name="stream-detail",
    ),
    path(
        "donations/<str:pk>/",
        views.CreateRetrieveDonationView.as_view(),
        name="stream-detail",
    ),
    path(
        "donations/",
        views.ListDonationView.as_view(),
        name="stream-detail",
    ),
    path(
        "comments/create/",
        views.CreateRetrieveCommentView.as_view(),
        name="stream-detail",
    ),
    path(
        "comments/<str:stream_id>/",
        views.CreateRetrieveCommentView.as_view(),
        name="stream-detail",
    ),
]