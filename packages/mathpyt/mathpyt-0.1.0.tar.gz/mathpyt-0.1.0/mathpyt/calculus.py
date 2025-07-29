"""
Шаблоны кода для математического анализа
"""
import numpy as np
from scipy import integrate
import sympy as sp


def numerical_derivative(f, x, h=1e-5):
    """
    Численное дифференцирование функции в точке
    
    Parameters:
    -----------
    f : callable
        Функция одной переменной
    x : float
        Точка, в которой вычисляется производная
    h : float, optional
        Шаг дифференцирования
        
    Returns:
    --------
    float
        Значение производной в точке x
    """
    return (f(x + h) - f(x - h)) / (2 * h)


def numerical_integral(f, a, b, n=1000):
    """
    Численное интегрирование функции методом трапеций
    
    Parameters:
    -----------
    f : callable
        Функция одной переменной
    a : float
        Нижний предел интегрирования
    b : float
        Верхний предел интегрирования
    n : int, optional
        Количество разбиений
        
    Returns:
    --------
    float
        Значение интеграла
    """
    x = np.linspace(a, b, n)
    y = np.array([f(xi) for xi in x])
    return np.trapz(y, x)


def scipy_integrate_quad(f, a, b):
    """
    Численное интегрирование с использованием scipy.integrate.quad
    
    Parameters:
    -----------
    f : callable
        Функция одной переменной
    a : float
        Нижний предел интегрирования
    b : float
        Верхний предел интегрирования
        
    Returns:
    --------
    tuple
        (значение интеграла, оценка погрешности)
    """
    return integrate.quad(f, a, b)


def symbolic_derivative():
    """
    Пример символьного дифференцирования с использованием sympy
    
    Returns:
    --------
    sympy.Expr
        Символьное выражение для производной
    """
    x = sp.Symbol('x')
    f = x**2 + sp.sin(x) + sp.exp(x)
    df_dx = sp.diff(f, x)
    return df_dx


def symbolic_integral():
    """
    Пример символьного интегрирования с использованием sympy
    
    Returns:
    --------
    sympy.Expr
        Символьное выражение для интеграла
    """
    x = sp.Symbol('x')
    f = x**2 + sp.sin(x)
    integral = sp.integrate(f, x)
    return integral


def taylor_series(func, x0, n=5):
    """
    Разложение функции в ряд Тейлора
    
    Parameters:
    -----------
    func : sympy.Expr
        Символьное выражение функции
    x0 : float
        Точка разложения
    n : int, optional
        Количество членов ряда
        
    Returns:
    --------
    sympy.Expr
        Разложение в ряд Тейлора
    """
    x = sp.Symbol('x')
    series = func.series(x, x0, n).removeO()
    return series 