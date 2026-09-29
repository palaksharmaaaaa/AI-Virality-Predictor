import os
import uuid


def allowed_file(filename, allowed_extensions):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )


def unique_filename(filename):
    extension = os.path.splitext(filename)[1].lower()
    return f"{uuid.uuid4().hex}{extension}"
