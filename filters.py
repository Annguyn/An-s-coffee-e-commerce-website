# filters.py
import base64
import imghdr

def b64encode(data):
    if isinstance(data, bytes):
        mime_type = imghdr.what(None, data)
        if mime_type is None:
            mime_type = 'jpeg'  # Default to jpeg if MIME type cannot be determined
        return f"data:image/{mime_type};base64,{base64.b64encode(data).decode('utf-8')}"
    else:
        raise TypeError("Expected bytes, got {}".format(type(data).__name__))