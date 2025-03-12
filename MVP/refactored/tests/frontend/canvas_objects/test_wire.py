import tkinter
import unittest
from unittest.mock import patch

from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.canvas_objects.spider import Spider
from MVP.refactored.frontend.canvas_objects.wire import Wire
from MVP.refactored.frontend.windows.main_diagram import MainDiagram


class TestApplication(unittest.TestCase):

    async def _start_app(self):
        self.app.mainloop()

    def setUp(self):
        self.app = MainDiagram(Receiver())
        self.custom_canvas = self.app.custom_canvas
        self._start_app()

    def tearDown(self):
        self.app.destroy()


class WireTest(TestApplication):
    def test__init__values(self):
        connection_start = Spider(None, 1010, 'spider', (111, 222), self.custom_canvas, self.app.receiver)
        connection_end = Spider(None, 1011, 'spider', (222, 444), self.custom_canvas, self.app.receiver)
        wire = Wire(self.custom_canvas, connection_start, self.app.receiver, connection_end)

        self.assertEqual(connection_start, wire.start_connection)
        self.assertEqual(connection_end, wire.end_connection)
        self.assertEqual(3, wire.wire_width)
        self.assertIsNotNone(wire.line)
        self.assertFalse(wire.is_temporary)

    @patch.object(Wire, 'update')
    def test__init__calls_update(self, update_mock):
        connection_start = Spider(None, 1010, 'spider', (100, 200), self.custom_canvas, self.app.receiver)
        connection_end = Spider(None, 1011, 'spider', (200, 400), self.custom_canvas, self.app.receiver)
        wire = Wire(self.custom_canvas, connection_start, self.app.receiver, connection_end)

        self.assertEqual(1, update_mock.call_count)

    def test__delete_self__removes_self_spider_wires(self):
        connection_start = Spider(None, 1010, 'spider', (111, 222), self.custom_canvas, self.app.receiver)
        connection_end = Spider(None, 1011, 'spider', (222, 444), self.custom_canvas, self.app.receiver)
        self.custom_canvas.start_wire_from_connection(connection_start)
        self.custom_canvas.end_wire_to_connection(connection_end)

        for wire in self.custom_canvas.wires:
            self.assertIn(wire, connection_start.wires)
            self.assertIn(wire, connection_end.wires)

            wire.delete_self()

            self.assertFalse(connection_start.has_wire)
            self.assertFalse(connection_end.has_wire)
            self.assertNotIn(wire, connection_start.wires)
            self.assertNotIn(wire, connection_end.wires)

    def test__delete_self__removes_self_connection_wire(self):
        self.custom_canvas.add_diagram_output()
        self.custom_canvas.add_diagram_input()
        canvas_input = self.custom_canvas.inputs[0]
        canvas_output = self.custom_canvas.outputs[0]
        self.custom_canvas.start_wire_from_connection(canvas_input)
        self.custom_canvas.end_wire_to_connection(canvas_output)

        for wire in self.custom_canvas.wires:
            self.assertTrue(canvas_input.has_wire)
            self.assertTrue(canvas_output.has_wire)
            self.assertEqual(wire, canvas_input.wire)
            self.assertEqual(wire, canvas_output.wire)

            wire.delete_self()

            self.assertFalse(canvas_input.has_wire)
            self.assertFalse(canvas_output.has_wire)
            self.assertIsNone(canvas_input.wire)
            self.assertIsNone(canvas_output.wire)

    def test__select__turn_line_green(self):
        connection_start = Spider(None, 1010, 'spider', (111, 222), self.custom_canvas, self.app.receiver)
        connection_end = Spider(None, 1011, 'spider', (222, 444), self.custom_canvas, self.app.receiver)
        wire = Wire(self.custom_canvas, connection_start, self.app.receiver, connection_end)

        expected_start_color = "black"
        actual_start_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_start_color, actual_start_color)

        wire.select()

        expected_end_color = "green"
        actual_end_color = self.custom_canvas.itemconfig(wire.line)['fill'][-1]
        self.assertEqual(expected_end_color, actual_end_color)

    def test__deselect__turn_line_original(self):
        connection_start = Spider(None, 1010, 'spider', (111, 222), self.custom_canvas, self.app.receiver)
        connection_end = Spider(None, 1011, 'spider', (222, 444), self.custom_canvas, self.app.receiver)
        wire = Wire(self.custom_canvas, connection_start, self.app.receiver, connection_end)

        wire.select()

        expected_start_color = "green"
        actual_start_color = self.custom_canvas.itemconfig(wire.line)['fill'][-1]
        self.assertEqual(expected_start_color, actual_start_color)

        wire.deselect()

        expected_end_color = "black"
        actual_end_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_end_color, actual_end_color)

    def test__search_highlight_secondary__turns_line_orange(self):
        connection_start = Spider(None, 1010, 'spider', (111, 222), self.custom_canvas, self.app.receiver)
        connection_end = Spider(None, 1011, 'spider', (222, 444), self.custom_canvas, self.app.receiver)
        wire = Wire(self.custom_canvas, connection_start, self.app.receiver, connection_end)

        expected_start_color = "black"
        actual_start_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_start_color, actual_start_color)

        wire.search_highlight_secondary()

        expected_end_color = "orange"
        actual_end_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_end_color, actual_end_color)

    def test__search_highlight_primary__turns_line_cyan(self):
        connection_start = Spider(None, 1010, 'spider', (111, 222), self.custom_canvas, self.app.receiver)
        connection_end = Spider(None, 1011, 'spider', (222, 444), self.custom_canvas, self.app.receiver)
        wire = Wire(self.custom_canvas, connection_start, self.app.receiver, connection_end)

        expected_start_color = "black"
        actual_start_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_start_color, actual_start_color)

        wire.search_highlight_primary()

        expected_end_color = "cyan"
        actual_end_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_end_color, actual_end_color)

    @patch("tkinter.Menu.add_command")
    @patch("tkinter.Menu.post")
    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.close_menu")
    def test__show_context_menu__callouts(self, post_mock, close_menu_mock, add_command_mock):
        connection_start = Spider(None, 1010, 'spider', (100, 200), self.custom_canvas, self.app.receiver)
        connection_end = Spider(None, 1011, 'spider', (200, 400), self.custom_canvas, self.app.receiver)
        wire = Wire(self.custom_canvas, connection_start, self.app.receiver, connection_end)

        event = tkinter.Event()
        event.x_root, event.y_root = 150, 300

        wire.show_context_menu(event)

        self.assertEqual(1, close_menu_mock.call_count)
        self.assertEqual(3, add_command_mock.call_count)
        self.assertEqual(1, post_mock.call_count)

    @patch("tkinter.Menu.destroy")
    def test__close_context_menu__closes(self, destroy_mock):
        connection_start = Spider(None, 1010, 'spider', (100, 200), self.custom_canvas, self.app.receiver)
        connection_end = Spider(None, 1011, 'spider', (200, 400), self.custom_canvas, self.app.receiver)
        wire = Wire(self.custom_canvas, connection_start, self.app.receiver, connection_end)

        wire.context_menu = tkinter.Menu()

        wire.close_menu()

        self.assertTrue(destroy_mock.called)

    def test__create_spider__creates_spider(self):
        connection_start = Spider(None, 1010, 'spider', (100, 200), self.custom_canvas, self.app.receiver)
        connection_end = Spider(None, 1011, 'spider', (200, 400), self.custom_canvas, self.app.receiver)
        wire = Wire(self.custom_canvas, connection_start, self.app.receiver, connection_end)

        self.assertEqual(0, len(self.custom_canvas.spiders))

        event = tkinter.Event()
        event.x, event.y = 150, 300

        wire.create_spider(event)

        spider = self.custom_canvas.spiders[0]

        self.assertEqual(1, len(self.custom_canvas.spiders))
        self.assertEqual(150, spider.x)
        self.assertEqual(300, spider.y)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.tag_bind")
    def test__update__calls_bind_event(self, bind_events_mock):
        connection_start = Spider(None, 1010, 'spider', (100, 200), self.custom_canvas, self.app.receiver)
        connection_end = Spider(None, 1011, 'spider', (200, 400), self.custom_canvas, self.app.receiver)
        wire = Wire(self.custom_canvas, connection_start, self.app.receiver, connection_end)

        self.assertTrue(bind_events_mock.called)
