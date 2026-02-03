from django.db import models
from project.models import Project

class Discussion(models.Model):
    title = models.CharField(max_length=100)
    summary = models.TextField(blank=True, null=True)
    short_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.project_under.name} - {self.title}'

    def get_prompt_text(self):
        text = f"===== {self.title} =====\n"
        text += self.summary + "\n"
        text += "=" * 10 + "\n"

        return text

class DiscussionChat(models.Model):
    discussion_under = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_by_user = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.discussion_under.title} - {self.content[:30]}'