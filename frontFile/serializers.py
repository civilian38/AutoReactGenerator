from rest_framework import serializers

from .models import *

class FrontFileSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = FrontFile
        fields = '__all__'

class FrontFileCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = FrontFile
        fields = '__all__'

class FrontFileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontFile
        fields = ['id', 'address']

class FolderCreateSerializer(serializers.ModelSerializer):
    project_under = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        write_only=True
    )
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

        if parent_folder.project_under != project:
            raise serializers.ValidationError("Parent Folder Belongs to Wrong Project")
        
        if Folder.objects.filter(parent_folder=parent_folder, name=data.get('name')).exists():
            raise serializers.ValidationError("There is Already Folder of Same Name")

        return data

class FolderStructureSerializer(serializers.ModelSerializer):
    subfolders = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = ('id', 'name', 'subfolders')
    
    def get_subfolders(self, obj):
        subfolders = obj.subfolders.all()
        serializer = FolderStructureSerializer(subfolders, many=True, context=self.context)
        
        return serializer.data