from django.urls import path

from users import views

app_name = 'users'

urlpatterns = [
    path("login/", views.login, name="login"),
    path("registration/", views.registration, name="registration"),
    path("profile/", views.profile, name="profile"),
    path("users-cart/", views.users_cart, name="users_cart"),
    path("logout/", views.logout, name="logout"),
    path("verify_email/<int:user_id>/", views.verify_email, name="verify_email"),
    path("reset_password_start/", views.reset_password_write_email, name="reset_password_write_email"),
    path("reset_password_end/<str:uidb64>/<str:token>/", views.reset_password_end, name="reset_password_end"),
    path("confirm_email/", views.confirm_email, name="confirm_email"),
    path("write-phone-number/", views.write_phone_number, name="write_phone_number"),
    path("confirm-phone-number/", views.confirm_phone_number, name="confirm_phone_number"),
    path("final-step-phone-number/", views.final_step_phone_number, name="final_step_phone_number"),
]
