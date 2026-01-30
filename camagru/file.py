import os
import uuid
from flask import current_app

EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024 #5MB

def is_valid_extension(filename):
    return "." in filename and filename.split(".")[-1].lower() in EXTENSIONS

def is_valid_size(file):
    size = os.fstat(file.fileno()).st_size
    return size < MAX_FILE_SIZE

def unique_filename(filename):
    ext = filename.split(".")[-1].lower()
    unique_id = uuid.uuid4().hex[:16]
    return f"{unique_id}.{ext}"


def save_image(file):
    error = None

    if not is_valid_extension(file.filename):
        error = "Invalid file extension"
        return False, error
    if not is_valid_size(file):
        error = "Invalid file size"
        return False, error
    
    storage_filename = unique_filename(file.filename)
    file.save(os.path.join(current_app.root_path, "static", "posts", storage_filename))

    return True, storage_filename