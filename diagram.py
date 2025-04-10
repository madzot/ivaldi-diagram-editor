import math

def invoke_0(*numbers: list) -> int:
    if len(numbers) < 2:
        raise ValueError('Numbers amount should be at least 2')
    return sum(numbers)


def invoke_1(*numbers: list) -> int:
    if len(numbers) < 2:
        raise ValueError('Numbers amount should be at least 2')
    return numbers[0] - sum(numbers[1:])


def invoke_2(x) -> list:
    return [x, x]


def main(input_0=None, input_1=None, input_2=None, input_3=None):
    res_0 = invoke_0(input_1, input_0)
    res_1 = invoke_0(input_3, input_2)
    res_2 = invoke_1(res_1, res_0)
    res_3 = invoke_2(res_2)
    return res_3[0], res_3[1]
