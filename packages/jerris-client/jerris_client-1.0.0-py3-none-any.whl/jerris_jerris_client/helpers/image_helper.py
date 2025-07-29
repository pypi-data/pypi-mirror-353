import magic

from jerris_jerris_client.const.globals import SUPPORTED_IMAGES_FORMATS


def image_is_supported(file_path: str) -> bool:
    mime_type = magic.from_buffer(file_path, mime=True)

    for format_type, info in SUPPORTED_IMAGES_FORMATS.items():
        if mime_type in info["mime"]:
            return True

    return False
