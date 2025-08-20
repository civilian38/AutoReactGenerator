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

