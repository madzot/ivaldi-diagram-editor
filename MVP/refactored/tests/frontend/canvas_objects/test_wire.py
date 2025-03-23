import tkinter
import unittest
from unittest.mock import patch

from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.canvas_objects.spider import Spider
from MVP.refactored.frontend.canvas_objects.types.wire_types import WireType
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

    @patch.object(Wire, 'update')
    def test__init__values(self, update_mock):
        self.custom_canvas.add_spider((100, 100))
        self.custom_canvas.add_spider((200, 200))
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.spiders[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.spiders[1])

        wire = self.custom_canvas.wires[0]

        self.assertEqual(self.custom_canvas.spiders[0], wire.start_connection)
        self.assertEqual(self.custom_canvas.spiders[1], wire.end_connection)
        self.assertEqual(3, wire.wire_width)
        self.assertIsNone(wire.line)
        self.assertFalse(wire.is_temporary)
        self.assertEqual(WireType.GENERIC, wire.type)
        self.assertEqual(2, update_mock.call_count)

    def test__delete_self__removes_self_spider_wires(self):
        self.custom_canvas.add_spider((100, 100))
        self.custom_canvas.add_spider((200, 200))
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.spiders[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.spiders[1])

        wire = self.custom_canvas.wires[0]

        for wire in self.custom_canvas.wires:
            self.assertIn(wire, self.custom_canvas.spiders[0].wires)
            self.assertIn(wire, self.custom_canvas.spiders[1].wires)

            wire.delete_self()

            self.assertFalse(self.custom_canvas.spiders[0].has_wire)
            self.assertFalse(self.custom_canvas.spiders[1].has_wire)
            self.assertNotIn(wire, self.custom_canvas.spiders[0].wires)
            self.assertNotIn(wire, self.custom_canvas.spiders[1].wires)

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
        self.custom_canvas.add_spider((100, 100))
        self.custom_canvas.add_spider((200, 200))
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.spiders[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.spiders[1])

        wire = self.custom_canvas.wires[0]

        expected_start_color = "black"
        actual_start_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_start_color, actual_start_color)

        wire.select()

        expected_end_color = "green"
        actual_end_color = self.custom_canvas.itemconfig(wire.line)['fill'][-1]
        self.assertEqual(expected_end_color, actual_end_color)

    def test__deselect__turn_line_original(self):
        self.custom_canvas.add_spider((100, 100))
        self.custom_canvas.add_spider((200, 200))
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.spiders[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.spiders[1])

        wire = self.custom_canvas.wires[0]

        wire.select()

        expected_start_color = "green"
        actual_start_color = self.custom_canvas.itemconfig(wire.line)['fill'][-1]
        self.assertEqual(expected_start_color, actual_start_color)

        wire.deselect()

        expected_end_color = "black"
        actual_end_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_end_color, actual_end_color)

    def test__search_highlight_secondary__turns_line_orange(self):
        self.custom_canvas.add_spider((100, 100))
        self.custom_canvas.add_spider((200, 200))
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.spiders[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.spiders[1])

        wire = self.custom_canvas.wires[0]

        expected_start_color = "black"
        actual_start_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_start_color, actual_start_color)

        wire.search_highlight_secondary()

        expected_end_color = "orange"
        actual_end_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_end_color, actual_end_color)

    def test__search_highlight_primary__turns_line_cyan(self):
        self.custom_canvas.add_spider((100, 100))
        self.custom_canvas.add_spider((200, 200))
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.spiders[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.spiders[1])

        wire = self.custom_canvas.wires[0]

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
        self.custom_canvas.add_spider((100, 200))
        self.custom_canvas.add_spider((200, 400))
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.spiders[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.spiders[1])

        wire = self.custom_canvas.wires[0]

        event = tkinter.Event()
        event.x_root, event.y_root = 150, 300

        wire.show_context_menu(event)

        self.assertEqual(1, close_menu_mock.call_count)
        self.assertEqual(4, add_command_mock.call_count)
        self.assertEqual(1, post_mock.call_count)

    @patch("tkinter.Menu.destroy")
    def test__close_context_menu__closes(self, destroy_mock):
        self.custom_canvas.add_spider((100, 100))
        self.custom_canvas.add_spider((200, 200))
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.spiders[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.spiders[1])

        wire = self.custom_canvas.wires[0]

        wire.context_menu = tkinter.Menu()

        wire.close_menu()

        self.assertTrue(destroy_mock.called)

    def test__create_spider__creates_spider(self):
        self.custom_canvas.add_spider((100, 200))
        self.custom_canvas.add_spider((200, 400))
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.spiders[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.spiders[1])

        wire = self.custom_canvas.wires[0]

        self.assertEqual(2, len(self.custom_canvas.spiders))

        event = tkinter.Event()
        event.x, event.y = 150, 300

        wire.create_spider(event)

        spider = self.custom_canvas.spiders[2]

        self.assertEqual(3, len(self.custom_canvas.spiders))
        self.assertEqual(150, spider.x)
        self.assertEqual(300, spider.y)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.tag_bind")
    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.update_wire_label")
    def test__update__calls_bind_event(self, update_wire_label_mock, bind_events_mock):
        self.custom_canvas.add_spider((100, 100))
        self.custom_canvas.add_spider((200, 200))
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.spiders[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.spiders[1])

        wire = self.custom_canvas.wires[0]

        self.assertTrue(bind_events_mock.called)
        self.assertTrue(update_wire_label_mock.called)

    @patch("tkinter.simpledialog.askstring", return_value="String")
    def test__define_type__with_param_define_type(self, ask_string_mock):
        self.custom_canvas.add_spider((100, 100))
        self.custom_canvas.add_spider((200, 200))
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.spiders[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.spiders[1])

        wire = self.custom_canvas.wires[0]

        wire.define_type()

        self.assertTrue(ask_string_mock.called)

        self.assertEqual(Wire.defined_wires[wire.type.name], "String")

    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.delete_labels")
    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.update_wire_label")
    @patch("tkinter.simpledialog.askstring",  return_value=None)
    def test__define_type__canceled(self, ask_string_mock, update_wire_label_mock, delete_labels_mock):
        self.custom_canvas.add_spider((100, 100))
        self.custom_canvas.add_spider((200, 200))
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.spiders[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.spiders[1])

        wire = self.custom_canvas.wires[0]

        update_wire_label_mock.call_count = 0

        wire.define_type()

        self.assertEqual(update_wire_label_mock.call_count, 0)
        self.assertFalse(delete_labels_mock.called)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.delete")
    @patch("tkinter.simpledialog.askstring", return_value="Int")
    def test__delete_label__delete_standard(self, ask_string_mock, delete_mock):
        self.custom_canvas.add_diagram_output()
        self.custom_canvas.add_diagram_input()
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.inputs[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.outputs[0])
        wire = self.custom_canvas.wires[0]

        wire.define_type()

        self.assertIsNotNone(wire.start_label)
        self.assertIsNotNone(wire.end_label)

        wire.delete_labels()

        self.assertIsNone(wire.start_label)
        self.assertIsNone(wire.end_label)
        self.assertEqual(delete_mock.call_count, 2)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.itemconfig")
    @patch("tkinter.simpledialog.askstring", return_value="Int")
    @patch("tkinter.simpledialog.askstring", return_value="String")
    def test__update_wire_label__existing_labels(self, ask_string_mock1, ask_string_mock2, itemconfig_mock):
        self.custom_canvas.add_diagram_output()
        self.custom_canvas.add_diagram_input()
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.inputs[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.outputs[0])
        wire = self.custom_canvas.wires[0]

        itemconfig_mock.call_count = 0

        wire.define_type()

        self.assertEqual(len(self.custom_canvas.wire_label_tags), 2)

        wire.define_type()

        self.assertEqual(self.custom_canvas.itemcget(self.custom_canvas.wire_label_tags[1], "text"), "Int")

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.create_text")
    @patch("tkinter.simpledialog.askstring", return_value="Int")
    def test__update_wire_label_creates__new_labels(self, ask_string_mock, create_text_mock):
        self.custom_canvas.add_diagram_output()
        self.custom_canvas.add_diagram_input()
        self.custom_canvas.start_wire_from_connection(self.custom_canvas.inputs[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.outputs[0])
        wire = self.custom_canvas.wires[0]

        wire.define_type()

        self.assertEqual(len(self.custom_canvas.wire_label_tags), 2)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.itemconfig")
    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.create_text")
    @patch("tkinter.simpledialog.askstring", return_value="Int")
    def test__update_wire_label__does_not_create_for_spiders(self, ask_string_mock, itemconfig_mock, create_text_mock):
        self.custom_canvas.add_spider((100, 100))
        self.custom_canvas.add_spider((200, 200))

        self.custom_canvas.start_wire_from_connection(self.custom_canvas.spiders[0])
        self.custom_canvas.end_wire_to_connection(self.custom_canvas.spiders[1])

        wire = self.custom_canvas.wires[0]

        itemconfig_mock.call_count = 0
        create_text_mock.call_count = 0

        wire.update_wire_label()

        self.assertEqual(itemconfig_mock.call_count, 0)
        self.assertEqual(create_text_mock.call_count, 0)
