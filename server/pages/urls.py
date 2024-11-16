from django.urls import path

from .views import homePageView, transferView, confirmView, csrfView

urlpatterns = [
    path('', homePageView, name='home'),
    path('transfer/', transferView, name='transfer'),
    path('confirm/', confirmView, name='confirm'),

    # to illustrate csrf vulnerability
    path('csrf/', csrfView, name='csrf'),
]
