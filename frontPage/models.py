from django.db import models
from project.models import Project

class FrontPage(models.Model):
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    url = models.URLField()
    page_description = models.TextField()
    is_implemented = models.BooleanField(default=False)

    def __str__(self):
        return f'[{self.id}] {self.project_under.name} - {self.url}'