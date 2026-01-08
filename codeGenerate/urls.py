from django.urls import path
from .views import GenerationSessionLCView

urlpatterns = [
    path('sessions/<int:project_id>/', GenerationSessionLCView.as_view(), name='session-list-create'),
]