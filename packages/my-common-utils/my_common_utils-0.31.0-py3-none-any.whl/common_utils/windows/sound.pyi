from _typeshed import Incomplete
from common_utils.config import ROOT_DIR as ROOT_DIR

class SoundHandler:
    default_volume: Incomplete
    def __init__(self, default_volume) -> None: ...
    def play_sound(self, file_path, volume: Incomplete | None = None) -> None: ...
