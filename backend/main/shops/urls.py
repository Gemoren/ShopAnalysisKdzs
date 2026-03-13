from django.urls import path

from . import views

urlpatterns = [
    path("upload_file", views.UploadFile.as_view(), name="upload_file"),
    path("get_shops", views.GetShops.as_view(), name="get_shops")
]
