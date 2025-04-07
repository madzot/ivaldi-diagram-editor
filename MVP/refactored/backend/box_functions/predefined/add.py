import math
import copy

def invoke(*numbers: list) -> int:
    if len(numbers) < 2:
        raise ValueError("Numbers amount should be at least 2")
    return sum(numbers)

if __name__ == "__main__":
    print("hui")


meta = {
    "name": "Add",
    "min_args": 2,
    "max_args": math.inf
}
