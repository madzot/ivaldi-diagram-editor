import math
x_0 = 5


def passs_1(*args):
    print(
        'This function is not supposed to be called. It is only used for testing purposes.'
    )


def passs_0(*args):
    print(
        'This function is not supposed to be called. It is only used for testing purposes.'
    )


def invoke_1(*numbers: list) -> int:
    if len(numbers) < 2:
        raise ValueError('Numbers amount should be at least 2')
    return numbers[0] - sum(numbers[1:])


def invoke_2(x) -> list:
    return [x, x]


def invoke_0(*numbers: list) -> int:
    global y
    if len(numbers) < 2:
        raise ValueError('Numbers amount should be at least 2')
    return sum(numbers)
