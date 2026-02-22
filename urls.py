from django.urls import path
from . import views

app_name = 'doc_templates'

urlpatterns = [
    # Dashboard (template list)
    path('', views.dashboard, name='dashboard'),

    # Template CRUD
    path('create/', views.template_create, name='template_create'),
    path('<uuid:pk>/edit/', views.template_edit, name='template_edit'),
    path('<uuid:pk>/delete/', views.template_delete, name='template_delete'),
    path('<uuid:pk>/duplicate/', views.template_duplicate, name='template_duplicate'),
    path('<uuid:pk>/preview/', views.template_preview, name='template_preview'),
    path('<uuid:pk>/set-default/', views.template_set_default, name='template_set_default'),

    # Variables
    path('variables/', views.variables, name='variables'),
    path('variables/create/', views.variable_create, name='variable_create'),
    path('variables/<uuid:pk>/delete/', views.variable_delete, name='variable_delete'),

    # Render API
    path('api/render/', views.api_render, name='api_render'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
    path('settings/save/', views.settings_save, name='settings_save'),
]
