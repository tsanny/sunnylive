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
