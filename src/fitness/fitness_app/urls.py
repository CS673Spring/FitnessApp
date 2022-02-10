from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="index"),
    path("contact", views.contact, name="contact"),
    path("gallery", views.gallery, name="gallery"),
    path("about", views.about, name="about"),
    path("portal", views.portal, name="portal"),
    path(
        "beginners-routines", views.beginners_routines, name="beginners_routines"
    ),
]