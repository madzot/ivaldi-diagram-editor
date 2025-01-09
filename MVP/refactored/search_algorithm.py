from MVP.refactored.box import Box
from MVP.refactored.custom_canvas import CustomCanvas
from MVP.refactored.spider import Spider


class SearchAlgorithm:
    def __init__(self, searchable: CustomCanvas, canvas: CustomCanvas):
        self.searchable = searchable
        self.canvas = canvas

    def get_potential_results(self, searchable_objects, canvas_objects):
        potential_results = []

        searchable_connections = self.create_connection_dictionary(searchable_objects)
        canvas_connections = self.create_connection_dictionary(canvas_objects)

        counter = 0
        for searchable_connection in searchable_connections.items():
            curr_search_left, curr_search_right = searchable_connection[1]
            for canvas_connection in canvas_connections.items():
                curr_canvas_id = canvas_connection[0]
                curr_canvas_left, curr_canvas_right = canvas_connection[1]

                if len(curr_canvas_left) == len(curr_search_left) or len(curr_search_left) == 0 or isinstance(canvas_objects[curr_canvas_id], Spider):
                    if len(curr_canvas_right) == len(curr_search_right) or len(curr_search_right) == 0 or isinstance(canvas_objects[curr_canvas_id], Spider):
                        if counter == 0:
                            print()
                            print("Adding potential results the first round")
                            print(f"Searchable connection: {searchable_connection}")
                            print(f"Canvas connection: {canvas_connection}")
                            if searchable_objects[counter].__class__ == canvas_objects[curr_canvas_id].__class__:
                                if isinstance(canvas_objects[curr_canvas_id], Spider):
                                    potential_results.append({curr_canvas_id: [[], []]})
                                else:
                                    potential_results.append({curr_canvas_id: [curr_canvas_left, curr_canvas_right]})
                        else:
                            for potential in potential_results:
                                if len(potential) == counter:
                                    for key in potential.keys():
                                        if key in curr_canvas_left:
                                            print()
                                            print("Adding potential results")
                                            print(f"Searchable connection: {searchable_connection}")
                                            print(f"Canvas connection: {canvas_connection}")
                                            if isinstance(canvas_objects[curr_canvas_id], Spider):
                                                potential[curr_canvas_id] = [[], []]
                                            else:
                                                potential[curr_canvas_id] = [curr_canvas_left, curr_canvas_right]
                                            break
            counter += 1

        potential_results = list(filter(lambda x: len(x) == len(searchable_connections), potential_results))
        print(f"Potential results: {potential_results}")
        return potential_results

    def contains_searchable(self):
        found = False
        result_ids = []
        canvas_objects = sorted(self.canvas.spiders + self.canvas.boxes, key=lambda item: [item.x, item.y])
        searchable_objects = sorted(self.searchable.spiders + self.searchable.boxes, key=lambda item: [item.x, item.y])

        if len(searchable_objects) == 0:
            print("TODO: create some sort of indication that there is nothing in search.")  # TODO

        searchable_connections_dict = self.create_connection_dictionary(searchable_objects)
        print(f"Searchable dict: {searchable_connections_dict}")
        canvas_connection_dict = self.create_connection_dictionary(canvas_objects)
        print(f"Canvas dict: {canvas_connection_dict}")

        potential_results = self.get_potential_results(searchable_objects, canvas_objects)

        for potential_result in potential_results:
            for i in range(len(searchable_objects)):
                potential = list(potential_result.items())[i]
                potential_id = potential[0]
                potential_left, potential_right = potential[1]
                potential_item = canvas_objects[potential_id]

                searchable = list(searchable_connections_dict.items())[i]
                searchable_id = searchable[0]
                searchable_left, searchable_right = searchable[1]
                searchable_item = searchable_objects[searchable_id]

                left_side_check = False
                right_side_check = False
                if searchable_item.__class__ == potential_item.__class__:
                    if isinstance(searchable_item, Box):

                        if searchable_item.left_connections:
                            matching_connection_count = 0
                            for j in range(searchable_item.left_connections):
                                if searchable_left[j] is None or searchable_objects[searchable_left[j]].__class__ == canvas_objects[potential_left[j]].__class__:
                                    matching_connection_count += 1
                            if matching_connection_count == searchable_item.left_connections:
                                left_side_check = True
                        else:
                            left_side_check = True

                        if searchable_item.right_connections:
                            matching_connection_count = 0
                            for j in range(searchable_item.right_connections):
                                if searchable_right[j] is None or searchable_objects[searchable_right[j]].__class__ == canvas_objects[potential_right[j]].__class__:
                                    matching_connection_count += 1
                            if matching_connection_count == searchable_item.right_connections:
                                right_side_check = True
                        else:
                            right_side_check = True

                    elif isinstance(searchable_item, Spider):
                        left_side_check = True
                        right_side_check = True

                if left_side_check and right_side_check:
                    found = True
                    for key in potential_result.keys():
                        result_ids.append(key)

        self.highlight_results(result_ids, canvas_objects)

        return found

    @staticmethod
    def highlight_results(result_indexes, canvas_objects):
        for result_index in result_indexes:
            canvas_objects[result_index].select()

    @staticmethod
    def create_connection_dictionary(canvas_objects):
        canvas_connection_dict = {}
        for i in range(len(canvas_objects)):
            curr_item = canvas_objects[i]
            left_wires = []
            right_wires = []
            if isinstance(curr_item, Box):
                for connection in curr_item.connections:
                    if connection.side == "left":
                        if connection.wire:
                            try:
                                index = canvas_objects.index(connection.wire.start_connection)
                            except ValueError:
                                index = canvas_objects.index(connection.wire.start_connection.box)
                        else:
                            index = None
                        left_wires.append(index)
                    elif connection.side == "right":
                        if connection.wire:
                            try:
                                index = canvas_objects.index(connection.wire.end_connection)
                            except ValueError:
                                index = canvas_objects.index(connection.wire.end_connection.box)
                        else:
                            index = None
                        right_wires.append(index)
            elif isinstance(curr_item, Spider):
                for wire in curr_item.wires:
                    if wire.start_connection == curr_item:
                        try:
                            index_of_end = canvas_objects.index(wire.end_connection)
                        except ValueError:
                            index_of_end = canvas_objects.index(wire.end_connection.box)
                        right_wires.append(index_of_end)
                    if wire.end_connection == curr_item:
                        try:
                            index_of_start = canvas_objects.index(wire.start_connection)
                        except ValueError:
                            index_of_start = canvas_objects.index(wire.start_connection.box)
                        left_wires.append(index_of_start)
            canvas_connection_dict[i] = [left_wires, right_wires]
        return canvas_connection_dict

