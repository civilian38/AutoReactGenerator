from django.db import models
from authentication.models import ARUser

class Project(models.Model):
    name = models.CharField(max_length=50)
    base_web_url = models.URLField(max_length=200)
    base_api_url = models.URLField(max_length=200)
    handover_context = models.TextField(default="No Handover Context Yet")
    handover_draft = models.TextField(null=True, blank=True)
    to_do_request = models.TextField(default="package.json, src/App.jsx, src/App.css, src/index.css 파일 내용을 반드시 추가하세요.", blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    instruction = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(ARUser, on_delete=models.CASCADE, related_name='created_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        owner_name = self.created_by.nickname if self.created_by.nickname else self.created_by.username
        return f'{self.name}({owner_name})'
    
    def get_prompt_text(self):
        if self.handover_draft:
            return self.handover_draft
        return self.handover_context