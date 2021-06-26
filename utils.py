def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


def columns(usable_width, n_columns, padding=0):
    col_width = (usable_width - padding * (n_columns + 1)) // n_columns
    x_values = [(i + 1) * padding + i * col_width for i in range(n_columns)]
    return col_width, x_values
