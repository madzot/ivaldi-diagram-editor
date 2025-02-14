import tkinter
import unittest
from unittest.mock import patch

from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.canvas_objects.wire import Wire
from MVP.refactored.frontend.windows.main_diagram import MainDiagram
from MVP.refactored.frontend.canvas_objects.spider import Spider


class TestMainDiagram(unittest.TestCase):

    async def _start_app(self):
        self.app.mainloop()

    def setUp(self):
        self.app = MainDiagram(Receiver())
        self.custom_canvas = self.app.custom_canvas
        self._start_app()

    def tearDown(self):
        self.app.destroy()


class SpiderTests(TestMainDiagram):

    def test__init__values(self):
        spider = Spider(None, 0, "spider", (100, 150), self.custom_canvas, self.app.receiver)

        self.assertEqual(self.custom_canvas, spider.canvas)
        self.assertEqual(100, spider.x)
        self.assertEqual(150, spider.y)
        self.assertEqual(10, spider.r)
        self.assertEqual((100, 150), spider.location)

        self.assertTrue(isinstance(spider.connections, list))
        self.assertFalse(spider.wires)
        self.assertFalse(spider.is_snapped)

    def test__is_spider__returns_true(self):
        spider = Spider(None, 0, "spider", (100, 150), self.custom_canvas, self.app.receiver)

        self.assertTrue(spider.is_spider())

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.tag_bind")
    def test__bind_events__callouts(self, tag_bind_mock):
        spider = Spider(None, 0, "spider", (100, 150), self.custom_canvas, self.app.receiver)
        tag_bind_mock.call_count = 0

        spider.bind_events()

        self.assertEqual(4, tag_bind_mock.call_count)

    @patch("tkinter.Menu.add_command")
    @patch("tkinter.Menu.tk_popup")
    @patch("MVP.refactored.frontend.canvas_objects.spider.Spider.close_menu")
    def test__show_context_menu__callouts(self, close_menu_mock, tk_popup_mock, add_command_mock):
        spider = Spider(None, 0, "spider", (100, 150), self.custom_canvas, self.app.receiver)
        event = tkinter.Event()
        event.x_root = 100
        event.y_root = 150

        spider.show_context_menu(event)

        self.assertEqual(1, close_menu_mock.call_count)
        self.assertEqual(1, tk_popup_mock.call_count)
        self.assertEqual(2, add_command_mock.call_count)

    @patch("MVP.refactored.backend.diagram_callback.Receiver.receiver_callback")
    def test__delete_spider__calls_receiver_if_sub_diagram(self, receiver_mock):
        spider = Spider(None, 0, "spider", (100, 150), self.custom_canvas, self.app.receiver)
        self.custom_canvas.spiders.append(spider)

        spider.delete_spider(action="sub_diagram")

        self.assertTrue(receiver_mock.called)

    @patch("MVP.refactored.frontend.canvas_objects.spider.Spider.delete")
    def test__delete_spider__calls_delete_function(self, delete_mock):
        spider = Spider(None, 0, "spider", (100, 150), self.custom_canvas, self.app.receiver)
        self.custom_canvas.spiders.append(spider)

        spider.delete_spider()
        self.assertTrue(delete_mock.called)

    def test__delete_spider__removes_spider_from_canvas_list(self):
        spider = Spider(None, 0, "spider", (100, 150), self.custom_canvas, self.app.receiver)
        self.custom_canvas.spiders.append(spider)

        spider.delete_spider()

        self.assertFalse(self.custom_canvas.spiders)

    @patch("tkinter.Menu.destroy")
    def test__close_menu__doesnt_close_if_no_menu(self, destroy_mock):
        spider = Spider(None, 0, "spider", (100, 150), self.custom_canvas, self.app.receiver)
        spider.context_menu = None
        spider.close_menu()
        self.assertFalse(destroy_mock.called)

    @patch("tkinter.Menu.destroy")
    def test__close_menu__closes_if_menu(self, destroy_mock):
        spider = Spider(None, 0, "spider", (100, 150), self.custom_canvas, self.app.receiver)
        spider.context_menu = tkinter.Menu()
        spider.close_menu()
        self.assertTrue(destroy_mock.called)

    def test__add_wire__adds_wire(self):
        spider = Spider(None, 0, "spider", (100, 150), self.custom_canvas, self.app.receiver)
        wire1 = Wire(None, None, self.app.receiver, None, temporary=True)
        wire2 = Wire(None, None, self.app.receiver, None, temporary=True)
        wire3 = Wire(None, None, self.app.receiver, None, temporary=True)

        spider.add_wire(wire1)
        spider.add_wire(wire2)
        spider.add_wire(wire3)

        self.assertEqual([wire1, wire2, wire3], spider.wires)
