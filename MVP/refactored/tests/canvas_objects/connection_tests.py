import tkinter
import unittest
from unittest.mock import patch

from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.canvas_objects.connection import Connection
from MVP.refactored.frontend.windows.main_diagram import MainDiagram
from MVP.refactored.frontend.canvas_objects.box import Box


class TestApplication(unittest.TestCase):

    async def _start_app(self):
        self.app.mainloop()

    def setUp(self):
        self.app = MainDiagram(Receiver())
        self.custom_canvas = self.app.custom_canvas
        self._start_app()

    def tearDown(self):
        self.app.destroy()


class ConnectionTests(TestApplication):

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.bind_events')
    def test__init__values(self, bind_events_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)

        self.assertIsNone(connection.box)
        self.assertEqual(1010, connection.index)
        self.assertEqual("left", connection.side)
        self.assertEqual((111, 222), connection.location)
        self.assertIsNone(connection.wire)
        self.assertFalse(connection.has_wire)
        self.assertEqual(5, connection.r)
        self.assertIsNone(connection.node)
        self.assertEqual(1, connection.width_between_boxes)
        self.assertTrue(bind_events_mock.called)

    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.tag_bind')
    def test__bind_events__number_of_tag_binds(self, tag_bind_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        tag_bind_mock.call_count = 0
        connection.bind_events()
        self.assertEqual(1, tag_bind_mock.call_count)

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.close_menu')
    @patch('tkinter.Menu.add_command')
    @patch('tkinter.Menu.post')
    def test__show_context_menu__closes_if_no_box(self, post_mock, add_command_mock, close_menu_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        event = tkinter.Event()
        event.x_root, event.y_root = 10, 10
        connection.show_context_menu(event)

        self.assertTrue(close_menu_mock.called)
        self.assertFalse(add_command_mock.called)
        self.assertFalse(post_mock.called)

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.close_menu')
    @patch('tkinter.Menu.add_command')
    @patch('tkinter.Menu.post')
    def test__show_context_menu__closes_if_locked_box(self, post_mock, add_command_mock, close_menu_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        connection.box = Box(self.custom_canvas, 10, 10, self.app.receiver)
        connection.box.locked = True
        event = tkinter.Event()
        event.x_root, event.y_root = 10, 10
        connection.show_context_menu(event)

        self.assertTrue(close_menu_mock.called)
        self.assertFalse(add_command_mock.called)
        self.assertFalse(post_mock.called)

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.close_menu')
    @patch('tkinter.Menu.add_command')
    @patch('tkinter.Menu.post')
    def test__show_context_menu__calls_all_if_has_box(self, post_mock, add_command_mock, close_menu_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        connection.box = Box(self.custom_canvas, 10, 10, self.app.receiver)
        event = tkinter.Event()
        event.x_root, event.y_root = 10, 10
        connection.show_context_menu(event)

        self.assertTrue(close_menu_mock.called)
        self.assertEqual(2, add_command_mock.call_count)
        self.assertEqual(1, post_mock.call_count)

    @patch('tkinter.Menu.destroy')
    def test__close_menu__destroys_menu(self, destroy_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)

        connection.close_menu()
        self.assertTrue(destroy_mock.called)
