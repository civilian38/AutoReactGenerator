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
