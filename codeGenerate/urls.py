from django.urls import path
from .views import GenerationSessionLCView, SessionStatusCompletedView, SessionStatusDiscardedView, PromptTestView, GenerationTestView

urlpatterns = [
    path('sessions/<int:project_id>/', GenerationSessionLCView.as_view(), name='session-list-create'),
    path('session/<int:pk>/complete/', SessionStatusCompletedView.as_view(), name='session-status-complete'),
    path('session/<int:pk>/discarded/', SessionStatusDiscardedView.as_view(), name='session-status-discarded'),
    path('session/<int:session_id>/prompttest/', PromptTestView.as_view(), name='session-prompttest'),
    # path('session/<int:session_id>/generationtest/', GenerationTestView.as_view(), name='session-generationtest')
]