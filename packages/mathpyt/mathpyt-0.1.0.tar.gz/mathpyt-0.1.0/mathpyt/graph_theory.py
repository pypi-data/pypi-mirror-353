"""
Шаблоны кода для теории графов
"""
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def create_graph_from_edges(edges, directed=False):
    """
    Создание графа из списка рёбер
    
    Parameters:
    -----------
    edges : list of tuples
        Список рёбер в формате (u, v) или (u, v, weight)
    directed : bool, optional
        Создавать ли ориентированный граф
        
    Returns:
    --------
    networkx.Graph or networkx.DiGraph
        Созданный граф
    """
    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
    
    for edge in edges:
        if len(edge) == 2:
            u, v = edge
            G.add_edge(u, v)
        elif len(edge) == 3:
            u, v, w = edge
            G.add_edge(u, v, weight=w)
    
    return G


def create_graph_from_matrix(matrix, directed=False):
    """
    Создание графа из матрицы смежности
    
    Parameters:
    -----------
    matrix : array-like
        Матрица смежности
    directed : bool, optional
        Создавать ли ориентированный граф
        
    Returns:
    --------
    networkx.Graph or networkx.DiGraph
        Созданный граф
    """
    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
    
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            if matrix[i][j] != 0:
                G.add_edge(i, j, weight=matrix[i][j])
    
    return G


def shortest_path(G, source, target):
    """
    Нахождение кратчайшего пути между двумя вершинами
    
    Parameters:
    -----------
    G : networkx.Graph
        Граф
    source : node
        Начальная вершина
    target : node
        Конечная вершина
        
    Returns:
    --------
    tuple
        (длина пути, список вершин пути)
    """
    try:
        path = nx.shortest_path(G, source=source, target=target, weight='weight')
        length = nx.shortest_path_length(G, source=source, target=target, weight='weight')
        return length, path
    except nx.NetworkXNoPath:
        return float('inf'), []


def dijkstra_algorithm(G, source):
    """
    Алгоритм Дейкстры для нахождения кратчайших путей из одной вершины
    
    Parameters:
    -----------
    G : networkx.Graph
        Граф
    source : node
        Начальная вершина
        
    Returns:
    --------
    tuple
        (словарь расстояний, словарь предшественников)
    """
    return nx.single_source_dijkstra(G, source)


def minimum_spanning_tree(G):
    """
    Нахождение минимального остовного дерева
    
    Parameters:
    -----------
    G : networkx.Graph
        Граф
        
    Returns:
    --------
    networkx.Graph
        Минимальное остовное дерево
    """
    return nx.minimum_spanning_tree(G)


def topological_sort(G):
    """
    Топологическая сортировка ориентированного ациклического графа
    
    Parameters:
    -----------
    G : networkx.DiGraph
        Ориентированный граф
        
    Returns:
    --------
    list
        Вершины в топологическом порядке
    """
    try:
        return list(nx.topological_sort(G))
    except nx.NetworkXUnfeasible:
        return []  # Граф содержит циклы


def strongly_connected_components(G):
    """
    Нахождение сильно связных компонент в ориентированном графе
    
    Parameters:
    -----------
    G : networkx.DiGraph
        Ориентированный граф
        
    Returns:
    --------
    list
        Список сильно связных компонент
    """
    return list(nx.strongly_connected_components(G))


def plot_graph(G, pos=None, with_labels=True, node_color='skyblue', node_size=500, 
               edge_color='black', width=1.0, title='Graph'):
    """
    Визуализация графа
    
    Parameters:
    -----------
    G : networkx.Graph
        Граф
    pos : dict, optional
        Позиции вершин
    with_labels : bool, optional
        Отображать ли метки вершин
    node_color : str, optional
        Цвет вершин
    node_size : int, optional
        Размер вершин
    edge_color : str, optional
        Цвет рёбер
    width : float, optional
        Толщина рёбер
    title : str, optional
        Заголовок графика
        
    Returns:
    --------
    tuple
        (figure, axis)
    """
    if pos is None:
        pos = nx.spring_layout(G)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    nx.draw(G, pos, with_labels=with_labels, node_color=node_color, 
            node_size=node_size, edge_color=edge_color, width=width, ax=ax)
    
    # Если есть веса рёбер, отобразим их
    edge_labels = nx.get_edge_attributes(G, 'weight')
    if edge_labels:
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    ax.set_title(title)
    ax.axis('off')
    
    return fig, ax 