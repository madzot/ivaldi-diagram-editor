def add(a, b):
    return a + b

def multiply(a, b):
    return a * b, a

def subtract(a, b):
    return a - b


if __name__ == "__main__":
    sum_result = add(2, 3)
    product_result = add(1, 1)
    print(product_result)
    product_result, popa = multiply(sum_result, sum_result)
    sum_result = add(popa, sum_result)
    final_result = subtract(product_result, sum_result)
