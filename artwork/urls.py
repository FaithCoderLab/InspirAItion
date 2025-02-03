from django.urls import path
from . import views

app_name = 'artwork'

urlpatterns = [
    path('', views.artwork_list, name='index'),
    path('list/', views.artwork_list, name='list'),
    path('create/', views.create_artwork, name='create'),
    path('<int:pk>/', views.artwork_detail, name='detail'),
    path('<int:pk>/edit/', views.artwork_edit, name='edit'),
    path('<int:pk>/delete/', views.delete_artwork, name='delete'),
    path('demo-generate/', views.demo_generate_image, name='demo_generate')
]