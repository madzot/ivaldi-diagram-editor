from abc import ABC, abstractmethod
from typing import TextIO

from MVP.refactored.custom_canvas import CustomCanvas


class Importer(ABC):

    def __init__(self, canvas):
        self.canvas: CustomCanvas = canvas

    @abstractmethod
    def start_import(self, file: TextIO):
        pass

    @abstractmethod
    def load_everything_to_canvas(self, data, canvas):
        pass
