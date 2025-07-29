"""
Шаблоны кода для численных методов
"""
import numpy as np
from scipy import linalg


def bisection_method(f, a, b, tol=1e-6, max_iter=100):
    """
    Метод бисекции для нахождения корня уравнения f(x) = 0
    
    Parameters:
    -----------
    f : callable
        Функция одной переменной
    a : float
        Левая граница интервала
    b : float
        Правая граница интервала
    tol : float, optional
        Точность
    max_iter : int, optional
        Максимальное количество итераций
        
    Returns:
    --------
    tuple
        (приближенное значение корня, количество итераций, история итераций)
    """
    if f(a) * f(b) > 0:
        raise ValueError("Функция должна иметь разные знаки на концах интервала")
    
    history = []
    
    for i in range(max_iter):
        c = (a + b) / 2
        fc = f(c)
        
        history.append((c, fc))
        
        if abs(fc) < tol:
            return c, i + 1, history
        
        if f(a) * fc < 0:
            b = c
        else:
            a = c
    
    return (a + b) / 2, max_iter, history


def newton_method_root(f, df, x0, tol=1e-6, max_iter=100):
    """
    Метод Ньютона для нахождения корня уравнения f(x) = 0
    
    Parameters:
    -----------
    f : callable
        Функция одной переменной
    df : callable
        Производная функции
    x0 : float
        Начальное приближение
    tol : float, optional
        Точность
    max_iter : int, optional
        Максимальное количество итераций
        
    Returns:
    --------
    tuple
        (приближенное значение корня, количество итераций, история итераций)
    """
    x = x0
    history = [(x, f(x))]
    
    for i in range(max_iter):
        fx = f(x)
        dfx = df(x)
        
        if abs(dfx) < 1e-10:
            raise ValueError("Производная близка к нулю")
        
        x_new = x - fx / dfx
        
        history.append((x_new, f(x_new)))
        
        if abs(x_new - x) < tol:
            return x_new, i + 1, history
        
        x = x_new
    
    return x, max_iter, history


def secant_method(f, x0, x1, tol=1e-6, max_iter=100):
    """
    Метод секущих для нахождения корня уравнения f(x) = 0
    
    Parameters:
    -----------
    f : callable
        Функция одной переменной
    x0 : float
        Первое начальное приближение
    x1 : float
        Второе начальное приближение
    tol : float, optional
        Точность
    max_iter : int, optional
        Максимальное количество итераций
        
    Returns:
    --------
    tuple
        (приближенное значение корня, количество итераций, история итераций)
    """
    f0 = f(x0)
    f1 = f(x1)
    
    history = [(x0, f0), (x1, f1)]
    
    for i in range(max_iter):
        if abs(f1 - f0) < 1e-10:
            raise ValueError("Разность функций близка к нулю")
        
        x_new = x1 - f1 * (x1 - x0) / (f1 - f0)
        f_new = f(x_new)
        
        history.append((x_new, f_new))
        
        if abs(x_new - x1) < tol:
            return x_new, i + 1, history
        
        x0, f0 = x1, f1
        x1, f1 = x_new, f_new
    
    return x1, max_iter, history


def gauss_elimination(A, b):
    """
    Метод Гаусса для решения системы линейных уравнений Ax = b
    
    Parameters:
    -----------
    A : array-like
        Матрица коэффициентов
    b : array-like
        Вектор правой части
        
    Returns:
    --------
    numpy.ndarray
        Решение системы
    """
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    
    n = len(b)
    
    # Прямой ход
    for i in range(n):
        # Выбор главного элемента
        max_row = i + np.argmax(abs(A[i:, i]))
        if max_row != i:
            A[[i, max_row]] = A[[max_row, i]]
            b[[i, max_row]] = b[[max_row, i]]
        
        # Обнуление элементов под главной диагональю
        for j in range(i + 1, n):
            factor = A[j, i] / A[i, i]
            b[j] -= factor * b[i]
            A[j, i:] -= factor * A[i, i:]
    
    # Обратный ход
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - np.dot(A[i, i+1:], x[i+1:])) / A[i, i]
    
    return x


def lu_decomposition(A):
    """
    LU-разложение матрицы
    
    Parameters:
    -----------
    A : array-like
        Исходная матрица
        
    Returns:
    --------
    tuple
        (L, U) - нижняя треугольная и верхняя треугольная матрицы
    """
    return linalg.lu(np.array(A), permute_l=True)[1:]


def jacobi_method(A, b, x0=None, tol=1e-6, max_iter=100):
    """
    Метод Якоби для решения системы линейных уравнений Ax = b
    
    Parameters:
    -----------
    A : array-like
        Матрица коэффициентов
    b : array-like
        Вектор правой части
    x0 : array-like, optional
        Начальное приближение
    tol : float, optional
        Точность
    max_iter : int, optional
        Максимальное количество итераций
        
    Returns:
    --------
    tuple
        (решение, количество итераций, история итераций)
    """
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    
    n = len(b)
    
    if x0 is None:
        x0 = np.zeros(n)
    
    x = np.array(x0, dtype=float)
    history = [x.copy()]
    
    for k in range(max_iter):
        x_new = np.zeros(n)
        
        for i in range(n):
            s = 0
            for j in range(n):
                if i != j:
                    s += A[i, j] * x[j]
            x_new[i] = (b[i] - s) / A[i, i]
        
        history.append(x_new.copy())
        
        if np.linalg.norm(x_new - x) < tol:
            return x_new, k + 1, history
        
        x = x_new
    
    return x, max_iter, history


def gauss_seidel_method(A, b, x0=None, tol=1e-6, max_iter=100):
    """
    Метод Гаусса-Зейделя для решения системы линейных уравнений Ax = b
    
    Parameters:
    -----------
    A : array-like
        Матрица коэффициентов
    b : array-like
        Вектор правой части
    x0 : array-like, optional
        Начальное приближение
    tol : float, optional
        Точность
    max_iter : int, optional
        Максимальное количество итераций
        
    Returns:
    --------
    tuple
        (решение, количество итераций, история итераций)
    """
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    
    n = len(b)
    
    if x0 is None:
        x0 = np.zeros(n)
    
    x = np.array(x0, dtype=float)
    history = [x.copy()]
    
    for k in range(max_iter):
        x_new = np.copy(x)
        
        for i in range(n):
            s1 = np.dot(A[i, :i], x_new[:i])
            s2 = np.dot(A[i, i+1:], x[i+1:])
            x_new[i] = (b[i] - s1 - s2) / A[i, i]
        
        history.append(x_new.copy())
        
        if np.linalg.norm(x_new - x) < tol:
            return x_new, k + 1, history
        
        x = x_new
    
    return x, max_iter, history 