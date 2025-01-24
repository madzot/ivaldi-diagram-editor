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
                if searchable_objects[counter].__class__ == canvas_objects[curr_canvas_id].__class__:

                    if len(curr_canvas_left) == len(curr_search_left) or len(curr_search_left) == 0 or isinstance(canvas_objects[curr_canvas_id], Spider):
                        if len(curr_canvas_right) == len(curr_search_right) or len(curr_search_right) == 0 or isinstance(canvas_objects[curr_canvas_id], Spider):
                            if counter == 0:
                                print()
                                print("Adding potential results the first round")
                                print(f"Searchable connection: {searchable_connection}")
                                print(f"Canvas connection: {canvas_connection}")
                                potential_results.append({curr_canvas_id: [curr_canvas_left, curr_canvas_right]})
                            else:
                                for potential in potential_results.copy():
                                    print("New potential")
                                    print(potential_results)
                                    print(potential)
                                    if len(potential) == counter:
                                        for key in potential.keys():
                                            if key in curr_canvas_left or not curr_search_left:
                                                print()
                                                print("Adding potential results")
                                                print(f"Searchable connection: {searchable_connection}")
                                                print(f"Canvas connection: {canvas_connection}")
                                                # if isinstance(canvas_objects[curr_canvas_id], Spider):
                                                #     potential_results.append(potential | {curr_canvas_id: [[], []]})
                                                #     # potential[curr_canvas_id] = [[], []]
                                                # else:
                                                potential_results.append(potential | {curr_canvas_id: [curr_canvas_left, curr_canvas_right]})
                                                # potential[curr_canvas_id] = [curr_canvas_left, curr_canvas_right]
                                                break
            counter += 1

        potential_results = list(filter(lambda x: len(x) == len(searchable_connections), potential_results))
        print(f"Potential results: {potential_results}")
        return potential_results

    @staticmethod
    def filter_connectivity(connection_dicts):
        connected_dicts = []
        for connection_dict in connection_dicts:
            connection_ids = []
            connected_ids = []
            connected = True
            connection_dict_items = list(connection_dict.items())
            for connection in connection_dict_items:
                connection_ids.append(connection[0])
                left_con, right_con = connection[1]
                connected_ids = connected_ids + left_con + right_con
            print(f"Connection ids: {connected_ids}")
            print(f"connected ids: {connected_ids}")
            for connection_id in connection_ids:
                if connection_id not in connected_ids:
                    connected = False
            if connected:
                connected_dicts.append(connection_dict)

        return connected_dicts

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

        potential_results = self.filter_connectivity(potential_results)
        print(f"Potential after filtering: {potential_results}")

        for potential_result in potential_results:
            print()
            print(f"POTENTIAL RESULT: {potential_result}")
            print(f"Normalized potential result: {self.normalize_dictionary(potential_result)}")
            normalized = self.normalize_dictionary(potential_result)
            not_correct = False
            for normalized_key in normalized.keys():
                if normalized_key not in searchable_connections_dict.keys():
                    not_correct = True
                    break
                print(f"Normalized {normalized}")
                print(f"searchable dict: {searchable_connections_dict}")
                normalized_item = normalized[normalized_key]
                normalized_left, normalized_right = normalized_item

                searchable = searchable_connections_dict[normalized_key]
                print(f"Searchable {searchable}")
                searchable_left, searchable_right = searchable

                print(f"Normalized key: {normalized_key}")
                for key in searchable_left:
                    if key not in normalized_left and key is not None:
                        not_correct = True
                for key in searchable_right:
                    if key not in normalized_right and key is not None:
                        not_correct = True

            if not_correct:
                print("SKIPPED")
                continue
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
                                if searchable_left[j] is None or potential_left[j] is None or searchable_objects[searchable_left[j]].__class__ == canvas_objects[potential_left[j]].__class__:
                                    matching_connection_count += 1
                            if matching_connection_count == searchable_item.left_connections:
                                left_side_check = True
                        else:
                            left_side_check = True

                        if searchable_item.right_connections:
                            matching_connection_count = 0
                            for j in range(searchable_item.right_connections):
                                if searchable_right[j] is None or potential_right[j] is None or searchable_objects[searchable_right[j]].__class__ == canvas_objects[potential_right[j]].__class__:
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
    def normalize_dictionary(dictionary):
        """{6: [[4], [9]], 9: [[7, 6], [11]]} -> {0: [[], [1]], 1: [[0], []]}"""
        number_correspondence_dict = {}
        result = {}

        number_count = 0
        for key in sorted(dictionary.keys()):
            number_correspondence_dict[key] = number_count
            number_count += 1

        for item in dictionary.items():
            corresponding_num = number_correspondence_dict[item[0]]
            left, right = item[1]
            new_left, new_right = [], []
            for num in left:
                if num in number_correspondence_dict:
                    new_left.append(number_correspondence_dict[num])
            for numb in right:
                if numb in number_correspondence_dict:
                    new_right.append(number_correspondence_dict[numb])
            result[corresponding_num] = [new_left, new_right]
        return result

    @staticmethod
    def create_connection_dictionary(canvas_objects):
        canvas_connection_dict = {}
        print(f"CANVAS OBJECTS: {canvas_objects}")
        for i in range(len(canvas_objects)):
            print()
            curr_item = canvas_objects[i]
            left_wires = []
            right_wires = []
            # print(f"Curr_item: {i}:{canvas_objects[i]}")
            if isinstance(curr_item, Box):
                for connection in curr_item.connections:
                    # print(connection.side)
                    if connection.side == "left":
                        if connection.wire:
                            try:
                                index = canvas_objects.index(connection.wire.start_connection)
                                # print(f"left index: {index}, {connection.wire.start_connection}")
                            except ValueError:
                                index = canvas_objects.index(connection.wire.start_connection.box)
                                # print(f"left index: {index}, {connection.wire.start_connection.box}")
                        else:
                            index = None
                        left_wires.append(index)
                    elif connection.side == "right":
                        if connection.wire:
                            try:
                                index = canvas_objects.index(connection.wire.end_connection)
                                # print(f"right index: {index}, {connection.wire.end_connection}")
                            except ValueError:
                                index = canvas_objects.index(connection.wire.end_connection.box)
                                # print(f"right index: {index}, {connection.wire.end_connection.box}")
                                # if index == 2:
                                    # print(f"wire end: {connection.wire.end_connection.box}")
                                    # print(f"wire start: {connection.wire.start_connection.box}")
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
            # print(f"canvas connection dict: {canvas_connection_dict}")
        return canvas_connection_dict

