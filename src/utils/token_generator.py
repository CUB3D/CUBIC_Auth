from secrets import choice


def gen_unique_token(length=32):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    return "".join([choice(alphabet) for _ in range(length)])
