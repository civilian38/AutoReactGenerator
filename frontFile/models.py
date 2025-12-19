from django.db import models
from authentication.models import ARUser
from project.models import Project

class Folder(models.Model):
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_folder = models.ForeignKey('self', null=True, blank=True, related_name='subfolders', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.get_full_path()}'

    def get_full_path(self):
        return f"{self.name}"
    
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
    
    def get_file_path(self):
        return f'{self.folder}/{self.name}'

class DraftFile(models.Model):
    class DraftType(models.TextChoices):
        CREATE = 'CREATE', '새 파일 생성'
        UPDATE = 'UPDATE', '수정'
        DELETE = 'DELETE', '삭제'

    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    draft_content = models.TextField(null=True, blank=True)
    draft_type = models.CharField(max_length=10, choices=DraftType.choices, default=DraftType.UPDATE)
    created_at = models.DateTimeField(auto_now_add=True)

    # UPDATE시 사용
    target_file = models.OneToOneField(ProjectFile, null=True, blank=True, related_name='draft', on_delete=models.CASCADE)

    # CREATE시 사용
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    file_name =  models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['project_under', 'folder', 'file_name'],
                condition=models.Q(target_file__isnull=True),
                name='unique_draft_creation_per_location'
            )
        ]

    def __str__(self):
        return f"[{self.draft_type}] {self.target_file.name if self.target_file else self.file_name}"
