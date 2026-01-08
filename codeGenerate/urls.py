from django.urls import path
from .views import GenerationSessionLCView, SessionStatusCompletedView, SessionStatusDiscardedView

urlpatterns = [
    path('sessions/<int:project_id>/', GenerationSessionLCView.as_view(), name='session-list-create'),
    path('session/<int:pk>/complete/', SessionStatusCompletedView.as_view(), name='session-status-complete'),
    path('session/<int:pk>/discarded/', SessionStatusDiscardedView.as_view(), name='session-status-discarded')
]