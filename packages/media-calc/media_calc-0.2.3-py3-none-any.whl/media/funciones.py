
def media(lista):
    """
    Returns the arithmetic mean of a list of numbers.
    
    Args:
        lista (list): A list of numbers (integers or floats)
    
    Returns:
        float: The arithmetic mean of the list, or 0 if the list is empty
    """
    if not lista:
        return 0
    return sum(lista) / len(lista)

def mediana(lista):
    """
    Returns the median of a list of numbers.
    
    Args:
        lista (list): A list of numbers (integers or floats)
    
    Returns:
        float: The median of the list, or 0 if the list is empty
    """
    if not lista:
        return 0
    sorted_list = sorted(lista)
    n = len(sorted_list)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_list[mid-1] + sorted_list[mid]) / 2
    return sorted_list[mid]

def moda(lista):
    """
    Returns the mode (most frequent value) of a list of numbers.
    
    Args:
        lista (list): A list of numbers (integers or floats)
    
    Returns:
        float: The mode of the list, or None if the list is empty
    """
    if not lista:
        return None
    from collections import Counter
    count = Counter(lista)
    return max(count.items(), key=lambda x: x[1])[0]

def varianza(lista):
    """
    Returns the variance of a list of numbers.
    
    Args:
        lista (list): A list of numbers (integers or floats)
    
    Returns:
        float: The variance of the list, or 0 if the list is empty
    """
    if not lista or len(lista) < 2:
        return 0
    med = media(lista)
    return sum((x - med) ** 2 for x in lista) / len(lista)

def desviacion_estandar(lista):
    """
    Returns the standard deviation of a list of numbers.
    
    Args:
        lista (list): A list of numbers (integers or floats)
    
    Returns:
        float: The standard deviation of the list, or 0 if the list is empty
    """
    from math import sqrt
    return sqrt(varianza(lista))