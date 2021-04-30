from rest_framework.routers import SimpleRouter

from notifications import views

app_name = "notifications"
router = SimpleRouter()
router.register(r"callbacks", views.CustomerCallbackViewset)
router.register(r"notifications", views.NotificationViewset)

urlpatterns = router.urls
