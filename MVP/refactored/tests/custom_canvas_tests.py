import tkinter
import unittest

from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.components.custom_canvas import CustomCanvas
from MVP.refactored.frontend.windows.main_diagram import MainDiagram


class TestCustomCanvas(unittest.TestCase):

    async def _start_app(self):
        self.app.mainloop()

    def setUp(self):
        self.app = MainDiagram(Receiver())
        self.custom_canvas = self.app.custom_canvas
        self._start_app()

    def tearDown(self):
        self.app.destroy()


class Tests(TestCustomCanvas):
    def test_placeholder(self):
        self.assertTrue(isinstance(self.custom_canvas, CustomCanvas))



