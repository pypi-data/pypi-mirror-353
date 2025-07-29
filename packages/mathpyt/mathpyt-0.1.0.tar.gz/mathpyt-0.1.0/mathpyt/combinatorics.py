"""
Шаблоны кода для комбинаторики
"""
import math
import numpy as np
from itertools import permutations, combinations, combinations_with_replacement


def factorial(n):
    """
    Вычисление факториала числа n
    
    Parameters:
    -----------
    n : int
        Неотрицательное целое число
        
    Returns:
    --------
    int
        Факториал числа n
    """
    if n < 0:
        raise ValueError("Факториал определен только для неотрицательных целых чисел")
    
    return math.factorial(n)


def binomial_coefficient(n, k):
    """
    Вычисление биномиального коэффициента C(n,k) = n! / (k! * (n-k)!)
    
    Parameters:
    -----------
    n : int
        Неотрицательное целое число
    k : int
        Неотрицательное целое число, не превосходящее n
        
    Returns:
    --------
    int
        Биномиальный коэффициент C(n,k)
    """
    if n < 0 or k < 0 or k > n:
        raise ValueError("Биномиальный коэффициент C(n,k) определен для 0 <= k <= n")
    
    return math.comb(n, k)


def permutation_count(n, k=None):
    """
    Вычисление количества перестановок P(n,k) = n! / (n-k)!
    
    Parameters:
    -----------
    n : int
        Неотрицательное целое число
    k : int, optional
        Неотрицательное целое число, не превосходящее n.
        Если не указано, считается k = n
        
    Returns:
    --------
    int
        Количество перестановок P(n,k)
    """
    if n < 0:
        raise ValueError("n должно быть неотрицательным")
    
    if k is None:
        k = n
    
    if k < 0 or k > n:
        raise ValueError("k должно быть неотрицательным и не превосходить n")
    
    return math.perm(n, k)


def generate_permutations(elements):
    """
    Генерация всех перестановок элементов
    
    Parameters:
    -----------
    elements : iterable
        Исходный набор элементов
        
    Returns:
    --------
    list
        Список всех перестановок
    """
    return list(permutations(elements))


def generate_combinations(elements, k):
    """
    Генерация всех сочетаний по k элементов из исходного набора
    
    Parameters:
    -----------
    elements : iterable
        Исходный набор элементов
    k : int
        Размер сочетания
        
    Returns:
    --------
    list
        Список всех сочетаний
    """
    return list(combinations(elements, k))


def generate_combinations_with_replacement(elements, k):
    """
    Генерация всех сочетаний с повторениями по k элементов из исходного набора
    
    Parameters:
    -----------
    elements : iterable
        Исходный набор элементов
    k : int
        Размер сочетания
        
    Returns:
    --------
    list
        Список всех сочетаний с повторениями
    """
    return list(combinations_with_replacement(elements, k))


def stirling_number_second_kind(n, k):
    """
    Вычисление числа Стирлинга второго рода S(n,k)
    
    Parameters:
    -----------
    n : int
        Неотрицательное целое число
    k : int
        Неотрицательное целое число, не превосходящее n
        
    Returns:
    --------
    int
        Число Стирлинга второго рода S(n,k)
    """
    if n < 0 or k < 0 or k > n:
        raise ValueError("Числа Стирлинга S(n,k) определены для 0 <= k <= n")
    
    if k == 0:
        return 1 if n == 0 else 0
    
    if k == 1 or k == n:
        return 1
    
    result = 0
    for j in range(k + 1):
        result += (-1)**(k - j) * binomial_coefficient(k, j) * j**n
    
    return result // math.factorial(k)


def catalan_number(n):
    """
    Вычисление числа Каталана C(n)
    
    Parameters:
    -----------
    n : int
        Неотрицательное целое число
        
    Returns:
    --------
    int
        Число Каталана C(n)
    """
    if n < 0:
        raise ValueError("Числа Каталана определены для неотрицательных целых чисел")
    
    return binomial_coefficient(2*n, n) // (n + 1)


def bell_number(n):
    """
    Вычисление числа Белла B(n)
    
    Parameters:
    -----------
    n : int
        Неотрицательное целое число
        
    Returns:
    --------
    int
        Число Белла B(n)
    """
    if n < 0:
        raise ValueError("Числа Белла определены для неотрицательных целых чисел")
    
    if n == 0:
        return 1
    
    # Используем формулу через числа Стирлинга второго рода
    result = 0
    for k in range(n + 1):
        result += stirling_number_second_kind(n, k)
    
    return result


def fibonacci_number(n):
    """
    Вычисление числа Фибоначчи F(n)
    
    Parameters:
    -----------
    n : int
        Неотрицательное целое число
        
    Returns:
    --------
    int
        Число Фибоначчи F(n)
    """
    if n < 0:
        raise ValueError("Числа Фибоначчи обычно определены для неотрицательных целых чисел")
    
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    
    return b 