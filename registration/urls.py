"""
URL configuration for registration project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from app1 import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'),
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('employees/', views.employees, name='employees'),
    path('addemployee/', views.addemployee, name='addemployee'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('update/<int:id>/', views.update, name='update'),
    path('update/updaterec/<int:id>/', views.updaterec, name='updaterec'),
    path('calculate-scale-fee/', views.scale_fee_view, name='calculate_scale_fee'),
    path('legal_scale_fee_calculator/', views.legal_scale_fee_calculator, name='legal_scale_fee_calculator'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('appointmenttb/', views.appointments, name='appointmenttb'),
    path('deletebooking/<int:id>/', views.deletebooking, name='deletebooking'),
    path('editBook/<int:id>/', views.editBook, name='editBook'),


    #path('', include('app1.urls'))
]