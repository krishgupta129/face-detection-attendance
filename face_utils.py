import face_recognition
import numpy as np
import io
from PIL import Image

def get_face_encodings(image_bytes):
    # Load image from bytes
    image = Image.open(io.BytesIO(image_bytes))
    image = np.array(image)

    # Convert RGB if needed (face_recognition expects RGB)
    if image.shape[2] == 4:  # PNG with alpha channel
        image = image[:, :, :3]

    encodings = face_recognition.face_encodings(image)
    return encodings

def recognize_face_from_encoding(unknown_encoding, known_users, tolerance=0.5):
    """
    known_users: list of tuples (user_id, name, phone, encoding)
    Returns (user_id, name) if matched else None
    """
    for user_id, name, phone, known_encoding in known_users:
        matches = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance)
        if matches[0]:
            return user_id, name
    return None
