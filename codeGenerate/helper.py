from .models import Folder

def _cleanup_empty_folders(folder_ids):
    count = 0
        
    for folder_id in folder_ids:
        try:
            current_folder = Folder.objects.get(id=folder_id)
        except Folder.DoesNotExist:
            continue

        while current_folder:
            has_files = current_folder.files.exists()
            has_subfolders = current_folder.subfolders.exists()

            if not has_files and not has_subfolders:
                parent = current_folder.parent_folder  # 삭제 전 부모 저장
                current_folder.delete()
                count += 1
                    
                current_folder = parent
            else:
                break
    return count

def get_root_folder_with_prefetch_related(all_folders, folder_dict):
    root_folder = None
    for folder in all_folders:
        # subfolders 캐시 초기화 (필수)
        if not hasattr(folder, '_prefetched_objects_cache'):
            folder._prefetched_objects_cache = {}
        if 'subfolders' not in folder._prefetched_objects_cache:
            folder._prefetched_objects_cache['subfolders'] = []

        if folder.parent_folder_id:
            # 부모를 찾아서 부모의 subfolders 캐시 리스트에 현재 폴더를 넣음
            parent = folder_dict.get(folder.parent_folder_id)
            if parent:
                # 여기 초기화는 부모 쪽이 먼저 안 되었을 수도 있으니 안전장치
                if not hasattr(parent, '_prefetched_objects_cache'):
                    parent._prefetched_objects_cache = {}
                if 'subfolders' not in parent._prefetched_objects_cache:
                    parent._prefetched_objects_cache['subfolders'] = []
                
                parent._prefetched_objects_cache['subfolders'].append(folder)
        else:
            # 부모가 없으면 루트 폴더
            root_folder = folder
    
    return root_folder