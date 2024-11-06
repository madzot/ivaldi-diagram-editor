def invoke(numbers: list) -> int:
    if len(numbers) < 2:
        raise ValueError("Numbers amount should be atleast 2")
    return sum(numbers)


meta = {
    "name": "Add",

}
