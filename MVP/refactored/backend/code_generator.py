from MVP.refactored.custom_canvas import CustomCanvas


class CodeGenerator:

    @classmethod
    def generate_code(cls, canvas: CustomCanvas, canvasses: {int: CustomCanvas}) -> str:
        code_parts = {}

        for box in canvas.boxes:
            box_function = box.box_function

            if canvasses[str(box.id)] is None:
                code = "\n" + box_function.code  # TODO change function name
                if code not in code_parts.keys():
                    code_parts[code] = [box.id]
                else:
                    code_parts[code].append(box.id)
            else:
                canvas: CustomCanvas = canvasses[str(box.id)]
                return CodeGenerator.generate_code(canvas, canvasses)

        return "".join(code_parts.keys())

    @classmethod
    def construct_main_function(cls, code_part: {str: [int]}, canvas) -> str:
        main_function = ""

        return ""
