from django.urls import path

from . import views

urlpatterns = [
    path("menu/", views.MenuView.as_view(), name="mess_menu"),
    path("menu/update/", views.MenuUpdateView.as_view(), name="menu_update"),
    path("registrations/", views.RegistrationListView.as_view(), name="registration_list"),
    path("register/", views.RegisterStudentView.as_view(), name="register_mess"),
    path("bills/", views.BillListView.as_view(), name="bill_list"),
    path("bills/generate/", views.GenerateBillView.as_view(), name="generate_bill"),
    path("bills/<int:pk>/paid/", views.MarkBillPaidView.as_view(), name="mark_paid"),
    path("bills/room/<int:pk>/paid/", views.MarkRoomBillPaidView.as_view(), name="mark_paid_room"),
]
