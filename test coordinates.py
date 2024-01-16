import matplotlib.pyplot as plt
import numpy as np

def distribute_points(center_x, center_y, radius, num_points):
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    x_coords = center_x + radius * np.cos(angles)
    y_coords = center_y + radius * np.sin(angles)
    print(x_coords, y_coords)
    return x_coords, y_coords

# Центральная точка
center_x, center_y = 0, 0

# Радиус и количество точек
radius = 1
num_points = 20

# Распределение точек
x_coords, y_coords = distribute_points(center_x, center_y, radius, num_points)

# Визуализация
plt.scatter(center_x, center_y, color='red')  # центральная точка
plt.scatter(x_coords, y_coords, color='blue')  # равномерно распределенные точки
plt.gca().set_aspect('equal', adjustable='box')  # равномерные масштабы осей
plt.show()