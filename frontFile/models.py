from django.db import models
from authentication.models import ARUser
from project.models import Project

class Folder(models.Model):
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_folder = models.ForeignKey('self', null=True, blank=True, related_name='subfolders', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'[{self.id}] {self.get_full_path()}'

    def get_full_path(self):
        return f"{self.parent_folder.get_full_path()}/{self.name}" if self.parent_folder else self.name
    
    def is_root(self):
        return self.parent_folder is None
    
    def get_tree_structure(self, parent_structure=""):
        return_text = str()
        if self.is_root():
            return_text += "[{폴더 ID}] {폴더 경로} | {(optional)설명}\n\n"
            
        if parent_structure:
            current_path = f"{parent_structure}/{self.name}"
        else:
            current_path = self.name
        
        return_text += f"[ID: {self.id}] {current_path}" + (f" | {self.description}" if self.description else "") + "\n"
        for subfolder in self.subfolders.all():
            return_text += subfolder.get_tree_structure(current_path)
        return return_text
    
    def get_or_create_by_path(self, path_str):
        path_parts = [p for p in path_str.strip('/').split('/') if p]
        if self.is_root() and path_parts[0] == self.name:
            path_parts.pop(0)
        
        current_folder = self
        for part_name in path_parts:
            current_folder, _ = current_folder.subfolders.get_or_create(
                name=part_name,
                defaults={'project_under': self.project_under}
            )
        
        return current_folder

class ProjectFile(models.Model):
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, related_name='files', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    draft_content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_required = models.BooleanField(default=False)
    description = models.TextField(blank=True, default="")
    draft_description = models.TextField(blank=True, default="")

    def __str__(self):
        return f'[{self.id}] {self.folder.get_full_path()}/{self.name}'
    
    def get_file_path(self):
        return f'{self.folder.get_full_path()}/{self.name}'
    
    def has_draft_content(self):
        return bool(self.draft_content)
    
    def get_list_text(self):
        description_text = self.draft_description if self.draft_description else self.description
        return f"[ID: {self.id}] {self.get_file_path()} | {description_text if description_text else "아직 description이 생성되지 않았습니다."}"
    
    def apply_draft(self):
        self.content = self.draft_content
        self.draft_content = ""
        self.description = self.draft_description
        self.draft_description = ""
        self.save()
    
    def discard_draft(self):
        self.draft_content = ""
        self.draft_description = ""
        self.save()
    
    def get_prompt_text(self):
        text = "=" * 5 + f"{self.get_file_path()} | File ID: {self.id}" + "=" * 5 + "\n"
        if self.draft_content:
            text += self.draft_content + "\n"
        else:
            text += self.content + "\n"
        text += "=" * 10 + "\n"

        return text

