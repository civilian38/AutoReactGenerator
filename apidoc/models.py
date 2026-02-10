from django.db import models
from project.models import Project
from authentication.models import ARUser

HTTP_METHOD_CHOICES = [
    ('GET', 'GET'),
    ('POST', 'POST'),
    ('PUT', 'PUT'),
    ('DELETE', 'DELETE'),
    ('PATCH', 'PATCH'),
    ('HEAD', 'HEAD'),
    ('OPTIONS', 'OPTIONS'),
]

class APIDoc(models.Model):
    url = models.URLField(max_length=250)
    http_method = models.CharField(max_length=20, choices=HTTP_METHOD_CHOICES, default='GET')
    method_order = models.IntegerField(default=0, db_index=True, editable=False)
    request_format = models.JSONField(default=dict, blank=True)
    request_headers = models.JSONField(default=dict, blank=True)
    query_params = models.JSONField(default=dict, blank=True)
    response_format = models.JSONField(default=dict, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(ARUser, on_delete=models.CASCADE)
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.project_under} - ({self.http_method}){self.url}'
    
    class Meta:
        ordering = ['url', 'method_order']
    
    def save(self, *args, **kwargs):
        ordering_map = {
            'GET': 1,
            'POST': 2,
            'PUT': 3,
            'DELETE': 4,
            'PATCH': 5,
            'HEAD': 6,
            'OPTIONS': 7
        }
        self.method_order = ordering_map.get(self.http_method, 99)
        super().save(*args, **kwargs)
    
    def get_prompt_text(self):
        text = f"URL: {self.url}\n"
        text += f"요청 종류: {self.http_method}\n"
        text += f"요청에 대한 설명: {self.description}\n"
        if self.request_format:
            text += f"Request Sample:\n{self.request_format}\n"
        if self.response_format:
            text += f"Response Sample:\n{self.response_format}\n"
        text += "=" * 10

        return text

