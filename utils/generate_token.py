import random


def generate_token():
    """ Generate a unique token for email verification"""
    token = str(random.randint(100000, 999999))
    return token
