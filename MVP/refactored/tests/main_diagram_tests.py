import unittest

from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.windows.main_diagram import MainDiagram


class TestMainDiagram(unittest.TestCase):

    async def _start_app(self):
        self.app.mainloop()

    def setUp(self):
        self.app = MainDiagram(Receiver())
        self._start_app()

    def tearDown(self):
        self.app.destroy()


class Test(TestMainDiagram):

    def test__init_title(self):
        expected = "Dynamic String Diagram Canvas"
        actual = self.app.title()
        self.assertEqual(expected, actual)

    def test__init_tree_hidden(self):
        expected = False
        actual = self.app.is_tree_visible
        self.assertEqual(expected, actual)

    def test__init_creates_1_custom_canvas(self):
        expected_size = 1
        actual_size = len(self.app.canvasses)
        self.assertEqual(expected_size, actual_size)

    def test__init_adds_custom_canvas_to_canvases(self):
        expected_key = self.app.custom_canvas.id
        expected_value = self.app.custom_canvas
        actual_item = list(self.app.canvasses.items())[0]
        actual_key = int(actual_item[0])
        actual_value = actual_item[1]
        self.assertEqual(expected_key, actual_key)
        self.assertEqual(expected_value, actual_value)

    def test__add_input__adds_input(self):
        self.app.add_diagram_input()
        expected = 1
        actual = len(self.app.custom_canvas.inputs)
        self.assertEqual(expected, actual, "Inputs are not added correctly")

    def test__add_input__adds_input_2(self):
        self.app.add_diagram_input()
        self.app.add_diagram_input()
        expected = 2
        actual = len(self.app.custom_canvas.inputs)
        self.assertEqual(expected, actual, "Inputs are not added correctly")

    def test__remove_input__removes_input(self):
        self.app.add_diagram_input()
        self.app.remove_diagram_input()
        expected = 0
        actual = len(self.app.custom_canvas.inputs)
        self.assertEqual(expected, actual, "Inputs are not removed correctly")

    def test__remove_input__removes_input_2(self):
        self.app.add_diagram_input()
        self.app.add_diagram_input()
        self.app.remove_diagram_input()
        expected = 1
        actual = len(self.app.custom_canvas.inputs)
        self.assertEqual(expected, actual, "Inputs are not removed correctly")

    def test__add_output__adds_output(self):
        self.app.add_diagram_output()
        expected = 1
        actual = len(self.app.custom_canvas.outputs)
        self.assertEqual(expected, actual, "Outputs are not added correctly")

    def test__add_output__adds_output_2(self):
        self.app.add_diagram_output()
        self.app.add_diagram_output()
        expected = 2
        actual = len(self.app.custom_canvas.outputs)
        self.assertEqual(expected, actual, "Outputs are not added correctly")

    def test__remove_output__removes_output(self):
        self.app.add_diagram_output()
        self.app.add_diagram_input()
        self.app.remove_diagram_output()
        expected = 0
        actual = len(self.app.custom_canvas.outputs)
        self.assertEqual(expected, actual, "Outputs are not removed correctly")

    def test__remove_output__removes_output_2(self):
        self.app.add_diagram_output()
        self.app.add_diagram_output()
        self.app.remove_diagram_output()
        expected = 1
        actual = len(self.app.custom_canvas.outputs)
        self.assertEqual(expected, actual, "Outputs are not removed correctly")

    # def test_load_functions():
    #     assert False
    #
    #
    # def test_generate_code():
    #     assert False
    #
    #
    # def test_open_manage_methods_window():
    #     assert False
    #
    #
    # def test_change_function_label():
    #     assert False
    #
    #
    # def test_create_algebraic_notation():
    #     assert False
    #
    #
    # def test_visualize_as_graph():
    #     assert False
    #
    #
    # def test_copy_to_clipboard():
    #     assert False
    #
    #
    # def test_open_children():
    #     assert False
    #
    #
    # def test_bind_buttons():
    #     assert False
    #
    #
    # def test_add_canvas():
    #     assert False
    #
    #
    # def test_get_canvas_by_id():
    #     assert False
    #
    #
    # def test_change_canvas_name():
    #     assert False
    #
    #
    # def test_rename():
    #     assert False
    #
    #
    # def test_switch_canvas():
    #     assert False
    #
    #
    # def test_del_from_canvasses():
    #     assert False
    #
    #
    # def test_on_tree_select():
    #     assert False
    #
    #
    # def test_add_diagram_input():
    #     assert False
    #
    #
    # def test_add_diagram_output():
    #     assert False
    #
    #
    # def test_remove_diagram_input():
    #     assert False
    #
    #
    # def test_remove_diagram_output():
    #     assert False
    #
    #
    # def test_find_connection_to_remove():
    #     assert False
    #
    #
    # def test_manage_boxes_method():
    #     assert False
    #
    #
    # def test_manage_quick_create():
    #     assert False
    #
    #
    # def test_update_dropdown_menu():
    #     assert False
    #
    #
    # def test_remove_option():
    #     assert False
    #
    #
    # def test_get_boxes_from_file():
    #     assert False
    #
    #
    # def test_add_custom_box():
    #     assert False
    #
    #
    # def test_save_box_to_diagram_menu():
    #     assert False
    #
    #
    # def test_set_title():
    #     assert False
    #
    #
    # def test_do_i_exit():
    #     assert False
    #
    #
    # def test_save_to_file():
    #     assert False
    #
    #
    # def test_load_from_file():
    #     assert False
    #
    #
    # def test_update_shape_dropdown_menu():
    #     assert False
    #
    #
    # def test_pairwise():
    #     assert False
    #
    #
    # def test_generate_tikz():
    #     assert False