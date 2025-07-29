import os
import uuid
from typing import List, Optional
from werkzeug.utils import secure_filename

class FileUpload:
    def __init__(self, app, upload_folder: str = "uploads",
                 allowed_extensions: Optional[List[str]] = None,
                 max_size: int = 16 * 1024 * 1024):  # 16MB default
        self.app = app
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions or ["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"]
        self.max_size = max_size
        os.makedirs(upload_folder, exist_ok=True)

    def allowed_file(self, filename: str) -> bool:
        return "." in filename and \
               filename.rsplit(".", 1)[1].lower() in self.allowed_extensions

    def save_file(self, file, folder: str = None) -> Optional[str]:
        if file and self.allowed_file(file.filename):
            if file.content_length > self.max_size:
                raise ValueError(f"File terlalu besar. Maksimal {self.max_size/1024/1024}MB")

            filename = secure_filename(file.filename)
            # Generate unique filename
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Create folder if specified
            if folder:
                upload_path = os.path.join(self.upload_folder, folder)
                os.makedirs(upload_path, exist_ok=True)
                file_path = os.path.join(upload_path, unique_filename)
            else:
                file_path = os.path.join(self.upload_folder, unique_filename)

            file.save(file_path)
            return file_path
        return None

    def delete_file(self, file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except:
            pass
        return False

    def get_file_url(self, file_path: str) -> str:
        if file_path:
            relative_path = os.path.relpath(file_path, self.upload_folder)
            return f"/uploads/{relative_path}"
        return None

class FileField:
    def __init__(self, required: bool = False, max_size: int = None,
                 allowed_extensions: List[str] = None):
        self.required = required
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions

    def validate(self, file) -> tuple:
        if self.required and not file:
            return False, "File wajib diupload"
        
        if file:
            if self.max_size and file.content_length > self.max_size:
                return False, f"File terlalu besar. Maksimal {self.max_size/1024/1024}MB"
            
            if self.allowed_extensions:
                ext = file.filename.rsplit(".", 1)[1].lower()
                if ext not in self.allowed_extensions:
                    return False, f"Format file tidak didukung. Format yang didukung: {', '.join(self.allowed_extensions)}"
        
        return True, None 