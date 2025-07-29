"""
Шаблоны кода для теории вероятностей
"""
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


def binomial_distribution(n, p, k=None):
    """
    Биномиальное распределение
    
    Parameters:
    -----------
    n : int
        Количество испытаний
    p : float
        Вероятность успеха в одном испытании
    k : int или array-like, optional
        Количество успехов
        
    Returns:
    --------
    float или array-like
        Вероятность k успехов в n испытаниях
    """
    if k is None:
        # Возвращаем все вероятности от 0 до n
        k = np.arange(n + 1)
    
    return stats.binom.pmf(k, n, p)


def poisson_distribution(lam, k=None):
    """
    Распределение Пуассона
    
    Parameters:
    -----------
    lam : float
        Параметр распределения (среднее значение)
    k : int или array-like, optional
        Количество событий
        
    Returns:
    --------
    float или array-like
        Вероятность k событий
    """
    if k is None:
        # Возвращаем вероятности от 0 до 3*lam (покрывает большую часть распределения)
        k = np.arange(int(3 * lam) + 1)
    
    return stats.poisson.pmf(k, lam)


def normal_distribution(x, mu=0, sigma=1):
    """
    Нормальное распределение
    
    Parameters:
    -----------
    x : float или array-like
        Точки, в которых вычисляется плотность вероятности
    mu : float, optional
        Математическое ожидание
    sigma : float, optional
        Стандартное отклонение
        
    Returns:
    --------
    float или array-like
        Плотность вероятности в точках x
    """
    return stats.norm.pdf(x, loc=mu, scale=sigma)


def normal_cdf(x, mu=0, sigma=1):
    """
    Функция распределения нормального закона
    
    Parameters:
    -----------
    x : float или array-like
        Точки, в которых вычисляется функция распределения
    mu : float, optional
        Математическое ожидание
    sigma : float, optional
        Стандартное отклонение
        
    Returns:
    --------
    float или array-like
        Значение функции распределения в точках x
    """
    return stats.norm.cdf(x, loc=mu, scale=sigma)


def exponential_distribution(x, lam):
    """
    Экспоненциальное распределение
    
    Parameters:
    -----------
    x : float или array-like
        Точки, в которых вычисляется плотность вероятности
    lam : float
        Параметр распределения (интенсивность)
        
    Returns:
    --------
    float или array-like
        Плотность вероятности в точках x
    """
    return stats.expon.pdf(x, scale=1/lam)


def uniform_distribution(x, a=0, b=1):
    """
    Равномерное распределение
    
    Parameters:
    -----------
    x : float или array-like
        Точки, в которых вычисляется плотность вероятности
    a : float, optional
        Нижняя граница интервала
    b : float, optional
        Верхняя граница интервала
        
    Returns:
    --------
    float или array-like
        Плотность вероятности в точках x
    """
    return stats.uniform.pdf(x, loc=a, scale=b-a)


def monte_carlo_integration(f, a, b, n=10000):
    """
    Интегрирование методом Монте-Карло
    
    Parameters:
    -----------
    f : callable
        Функция одной переменной
    a : float
        Нижний предел интегрирования
    b : float
        Верхний предел интегрирования
    n : int, optional
        Количество случайных точек
        
    Returns:
    --------
    tuple
        (значение интеграла, оценка погрешности)
    """
    # Генерация случайных точек
    x = np.random.uniform(a, b, n)
    y = np.array([f(xi) for xi in x])
    
    # Оценка интеграла
    integral = (b - a) * np.mean(y)
    
    # Оценка погрешности
    error = (b - a) * np.std(y) / np.sqrt(n)
    
    return integral, error


def plot_distribution(x, pdf, title='Probability Density Function', 
                      xlabel='x', ylabel='Probability Density'):
    """
    Построение графика плотности вероятности
    
    Parameters:
    -----------
    x : array-like
        Точки по оси X
    pdf : array-like
        Значения плотности вероятности
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
    ax.plot(x, pdf, 'b-', linewidth=2)
    ax.fill_between(x, pdf, alpha=0.2)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    return fig, ax


def bayes_theorem(p_a, p_b_given_a, p_b_given_not_a):
    """
    Теорема Байеса для вычисления апостериорной вероятности
    
    Parameters:
    -----------
    p_a : float
        Априорная вероятность события A
    p_b_given_a : float
        Условная вероятность события B при условии A
    p_b_given_not_a : float
        Условная вероятность события B при условии не-A
        
    Returns:
    --------
    float
        Апостериорная вероятность события A при условии B
    """
    # Вычисление полной вероятности события B
    p_b = p_b_given_a * p_a + p_b_given_not_a * (1 - p_a)
    
    # Теорема Байеса
    p_a_given_b = (p_b_given_a * p_a) / p_b
    
    return p_a_given_b 