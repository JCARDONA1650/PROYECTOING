from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Cambia 'core' por el nombre de tu app si es diferente
    path('', include('core.urls')),
]
