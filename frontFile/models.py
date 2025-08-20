from django.db import models
from authentication.models import ARUser
from project.models import Project

class FrontFile(models.Model):
    address = models.CharField(max_length=150)
    content = models.TextField(null=True, blank=True)
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(ARUser, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.project_under} - {self.address}'