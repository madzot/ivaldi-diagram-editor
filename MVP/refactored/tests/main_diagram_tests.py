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
    def test__add_input__adds_input(self):
        self.app.add_diagram_input()
        self.assertEqual(len(self.app.custom_canvas.inputs), 1)
        # assert len(self.app.custom_canvas.inputs) == 1

    def test__add_input__adds_input_2(self):
        self.app.add_diagram_input()
        self.app.add_diagram_input()
        self.assertEqual(len(self.app.custom_canvas.inputs), 2)
        # assert len(self.app.custom_canvas.inputs) == 2

    def test__add_input__adds_input_3(self):
        self.app.add_diagram_input()
        self.app.add_diagram_input()
        self.app.add_diagram_input()
        self.assertEqual(len(self.app.custom_canvas.inputs), 3)
        # assert len(self.app.custom_canvas.inputs) == 3


    # def pump_events(self):
    #     while self.main_diagram.mainloop(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
    #         pass
    #
    # def tearDown(self):
    #     if self.main_diagram:
    #         self.main_diagram.destroy()
    #         self.pump_events()
    #
    # def test_calculate_boxes_json_file_hash(self):
    #     # self.main_diagram = MainDiagram(Receiver())
    #     self.pump_events()
    #     # main_diagram.destroy()
    #     self.main_diagram.add_diagram_input()
    #     assert len(self.main_diagram.custom_canvas.inputs) == 1


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