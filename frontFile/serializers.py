from rest_framework import serializers
from .models import *

class FolderCreateSerializer(serializers.ModelSerializer):
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Folder
        fields = ['name', 'parent_folder', 'project_under']
    
    def validate(self, data):
        project = self.context.get('project')
        parent_folder = data.get('parent_folder')

        if parent_folder.project_under != project:
            raise serializers.ValidationError("Parent Folder Belongs to Wrong Project")
        
        if Folder.objects.filter(parent_folder=parent_folder, name=data.get('name')).exists():
            raise serializers.ValidationError("There is Already Folder of Same Name")

        return data

class FolderRetrieveSerializer(serializers.ModelSerializer):
    full_path = serializers.CharField(source='get_full_path', read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'parent_folder', 'project_under', 'full_path']
        read_only_fields = fields

class FolderUpdateDeleteSerializer(serializers.ModelSerializer):
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Folder
        fields = '__all__'
    
    def validate(self, data):
        project = self.context.get('project')
        parent_folder = data.get('parent_folder')
        if not parent_folder:
            parent_folder = self.instance.parent_folder

        if parent_folder.project_under != project:
            raise serializers.ValidationError("Parent Folder Belongs to Wrong Project")
        
        if Folder.objects.filter(parent_folder=parent_folder, name=data.get('name')).exists():
            raise serializers.ValidationError("There is Already Folder of Same Name")

        return data
    
class ProjectFileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = '__all__'
        read_only_fields = ['draft_content', 'created_at', 'updated_at', 'description', 'draft_description']
    
    def validate(self, data):
        project_object = data.get('project_under')
        folder_object = data.get('folder')
        
        if folder_object.project_under != project_object:
            raise serializers.ValidationError("Folder Belongs to Wrong Project")
        if ProjectFile.objects.filter(folder=folder_object, name=data.get('name')).exists():
            raise serializers.ValidationError("There is Already File of Same Name")
        
        return data


class ProjectFileUpdateDeleteSerializer(serializers.ModelSerializer):
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = ProjectFile
        fields = ('id', 'project_under', 'folder', 'name', 'content', 'is_required')
    
    def validate(self, data):
        project_object = self.instance.project_under
        folder_object = data.get('folder', self.instance.folder)
        
        if folder_object.project_under != project_object:
            raise serializers.ValidationError("Folder Belongs to Wrong Project")
        
        instance = self.instance
        if 'name' in data:
            queryset = ProjectFile.objects.filter(folder=folder_object, name=data['name'])
            if queryset.exclude(pk=instance.pk).exists():
                raise serializers.ValidationError("There is Already File of Same Name")

        return data 

class ProjectFileRetrieveSerializer(serializers.ModelSerializer):
    file_path = serializers.CharField(source='get_file_path', read_only=True)
    has_draft = serializers.BooleanField(source='has_draft_content', read_only=True)

    class Meta:
        model = ProjectFile
        fields = ['id', 'project_under', 'folder', 'name', 'content', 'draft_content', 'has_draft', 'created_at', 'updated_at', 'file_path', 'is_required']
        read_only_fields = fields   

class ProjectFileListSerializer(serializers.ModelSerializer):
    has_draft = serializers.BooleanField(source='has_draft_content', read_only=True)

    class Meta:
        model = ProjectFile
        fields = ('id', 'name', 'has_draft')

class FolderStructureSerializer(serializers.ModelSerializer):
    subfolders = serializers.SerializerMethodField()
    files = ProjectFileListSerializer(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ('id', 'name', 'subfolders', 'files')
    
    def get_subfolders(self, obj):
        subfolders = obj.subfolders.all()
        serializer = FolderStructureSerializer(subfolders, many=True, context=self.context)
        
        return serializer.data