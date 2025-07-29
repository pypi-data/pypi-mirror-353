import time
from functools import wraps


def execution_time(func: callable):
    """
    Decorator that measures and prints the execution time of the decorated function.

    Args:
        func (callable): The function to be decorated and measured.

    Returns:
        callable: The wrapped function with execution time measurement.

    Raises:
        Exception: Propagates any exception raised by the decorated function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper function that executes the decorated function and measures its execution time.

        Args:
            *args: Variable length argument list for the decorated function.
            **kwargs: Arbitrary keyword arguments for the decorated function.

        Returns:
            Any: The result returned by the decorated function.

        Raises:
            Exception: Propagates any exception raised by the decorated function.
        """
        print(f"Func: {func.__name__}, Started at: {time.ctime()}\n")
        start_time = time.time()
        res = func(*args, **kwargs)
        exec_time = round(time.time() - start_time, 3)
        print(f"Func: {func.__name__}, Execution time: {exec_time} sec.\n")
        print(f"Func: {func.__name__}, Finished at: {time.ctime()}")
        return res

    return wrapper