"""
Шаблоны кода для линейной алгебры
"""
import numpy as np


def matrix_multiplication(A, B):
    """
    Умножение матриц A и B
    
    Parameters:
    -----------
    A : numpy.ndarray
        Первая матрица
    B : numpy.ndarray
        Вторая матрица
        
    Returns:
    --------
    numpy.ndarray
        Результат умножения матриц A и B
    """
    return np.dot(A, B)


def matrix_determinant(A):
    """
    Вычисление определителя матрицы A
    
    Parameters:
    -----------
    A : numpy.ndarray
        Матрица
        
    Returns:
    --------
    float
        Определитель матрицы A
    """
    return np.linalg.det(A)


def solve_linear_system(A, b):
    """
    Решение системы линейных уравнений Ax = b
    
    Parameters:
    -----------
    A : numpy.ndarray
        Матрица коэффициентов
    b : numpy.ndarray
        Вектор правой части
        
    Returns:
    --------
    numpy.ndarray
        Решение системы
    """
    return np.linalg.solve(A, b)


def matrix_inverse(A):
    """
    Нахождение обратной матрицы
    
    Parameters:
    -----------
    A : numpy.ndarray
        Матрица
        
    Returns:
    --------
    numpy.ndarray
        Обратная матрица
    """
    return np.linalg.inv(A)


def eigenvalues(A):
    """
    Нахождение собственных значений матрицы
    
    Parameters:
    -----------
    A : numpy.ndarray
        Матрица
        
    Returns:
    --------
    numpy.ndarray
        Собственные значения
    """
    return np.linalg.eigvals(A)


def eigenvectors(A):
    """
    Нахождение собственных значений и собственных векторов матрицы
    
    Parameters:
    -----------
    A : numpy.ndarray
        Матрица
        
    Returns:
    --------
    tuple
        (собственные значения, собственные векторы)
    """
    return np.linalg.eig(A) 