from django.contrib import admin
from django.urls import path, include
#from django.shortcuts import redirect

urlpatterns = [
    #path('', redirect('hello_world_api')),
    path("admin/", admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/deployTest/', include('deployTest.urls'))
]
