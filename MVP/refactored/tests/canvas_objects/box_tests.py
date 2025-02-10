import tkinter
import unittest
from unittest.mock import patch

from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.windows.main_diagram import MainDiagram
from MVP.refactored.frontend.canvas_objects.box import Box


class TestMainDiagram(unittest.TestCase):

    async def _start_app(self):
        self.app.mainloop()

    def setUp(self):
        self.app = MainDiagram(Receiver())
        self.custom_canvas = self.app.custom_canvas
        self._start_app()

    def tearDown(self):
        self.app.destroy()


class BoxTests(TestMainDiagram):
    def test__init__values(self):
        expected_x = 25
        expected_y = 50

        expected_width = 100
        expected_height = 125

        box = Box(self.custom_canvas, expected_x, expected_y, self.app.receiver, size=(expected_width, expected_height))

        self.assertEqual(expected_x, box.x)
        self.assertEqual(expected_y, box.y)

        self.assertEqual((expected_width, expected_height), box.size)

        self.assertFalse(box.connections)

        self.assertEqual(0, box.left_connections)
        self.assertEqual(0, box.right_connections)

        self.assertIsNone(box.label)

        self.assertFalse(box.label_text)
        self.assertFalse(box.wires)

        self.assertIsNone(box.node)

        self.assertTrue(isinstance(box.context_menu, tkinter.Menu))

        self.assertFalse(False, box.locked)

        self.assertIsNone(box.sub_diagram)

        self.assertFalse(box.is_snapped)

        self.assertEqual(expected_x, box.start_x)
        self.assertEqual(expected_y, box.start_y)
        self.assertEqual(0, box.x_dif)
        self.assertEqual(0, box.y_dif)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_position")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_connections")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_wires")
    def test__update_size__changes_size(self, mock, mock2, mock3):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        expected_size = (100, 100)
        box.update_size(expected_size[0], expected_size[1])
        self.assertEqual(expected_size, box.size)
        self.assertTrue(mock.called)
        self.assertTrue(mock2.called)
        self.assertTrue(mock3.called)

    def test__add_left_connection__adds_connection(self):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        box.add_left_connection()

        self.assertEqual(1, len(box.connections))
        self.assertEqual(1, box.left_connections)
        self.assertEqual(0, box.right_connections)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_connections")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_wires")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.resize_by_connections")
    def test__add_left_connection__calls_other_methods(self,
                                                       resize_by_connections_mock,
                                                       update_wires_mock,
                                                       update_connections_mock):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        box.add_left_connection()

        self.assertTrue(resize_by_connections_mock.called)
        self.assertTrue(update_wires_mock.called)
        self.assertTrue(update_connections_mock.called)

    def test__add_right_connection__adds_connection(self):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        box.add_right_connection()

        self.assertEqual(1, len(box.connections))
        self.assertEqual(1, box.right_connections)
        self.assertEqual(0, box.left_connections)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_connections")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_wires")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.resize_by_connections")
    def test__add_right_connection__calls_other_methods(self,
                                                        resize_by_connections_mock,
                                                        update_wires_mock,
                                                        update_connections_mock):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        box.add_right_connection()

        self.assertTrue(resize_by_connections_mock.called)
        self.assertTrue(update_wires_mock.called)
        self.assertTrue(update_connections_mock.called)
