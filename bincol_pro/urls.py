from django.urls import path
from . import views
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetConfirmView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetCompleteView

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', views.user_login, name='login'),
    #path('profile/create/', views.profile_create, name='profile_create'),
    path('dashboard/', views.dashboard, name='dashboard'),  # User dashboard
    path('change_password/', views.change_password, name='change_password'),
    path('password-reset/', views.password_reset_form, name='password_reset_form'),
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset_form'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    #path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    #path('reset_password_complete/', PasswordResetCompleteView.as_view(success_url=reverse_lazy('login')), name='password_reset_complete'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
        extra_context={'next_page': '/login/'}), name='password_reset_complete'),
    path('lodge_complaint/', views.lodge_complaint, name='lodge_complaint'),
    path('complaint_history/', views.complaint_history, name='complaint_history'),
    path('upload-complaints/', views.upload_complaints, name='upload_complaints'),
]