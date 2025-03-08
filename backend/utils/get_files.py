import os

def get_files(id):
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'public', 'files', str(id)))
    files = {}

    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        
        if os.path.isfile(full_path):
            # Extract the filename without extension
            name_without_extension = os.path.splitext(filename)[0]
            files[name_without_extension] = full_path
    return files