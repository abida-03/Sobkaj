# helpers.py - utility functions shared across different route files
# Photo upload processing, NID verification mock, and a SQL compatibility helper.

import os
import uuid

from PIL import Image, ImageOps
from flask import current_app
from werkzeug.utils import secure_filename


# only these image formats are accepted for profile photos
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_PROFILE_PHOTO_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_PROFILE_PHOTO_SIZE_MB = MAX_PROFILE_PHOTO_SIZE // (1024 * 1024)


# We don't have access to a real government NID API, so we simulate
# verification using a small dictionary of test NIDs.
# In a real system, this would be replaced by an API call.
DUMMY_NID_DATABASE = {
    "1234567890":        {"name": "Rahim Uddin",   "dob": "1990-05-15", "address": "Mirpur, Dhaka"},
    "9876543210":        {"name": "Karim Hossain",  "dob": "1985-11-22", "address": "Dhanmondi, Dhaka"},
    "19901234567890123": {"name": "Fatima Begum",   "dob": "1990-12-01", "address": "Uttara, Dhaka"},
    "19851234567890456": {"name": "Aminul Islam",   "dob": "1985-03-10", "address": "Gulshan, Dhaka"},
    "5678901234":        {"name": "Nasreen Akter",  "dob": "1992-07-08", "address": "Mohammadpur, Dhaka"},
}


def allowed_file(filename):
    """Returns True if the file extension is in our allowed list."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_uploaded_file_size(file_storage):
    """Measures the file size without consuming the upload stream.
    We seek to the end to get the size, then seek back so the
    file can still be read normally afterwards."""
    stream = file_storage.stream
    current_pos = stream.tell()
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(current_pos)
    return size


def save_profile_photo(photo_file):
    """Processes an uploaded profile photo:
    1. Validates format and size
    2. Fixes rotation using EXIF data
    3. Center-crops to a square
    4. Resizes to 400x400 pixels
    5. Saves as WebP for smaller file size

    Returns a tuple: (photo_url, error_message)
    One of them will always be None."""

    safe_name = secure_filename(photo_file.filename or "")
    if not safe_name:
        return None, "Please choose a valid photo file."
    if not allowed_file(safe_name):
        return None, "Invalid photo format. Use png, jpg, jpeg, gif, or webp."

    file_size = get_uploaded_file_size(photo_file)
    if file_size > MAX_PROFILE_PHOTO_SIZE:
        return None, f"Profile picture must be {MAX_PROFILE_PHOTO_SIZE_MB} MB or smaller."

    # generate a unique filename so uploads never overwrite each other
    unique_name = f"{uuid.uuid4().hex}.webp"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, unique_name)
    photo_file.stream.seek(0)

    try:
        with Image.open(photo_file) as img:
            # fix phone photos that appear rotated
            img = ImageOps.exif_transpose(img)

            # handle transparency by pasting onto white background
            if img.mode in ("RGBA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # crop the center into a square (looks better as a profile pic)
            width, height = img.size
            if width != height:
                min_dim = min(width, height)
                left = (width - min_dim) / 2
                top = (height - min_dim) / 2
                img = img.crop((left, top, left + min_dim, top + min_dim))

            # resize and save as WebP
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            img.save(save_path, "WEBP", quality=85)
    except Exception as e:
        print(f"[Photo Processing Error] {e}")
        return None, "An error occurred while processing your photo."

    return f"/static/uploads/{unique_name}", None


def get_background_verification_sql(cursor, table_alias="wp"):
    """The column for police/background verification was renamed at one point.
    Some databases still have the old name 'police_verified' while newer
    ones use 'background_verified'. This function checks which column
    actually exists and returns SQL that works either way."""

    cursor.execute("SHOW COLUMNS FROM worker_profiles")
    columns = {
        row["Field"] if isinstance(row, dict) else row[0]
        for row in cursor.fetchall()
    }

    verification_column = None
    if "background_verified" in columns:
        verification_column = "background_verified"
    elif "police_verified" in columns:
        verification_column = "police_verified"

    if verification_column:
        return (
            f"{table_alias}.{verification_column} AS police_verified",
            f", {table_alias}.{verification_column}",
        )
    return "FALSE AS police_verified", ""
