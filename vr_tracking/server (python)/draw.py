import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import json, math

def normalize_angle(angle):
    """Приводит угол к диапазону [-π; π]."""
    angle = angle % (2 * math.pi)
    if angle > math.pi:
        angle -= 2 * math.pi
    return angle

def lerp_angle(a, b, t):
    """
    Плавно интерполирует между углами a и b с учётом цикличности.
    t – коэффициент интерполяции (0..1).
    """
    diff = (b - a + math.pi) % (2 * math.pi) - math.pi
    return a + diff * t

def euler_to_matrix(yaw, pitch, roll):
    """
    Вычисляет матрицу поворота для углов Эйлера по порядку Y, X, Z.
    Здесь:
      yaw   – поворот вокруг Y,
      pitch – поворот вокруг X,
      roll  – поворот вокруг Z.
    Композиция: R = R_y * R_x * R_z.
    """
    # Поворот вокруг Y (yaw)
    cy = math.cos(yaw)
    sy = math.sin(yaw)
    R_y = [
        [cy, 0, sy],
        [0, 1, 0],
        [-sy, 0, cy]
    ]
    # Поворот вокруг X (pitch)
    cx = math.cos(pitch)
    sx = math.sin(pitch)
    R_x = [
        [1, 0, 0],
        [0, cx, -sx],
        [0, sx, cx]
    ]
    # Поворот вокруг Z (roll)
    cz = math.cos(roll)
    sz = math.sin(roll)
    R_z = [
        [cz, -sz, 0],
        [sz, cz, 0],
        [0, 0, 1]
    ]
    # Композитная матрица: сначала R_y, затем R_x, затем R_z
    R_temp = [[sum(R_y[i][k] * R_x[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    R = [[sum(R_temp[i][k] * R_z[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return R

def draw_cube():
    """Рисует куб с разными цветами граней."""
    glBegin(GL_QUADS)
    # Передняя грань
    glColor3f(0, 1, 1)
    glVertex3f(-1, -1,  1)
    glVertex3f( 1, -1,  1)
    glVertex3f( 1,  1,  1)
    glVertex3f(-1,  1,  1)
    # Задняя грань
    glColor3f(1, 0.5, 0)
    glVertex3f(-1, -1, -1)
    glVertex3f(-1,  1, -1)
    glVertex3f( 1,  1, -1)
    glVertex3f( 1, -1, -1)
    # Левая грань
    glColor3f(0.5, 0, 0.5)
    glVertex3f(-1, -1, -1)
    glVertex3f(-1, -1,  1)
    glVertex3f(-1,  1,  1)
    glVertex3f(-1,  1, -1)
    # Правая грань
    glColor3f(0, 0.5, 0.5)
    glVertex3f(1, -1, -1)
    glVertex3f(1,  1, -1)
    glVertex3f(1,  1,  1)
    glVertex3f(1, -1,  1)
    # Верхняя грань
    glColor3f(1, 1, 0)
    glVertex3f(-1, 1, -1)
    glVertex3f(-1, 1,  1)
    glVertex3f( 1, 1,  1)
    glVertex3f( 1, 1, -1)
    # Нижняя грань
    glColor3f(1, 0, 0)
    glVertex3f(-1, -1, -1)
    glVertex3f( 1, -1, -1)
    glVertex3f( 1, -1,  1)
    glVertex3f(-1, -1,  1)
    glEnd()

# Инициализация Pygame и создание окна с OpenGL-контекстом
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

# Включаем тест глубины и задаём цвет очистки (фон)
glEnable(GL_DEPTH_TEST)
glClearColor(0.2, 0.2, 0.2, 1.0)

# Настройка матрицы проекции
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
# Переход в режим модели
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glTranslatef(0, 0, -5)

# Начальные значения углов куба (в радианах)
current_yaw   = 0.0
current_pitch = 0.0
current_roll  = 0.0

# Целевые значения углов
target_yaw   = 0.0
target_pitch = 0.0
target_roll  = 0.0

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            quit()

    # Пытаемся прочитать данные из orientation.json
    try:
        with open("orientation.json", "r") as f:
            data = json.load(f)
        # Читаем и нормализуем углы:
        # yaw и pitch оставляем как есть (но нормализуем yaw)
        target_yaw   = normalize_angle(data["y"])    # yaw
        target_pitch = data["p"]                     # pitch
        # Инвертируем roll сразу и нормализуем в диапазоне [-π; π]
        target_roll  = normalize_angle(-data["r"])    # roll
    except Exception:
        pass  # Если файл не прочитан, оставляем предыдущие значения
    
    
    # Плавная интерполяция текущих углов к целевым
    current_yaw   = lerp_angle(current_yaw, target_yaw, 0.1)
    current_pitch = lerp_angle(current_pitch, target_pitch, 0.1)
    current_roll  = lerp_angle(current_roll, target_roll, 0.1)

    # Очистка буфера цвета и глубины, сброс модели
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, -5)

    # Вычисляем матрицу поворота из текущих углов
    R = euler_to_matrix(current_yaw, current_pitch, current_roll)
    # Формируем 4x4 матрицу (OpenGL ожидает столбцовый порядок)
    mat = [
         R[0][0], R[1][0], R[2][0], 0.0,
         R[0][1], R[1][1], R[2][1], 0.0,
         R[0][2], R[1][2], R[2][2], 0.0,
         0.0,     0.0,     0.0,     1.0
    ]
    glMultMatrixf(mat)

    draw_cube()

    pygame.display.flip()
    clock.tick(30)