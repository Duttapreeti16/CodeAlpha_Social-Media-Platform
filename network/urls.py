from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("post/<int:post_id>/comment", views.add_comment, name="add_comment"),
    
    # API endpoints
    path("api/like/<int:post_id>", views.toggle_like, name="toggle_like"),
    path("api/follow/<str:username>", views.toggle_follow, name="toggle_follow"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
