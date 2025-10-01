from django.db import models
from authentication.models import ARUser
from project.models import Project

class Folder(models.Model):
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_folder = models.ForeignKey('self', null=True, blank=True, related_name='subfolders', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)    

    def __str__(self):
        if self.parent:
            return f"{self.parent}/{self.name}"
        return f"/{self.name}"
    
    def is_root(self):
        return self.parent_folder is None

class ProjectFile(models.Model):
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, related_name='files', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'({self.project_under}) {self.folder}/{self.name}'
    
    def file_path(self):
        return f'{self.folder}/{self.name}'

class FrontFile(models.Model):
    address = models.CharField(max_length=150)
    content = models.TextField(null=True, blank=True)
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_by = models.ForeignKey(ARUser, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.project_under} - {self.address}'