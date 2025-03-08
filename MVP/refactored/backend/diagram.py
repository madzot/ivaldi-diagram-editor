import json
from MVP.refactored.backend.generator import Generator
from MVP.refactored.backend.resource import Resource
from MVP.refactored.backend.types.connection_info import ConnectionInfo


class Diagram:
    def __init__(self):
        self.input: list[ConnectionInfo] = []
        self.output: list[ConnectionInfo] = []
        self.boxes: list[Generator] = []
        self.resources: list[Resource] = []
        self.spiders: list[Resource] = []
        self.sub_diagrams: list[Diagram] = [] # There is sub diagram of diagram. If sub diagram contains one more sub diagram,
        # it won't be added here. Only to sub diagram`s sub diagram

    def add_resource(self, resource):
        self.resources.append(resource)

    def add_box(self, box):
        self.boxes.append(box)

    def add_input(self, connection_info: ConnectionInfo):
        self.input.insert(connection_info.index, connection_info)

    def add_output(self, connection_info: ConnectionInfo):
        self.output.insert(connection_info.index, connection_info)

    def remove_input(self, connection_id: int):
        for i in self.input:
            if i.id == connection_id:
                self.input.remove(i)
                return

    def remove_output(self, connection_id: int):
        for i in self.output:
            if i.id == connection_id:
                self.output.remove(i)
                return

    def remove_box(self, boxes):
        self.boxes.remove(boxes)

    def remove_box_by_id(self, id: int):
        for box in self.boxes:
            if box.id == id:
                self.boxes.remove(box)
                return

    def remove_resource(self, resources):
        if resources in self.resources:
            self.resources.remove(resources)

    def remove_resource_by_id(self, id: int):
        for resource in self.resources:
            if resource.id == id:
                self.resources.remove(resource)
                return

    def diagram_import(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            self._from_dict(data)

    def diagram_export(self, file_path):
        data = self._to_dict()
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def _to_dict(self):
        return {
            "input": self.input,
            "output": self.output,
            "boxes": [box.to_dict() for box in self.boxes],
            "resources": [resource.to_dict() for resource in self.resources]
        }

    def _from_dict(self, data):
        self.input = data.get("input", [])
        self.output = data.get("output", [])
        self.boxes = [Generator.from_dict(box_data) for box_data in data.get("boxes", [])]
        self.resources = [Resource.from_dict(resource_data) for resource_data in data.get("resources", [])]
