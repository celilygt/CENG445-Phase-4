"""phase3_final URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.urls import re_path
from phase3 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('new_deneme', views.new_deneme),
    path('cargo_list', views.cargo_list),
    path('delete_cargo/<int:id>', views.delete_cargo),
    path('delete_container/<int:cid>', views.delete_container),
    path('tracker_list', views.tracker_list),
    path('container_list', views.container_list),
    path('add_cargo', views.add_cargo),
    path('create_cargo', views.create_cargo),
    path('add_user', views.create_user),
    path('create_container', views.create_container),
    path('add_container', views.add_container),
    path('create_tracker', views.create_tracker),
    path('edit_tracker/<int:tid>', views.create_tracker),
    path('add_tracker', views.add_tracker),
    path('move_cargo/<int:cid>/<int:id>', views.add_move_cargo),
    path('add_move_cargo/<int:id>', views.move_cargo),
    path('create_user', views.create_user_form),
    path('register', views.register),
    path('add_tracker_cargo/<int:tid>', views.add_tracker_cargo),
    path('create_tracker_cargo/<int:tid>', views.create_tracker_cargo),
    path('create_tracker_container/<int:tid>', views.create_tracker_container),
    path('add_tracker_container/<int:tid>', views.add_tracker_container),
    path('', views.home_page),
    path('accounts/', include('django.contrib.auth.urls')),
    path('view_tracker/<int:tid>', views.view_tracker),
    path('delete_tracker/<int:tid>', views.delete_tracker),
    path('delete_tracker_cargo/<int:tid>/<int:id>', views.delete_tracker_cargo),
    path('delete_tracker_container/<int:tid>/<int:cid>', views.delete_tracker_container),
    path('user_list', views.user_list),
    path('delete_user/<int:id>', views.delete_user),
    path('create_user_by_admin', views.create_user_by_admin),
    path('register_by_admin', views.register_by_admin),
    path('update_role_form/<int:id>',views.update_role_form),
    path('update_role/<int:id>', views.update_role),
    path('edit_container/<int:cid>',views.create_container),
    path('reposition/<int:cid>',views.reposition_form),
    path('reposition',views.reposition),
    path('view_cargo/<int:cid>',views.view_container),
    path('unload_cargo/<int:id>',views.unload_cargo),
    path('dashboard', views.dashboardFunction),
    path('new_tracker', views.get_trackers),
    path('new_tracker_cargo', views.get_tracker_cargos),
    path('new_tracker_container/<int:tid>',views.get_tracker_containers),
    path('get_updated_cargo_form',views.get_updated_cargo_form),
    path('get_updated_container_form',views.get_updated_container_form),
    path('get_containers',views.get_containers),
    path('contained_cargos/<int:cid>',views.contained_cargos),
    path('move_cargo/<int:id>',views.move_cargo_new),
    path('alarm',views.alarm_cargo),
]
