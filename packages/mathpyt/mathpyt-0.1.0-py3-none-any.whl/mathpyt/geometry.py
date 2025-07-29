"""
Шаблоны кода для геометрии
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def distance_2d(p1, p2):
    """
    Вычисление расстояния между двумя точками на плоскости
    
    Parameters:
    -----------
    p1 : tuple или list
        Координаты первой точки (x1, y1)
    p2 : tuple или list
        Координаты второй точки (x2, y2)
        
    Returns:
    --------
    float
        Расстояние между точками
    """
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def distance_3d(p1, p2):
    """
    Вычисление расстояния между двумя точками в пространстве
    
    Parameters:
    -----------
    p1 : tuple или list
        Координаты первой точки (x1, y1, z1)
    p2 : tuple или list
        Координаты второй точки (x2, y2, z2)
        
    Returns:
    --------
    float
        Расстояние между точками
    """
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)


def triangle_area(a, b, c):
    """
    Вычисление площади треугольника по длинам сторон (формула Герона)
    
    Parameters:
    -----------
    a : float
        Длина первой стороны
    b : float
        Длина второй стороны
    c : float
        Длина третьей стороны
        
    Returns:
    --------
    float
        Площадь треугольника
    """
    # Полупериметр
    s = (a + b + c) / 2
    
    # Формула Герона
    area = np.sqrt(s * (s - a) * (s - b) * (s - c))
    
    return area


def triangle_area_vertices(p1, p2, p3):
    """
    Вычисление площади треугольника по координатам вершин
    
    Parameters:
    -----------
    p1 : tuple или list
        Координаты первой вершины (x1, y1)
    p2 : tuple или list
        Координаты второй вершины (x2, y2)
    p3 : tuple или list
        Координаты третьей вершины (x3, y3)
        
    Returns:
    --------
    float
        Площадь треугольника
    """
    # Вычисляем длины сторон
    a = distance_2d(p1, p2)
    b = distance_2d(p2, p3)
    c = distance_2d(p3, p1)
    
    return triangle_area(a, b, c)


def circle_area(radius):
    """
    Вычисление площади круга
    
    Parameters:
    -----------
    radius : float
        Радиус круга
        
    Returns:
    --------
    float
        Площадь круга
    """
    return np.pi * radius**2


def sphere_volume(radius):
    """
    Вычисление объема шара
    
    Parameters:
    -----------
    radius : float
        Радиус шара
        
    Returns:
    --------
    float
        Объем шара
    """
    return (4/3) * np.pi * radius**3


def dot_product(v1, v2):
    """
    Вычисление скалярного произведения векторов
    
    Parameters:
    -----------
    v1 : array-like
        Первый вектор
    v2 : array-like
        Второй вектор
        
    Returns:
    --------
    float
        Скалярное произведение
    """
    return np.dot(v1, v2)


def cross_product(v1, v2):
    """
    Вычисление векторного произведения векторов
    
    Parameters:
    -----------
    v1 : array-like
        Первый вектор
    v2 : array-like
        Второй вектор
        
    Returns:
    --------
    numpy.ndarray
        Векторное произведение
    """
    return np.cross(v1, v2)


def vector_length(v):
    """
    Вычисление длины вектора
    
    Parameters:
    -----------
    v : array-like
        Вектор
        
    Returns:
    --------
    float
        Длина вектора
    """
    return np.linalg.norm(v)


def angle_between_vectors(v1, v2):
    """
    Вычисление угла между векторами в радианах
    
    Parameters:
    -----------
    v1 : array-like
        Первый вектор
    v2 : array-like
        Второй вектор
        
    Returns:
    --------
    float
        Угол между векторами в радианах
    """
    dot = dot_product(v1, v2)
    len1 = vector_length(v1)
    len2 = vector_length(v2)
    
    # Защита от деления на ноль
    if len1 * len2 == 0:
        return 0
    
    # Защита от ошибок округления
    cos_angle = dot / (len1 * len2)
    cos_angle = max(-1.0, min(1.0, cos_angle))
    
    return np.arccos(cos_angle)


def point_line_distance_2d(point, line_point1, line_point2):
    """
    Вычисление расстояния от точки до прямой на плоскости
    
    Parameters:
    -----------
    point : tuple или list
        Координаты точки (x, y)
    line_point1 : tuple или list
        Координаты первой точки на прямой (x1, y1)
    line_point2 : tuple или list
        Координаты второй точки на прямой (x2, y2)
        
    Returns:
    --------
    float
        Расстояние от точки до прямой
    """
    x0, y0 = point
    x1, y1 = line_point1
    x2, y2 = line_point2
    
    # Вычисляем расстояние
    numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denominator = np.sqrt((y2 - y1)**2 + (x2 - x1)**2)
    
    # Защита от деления на ноль
    if denominator == 0:
        return distance_2d(point, line_point1)
    
    return numerator / denominator


def plot_2d_points(points, labels=None, title='Points in 2D', xlabel='X', ylabel='Y'):
    """
    Построение точек на плоскости
    
    Parameters:
    -----------
    points : list of tuples или numpy.ndarray
        Список точек в формате [(x1, y1), (x2, y2), ...]
    labels : list, optional
        Список меток для точек
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
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Преобразуем список точек в массивы координат
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    
    # Строим точки
    ax.scatter(x, y, c='blue', s=50)
    
    # Добавляем метки, если они есть
    if labels is not None:
        for i, label in enumerate(labels):
            ax.annotate(label, (x[i], y[i]), xytext=(5, 5), textcoords='offset points')
    
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    return fig, ax


def plot_3d_points(points, labels=None, title='Points in 3D', xlabel='X', ylabel='Y', zlabel='Z'):
    """
    Построение точек в пространстве
    
    Parameters:
    -----------
    points : list of tuples или numpy.ndarray
        Список точек в формате [(x1, y1, z1), (x2, y2, z2), ...]
    labels : list, optional
        Список меток для точек
    title : str, optional
        Заголовок графика
    xlabel : str, optional
        Подпись оси X
    ylabel : str, optional
        Подпись оси Y
    zlabel : str, optional
        Подпись оси Z
        
    Returns:
    --------
    tuple
        (figure, axis)
    """
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Преобразуем список точек в массивы координат
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    z = [p[2] for p in points]
    
    # Строим точки
    ax.scatter(x, y, z, c='blue', s=50)
    
    # Добавляем метки, если они есть
    if labels is not None:
        for i, label in enumerate(labels):
            ax.text(x[i], y[i], z[i], label)
    
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    
    return fig, ax 