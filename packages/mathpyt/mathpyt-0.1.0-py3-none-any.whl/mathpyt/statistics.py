"""
Шаблоны кода для статистики
"""
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


def descriptive_statistics(data):
    """
    Вычисление основных статистических показателей
    
    Parameters:
    -----------
    data : array-like
        Массив данных
        
    Returns:
    --------
    dict
        Словарь со статистическими показателями
    """
    return {
        'mean': np.mean(data),
        'median': np.median(data),
        'std': np.std(data),
        'var': np.var(data),
        'min': np.min(data),
        'max': np.max(data),
        'q1': np.percentile(data, 25),
        'q3': np.percentile(data, 75)
    }


def confidence_interval(data, confidence=0.95):
    """
    Вычисление доверительного интервала для среднего
    
    Parameters:
    -----------
    data : array-like
        Массив данных
    confidence : float, optional
        Уровень доверия
        
    Returns:
    --------
    tuple
        (нижняя граница, верхняя граница)
    """
    n = len(data)
    mean = np.mean(data)
    sem = stats.sem(data)
    interval = sem * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean - interval, mean + interval


def t_test(data1, data2, alpha=0.05):
    """
    Проведение t-теста для двух независимых выборок
    
    Parameters:
    -----------
    data1 : array-like
        Первая выборка
    data2 : array-like
        Вторая выборка
    alpha : float, optional
        Уровень значимости
        
    Returns:
    --------
    dict
        Результаты теста
    """
    t_stat, p_value = stats.ttest_ind(data1, data2)
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < alpha
    }


def correlation_analysis(x, y):
    """
    Анализ корреляции между двумя наборами данных
    
    Parameters:
    -----------
    x : array-like
        Первый набор данных
    y : array-like
        Второй набор данных
        
    Returns:
    --------
    dict
        Результаты анализа корреляции
    """
    pearson_r, pearson_p = stats.pearsonr(x, y)
    spearman_r, spearman_p = stats.spearmanr(x, y)
    
    return {
        'pearson_r': pearson_r,
        'pearson_p': pearson_p,
        'spearman_r': spearman_r,
        'spearman_p': spearman_p
    }


def linear_regression(x, y):
    """
    Линейная регрессия
    
    Parameters:
    -----------
    x : array-like
        Независимая переменная
    y : array-like
        Зависимая переменная
        
    Returns:
    --------
    dict
        Результаты регрессионного анализа
    """
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_value**2,
        'p_value': p_value,
        'std_err': std_err
    }


def plot_histogram(data, bins=10, title='Histogram', xlabel='Value', ylabel='Frequency'):
    """
    Построение гистограммы
    
    Parameters:
    -----------
    data : array-like
        Данные для построения гистограммы
    bins : int, optional
        Количество бинов
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
    ax.hist(data, bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    return fig, ax 