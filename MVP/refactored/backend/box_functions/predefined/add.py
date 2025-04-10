import math

x = 5
def invoke(*numbers: list) -> int:
    global y
    if len(numbers) < 2:
        raise ValueError("Numbers amount should be at least 2")
    return sum(numbers)


if __name__ == "__main__":
    print("hui")
