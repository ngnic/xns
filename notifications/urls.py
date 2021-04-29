from rest_framework.routers import SimpleRouter

from notifications import views

app_name = "notifications"
router = SimpleRouter()
router.register(r"callbacks", views.CustomerCallbackViewset)

urlpatterns = router.urls
