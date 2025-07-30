
def media(lista):
    """
    Returns the average of a list of integers
    """
    if not lista:
        return 0
    return sum(lista) / len(lista)