from typing import List

# function to calculate average of a list of numbers
def calculate_average(numbers: List[float]) -> float:
    """
    Calculate the average of a list of numbers.

    Args:
        numbers (List[float]): A list of numbers to calculate the average for.

    Returns:
        float: The average of the numbers. Returns 0 if the list is empty.
    """
    if len(numbers) == 0:
        return 0
    total = sum(numbers)
    average = total / len(numbers)
    return average