# (c) @AbirHasan2005

import os


class Config:
    ENCODING_SPEED_PRESET = str(os.environ.get("ENCODING_SPEED_PRESET", "ultrafast"))  # the encoding speed to "ultrafast" mode, which uses the least amount of CPU and RAM.
    ALLOWED_QUALITIES = "144p, 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p".split(", ")  # change according to your need.
