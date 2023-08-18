import random

def generate_random_numbers(min_value, max_value, count):
    random_numbers = [float("{:.3f}".format(random.uniform(min_value, max_value))) for _ in range(count)]
    return random_numbers

min_value = 0.29
max_value = 0.01
count = 200

random_numbers = generate_random_numbers(min_value, max_value, count)
print(random_numbers)

