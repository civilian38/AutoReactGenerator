from django.urls import path
from .views import GenerationSessionLCView, SessionStatusCompletedView, SessionStatusDiscardedView, SessionChatView, PromptTestView, FolderPromptTestView, GenerationTestView, FolderGenerationTestView

urlpatterns = [
    path('sessions/<int:project_id>/', GenerationSessionLCView.as_view(), name='session-list-create'),
    path('session/<int:pk>/complete/', SessionStatusCompletedView.as_view(), name='session-status-complete'),
    path('session/<int:pk>/discarded/', SessionStatusDiscardedView.as_view(), name='session-status-discarded'),
    path('session/<int:session_id>/request-generation/', SessionChatView.as_view(), name='request-code-generate'),

    # URLS FOR TEST

    path('session/<int:session_id>/prompttest/', PromptTestView.as_view(), name='session-prompttest'),
    path('session/<int:session_id>/folderprompttest/', FolderPromptTestView.as_view(), name='folder-promopttest'),
    # path('session/<int:session_id>/generationtest/', GenerationTestView.as_view(), name='session-generationtest'),
    # path('session/<int:session_id>/foldergenerationtest/', FolderGenerationTestView.as_view(), name='folder-generationtest'), 
]