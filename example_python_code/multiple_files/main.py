from math_utils import add, multiply, divide, square
from string_utils import reverse_string, to_uppercase, is_palindrome


def not_used():
    print("This function is not used.")


def return_argument(arg):
    return arg


if __name__ == "__main__":
    num1, num2 = 12, 8
    sum_result = add(num1, num2)
    product_result = multiply(num1, num2)
    quotient_result = divide(num1, num2)
    squared_result = square(num1)

    test_string = "level"
    reversed_str = reverse_string(test_string)
    uppercase_str = to_uppercase(test_string)
    palindrome_check = is_palindrome(test_string)

    result = return_argument(sum_result)

    print("Sum:", sum_result)
    print("Product:", product_result)
    print("Quotient:", quotient_result)
    print("Square:", squared_result)

    print("Reversed String:", reversed_str)
    print("Uppercase String:", uppercase_str)
    print("Is Palindrome:", palindrome_check)
