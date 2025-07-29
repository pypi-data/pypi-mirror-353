"""
Шаблоны кода для дифференциальных уравнений
"""
import numpy as np
from scipy import integrate
import matplotlib.pyplot as plt


def euler_method(f, t0, y0, t_end, h):
    """
    Метод Эйлера для решения ОДУ dy/dt = f(t, y)
    
    Parameters:
    -----------
    f : callable
        Правая часть уравнения dy/dt = f(t, y)
    t0 : float
        Начальное значение аргумента
    y0 : float или array-like
        Начальное значение функции
    t_end : float
        Конечное значение аргумента
    h : float
        Шаг интегрирования
        
    Returns:
    --------
    tuple
        (массив значений аргумента, массив значений функции)
    """
    # Количество шагов
    n_steps = int((t_end - t0) / h)
    
    # Массивы для хранения результатов
    t = np.zeros(n_steps + 1)
    y = np.zeros((n_steps + 1, *np.atleast_1d(y0).shape))
    
    # Начальные условия
    t[0] = t0
    y[0] = y0
    
    # Метод Эйлера
    for i in range(n_steps):
        y[i+1] = y[i] + h * f(t[i], y[i])
        t[i+1] = t[i] + h
    
    return t, y


def runge_kutta4(f, t0, y0, t_end, h):
    """
    Метод Рунге-Кутты 4-го порядка для решения ОДУ dy/dt = f(t, y)
    
    Parameters:
    -----------
    f : callable
        Правая часть уравнения dy/dt = f(t, y)
    t0 : float
        Начальное значение аргумента
    y0 : float или array-like
        Начальное значение функции
    t_end : float
        Конечное значение аргумента
    h : float
        Шаг интегрирования
        
    Returns:
    --------
    tuple
        (массив значений аргумента, массив значений функции)
    """
    # Количество шагов
    n_steps = int((t_end - t0) / h)
    
    # Массивы для хранения результатов
    t = np.zeros(n_steps + 1)
    y = np.zeros((n_steps + 1, *np.atleast_1d(y0).shape))
    
    # Начальные условия
    t[0] = t0
    y[0] = y0
    
    # Метод Рунге-Кутты 4-го порядка
    for i in range(n_steps):
        k1 = f(t[i], y[i])
        k2 = f(t[i] + h/2, y[i] + h*k1/2)
        k3 = f(t[i] + h/2, y[i] + h*k2/2)
        k4 = f(t[i] + h, y[i] + h*k3)
        
        y[i+1] = y[i] + h * (k1 + 2*k2 + 2*k3 + k4) / 6
        t[i+1] = t[i] + h
    
    return t, y


def scipy_solve_ivp(f, t_span, y0, method='RK45', t_eval=None):
    """
    Решение задачи Коши для ОДУ с использованием scipy.integrate.solve_ivp
    
    Parameters:
    -----------
    f : callable
        Правая часть уравнения dy/dt = f(t, y)
    t_span : tuple
        Интервал интегрирования (t0, t_end)
    y0 : array-like
        Начальное значение функции
    method : str, optional
        Метод интегрирования
    t_eval : array-like, optional
        Точки, в которых нужно вычислить решение
        
    Returns:
    --------
    scipy.integrate.OdeResult
        Результат интегрирования
    """
    return integrate.solve_ivp(f, t_span, y0, method=method, t_eval=t_eval)


def system_of_odes(f, t0, y0, t_end, h):
    """
    Решение системы ОДУ методом Рунге-Кутты 4-го порядка
    
    Parameters:
    -----------
    f : callable
        Правая часть системы dy/dt = f(t, y)
    t0 : float
        Начальное значение аргумента
    y0 : array-like
        Начальные значения функций
    t_end : float
        Конечное значение аргумента
    h : float
        Шаг интегрирования
        
    Returns:
    --------
    tuple
        (массив значений аргумента, массив значений функций)
    """
    # Используем тот же метод Рунге-Кутты, что и для одного уравнения
    return runge_kutta4(f, t0, y0, t_end, h)


