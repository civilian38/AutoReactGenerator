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
        fields = '__all__'
    
    def validate(self, data):
        project_object = self.instance.project_under
        folder_object = data.get('folder', self.instance.folder)
        
        if folder_object.project_under != project_object:
            raise serializers.ValidationError("Folder Belongs to Wrong Project")
        
        instance = self.instance
        queryset = ProjectFile.objects.filter(folder=folder_object, name=data.get('name', self.instance.name))
        if queryset.exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("There is Already File of Same Name")

        return data


class ProjectFileRetrieveSerializer(serializers.ModelSerializer):
    file_path = serializers.CharField(source='get_file_path', read_only=True)

    # 원본 내용과 별개로 드래프트 정보 추가
    draft_info = serializers.SerializerMethodField()

    # 실제로 보여줄 컨텐츠 (뷰 로직에 따라 선택적으로 사용)
    display_content = serializers.SerializerMethodField()

    class Meta:
        model = ProjectFile
        fields = [
            'id', 'project_under', 'folder', 'name',
            'content', 'display_content',  # 원본 content와 표시용 display_content 분리
            'created_at', 'updated_at', 'file_path',
            'draft_info'
        ]
        read_only_fields = fields

    def get_draft_info(self, obj):
        if hasattr(obj, 'draft'):
            return {
                'id': obj.draft.id,
                'type': obj.draft.draft_type,
                'draft_content': obj.draft.draft_content,
                'created_at': obj.draft.created_at
            }
        return None

    def get_display_content(self, obj):
        """
        프론트엔드 에디터에 보여줄 내용.
        수정 대기중(UPDATE)인 경우 드래프트 내용을 보여준다.
        """
        if hasattr(obj, 'draft') and obj.draft.draft_type == 'UPDATE':
            return obj.draft.draft_content
        return obj.content

class ProjectFileListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    draft_id = serializers.SerializerMethodField()

    class Meta:
        model = ProjectFile
        fields = ('id', 'name', 'status', 'draft_id')

    def get_status(self, obj):
        # OneToOne 관계인 draft가 있는지 확인
        if hasattr(obj, 'draft'):
            if obj.draft.draft_type == 'UPDATE':
                return 'ON_UPDATE' # 수정 대기 중 (노란색 등)
            elif obj.draft.draft_type == 'DELETE':
                return 'ON_DELETE'  # 삭제 대기 중 (빨간색/취소선 등)
        return 'STABLE' # 변경 사항 없음

    def get_draft_id(self, obj):
        # 드래프트가 있다면 해당 ID 반환 (승인/거절 API 호출용)
        if hasattr(obj, 'draft'):
            return obj.draft.id
        return None

class DraftCreationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='file_name')  # ProjectFile과 키를 맞추기 위해 alias 사용
    status = serializers.SerializerMethodField()
    draft_id = serializers.IntegerField(source='id')

    class Meta:
        model = DraftFile
        fields = ('draft_id', 'name', 'status', 'draft_type', 'created_at')

    def get_status(self, obj):
        return 'ON_CREATE'  # 프론트엔드에서 녹색 등으로 표시


class FolderStructureSerializer(serializers.ModelSerializer):
    subfolders = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()  # ModelSerializer 기본 동작 대신 커스텀 메서드 사용

    class Meta:
        model = Folder
        fields = ('id', 'name', 'subfolders', 'files')

    def get_subfolders(self, obj):
        subfolders = obj.subfolders.all()
        return FolderStructureSerializer(subfolders, many=True, context=self.context).data

    def get_files(self, obj):
        # A. 기존 파일들 (ProjectFile)
        existing_files = obj.files.all()
        existing_data = ProjectFileListSerializer(existing_files, many=True, context=self.context).data

        # B. 새로 생성된 드래프트들 (DraftFile - CREATE type)
        # target_file이 null이고, 현재 폴더에 속한 것들
        new_drafts = DraftFile.objects.filter(folder=obj, target_file__isnull=True)
        new_data = DraftCreationSerializer(new_drafts, many=True, context=self.context).data

        # C. 두 리스트 병합
        return existing_data + new_data