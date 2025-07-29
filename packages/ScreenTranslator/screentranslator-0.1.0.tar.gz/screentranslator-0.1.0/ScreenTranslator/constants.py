import os
from pathlib import Path

FOLDER_SCREENTRANSLATOR = Path(__file__).resolve().parent
FOLDER_RESOURCES = os.path.join(FOLDER_SCREENTRANSLATOR, "resources")
FOLDER_UPLOADS = os.path.join(FOLDER_SCREENTRANSLATOR, "server", "static", "uploads")
FOLDER_PROCESSED = os.path.join(FOLDER_SCREENTRANSLATOR, "server", "static", "processed")
FOLDER_PARAMS = os.path.join(FOLDER_PROCESSED, "params")
FOLDER_IMAGE_BOXED = os.path.join(FOLDER_PROCESSED, "image_boxed")
FOLDER_IMAGE_BOXED_CHARACTERS = os.path.join(FOLDER_IMAGE_BOXED, "characters")
FOLDER_IMAGE_BOXED_WORDS = os.path.join(FOLDER_IMAGE_BOXED, "words")
FOLDER_LABELS = os.path.join(FOLDER_PROCESSED, "labels")
FOLDER_LABELS_CHARACTERS = os.path.join(FOLDER_LABELS, "characters")
FOLDER_LABELS_WORDS = os.path.join(FOLDER_LABELS, "words")
FOLDER_IMAGE_TRANSLATED = os.path.join(FOLDER_PROCESSED, "image_translated")
FOLDER_IMAGE_TRANSLATED_ROUGH = os.path.join(FOLDER_IMAGE_TRANSLATED, "rough")
FOLDER_IMAGE_TRANSLATED_CORRECTED = os.path.join(FOLDER_IMAGE_TRANSLATED, "corrected")
TEMP_FOLDERS = [ 
    FOLDER_UPLOADS, FOLDER_PROCESSED,
    FOLDER_PARAMS,
    FOLDER_IMAGE_BOXED, FOLDER_IMAGE_BOXED_CHARACTERS, FOLDER_IMAGE_BOXED_WORDS, 
    FOLDER_LABELS, FOLDER_LABELS_CHARACTERS, FOLDER_LABELS_WORDS,
    FOLDER_IMAGE_TRANSLATED, FOLDER_IMAGE_TRANSLATED_ROUGH, FOLDER_IMAGE_TRANSLATED_CORRECTED
]

RESOURCES_MODEL_SCREENTRANSLATOR = os.path.join(FOLDER_RESOURCES, "best.pt")
MODEL_PATHS = [
    RESOURCES_MODEL_SCREENTRANSLATOR
]
RESOURCES_3_GRAMM_INDEX = os.path.join(FOLDER_RESOURCES, "3_gramm_index.json")
RESOURCES_ARIAL = os.path.join(FOLDER_RESOURCES, "arialmt.ttf")
RESOURCES_EN_US_LARGE = os.path.join(FOLDER_RESOURCES, "en_US-large.txt")

YOLO_LABES =  [ 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 
                'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                'U', 'V', 'W', 'X', 'Y', 'Z', 
                '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
                '.', ',', '?', '!', '@' ]
PUNCTUATION_CHARACTERS = {
    'dot': '.', 'comma': ',', 'quest': '?', 'excl': '!', 'dog': '@'
}
SIMILAR_CHARACTERS = {
        "@": ["a"],
        "!": ["i"],
        "0": ["o"],
        "1": ["i", "l"],
        "3": ["e"],
        "5": ["s"],
        "6": ["b"],
        "7": ["t"],
        "8": ["B"],
        "9": ["g"]
    }

FRAME_QUEUE_SIZE = 2
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

DEFAULT_SIZE = 1500             # Inference image size          (256 - 4096)
DEFAULT_CONF = 0.2              # NMS confidence threshold      (0 - 1)
DEFAULT_IOU = 0.3               # NMS IoU threshold             (0 - 1)
DEFAULT_AGNOSTIC = True         # NMS class-agnostic            (True/False)
DEFAULT_MULTILABEL = False      # NMS multiple labels per box   (True/False)
DEFAULT_MAXDET = 3000           # Max detections per image      (0 - 10000)
DEFAULT_AMP = True              # Automatic Mixed Precision     (True/False)
DEFAULT_HALFPRECISION = True    # Floating Point 16             (True/False)

SIZE_MIN = 256
SIZE_MAX = 4096
CONF_MIN = 0
CONF_MAX = 1
IOU_MIN = 0
IOU_MAX = 1
MAXDET_MIN = 0
MAXDET_MAX = 10000

IMAGE_TYPES = [
    ".bmp",     # Bitmap Image
    ".dib",     # Device-Independent Bitmap
    ".jpeg",    # Joint Photographic Experts Group
    ".jpg",     # Commonly used extension for JPEG images
    ".jpe",     # Another extension for JPEG images
    ".jp2",     # JPEG 2000
    ".png",     # Portable Network Graphics
    ".pbm",     # Portable Bitmap
    ".pgm",     # Portable Graymap
    ".ppm",     # Portable Pixmap
    ".sr",      # Sun Raster
    ".ras",     # Another extension for Sun Raster
    ".tiff",    # Tagged Image File Format
    ".tif",     # Common extension for TIFF images
    ".webp"     # WebP Image
]
VIDEO_TYPES = [
    ".avi",     # Audio Video Interleave
    ".mp4",     # MPEG-4 Part 14
    ".mov",     # QuickTime File Format
    ".mkv",     # Matroska Multimedia Container
    ".flv",     # Flash Video
    ".wmv",     # Windows Media Video
    ".mpeg",    # Moving Picture Experts Group
    ".mpg",     # Common extension for MPEG files
    ".mpe",     # Another extension for MPEG files
    ".m4v",     # MPEG-4 Video File
    ".3gp",     # 3GPP Multimedia File
    ".3g2",     # 3GPP2 Multimedia File
    ".asf",     # Advanced Systems Format
    ".divx",    # DivX Media Format
    ".f4v",     # Flash MP4 Video File
    ".m2ts",    # MPEG-2 Transport Stream
    ".m2v",     # MPEG-2 Video File
    ".m4p",     # MPEG-4 Protected Audio/Video File
    ".mts",     # AVCHD Video File
    ".ogm",     # Ogg Media File
    ".ogv",     # Ogg Video File
    ".qt",      # QuickTime File Format
    ".rm",      # RealMedia File
    ".vob",     # DVD Video Object
    ".webm",    # WebM Video File
    ".xvid"     # Xvid Video Codec
]
ALLOWED_EXTENSIONS = IMAGE_TYPES + VIDEO_TYPES
