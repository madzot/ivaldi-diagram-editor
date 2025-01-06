from MVP.refactored.box import Box
from MVP.refactored.custom_canvas import CustomCanvas


class SearchAlgorithm:
    def __init__(self, searchable: CustomCanvas, canvas: CustomCanvas):
        self.searchable = searchable
        self.canvas = canvas

    def contains_searchable(self):
        found = False
        result_count = 0
        result_ids = []
        canvas_objects = sorted(self.canvas.spiders + self.canvas.boxes, key=lambda item: [item.x, item.y])
        searchable_objects = sorted(self.searchable.spiders + self.searchable.boxes, key=lambda item: [item.x, item.y])

        searchable_connections_dict = self.create_connection_dictionary(searchable_objects)
        canvas_connection_dict = self.create_connection_dictionary(canvas_objects)

        searchable_length = len(searchable_objects)

        count = 0
        canvas_id = 0
        for canvas_object in list(canvas_connection_dict.items()):
            curr = searchable_connections_dict[count]
            search_left, search_right = curr

            left, right = canvas_object[1]
            if count == 0:
                canvas_id = canvas_object[0]
            left = {i - canvas_id for i in left}
            right = {i - canvas_id for i in right}

            print()
            print(f"curr : {curr}")
            print(f"left : {left}")
            print(f"right: {right}")
            print()
            print(searchable_objects[count].__class__)
            print(canvas_objects[canvas_id].__class__)

            if searchable_objects[count].__class__ == canvas_objects[canvas_id + count].__class__:
                if isinstance(searchable_objects[count], Box):
                    if searchable_objects[count].left_connections:
                        if not search_left == left and search_left:
                            print("box left continue")
                            result_ids.clear()
                            count = 0
                            continue

                    if searchable_objects[count].right_connections:
                        if not search_right == right and search_right:
                            print("box right continue")
                            result_ids.clear()
                            count = 0
                            continue
                else:
                    if not search_left == left and search_left:
                        count = 0
                        result_ids.clear()
                        print("left continue")
                        continue

                    if not search_right == right and search_right:
                        count = 0
                        result_ids.clear()
                        print("right continue")
                        continue
                result_ids.append(canvas_id + count)
                count += 1
                print(f"count: {count}")
                if count == searchable_length:
                    found = True
                    result_count += 1
                    break
            else:
                result_ids.clear()
                count = 0


        print()
        print(f"End count: {count}")

        self.highlight_results(result_ids, canvas_objects)

        return found

    @staticmethod
    def highlight_results(result_indexes, canvas_objects):
        for result_index in result_indexes:
            print(result_index)
            canvas_objects[result_index].select()

    @staticmethod
    def create_connection_dictionary(canvas_objects):
        canvas_connection_dict = {}
        for i in range(len(canvas_objects)):
            curr_item = canvas_objects[i]
            left_wires = set()
            right_wires = set()
            for wire in canvas_objects[i].wires:
                if wire.start_connection == curr_item or wire.start_connection in curr_item.connections:
                    try:
                        index_of_end = canvas_objects.index(wire.end_connection)
                    except ValueError:
                        index_of_end = canvas_objects.index(wire.end_connection.box)
                    right_wires.add(index_of_end)
                if wire.end_connection == curr_item or wire.end_connection in curr_item.connections:
                    try:
                        index_of_start = canvas_objects.index(wire.start_connection)
                    except ValueError:
                        index_of_start = canvas_objects.index(wire.start_connection.box)
                    left_wires.add(index_of_start)
            canvas_connection_dict[i] = [left_wires, right_wires]
        print(canvas_connection_dict)
        print(list(canvas_connection_dict.items()))
        return canvas_connection_dict

