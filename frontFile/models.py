from django.db import models
from authentication.models import ARUser
from project.models import Project

class Folder(models.Model):
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_folder = models.ForeignKey('self', null=True, blank=True, related_name='subfolders', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'[{self.id}] {self.get_full_path()}'

    def get_full_path(self):
        return f"{self.parent_folder.get_full_path()}/{self.name}" if self.parent_folder else self.name
    
    def is_root(self):
        return self.parent_folder is None

class ProjectFile(models.Model):
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, related_name='files', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    draft_content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'[{self.id}] ({self.project_under}) {self.folder}/{self.name}'
    
    def get_file_path(self):
        return f'{self.folder.get_full_path()}/{self.name}'
    
    def has_draft_content(self):
        return bool(self.draft_content)
    
    def get_prompt_text(self):
        text = "=" * 5 + f"{self.get_file_path()} | File ID: {self.id}" + "=" * 5 + "\n"
        if self.draft_content:
            text += self.draft_content + "\n"
        else:
            text += self.content + "\n"
        text += "=" * 10 + "\n"

        return text

