import tkinter
import unittest
from unittest.mock import patch

from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.canvas_objects.connection import Connection
from MVP.refactored.frontend.canvas_objects.wire import Wire
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
        self.assertEqual(2, tag_bind_mock.call_count)

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.add_type_choice')
    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.close_menu')
    @patch('tkinter.Menu.add_command')
    @patch('tkinter.Menu.tk_popup')
    def test__show_context_menu__shows_if_no_box(self, tk_popup_mock, add_command_mock, close_menu_mock, type_choice_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        event = tkinter.Event()
        event.x_root, event.y_root = 10, 10
        connection.show_context_menu(event)

        self.assertTrue(close_menu_mock.called)
        self.assertTrue(type_choice_mock.called)
        self.assertEqual(2, add_command_mock.call_count)
        self.assertEqual(1, tk_popup_mock.call_count)

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

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.add_type_choice')
    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.close_menu')
    @patch('tkinter.Menu.add_command')
    @patch('tkinter.Menu.tk_popup')
    def test__show_context_menu__calls_all_if_has_box(self, tk_popup, add_command_mock,
                                                      close_menu_mock, type_choice_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        connection.box = Box(self.custom_canvas, 10, 10, self.app.receiver)
        event = tkinter.Event()
        event.x_root, event.y_root = 10, 10
        connection.show_context_menu(event)

        self.assertTrue(close_menu_mock.called)
        self.assertTrue(type_choice_mock.called)
        self.assertEqual(2, add_command_mock.call_count)
        self.assertEqual(1, tk_popup.call_count)

    @patch('tkinter.Menu.destroy')
    def test__close_menu__destroys_menu(self, destroy_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)

        connection.close_menu()
        self.assertTrue(destroy_mock.called)

    @patch('MVP.refactored.frontend.canvas_objects.box.Box.remove_connection')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_output')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_input')
    def test__delete_from_parent__has_box_is_input(self, input_mock, output_mock, remove_connection_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        connection.box = Box(self.custom_canvas, 10, 10, self.app.receiver)
        connection.box.sub_diagram = self.custom_canvas
        self.custom_canvas.diagram_source_box = connection.box
        connection.box.connections.append(connection)
        self.custom_canvas.inputs.append(connection)

        connection.delete_from_parent()

        self.assertTrue(input_mock.called)

    @patch('MVP.refactored.frontend.canvas_objects.box.Box.remove_connection')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_output')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_input')
    def test__delete_from_parent__no_call_if_not_in_canvas_inputs(self, input_mock, output_mock, remove_connection_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        connection.box = Box(self.custom_canvas, 10, 10, self.app.receiver)
        connection.box.sub_diagram = self.custom_canvas
        connection.box.connections.append(connection)

        connection.delete_from_parent()

        self.assertFalse(input_mock.called)
        self.assertTrue(remove_connection_mock.called)

    @patch('MVP.refactored.frontend.canvas_objects.box.Box.remove_connection')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_output')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_input')
    def test__delete_from_parent__wrong_side_is_not_called_in_diagram_removal(self, input_mock, output_mock, remove_connection_mock):
        connection = Connection(None, 1010, "right", (111, 222), self.custom_canvas)
        connection.box = Box(self.custom_canvas, 10, 10, self.app.receiver)
        connection.box.sub_diagram = self.custom_canvas
        connection.box.connections.append(connection)
        self.custom_canvas.inputs.append(connection)

        connection.delete_from_parent()

        self.assertFalse(input_mock.called)
        self.assertFalse(output_mock.called)
        self.assertTrue(remove_connection_mock.called)

    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_output')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_input')
    def test__delete_from_parent__right_calls_output(self, input_mock, output_mock):
        connection = Connection(None, 1010, "right", (111, 222), self.custom_canvas)
        connection.box = Box(self.custom_canvas, 10, 10, self.app.receiver)
        connection.box.sub_diagram = self.custom_canvas
        connection.box.connections.append(connection)
        self.custom_canvas.outputs.append(connection)

        connection.delete_from_parent()

        self.assertFalse(input_mock.called)
        self.assertTrue(output_mock.called)

    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_input')
    def test__delete_from_parent__without_box_is_input(self, input_mock):
        connection = Connection(None, 1010, "right", (111, 222), self.custom_canvas)
        self.custom_canvas.inputs.append(connection)

        connection.delete_from_parent()

        self.assertTrue(input_mock.called)

    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_output')
    def test__delete_from_parent__without_box_is_output(self, output_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        self.custom_canvas.outputs.append(connection)

        connection.delete_from_parent()

        self.assertTrue(output_mock.called)

    def test__color_black__changes_config_fill_to_black(self):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        connection.color_black()
        config = self.custom_canvas.itemconfig(connection.circle)["fill"]
        self.assertTrue('black' in config)

    def test__color_green__changes_config_fill_to_green(self):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        connection.color_green()
        config = self.custom_canvas.itemconfig(connection.circle)["fill"]
        self.assertTrue('green' in config)

    def test__move_to__changes_location(self):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        connection.move_to((1010, 2020))
        self.assertEqual(1010, connection.location[0])
        self.assertEqual(2020, connection.location[1])

    def test__lessen_index_by_one__lowers_index(self):
        connection = Connection(None, 2, "left", (111, 222), self.custom_canvas)

        connection.lessen_index_by_one()

        self.assertEqual(1, connection.index)

    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.delete')
    def test__delete__no_wire_calls_delete_once(self, delete_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        connection.delete()

        self.assertEqual(1, delete_mock.call_count)

    @patch('MVP.refactored.frontend.canvas_objects.wire.Wire.delete_self')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.delete')
    def test__delete__has_wire_calls_delete_twice(self, delete_mock, delete_self_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection, self.app.receiver, None, temporary=True)
        connection.wire = wire
        connection.has_wire = True
        connection.delete()

        self.assertEqual(2, delete_mock.call_count)
        self.assertEqual(1, delete_self_mock.call_count)

    def test__add_wire__adds_wire(self):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        connection2 = Connection(None, 1011, "right", (222, 222), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection, self.app.receiver, connection2, temporary=True)
        self.assertIsNone(connection.wire)
        self.assertFalse(connection.has_wire)

        connection.add_wire(wire)
        self.assertEqual(wire, connection.wire)
        self.assertTrue(connection.has_wire)

    def test__add_wire__does_not_change_wire_if_connection_has_wire(self):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        connection2 = Connection(None, 1011, "right", (222, 222), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection, self.app.receiver, connection2, temporary=True)
        wire2 = Wire(self.custom_canvas, connection2, self.app.receiver, connection, temporary=True)

        connection.add_wire(wire)

        connection.add_wire(wire2)

        self.assertEqual(wire, connection.wire)
        self.assertTrue(connection.has_wire)

    def test__is_spider__returns_false(self):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        self.assertFalse(connection.is_spider())

    def test__remove_wire__removes_wire(self):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        connection2 = Connection(None, 1011, "right", (222, 222), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection, self.app.receiver, connection2, temporary=True)

        connection.add_wire(wire)
        self.assertEqual(wire, connection.wire)
        self.assertTrue(connection.has_wire)

        connection.remove_wire(wire)
        self.assertIsNone(connection.wire)
        self.assertFalse(connection.has_wire)

    def test__select__turns_item_green(self):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        self.assertTrue("black" in self.custom_canvas.itemconfig(connection.circle)["fill"])

        connection.select()
        self.assertTrue("green" in self.custom_canvas.itemconfig(connection.circle)["fill"])

    def test__search_highlight_secondary__turns_item_orange_and_adds_to_search_highlights(self):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        self.assertTrue("black" in self.custom_canvas.itemconfig(connection.circle)["fill"])
        self.assertListEqual([], self.custom_canvas.search_result_highlights)

        connection.search_highlight_secondary()
        self.assertTrue("orange" in self.custom_canvas.itemconfig(connection.circle)["fill"])
        self.assertListEqual([connection], self.custom_canvas.search_result_highlights)

    def test__search_highlight_primary__turns_item_cyan_and_adds_to_search_highlights(self):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        self.assertTrue("black" in self.custom_canvas.itemconfig(connection.circle)["fill"])
        self.assertListEqual([], self.custom_canvas.search_result_highlights)

        connection.search_highlight_primary()
        self.assertTrue("cyan" in self.custom_canvas.itemconfig(connection.circle)["fill"])
        self.assertListEqual([connection], self.custom_canvas.search_result_highlights)

    def test__deselect__turns_item_black(self):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)
        connection.select()
        self.assertTrue("green" in self.custom_canvas.itemconfig(connection.circle)["fill"])
        self.assertFalse("black" in self.custom_canvas.itemconfig(connection.circle)["fill"])

        connection.deselect()
        self.assertFalse("green" in self.custom_canvas.itemconfig(connection.circle)["fill"])
        self.assertTrue("black" in self.custom_canvas.itemconfig(connection.circle)["fill"])
