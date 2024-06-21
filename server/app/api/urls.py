from django.urls import path

from . import views


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name="register"),
    path('login/', views.CreateTokenView.as_view(), name="token"),
    # path('logout/', views.CreateTokenView.as_view(), name="token"),
    path('streams/', views.CreateStreamView.as_view(), name='new-stream'),
    path('streams/<pk>/start/', views.StartStreamView.as_view(), name='start-stream'),
    path('streams/<pk>/stop/', views.EndStreamView.as_view(), name='end-stream'),
]
