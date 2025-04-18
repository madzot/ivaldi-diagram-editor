import random
import string


class StringUtil:

    @staticmethod
    def generate_random_string(length):
        """Generate a random string of the specified length."""
        # Define the possible characters for the random string
        characters = string.ascii_letters + string.digits + string.punctuation
        # Generate a random string using the specified characters
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    @staticmethod
    def generate_new_variable_name(variable_name: str) -> str:
        """Generate a new variable name by appending a random suffix."""
        suffix = StringUtil.generate_random_string(10)
        return f"{variable_name}_{suffix}"
