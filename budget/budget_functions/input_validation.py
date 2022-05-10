def validate_inputs(*args):
    for input_ in args:
        if input_ != "":
            try:
                float(input_)
            except ValueError:
                return False
        else:
            continue
    return True