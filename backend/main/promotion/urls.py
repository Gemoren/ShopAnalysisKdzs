from django.urls import path

from . import views

urlpatterns = [
    path("upload_file", views.UploadFile.as_view(), name="upload_file"),
    path("get_promotions", views.GetPromotions.as_view(), name="get_promotions")
]
