from MVP.refactored.modules.notations.hypergraph_notation.hypergraph_notation import HypergraphNotation
from MVP.refactored.modules.notations.pseudo_notation.pseudo_notation import PseudoNotation


def is_canvas_complete(canvas):
    for spider in canvas.spiders:
        if len(spider.wires) == 0:
            return False
    for circle in [c for box in canvas.boxes for c in
                   box.connections] + canvas.outputs + canvas.inputs:
        if not circle.has_wire:
            return False
    if len(canvas.boxes) == len(canvas.wires) == len(canvas.inputs) == len(canvas.outputs) == len(
            canvas.spiders) == 0:
        return False
    return True


def get_notations(canvas):
    pseudo = PseudoNotation()
    hypergraph_notation = HypergraphNotation(canvas.receiver.diagram)

    # TODO add all different notations here
    ...
    return {"Pseudo notation": pseudo.get_pseudo_notations(canvas),
            # TODO add notations' method calls here to combine all to one dict
            "Hypergraph notation": hypergraph_notation.get_graph_string(),
            "Back end logic notation": "to be added"}
