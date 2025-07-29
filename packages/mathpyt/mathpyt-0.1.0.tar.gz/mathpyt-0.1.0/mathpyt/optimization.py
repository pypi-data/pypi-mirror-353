"""
Шаблоны кода для оптимизации
"""
import numpy as np
from scipy import optimize


def gradient_descent(func, grad_func, x0, learning_rate=0.01, max_iter=1000, tol=1e-6):
    """
    Реализация градиентного спуска
    
    Parameters:
    -----------
    func : callable
        Целевая функция
    grad_func : callable
        Функция, вычисляющая градиент
    x0 : array-like
        Начальная точка
    learning_rate : float, optional
        Скорость обучения
    max_iter : int, optional
        Максимальное количество итераций
    tol : float, optional
        Порог сходимости
        
    Returns:
    --------
    tuple
        (оптимальная точка, значение функции, история итераций)
    """
    x = np.array(x0, dtype=float)
    history = [x.copy()]
    
    for i in range(max_iter):
        grad = grad_func(x)
        x_new = x - learning_rate * grad
        
        if np.linalg.norm(x_new - x) < tol:
            break
            
        x = x_new
        history.append(x.copy())
    
    return x, func(x), history


def scipy_minimize(func, x0, method='BFGS', jac=None, bounds=None, constraints=None):
    """
    Оптимизация с использованием scipy.optimize.minimize
    
    Parameters:
    -----------
    func : callable
        Целевая функция
    x0 : array-like
        Начальная точка
    method : str, optional
        Метод оптимизации
    jac : callable, optional
        Якобиан функции
    bounds : sequence, optional
        Границы для переменных
    constraints : dict или sequence of dict, optional
        Ограничения
        
    Returns:
    --------
    scipy.optimize.OptimizeResult
        Результат оптимизации
    """
    return optimize.minimize(func, x0, method=method, jac=jac, bounds=bounds, constraints=constraints)


def linear_programming(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, bounds=None):
    """
    Решение задачи линейного программирования
    
    Parameters:
    -----------
    c : array-like
        Коэффициенты целевой функции
    A_ub : array-like, optional
        Матрица коэффициентов для неравенств
    b_ub : array-like, optional
        Правая часть для неравенств
    A_eq : array-like, optional
        Матрица коэффициентов для равенств
    b_eq : array-like, optional
        Правая часть для равенств
    bounds : sequence, optional
        Границы для переменных
        
    Returns:
    --------
    scipy.optimize.OptimizeResult
        Результат оптимизации
    """
    return optimize.linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds)


def newton_method(func, grad_func, hess_func, x0, max_iter=100, tol=1e-6):
    """
    Реализация метода Ньютона для оптимизации
    
    Parameters:
    -----------
    func : callable
        Целевая функция
    grad_func : callable
        Функция, вычисляющая градиент
    hess_func : callable
        Функция, вычисляющая гессиан
    x0 : array-like
        Начальная точка
    max_iter : int, optional
        Максимальное количество итераций
    tol : float, optional
        Порог сходимости
        
    Returns:
    --------
    tuple
        (оптимальная точка, значение функции, история итераций)
    """
    x = np.array(x0, dtype=float)
    history = [x.copy()]
    
    for i in range(max_iter):
        grad = grad_func(x)
        hess = hess_func(x)
        
        try:
            delta = np.linalg.solve(hess, -grad)
        except np.linalg.LinAlgError:
            # Если гессиан вырожден, используем псевдообратную матрицу
            delta = -np.dot(np.linalg.pinv(hess), grad)
        
        x_new = x + delta
        
        if np.linalg.norm(x_new - x) < tol:
            break
            
        x = x_new
        history.append(x.copy())
    
    return x, func(x), history


def simulated_annealing(func, x0, T0=100.0, T_min=1e-5, alpha=0.9, max_iter=1000):
    """
    Реализация метода имитации отжига
    
    Parameters:
    -----------
    func : callable
        Целевая функция
    x0 : array-like
        Начальная точка
    T0 : float, optional
        Начальная температура
    T_min : float, optional
        Минимальная температура
    alpha : float, optional
        Коэффициент охлаждения
    max_iter : int, optional
        Максимальное количество итераций
        
    Returns:
    --------
    tuple
        (оптимальная точка, значение функции, история итераций)
    """
    x = np.array(x0, dtype=float)
    f_x = func(x)
    
    x_best = x.copy()
    f_best = f_x
    
    history = [(x.copy(), f_x)]
    
    T = T0
    
    for i in range(max_iter):
        if T < T_min:
            break
            
        # Генерация нового решения
        x_new = x + np.random.normal(0, T, size=x.shape)
        f_new = func(x_new)
        
        # Критерий Метрополиса
        delta_f = f_new - f_x
        
        if delta_f < 0 or np.random.random() < np.exp(-delta_f / T):
            x = x_new
            f_x = f_new
            
            if f_x < f_best:
                x_best = x.copy()
                f_best = f_x
        
        history.append((x.copy(), f_x))
        T *= alpha
    
    return x_best, f_best, history 