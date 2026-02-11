def norm_phone_number(phone_raw: str):
    int_repr = ""

    for char in phone_raw:
        if char in "1234567890":
            int_repr += char

    return int(int_repr)
