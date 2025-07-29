"""
Шаблоны кода для комплексного анализа
"""
import numpy as np
import matplotlib.pyplot as plt
import cmath


def complex_plot(z_list, title='Complex Numbers', marker='o', color='blue', size=50):
    """
    Построение комплексных чисел на комплексной плоскости
    
    Parameters:
    -----------
    z_list : list или array
        Список комплексных чисел
    title : str, optional
        Заголовок графика
    marker : str, optional
        Маркер для точек
    color : str, optional
        Цвет точек
    size : int, optional
        Размер точек
        
    Returns:
    --------
    tuple
        (figure, axis)
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Разделяем действительную и мнимую части
    real_parts = [z.real for z in z_list]
    imag_parts = [z.imag for z in z_list]
    
    # Строим точки
    ax.scatter(real_parts, imag_parts, c=color, s=size, marker=marker)
    
    # Добавляем оси
    ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    
    # Настраиваем график
    ax.set_title(title)
    ax.set_xlabel('Re(z)')
    ax.set_ylabel('Im(z)')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Устанавливаем одинаковый масштаб по осям
    ax.set_aspect('equal')
    
    return fig, ax


def complex_function_plot(f, x_range=(-5, 5), y_range=(-5, 5), n_points=100, 
                         plot_type='magnitude', cmap='viridis'):
    """
    Построение комплексной функции на комплексной плоскости
    
    Parameters:
    -----------
    f : callable
        Комплексная функция одной комплексной переменной
    x_range : tuple, optional
        Диапазон по действительной оси
    y_range : tuple, optional
        Диапазон по мнимой оси
    n_points : int, optional
        Количество точек по каждой оси
    plot_type : str, optional
        Тип графика: 'magnitude' - модуль, 'phase' - аргумент, 'real' - действительная часть, 'imag' - мнимая часть
    cmap : str, optional
        Цветовая карта
        
    Returns:
    --------
    tuple
        (figure, axis)
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = np.linspace(y_range[0], y_range[1], n_points)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    
    # Вычисляем значения функции
    W = np.zeros_like(Z, dtype=complex)
    for i in range(n_points):
        for j in range(n_points):
            try:
                W[i, j] = f(Z[i, j])
            except:
                W[i, j] = np.nan + 1j * np.nan
    
    # Выбираем, что отображать
    if plot_type == 'magnitude':
        plot_data = np.abs(W)
        title = 'Magnitude of f(z)'
    elif plot_type == 'phase':
        plot_data = np.angle(W)
        title = 'Phase of f(z)'
    elif plot_type == 'real':
        plot_data = np.real(W)
        title = 'Real part of f(z)'
    elif plot_type == 'imag':
        plot_data = np.imag(W)
        title = 'Imaginary part of f(z)'
    else:
        raise ValueError("plot_type должен быть 'magnitude', 'phase', 'real' или 'imag'")
    
    # Создаем график
    fig, ax = plt.subplots(figsize=(10, 8))
    c = ax.pcolormesh(X, Y, plot_data, cmap=cmap, shading='auto')
    fig.colorbar(c, ax=ax)
    
    ax.set_title(title)
    ax.set_xlabel('Re(z)')
    ax.set_ylabel('Im(z)')
    
    # Устанавливаем одинаковый масштаб по осям
    ax.set_aspect('equal')
    
    return fig, ax


def complex_roots(z, n):
    """
    Вычисление всех корней n-й степени из комплексного числа
    
    Parameters:
    -----------
    z : complex
        Комплексное число
    n : int
        Степень корня
        
    Returns:
    --------
    list
        Список всех корней n-й степени
    """
    if n <= 0:
        raise ValueError("n должно быть положительным целым числом")
    
    # Вычисляем модуль и аргумент
    r = abs(z)
    phi = cmath.phase(z)
    
    # Вычисляем корни
    roots = []
    for k in range(n):
        # r^(1/n) * exp(i * (phi + 2*pi*k) / n)
        root_r = r ** (1/n)
        root_phi = (phi + 2 * np.pi * k) / n
        root = root_r * (np.cos(root_phi) + 1j * np.sin(root_phi))
        roots.append(root)
    
    return roots


def complex_power(z, n):
    """
    Возведение комплексного числа в степень
    
    Parameters:
    -----------
    z : complex
        Комплексное число
    n : int или float
        Показатель степени
        
    Returns:
    --------
    complex
        Результат возведения в степень
    """
    return z ** n


def complex_exponential(z):
    """
    Вычисление экспоненты от комплексного числа
    
    Parameters:
    -----------
    z : complex
        Комплексное число
        
    Returns:
    --------
    complex
        Экспонента от z
    """
    return cmath.exp(z)


def complex_logarithm(z):
    """
    Вычисление натурального логарифма от комплексного числа
    
    Parameters:
    -----------
    z : complex
        Комплексное число
        
    Returns:
    --------
    complex
        Главное значение логарифма
    """
    return cmath.log(z)


def complex_sine(z):
    """
    Вычисление синуса от комплексного числа
    
    Parameters:
    -----------
    z : complex
        Комплексное число
        
    Returns:
    --------
    complex
        Синус от z
    """
    return cmath.sin(z)


def complex_cosine(z):
    """
    Вычисление косинуса от комплексного числа
    
    Parameters:
    -----------
    z : complex
        Комплексное число
        
    Returns:
    --------
    complex
        Косинус от z
    """
    return cmath.cos(z)


def moebius_transform(z, a, b, c, d):
    """
    Вычисление дробно-линейного преобразования (преобразования Мёбиуса)
    f(z) = (a*z + b) / (c*z + d)
    
    Parameters:
    -----------
    z : complex
        Комплексное число
    a, b, c, d : complex
        Коэффициенты преобразования
        
    Returns:
    --------
    complex
        Результат преобразования
    """
    if c * z + d == 0:
        return float('inf')  # Точка на бесконечности
    
    return (a * z + b) / (c * z + d)


def residue(f, z0, h=1e-5, n=32):
    """
    Вычисление вычета функции в точке
    
    Parameters:
    -----------
    f : callable
        Комплексная функция одной комплексной переменной
    z0 : complex
        Точка, в которой вычисляется вычет
    h : float, optional
        Радиус контура интегрирования
    n : int, optional
        Количество точек для численного интегрирования
        
    Returns:
    --------
    complex
        Вычет функции в точке z0
    """
    # Вычисляем интеграл по окружности радиуса h вокруг z0
    theta = np.linspace(0, 2*np.pi, n+1)[:-1]  # n точек на окружности
    z = z0 + h * np.exp(1j * theta)
    dz = 1j * h * np.exp(1j * theta)  # дифференциал
    
    # Вычисляем значения функции
    try:
        f_values = np.array([f(zi) for zi in z])
    except:
        # Если функция не определена в некоторых точках, используем другой подход
        return None
    
    # Вычисляем интеграл
    integral = np.sum(f_values * dz) / (2*np.pi*1j)
    
    return integral 