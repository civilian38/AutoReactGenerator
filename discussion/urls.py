from django.urls import path
from .views import *

urlpatterns = [
    path('<int:project_id>/', DiscussionLCView.as_view(), name='discussion-list-create'),
    path('detail/<int:pk>/', DiscussionRUDView.as_view(), name='discussion-retrieve-update-delete'),
    path('chat/<int:discussion_id>/', ChatAPIView.as_view(), name='discussion-chat'),
    path('chat/<int:discussion_id>/list/', DiscussChatListView.as_view(), name='discussion-chat-list'),
]