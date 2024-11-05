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

    def __call__(self, *args):
        if callable(self.code):
            return self.code(*args)
        else:
            function = {}
            try:
                exec(self.code, {}, function)
                return function["invoke"](args)
            except Exception as e:
                print(f"Error executing code in '{self.name}':", e)
                return None

    def __str__(self):
        return self.name


def test_box():
    custom_code = """def call(*args):
        return sum(args)
    """
    function = {}
    exec(custom_code, {}, function)

    print(function["call"](3, 4, 5, 6))

test_box()