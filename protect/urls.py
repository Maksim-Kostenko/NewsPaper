from protect.views import IndexView, upgrade_author

from django.urls import path

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('upgrade/', upgrade_author, name='upgrade_author'),
]