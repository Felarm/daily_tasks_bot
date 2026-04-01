from datetime import time


def process_integer_num(input_value: str) -> int | None:
    try:
        return int(input_value)
    except ValueError:
        return None


def process_string_of_nums(input_value: str) -> list[int] | None:
    try:
        return [int(_.strip()) for _ in input_value.split(",")]
    except ValueError:
        return None


def process_time_from_string(input_value: str) -> time | None:
    try:
        return time.fromisoformat(input_value)
    except ValueError:
        return None
