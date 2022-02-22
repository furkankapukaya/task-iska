from django.urls import include, path
from rest_framework import routers


from subscriptions import views

router = routers.SimpleRouter()

router.register(r'subscriptions', views.SubscriptionViewSet)


urlpatterns = [
    path('api/v1/', include(router.urls)),
]
