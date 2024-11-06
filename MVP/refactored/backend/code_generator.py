from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.hypergraph_manage import HypergraphManager
from MVP.refactored.custom_canvas import CustomCanvas
from inspect import getsource


class CodeGenerator:
    hypergraph_ids = [x.id for x in HypergraphManager.hypergraphs]

    @classmethod
    def generate_code(cls, canvas: CustomCanvas, canvasses: {int: CustomCanvas}) -> str:
        code = ""
        print("_____________")
        print("canvas id is: ", canvas.id)
        print("boxes ids on current canvas are: ", [x.id for x in canvas.boxes])
        print("hypergraph ids are: ", [x.id for x in HypergraphManager.hypergraphs])
        print(canvasses)

        for box in canvas.boxes:
            hypergraph: Hypergraph = HypergraphManager.get_graph_by_id(box.sub_diagram_id)
            print("box has sub diagram: ", box.sub_diagram_id)
            box_function = box.box_function
            if hypergraph is None:
                code += "\n" + CodeGenerator.get_box_function_as_string(box_function)
            else:
                canvas: CustomCanvas = canvasses[str(box.sub_diagram_id)]
                code += "\n" + CodeGenerator.generate_code(canvas, canvasses)
        return code

    @classmethod
    def get_box_function_as_string(cls, box_function) -> str:
        if callable(box_function.code):
            function_code = getsource(box_function.code)
            return function_code
        else:
            raise TypeError("Expected box_function.code to be a function")


function_str = """
def example(x):
    return math.sqrt(x) + datetime.datetime.now().year
"""
