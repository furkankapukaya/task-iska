from django.urls import include, path
from rest_framework import routers

from forecasts import views

router = routers.SimpleRouter()

router.register(r'forecasts', views.ForecastViewSet)


urlpatterns = [
    path('api/v1/', include(router.urls)),
]
