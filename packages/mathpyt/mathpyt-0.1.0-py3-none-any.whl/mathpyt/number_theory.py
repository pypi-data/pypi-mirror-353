"""
Шаблоны кода для теории чисел
"""
import math
import numpy as np
import matplotlib.pyplot as plt
from sympy import isprime, prime, primerange, factorint


def is_prime(n):
    """
    Проверка числа на простоту
    
    Parameters:
    -----------
    n : int
        Целое число для проверки
        
    Returns:
    --------
    bool
        True, если число простое, иначе False
    """
    if n <= 1:
        return False
    
    # Проверяем делители до корня из n
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    
    return True


def sieve_of_eratosthenes(n):
    """
    Решето Эратосфена для нахождения всех простых чисел до n
    
    Parameters:
    -----------
    n : int
        Верхняя граница
        
    Returns:
    --------
    list
        Список простых чисел до n
    """
    # Инициализируем массив: True для всех чисел
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    
    # Просеиваем составные числа
    for i in range(2, int(math.sqrt(n)) + 1):
        if is_prime[i]:
            # Вычеркиваем все кратные i
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    
    # Собираем все простые числа
    primes = [i for i in range(n + 1) if is_prime[i]]
    
    return primes


def prime_factorization(n):
    """
    Разложение числа на простые множители
    
    Parameters:
    -----------
    n : int
        Целое число для разложения
        
    Returns:
    --------
    dict
        Словарь, где ключи - простые множители, значения - их степени
    """
    if n <= 0:
        raise ValueError("Число должно быть положительным")
    
    # Используем sympy для эффективного разложения
    return dict(factorint(n))


def gcd(a, b):
    """
    Нахождение наибольшего общего делителя (НОД)
    
    Parameters:
    -----------
    a : int
        Первое целое число
    b : int
        Второе целое число
        
    Returns:
    --------
    int
        Наибольший общий делитель
    """
    while b:
        a, b = b, a % b
    return abs(a)


def lcm(a, b):
    """
    Нахождение наименьшего общего кратного (НОК)
    
    Parameters:
    -----------
    a : int
        Первое целое число
    b : int
        Второе целое число
        
    Returns:
    --------
    int
        Наименьшее общее кратное
    """
    return abs(a * b) // gcd(a, b)


def extended_gcd(a, b):
    """
    Расширенный алгоритм Евклида
    Находит НОД(a, b) и коэффициенты x, y такие, что ax + by = НОД(a, b)
    
    Parameters:
    -----------
    a : int
        Первое целое число
    b : int
        Второе целое число
        
    Returns:
    --------
    tuple
        (НОД(a, b), x, y)
    """
    if a == 0:
        return b, 0, 1
    
    gcd_val, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd_val, x, y


def modular_inverse(a, m):
    """
    Нахождение мультипликативного обратного по модулю m
    a * x ≡ 1 (mod m)
    
    Parameters:
    -----------
    a : int
        Целое число
    m : int
        Модуль
        
    Returns:
    --------
    int или None
        Мультипликативное обратное или None, если оно не существует
    """
    gcd_val, x, y = extended_gcd(a, m)
    
    if gcd_val != 1:
        # Мультипликативное обратное не существует
        return None
    else:
        # Приводим результат к диапазону [0, m-1]
        return (x % m + m) % m


