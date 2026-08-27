try:
    from decorlib import cache, timeit, validate_types
except (ImportError, TypeError):
    from decorlib.decorlib import cache, timeit, validate_types

@timeit
@cache
@validate_types
def add(a: int, b: int) -> int:
    return a + b

print(add(2, 3))
print(add(2, 3))  # cached