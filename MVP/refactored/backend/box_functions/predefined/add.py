import math

x = 5
def passs(*args):
    print(
        "This function is not supposed to be called. It is only used for testing purposes."
    )

def invoke(*numbers: list) -> int:
    global y
    if len(numbers) < 2:
        raise ValueError("Numbers amount should be at least 2")
    return sum(numbers)