def chinese_remainder_theorem(remainders, moduli):
    """
    Китайская теорема об остатках
    Решает систему сравнений: x ≡ r_i (mod m_i)
    
    Parameters:
    -----------
    remainders : list
        Список остатков [r_1, r_2, ..., r_k]
    moduli : list
        Список модулей [m_1, m_2, ..., m_k]
        
    Returns:
    --------
    int или None
        Решение системы сравнений или None, если решения нет
    """
    if len(remainders) != len(moduli):
        raise ValueError("Списки остатков и модулей должны иметь одинаковую длину")
    
    # Проверяем, что модули взаимно просты
    for i in range(len(moduli)):
        for j in range(i+1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                return None
    
    # Произведение всех модулей
    M = 1
    for m in moduli:
        M *= m
    
    result = 0
    for i in range(len(moduli)):
        # M_i = M / m_i
        M_i = M // moduli[i]
        
        # Находим мультипликативное обратное M_i по модулю m_i
        inv = modular_inverse(M_i, moduli[i])
        
        # Прибавляем к результату
        result += remainders[i] * M_i * inv
    
    return result % M


def euler_totient(n):
    """
    Функция Эйлера φ(n) - количество чисел от 1 до n, взаимно простых с n
    
    Parameters:
    -----------
    n : int
        Положительное целое число
        
    Returns:
    --------
    int
        Значение функции Эйлера
    """
    if n <= 0:
        raise ValueError("Число должно быть положительным")
    
    # Используем формулу через разложение на простые множители
    factors = prime_factorization(n)
    
    result = n
    for p in factors:
        result *= (1 - 1/p)
    
    return int(result)


def mobius_function(n):
    """
    Функция Мёбиуса μ(n)
    μ(n) = 0, если n делится на квадрат простого числа
    μ(n) = 1, если n - произведение четного числа различных простых чисел
    μ(n) = -1, если n - произведение нечетного числа различных простых чисел
    
    Parameters:
    -----------
    n : int
        Положительное целое число
        
    Returns:
    --------
    int
        Значение функции Мёбиуса
    """
    if n <= 0:
        raise ValueError("Число должно быть положительным")
    
    if n == 1:
        return 1
    
    # Разложение на простые множители
    factors = prime_factorization(n)
    
    # Проверяем, делится ли n на квадрат простого числа
    for p, exp in factors.items():
        if exp > 1:
            return 0
    
    # Возвращаем (-1)^k, где k - количество различных простых делителей
    return (-1) ** len(factors)


def legendre_symbol(a, p):
    """
    Символ Лежандра (a/p)
    
    Parameters:
    -----------
    a : int
        Целое число
    p : int
        Нечетное простое число
        
    Returns:
    --------
    int
        1, если a является квадратичным вычетом по модулю p
        -1, если a является квадратичным невычетом по модулю p
        0, если a делится на p
    """
    if p <= 1 or not isprime(p):
        raise ValueError("p должно быть простым числом")
    
    a = a % p
    
    if a == 0:
        return 0
    
    if a == 1:
        return 1
    
    # Закон квадратичной взаимности
    if a % 2 == 0:
        # Если a четное, используем свойство (2/p) = (-1)^((p^2-1)/8)
        result = legendre_symbol(a // 2, p)
        if p % 8 == 3 or p % 8 == 5:
            result = -result
        return result
    
    # Закон квадратичной взаимности для нечетных a
    if a % 4 == 3 and p % 4 == 3:
        return -legendre_symbol(p, a)
    else:
        return legendre_symbol(p, a)


def plot_prime_distribution(n, bins=50):
    """
    Построение графика распределения простых чисел
    
    Parameters:
    -----------
    n : int
        Верхняя граница для поиска простых чисел
    bins : int, optional
        Количество интервалов для гистограммы
        
    Returns:
    --------
    tuple
        (figure, axis)
    """
    # Находим все простые числа до n
    primes = sieve_of_eratosthenes(n)
    
    # Строим гистограмму
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.hist(primes, bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
    ax.set_title(f'Распределение простых чисел до {n}')
    ax.set_xlabel('Число')
    ax.set_ylabel('Частота')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Добавляем график функции π(x) - количество простых чисел до x
    x = np.linspace(1, n, 1000)
    y = [len([p for p in primes if p <= xi]) for xi in x]
    
    ax_twin = ax.twinx()
    ax_twin.plot(x, y, 'r-', linewidth=2)
    ax_twin.set_ylabel('π(x) - количество простых чисел до x', color='r')
    
    return fig, ax 