from homewiz.models import Channel


def generate_code(iteration=0):
    '''
    Generates a random code consisting of XXXXX-XXXXX, where X is a alphanumeric character.
    This code is ensured to be unique across all channels.

    :param iteration: The number of times the function has been called recursively
    :return:
    '''
    import random
    import string

    # if the function has been called more than 400 times, raise an error
    if iteration > 400:
        return None

    # generate a random code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)) + '-' + ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=5))

    # check if the code is unique
    if Channel.objects.filter(code=code).first() is not None:
        # if not, generate another code
        return generate_code(iteration + 1)

    return code