def plot_solution(t, y, title='Solution of ODE', xlabel='t', ylabel='y'):
    """
    Построение графика решения ОДУ
    
    Parameters:
    -----------
    t : array-like
        Значения аргумента
    y : array-like
        Значения функции
    title : str, optional
        Заголовок графика
    xlabel : str, optional
        Подпись оси X
    ylabel : str, optional
        Подпись оси Y
        
    Returns:
    --------
    tuple
        (figure, axis)
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Если y - массив векторов, строим график для каждой компоненты
    if len(y.shape) > 1 and y.shape[1] > 1:
        for i in range(y.shape[1]):
            ax.plot(t, y[:, i], label=f'{ylabel}_{i+1}')
        ax.legend()
    else:
        ax.plot(t, y, 'b-', linewidth=2)
    
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    return fig, ax


def phase_portrait(t, y, title='Phase Portrait', xlabel='y_1', ylabel='y_2'):
    """
    Построение фазового портрета для системы из двух ОДУ
    
    Parameters:
    -----------
    t : array-like
        Значения аргумента
    y : array-like
        Значения функций (должно быть двумерным)
    title : str, optional
        Заголовок графика
    xlabel : str, optional
        Подпись оси X
    ylabel : str, optional
        Подпись оси Y
        
    Returns:
    --------
    tuple
        (figure, axis)
    """
    if len(y.shape) <= 1 or y.shape[1] < 2:
        raise ValueError("Для построения фазового портрета нужно минимум 2 переменные")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Строим фазовый портрет
    ax.plot(y[:, 0], y[:, 1], 'b-', linewidth=2)
    
    # Отмечаем начальную точку
    ax.plot(y[0, 0], y[0, 1], 'go', markersize=8, label='Start')
    
    # Отмечаем конечную точку
    ax.plot(y[-1, 0], y[-1, 1], 'ro', markersize=8, label='End')
    
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    return fig, ax


def boundary_value_problem(p, q, r, a, b, alpha, beta, gamma, delta, n):
    """
    Решение краевой задачи методом конечных разностей
    y'' + p(x)y' + q(x)y = r(x), y(a) = alpha, y(b) = beta
    или
    y(a) = alpha, y'(a) = beta (если gamma=0, delta=1)
    или
    y'(b) = alpha, y(b) = beta (если gamma=1, delta=0)
    
    Parameters:
    -----------
    p : callable
        Коэффициент при y'
    q : callable
        Коэффициент при y
    r : callable
        Правая часть уравнения
    a : float
        Левая граница интервала
    b : float
        Правая граница интервала
    alpha : float
        Первое краевое условие
    beta : float
        Второе краевое условие
    gamma : float
        Коэффициент при y(a) в первом краевом условии
    delta : float
        Коэффициент при y'(a) в первом краевом условии
    n : int
        Количество узлов сетки
        
    Returns:
    --------
    tuple
        (массив узлов сетки, массив значений решения)
    """
    # Шаг сетки
    h = (b - a) / (n - 1)
    
    # Узлы сетки
    x = np.linspace(a, b, n)
    
    # Формирование системы уравнений
    A = np.zeros((n, n))
    f = np.zeros(n)
    
    # Внутренние узлы
    for i in range(1, n-1):
        A[i, i-1] = 1 - h * p(x[i]) / 2
        A[i, i] = -2 + h**2 * q(x[i])
        A[i, i+1] = 1 + h * p(x[i]) / 2
        f[i] = h**2 * r(x[i])
    
    # Граничные условия
    if gamma == 1 and delta == 0:  # y(a) = alpha, y'(b) = beta
        A[0, 0] = 1
        f[0] = alpha
        
        A[n-1, n-2] = -1
        A[n-1, n-1] = 1
        f[n-1] = h * beta
    elif gamma == 0 and delta == 1:  # y'(a) = alpha, y(b) = beta
        A[0, 0] = -1
        A[0, 1] = 1
        f[0] = h * alpha
        
        A[n-1, n-1] = 1
        f[n-1] = beta
    else:  # y(a) = alpha, y(b) = beta
        A[0, 0] = 1
        f[0] = alpha
        
        A[n-1, n-1] = 1
        f[n-1] = beta
    
    # Решение системы
    y = np.linalg.solve(A, f)
    
    return x, y 