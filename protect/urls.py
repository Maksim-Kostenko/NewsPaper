from protect.views import IndexView

from django.urls import path

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
]