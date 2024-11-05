from inspect import signature


def add(numbers: list) -> int:
    return sum(numbers)


def subtract(numbers: list) -> int:
    return numbers[0] - sum(numbers[1:])


functions = {
    "Copy": lambda x: [x, x],
    "Add": add,
    "Subtract": subtract
}


class BoxFunction:
    def __init__(self, name, code):
        self.name = name
        self.code = code or functions.get(name)
        if isinstance(self.code, str):
            function = {}
            exec(self.code, {}, function)
            self.code = function["invoke"]

    def __call__(self, *args):
        return self.code(*args)

    def count_inputs(self):
        sig = signature(self.code)
        params = sig.parameters
        count = len(params)
        if params["self"]:
            count -= 1
        return count

    def __str__(self):
        return self.name


def test_box():
    custom_code = """def invoke(n, l, g, *args):
        return sum(args)
    """
    function = BoxFunction("test", custom_code)
    print(function.count_inputs())
