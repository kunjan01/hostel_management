from django.urls import path

from . import views

urlpatterns = [
    path("blocks/", views.block_list, name="block_list"),
    path("blocks/add/", views.block_add, name="block_add"),
    path("blocks/<int:pk>/", views.block_detail, name="block_detail"),
    path("rooms/", views.room_list, name="room_list"),
    path("rooms/add/", views.room_add, name="room_add"),
    path("rooms/<int:pk>/", views.room_detail, name="room_detail"),
    path("allocate/", views.allocate_room, name="allocate_room"),
    path("allocations/", views.allocation_list, name="allocation_list"),
    path("allocations/<int:pk>/vacate/", views.vacate_room, name="vacate_room"),
]
