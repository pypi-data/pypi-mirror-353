from django.urls import path, include
from . import views

app_name = 'workflows'

urlpatterns = [
    path('api/workflows-token', views.workflows_token, name='get-workflows-token'),
    path('api/workflows-listing', views.workflows_listing, name='get-workflows-listing'),
    path('api/workflows-listing/<str:template_id>', views.workflows_listing_detail, name='get-workflows-listing-detail'),
    path('api/workflows-listing/<str:template_id>/create-template', views.workflows_create_template, name='get-workflows-create-template'),
    path('api/workflows-listing/categories', views.workflows_categories, name='get-workflows-categories'),
]
