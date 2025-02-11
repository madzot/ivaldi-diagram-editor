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

    def test__lock_box__turns_locked_to_true(self):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        self.assertFalse(box.locked)

        box.lock_box()
        self.assertTrue(box.locked)

    def test__unlock_box__turns_locked_to_false(self):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        box.lock_box()
        self.assertTrue(box.locked)

        box.unlock_box()
        self.assertFalse(box.locked)

    def test__select__turns_rect_outline_green(self):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)

        expected_start_color = "black"
        actual_start_color = self.custom_canvas.itemconfig(box.rect)["outline"][-1]
        self.assertEqual(expected_start_color, actual_start_color)

        box.select()
        expected_selected_color = "green"
        actual_selected_color = self.custom_canvas.itemconfig(box.rect)["outline"][-1]
        self.assertEqual(expected_selected_color, actual_selected_color)

    def test__deselect__turns_rect_outline_black(self):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)

        box.select()
        expected_selected_color = "green"
        actual_selected_color = self.custom_canvas.itemconfig(box.rect)["outline"][-1]
        self.assertEqual(expected_selected_color, actual_selected_color)

        box.deselect()
        expected_start_color = "black"
        actual_start_color = self.custom_canvas.itemconfig(box.rect)["outline"][-1]
        self.assertEqual(expected_start_color, actual_start_color)

    def test__move__updates_x_y(self):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        self.assertEqual((100, 100), (box.x, box.y))

        expected_x = 500
        expected_y = 600
        box.move(expected_x, expected_y)
        self.assertEqual((expected_x, expected_y), (box.x, box.y))

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_position")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_connections")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_wires")
    def test__move__calls_out_methods(self, update_wires_mock, update_connections_mock, update_position_mock):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        box.move(100, 100)

        self.assertTrue(update_wires_mock.called)
        self.assertTrue(update_connections_mock.called)
        self.assertTrue(update_position_mock.called)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.is_illegal_move")
    def test__move__checks_for_illegal_move_when_connections_with_wire_exist(self, is_illegal_move_mock):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        box.add_left_connection()
        box.connections[0].has_wire = True

        box.move(100, 100)
        self.assertTrue(is_illegal_move_mock.called)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.is_illegal_move", return_value=True)
    def test__move__if_illegal_doesnt_change_x(self, is_illegal_move_mock):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        box.add_left_connection()
        box.connections[0].has_wire = True

        box.move(500, 600)
        self.assertTrue(is_illegal_move_mock.called)
        self.assertEqual(100, box.x)
        self.assertEqual(600, box.y)

    @patch("tkinter.simpledialog.askstring", return_value="1")
    def test__set_inputs_outputs__asks_user_for_input(self, ask_string_mock):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        box.set_inputs_outputs("_")

        self.assertTrue(ask_string_mock.called)
        self.assertEqual(2, len(box.connections))

    @patch("tkinter.simpledialog.askstring", return_value="2")
    def test__set_inputs_outputs__removes_outputs_if_needed(self, ask_string_mock):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        for i in range(3):
            box.add_left_connection()
            box.add_right_connection()

        self.assertEqual(6, len(box.connections))
        self.assertEqual(3, box.left_connections)
        self.assertEqual(3, box.right_connections)

        box.set_inputs_outputs("_")

        self.assertEqual(2, ask_string_mock.call_count)
        self.assertEqual(4, len(box.connections))
        self.assertEqual(2, box.left_connections)
        self.assertEqual(2, box.right_connections)

    # @patch("MVP.refactored.frontend.canvas_objects.box.Box.change_label")
    # def test__set_label__set

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.tag_bind")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.change_label")
    def test__edit_label__with_param_changes_label(self, change_label_mock, tag_bind_mock):
        box = Box(self.custom_canvas, 100, 100, self.app.receiver)
        tag_bind_mock.call_count = 0  # resetting tag_bind amount from box creation

        expected_label = "new label"
        box.edit_label(expected_label)

        self.assertEqual(expected_label, box.label_text)
        self.assertTrue(change_label_mock.called)
        self.assertEqual(4, tag_bind_mock.call_count)








