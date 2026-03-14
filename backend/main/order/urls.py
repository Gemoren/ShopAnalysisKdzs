from django.urls import path
from . import views

urlpatterns = [
    path("upload_file", views.UploadFile.as_view(), name="upload_file"),
    path("get_orders", views.GetOrders.as_view(), name="get_orders"),
    path("get_orders_by_month", views.GetOrdersByMonth.as_view(), name="get_orders_by_month")
]
