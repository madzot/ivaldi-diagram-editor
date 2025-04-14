import math
x_1 = 5


def passs_2(*args):
    print(
        'This function is not supposed to be called. It is only used for testing purposes.'
    )


def passs_1(*args):
    print(
        'This function is not supposed to be called. It is only used for testing purposes.'
    )


def invoke_0(x) -> list:
    return [x, x]


def invoke_2(*numbers: list) -> int:
    if len(numbers) < 2:
        raise ValueError('Numbers amount should be at least 2')
    return numbers[0] - sum(numbers[1:])


def invoke_1(*numbers: list) -> int:
    global y
    if len(numbers) < 2:
        raise ValueError('Numbers amount should be at least 2')
    return sum(numbers)


def main_0(input_0=None, input_1=None, input_2=None):
    res_0 = invoke_0(input_0)
    res_1 = invoke_1(res_0[0], input_1)
    res_2 = invoke_2(res_0[1], input_2)
    return res_1, res_2
