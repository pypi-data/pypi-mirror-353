import pyperclip

def z_1_1():
    answer = f"""
# Переполнение
a = 1e308
b = 1e308
c = a * b  # Это может привести к переполнению, результат будет 'inf' (бесконечность)
print(c)
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_1_2():
    answer = f"""
# Потеря точности
a = 0.1 + 0.2
b = 0.3
print(f'a = ', a, ', b = ', b, ', a == b: ',a == b')  # Ожидается True, но результат False
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_1_3():
    answer = f"""
# Ошибка округления
a = 1.0000000000000001
b = 1.000000000000002
print(a + b)  # Ожидаем 2.0000000000000021, но результат может быть немного другим из-за округления
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_1_4():
    answer = f"""
# Накопление ошибок
sum = 0.0
for i in range(100000):
    sum += 0.0001
print(sum)  # Может быть немного меньше 10, в зависимости от точности чисел"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_1_5():
    answer = f"""
# Потеря значимости
a = 1.0000000000000001
b = 1.0000000000000002
print(a + b)   # Очень маленькая разница, которая может быть искажена из-за ограниченной точности
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_1_6():
    answer = f"""
def kahan_sum(x):
    s = 0.0
    c = 0.0
    for i in range(len(x)):
        y = x[i] - c
        t = s + y
        c = (t - s) - y
        s = t
    return s"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_1_7():
    answer = f"""
import numpy as np
import time
from numba import jit

n = 10**6

np.random.seed(42)
x = np.random.uniform(-1,1,n).astype(np.float32)

true_sum = np.sum(x, dtype=np.float64)

def naive_sum(x):
    s = np.float32(0.0)
    for i in range(len(x)):
        s += x[i]
    return s

@jit(nopython=True)
def kahan_sum(x):
    s = np.float32(0.0)
    c = np.float32(0.0)
    for i in range(len(x)):
        y = x[i] - c
        t = s + y
        c = (t - s) - y
        s = t
    return s

start = time.time()
d_sum = naive_sum(x)
time_naive = time.time() - start

start = time.time()
k_sum = kahan_sum(x)
time_kahan = time.time() - start

start = time.time()
np_sum = np.sum(x, dtype=np.float32)
time_numpy = time.time() - start

print("Ошибка в naive sum: ",d_sum - true_sum)
print("Ошибка в Kahan sum: ",k_sum - true_sum)
print("Ошибка в NumPy sum: ",np_sum - true_sum)

print("\nВремя выполнения:")
print(f"Naive sum: ", time_naive, "сек")
print(f"Kahan sum: ", time_kahan, "сек")
print(f"NumPy sum: ", time_numpy, "сек")"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_2_1():
    answer = f"""
import numpy as np

def simple_iteration(x0, y0, eps=1e-3, max_iter=100):
    # Инициализируем начальные значения
    x = x0
    y = y0

    # Выводим начальное приближение
    print("Начальное приближение:")
    print("x =", round(x, 5))
    print("y =", round(y, 5))
    print("-----------------------")

    # Основной цикл итераций
    for k in range(1, max_iter + 1):
        # Вычисляем новые значения x и y по формулам метода
        # x = (1/4)*cos(y) + 1
        x_new = 0.25 * np.cos(y) + 1

        # y = (1/5)*sin(x)
        y_new = 0.2 * np.sin(x)

        # Проверяем условие остановки:
        # Если максимальное изменение x и y меньше заданной точности
        if max(abs(x_new - x), abs(y_new - y)) < eps:
            print("\nРешение найдено за", k, "итераций!")
            return x_new, y_new, k

        # Обновляем значения для следующей итерации
        x = x_new
        y = y_new

        # Выводим информацию о текущей итерации
        print("Итерация", k)
        print("x =", round(x, 5))
        print("y =", round(y, 5))
        print("-----------------------")

    # Если достигнуто максимальное число итераций
    print("\nДостигнут максимум итераций!")
    return x, y, max_iter

# Задаем начальные значения
x_start = 0.5
y_start = 0.5
precision = 1e-3  # Точность вычислений

# Вызываем функцию для решения системы
x_final, y_final, iters = simple_iteration(x_start, y_start, precision)

# Выводим результаты
print("\nФинальные значения:")
print("x =", round(x_final, 5))
print("y =", round(y_final, 5))

# Проверяем корректность решения
print("\nПроверка решения:")
# Вычисляем невязки уравнений
check1 = x_final - 0.25 * np.cos(y_final) - 1
check2 = y_final - 0.2 * np.sin(x_final)
print("Первое уравнение (должно быть ~0):", round(check1, 6))
print("Второе уравнение (должно быть ~0):", round(check2, 6))    
    """
    pyperclip.copy(answer)
    pyperclip.paste()

def z_2_2():
    answer = f"""
import numpy as np

# Функция для решения уравнения методом хорд
def chord_method(f, x0, x1, eps=1e-6, max_iter=100):
    # Начинаем итерационный процесс
    for n in range(max_iter):
        # Вычисляем значения функции в текущих точках
        fx0 = f(x0)
        fx1 = f(x1)

        # Проверяем, не достигли ли мы нужной точности
        if abs(fx1) < eps:
            return x1, n  # Возвращаем найденный корень и число итераций

        # Основная формула метода хорд:
        # x_new = x1 - f(x1)*(x1-x0)/(f(x1)-f(x0))
        x_new = x1 - fx1 * (x1 - x0) / (fx1 - fx0)

        # Проверяем изменение значения x
        if abs(x_new - x1) < eps:
            return x_new, n  # Возвращаем результат, если достигнута точность

        # Обновляем точки для следующей итерации
        x0, x1 = x1, x_new

    # Если вышли за пределы максимального числа итераций
    print("Достигнуто максимальное число итераций!")
    return x1, max_iter

# Определяем функцию, корень которой нужно найти
# В данном случае: x^3 - 2x - 5 = 0
def f(x):
    return x**3 - 2*x - 5

# Задаем начальные приближения
# Важно: значения функции в этих точках должны быть разных знаков
x_start1 = 2.0
x_start2 = 3.0

# Задаем точность вычислений
tolerance = 1e-6

# Вызываем метод хорд для решения уравнения
solution, num_iterations = chord_method(f, x_start1, x_start2, eps=tolerance)

# Выводим результаты
print("\nРезультаты решения:")
print("Найденный корень: x =", round(solution, 6))
print("Значение функции в корне: f(x) =", round(f(solution), 6))
print("Количество итераций:", num_iterations)"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_2_3():
    answer = f"""
import numpy as np

def wegstein_method(f, x0, x1, eps=1e-6, max_iter=100):
    # Вычисляем значения функции в начальных точках
    fx0 = f(x0)
    fx1 = f(x1)

    # Начинаем итерационный процесс (начинаем с 2, так как нужно 2 начальных значения)
    for n in range(2, max_iter + 1):
        # Проверяем, не достигли ли мы нужной точности по значению функции
        if abs(fx1) < eps:
            return x1, n - 1  # Возвращаем текущее приближение и количество итераций

        # Основная формула метода Вегстейна:
        # x_new = x1 - f(x1)*(x1-x0)/(f(x1)-f(x0))
        x_new = x1 - fx1 * (x1 - x0) / (fx1 - fx0)

        # Проверяем изменение значения x (вторая условие остановки)
        if abs(x_new - x1) < eps:
            return x_new, n

        # Подготавливаем значения для следующей итерации:
        # Текущие значения становятся предыдущими
        x0, x1 = x1, x_new
        fx0, fx1 = fx1, f(x_new)  # Вычисляем новое значение функции

    # Если вышли за пределы максимального числа итераций
    print("Достигнуто максимальное число итераций!")
    return x1, max_iter

# Определяем функцию, корень которой нужно найти
# В данном случае решаем уравнение: x^3 - 2x - 5 = 0
def our_function(x):
    return x**3 - 2*x - 5

# Задаем начальные приближения
initial_guess1 = 2.0
initial_guess2 = 3.0

# Задаем точность вычислений
tolerance = 1e-6

# Вызываем метод Вегстейна для решения уравнения
solution, iterations_needed = wegstein_method(our_function, initial_guess1, initial_guess2, eps=tolerance)

# Выводим результаты
print("\nРезультаты решения уравнения x^3 - 2x - 5 = 0")
print("Найденный корень: x =", round(solution, 6))
print("Значение функции в корне: f(x) =", round(our_function(solution), 6))
print("Потребовалось итераций:", iterations_needed)"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_2_4():
    answer = f"""
import numpy as np

def newton_method(f, df, x0, eps=1e-6, max_iter=100):
    # Инициализация начального значения
    x = x0

    # Основной итерационный процесс
    for n in range(max_iter):
        # Вычисляем значение функции и её производной в текущей точке
        fx = f(x)
        dfx = df(x)

        # Проверка на достижение необходимой точности
        if abs(fx) < eps:
            return x, n

        # Проверка, что производная не равна нулю (иначе деление невозможно)
        if dfx == 0:
            raise ValueError("Производная равна нулю - метод не может продолжаться")

        # Основная формула метода Ньютона: x_new = x - f(x)/f'(x)
        x_new = x - fx / dfx

        # Проверка изменения значения x (второй критерий остановки)
        if abs(x_new - x) < eps:
            return x_new, n + 1

        # Обновляем значение x для следующей итерации
        x = x_new

    # Если достигнуто максимальное число итераций
    print("Достигнуто максимальное число итераций!")
    return x, max_iter

# Пример 1: Решение уравнения x - cos(x) = 0
# Определяем функцию и её производную
def func1(x):
    return x - np.cos(x)

def dfunc1(x):
    return 1 + np.sin(x)

# Начальное приближение (выбираем x0=0.5 согласно правилу выбора)
initial_guess1 = 0.5

# Решаем уравнение
solution1, iter1 = newton_method(func1, dfunc1, initial_guess1)

# Выводим результаты для первого примера
print("\nПример 1: Решение уравнения x - cos(x) = 0")
print("Найденный корень: x =", round(solution1, 6))
print("Значение функции в корне:", round(func1(solution1), 6))
print("Потребовалось итераций:", iter1)

# Пример 2: Решение уравнения x^2 - 2 = 0 (вычисление √2)
# Определяем функцию и её производную
def func2(x):
    return x**2 - 2

def dfunc2(x):
    return 2 * x

# Начальное приближение
initial_guess2 = 2.0

# Решаем уравнение
solution2, iter2 = newton_method(func2, dfunc2, initial_guess2)

# Выводим результаты для второго примера
print("\nПример 2: Решение уравнения x^2 - 2 = 0 (вычисление √2)")
print("Найденный корень: x =", round(solution2, 6))
print("Значение функции в корне:", round(func2(solution2), 6))
print("Потребовалось итераций:", iter2)
print("Проверка: квадрат найденного корня =", round(solution2**2, 6))"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_3():
    answer = f"""
import numpy as np

def dichotomy_method(f, a, b, epsilon=1e-5):
    "
    Метод половинного деления для нахождения минимума функции.
    
    f: функция, минимум которой ищем
    a, b: границы интервала
    epsilon: точность, до которой требуется найти минимум
    "
    
    # Начальные значения
    c = (a + b) / 2
    
    # Итерации
    while (b - a) / 2 > epsilon:
        left = f(c - epsilon / 2)
        right = f(c + epsilon / 2)
        
        if left < right:
            b = c
        else:
            a = c
            
        c = (a + b) / 2
    
    return c

# Пример использования
def example_function(x):
    return x**2 - 4*x + 4  # Пример функции

# Нахождение минимума на интервале [0, 5]
minimum = dichotomy_method(example_function, 0, 5)
print('Минимум функции находится в точке x = ',minimum')
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_4_1():
    answer = f"""
import numpy as np
import matplotlib.pyplot as plt


# Пример решения системы нелинейных уравнений
def solve_nonlinear_system():
    # Пример системы уравнений:
    # x^2 + y^2 = 4
    # x - y = 1

    # Перепишем систему в виде уравнений для метода простых итераций:
    # x = sqrt(4 - y^2)
    # y = x - 1

    def g1(y):  # x = sqrt(4 - y^2)
        return np.sqrt(4 - y**2)

    def g2(x):  # y = x - 1
        return x - 1

    # Начальные приближения
    x_init = 1.0
    y_init = 1.0

    tol = 1e-6  # Порог точности
    max_iters = 1000  # Максимальное количество итераций

    # Итерационный процесс для нахождения решения системы
    for it in range(max_iters):
        x_new = g1(y_init)  # Вычисляем новое значение x
        y_new = g2(x_init)  # Вычисляем новое значение y

        # Проверка на сходимость
        if abs(x_new - x_init) < tol and abs(y_new - y_init) < tol:
            break  # Если разница меньше порога, выходим из цикла

        # Обновляем значения x и y для следующей итерации
        x_init = x_new
        y_init = y_new

    return x_new, y_new, it + 1  # Возвращаем результат


tol = 1e-6         # Порог точности
max_iters = 1000   # Максимальное количество итераций


# Решение системы нелинейных уравнений
x, y, iterations = solve_nonlinear_system()
print(f"\nРешение системы нелинейных уравнений:")
print('x = ',x, 'y = ',y:.6f,' итераций = ',iterations)"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_4_2():
    answer = f"""
import numpy as np
#sin(x)−0.5−y=1.5
#2𝑥 −cos𝑦 = 0,6
# Функции для итераций по методу Зейделя
def f1(y):
    return 0.5 * np.cos(y) + 0.3  # Функция для x тут выражаем через одну переменную

def f2(x):
    return np.sin(x) - 0.5 - 1.5  # Функция для y

# Метод Зейделя для решения системы нелинейных уравнений
def seidel_method(x_init, y_init, tol, max_iters):
    x = x_init
    y = y_init
    
    for k in range(max_iters):
        # Обновление x и y поочередно
        x_new = f1(y)  # Новый x вычисляется на основе старого y
        y_new = f2(x_new)  # Новый y вычисляется на основе нового x
        
        # Проверка условия остановки
        if abs(x_new - x) < tol and abs(y_new - y) < tol:
            break  # Если разница меньше порога, остановим итерации
        
        # Обновляем значения для следующей итерации
        x = x_new
        y = y_new
    
    return x_new, y_new, k + 1  # Возвращаем результат

# Пример решения системы с помощью метода Зейделя
x_init = 0.13  # Начальное приближение для x
y_init = -1.8  # Начальное приближение для y
tol = 0.001  # Порог точности
max_iters = 1000  # Максимальное количество итераций

x, y, iterations = seidel_method(x_init, y_init, tol, max_iters)

# Выводим результаты
print(f"Решение системы уравнений методом Зейделя:")
print('x =', x,' y = ',y, 'итераций =',iterations)    
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_4_3():
    answer = f"""
import numpy as np
#F1(x,y) = sin x - 0,5-y = 1,5
#F2(x,y) = 2x-cosy=0,6
#их нужно привести к виду чтобы справа был ноль
# Функции для вычисления значений системы
def F1(x, y):
    return np.sin(x) - 0.5 - y - 1.5

def F2(x, y):
    return 2*x - np.cos(y) - 0.6

# Частные производные
def dF1_dx(x, y):
    return np.cos(x)

def dF1_dy(x, y):
    return -1

def dF2_dx(x, y):
    return 2

def dF2_dy(x, y):
    return np.sin(y)

# Метод Ньютона для решения системы нелинейных уравнений
def newton_method(x_init, y_init, tol, max_iters):
    x = x_init
    y = y_init
    
    for k in range(max_iters):
        # Вычисляем частные производные в текущей точке
        jacobian = np.array([
            [dF1_dx(x, y), dF1_dy(x, y)],
            [dF2_dx(x, y), dF2_dy(x, y)]
        ])
        
        # Вектор правой части (значения функции в текущей точке)
        F_values = np.array([F1(x, y), F2(x, y)])
        
        # Решение системы линейных уравнений для приращений
        delta = np.linalg.solve(jacobian, -F_values)
        
        # Обновление значений переменных
        x_new = x + delta[0]
        y_new = y + delta[1]
        
        # Проверка на сходимость
        if np.max(np.abs(delta)) < tol:
            break
        
        # Обновление значений для следующей итерации
        x, y = x_new, y_new
    
    return x_new, y_new, k + 1  # Возвращаем решение и количество итераций

# Пример решения системы с помощью метода Ньютона
x_init = 0.13  # Начальное приближение для x
y_init = -1.8  # Начальное приближение для y
tol = 0.001  # Порог точности
max_iters = 1000  # Максимальное количество итераций

x, y, iterations = newton_method(x_init, y_init, tol, max_iters)

# Выводим результаты
print(f"Решение системы уравнений методом Ньютона:")
print('x = ',x,' y = ',y,' итераций = ',iterations) 
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_4_4():
    answer = f"""
import numpy as np
#F1(x,y) = sin x - 0,5-y = 1,5
#F2(x,y) = 2x-cosy=0,6
#их нужно привести к виду чтобы справа был ноль
# Функции для вычисления значений системы
def F1(x, y):
    return np.sin(x) - 0.5 - y - 1.5

def F2(x, y):
    return 2*x - np.cos(y) - 0.6

# Частные производные в начальной точке
def dF1_dx(x, y):
    return np.cos(x)

def dF1_dy(x, y):
    return -1

def dF2_dx(x, y):
    return 2

def dF2_dy(x, y):
    return np.sin(y)

# Модифицированный метод Ньютона для решения системы нелинейных уравнений
def modified_newton_method(x_init, y_init, tol, max_iters):
    x = x_init
    y = y_init
    
    # Вычисляем частные производные в начальной точке (фиксируем их)
    jacobian = np.array([
        [dF1_dx(x, y), dF1_dy(x, y)],
        [dF2_dx(x, y), dF2_dy(x, y)]
    ])
    
    # Вектор правой части (значения функции в текущей точке)
    F_values = np.array([F1(x, y), F2(x, y)])
    
    for k in range(max_iters):
        # Решаем систему линейных уравнений для приращений
        delta = np.linalg.solve(jacobian, -F_values)
        
        # Обновление значений переменных
        x_new = x + delta[0]
        y_new = y + delta[1]
        
        # Проверка на сходимость
        if np.max(np.abs(delta)) < tol:
            break
        
        # Обновление значений для следующей итерации
        x, y = x_new, y_new
        # Обновляем F_values для новой итерации
        F_values = np.array([F1(x, y), F2(x, y)])
    
    return x_new, y_new, k + 1  # Возвращаем решение и количество итераций

# Пример решения системы с помощью модифицированного метода Ньютона
x_init = 0.13  # Начальное приближение для x
y_init = -1.8  # Начальное приближение для y
tol = 0.001  # Порог точности
max_iters = 1000  # Максимальное количество итераций

x, y, iterations = modified_newton_method(x_init, y_init, tol, max_iters)

# Выводим результаты
print(f"Решение системы уравнений модифицированным методом Ньютона:")
print(f"x = ',x,' y = ',y,' итераций = ',iterations')
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_5_1():
    answer = f"""
# 1. Интерполяция – функция должна пройти через все точки. Способ нахождения промежуточных значений величины по имеющемуся дискретному набору известных значений.
# 2. Экстраполяция – особый тип аппроксимации, при котором функция аппроксимируется вне заданного интервала, а не между заданными значениями.
# 3. Аппроксимация (например, регрессия/метод наименьших квадратов) – аппроксимирующая функция не обязательно должна проходить через все точки. Происходит замена одних объектов другими, в каком-то смысле близкими к исходным, но более простыми.
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_5_2():
    answer = f"""
# ПРОСТЕЙШИЕ СПОСОБЫ ИНТЕРПОЛЯЦИИ

# Простейшим способом интерполяции функции f по таблице является ступенчатая интерполяция. Один из ее вариантов формулируется так:

# 𝑓̃(𝑥) = 𝑓(𝑥ᵢ), i: ∀j ≠ i, |𝑥 − 𝑥ⱼ| > |𝑥 − 𝑥ᵢ|

# То есть за значение функции 𝑓̃(𝑥) берется значение функции f в точке, ближайшей к рассматриваемой. Более точным способом интерполяции является кусочно-линейная интерполяция. При таком подходе значение 𝑓(𝑥) интерполируется по двум соседним с точкой x точкам.

# 𝑓̃(𝑥) = (f(xᵢ)(xᵢ₊₁ − x) + f(xᵢ₊₁)(x − xᵢ)) / (xᵢ₊₁ − xᵢ), i: 𝑥ᵢ < 𝑥 < 𝑥ᵢ₊₁

# (здесь подразумевается монотонное возрастание последовательности 𝑥ᵢ)

# Интересно понять, с какой точностью интерполяционные формулы аппроксимируют функцию f. Предположим, что производная функции f ограничена величиной g. Тогда на отрезке [𝑥ᵢ, 𝑥ᵢ₊₁ ] функция f не может отклониться от линейной интерполяции более, чем на h(g - |(f(xᵢ₊₁)-f(xᵢ)) / (xᵢ₊₁ − xᵢ)|).


def interpolate_nearest(x, xs, fs):
    "
    Интерполяция методом ближайшего соседа.

    :param x: точка, в которой нужно оценить значение функции
    :param xs: список координат узлов
    :param fs: список значений функции в узлах xs
    :return: интерполированное значение функции в точке x
    "
    # Находим индекс узла, ближайшего к x
    distances = [abs(x - xi) for xi in xs]
    idx = distances.index(min(distances))
    return fs[idx]


def interpolate_linear(x, xs, fs):
    "
    Кусочно-линейная интерполяция.

    :param x: точка, в которой нужно оценить значение функции
    :param xs: список координат узлов (предполагается, что xs отсортирован по возрастанию)
    :param fs: список значений функции в узлах xs
    :return: интерполированное значение функции в точке x
    "
    # Если x вне диапазона xs, можно вернуть крайнее значение
    if x <= xs[0]:
        return fs[0]
    if x >= xs[-1]:
        return fs[-1]

    # Находим интервал, содержащий x
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            # Применяем формулу линейной интерполяции:
            # f(x) = f(x_i) * (x_i+1 - x) / (x_i+1 - x_i) + f(x_i+1) * (x - x_i) / (x_i+1 - x_i)
            return fs[i] * (xs[i + 1] - x) / (xs[i + 1] - xs[i]) + fs[i + 1] * (x - xs[i]) / (xs[i + 1] - xs[i])

    # Если интервал не найден (что маловероятно при корректном входе)
    return None


# Пример использования:
if __name__ == "__main__":
    # Таблица значений: пусть f(x) = x^2
    xs = [0, 1, 2, 3, 4]
    fs = [0, 1, 4, 9, 16]

    x_val = 2.5
    nearest = interpolate_nearest(x_val, xs, fs)
    linear = interpolate_linear(x_val, xs, fs)

    print("Интерполяция методом ближайшего соседа для x =", x_val, ":", nearest)
    print("Кусочно-линейная интерполяция для x =", x_val, ":", linear)


def linear_interpolation(x_values, y_values, x_new):
    for i in range(len(x_values) - 1):
        if x_values[i] <= x_new <= x_values[i+1]:
            y_new = y_values[i]+(y_values[i+1]-y_values[i])*(x_new-x_values[i])/(x_values[i+1]-x_values[i])
            return y_new
    return None

x = [0, 1, 2]
y = [1, 3, 2]

y_hat = linear_interpolation(x, y, 1.5)
print('Интерполированное значение: ',y_hat)
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_5_3():
    answer = f"""
# Функция 𝑦(𝑥) аппроксимируется на каждом частичном отрезке прямой.
# (𝑥 − 𝑥ᵢ) / (𝑥ᵢ₊₁ − 𝑥ᵢ) = (𝑦 − 𝑦ᵢ) / (𝑦ᵢ₊₁ − 𝑦ᵢ)
#𝑦 = 𝑦ᵢ + ((𝑥 − 𝑥ᵢ) / (𝑥ᵢ₊₁ − 𝑥ᵢ)) × (𝑦ᵢ₊₁ − 𝑦ᵢ)

def linear_interpolation(x, x_i, y_i, x_i_plus_1, y_i_plus_1):
    "
    Функция для вычисления значения y(x) с использованием линейной интерполяции.

    :param x: Точка, для которой нужно вычислить значение y
    :param x_i: x-координата первой точки интервала
    :param y_i: y-координата первой точки интервала
    :param x_i_plus_1: x-координата второй точки интервала
    :param y_i_plus_1: y-координата второй точки интервала
    :return: Значение y(x)
    "
    # Линейная интерполяция
    return y_i + ((x - x_i) / (x_i_plus_1 - x_i)) * (y_i_plus_1 - y_i)

# Пример использования
x_i = 1
y_i = 2
x_i_plus_1 = 3
y_i_plus_1 = 6

# Точка x, для которой нужно найти значение y
x = 2

y = linear_interpolation(x, x_i, y_i, x_i_plus_1, y_i_plus_1)
print('Значение функции в точке x = ',x,': y = ',y)"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_5_4():
    answer = f"""
#Алгебраическим интерполяционным многочленом Pₙ(x, f, x₀,..., xₙ) называется многочлен Pₙ(x) = c₀ + c₁x + c₂x² + ... + cₙxⁿ степени не выше n, принимающий в точках x₀, x₁, ..., xₙ значения f(x₀), f(x₁), ..., f(xₙ).

#Теорема. Если заданы попарно различные узлы x₀, x₁, x₂, ..., xₙ и значения f(x₀), f(x₁), ..., f(xₙ), то алгебраический интерполяционный многочлен существует и единственен.

#Доказательство. Сначала докажем, что существует не более чем один интерполяционный многочлен, а затем построим его. Если бы их было два, то их разность – многочлен степени не больше n, обращалась бы в 0 в n + 1 точке – x₀, x₁, ..., xₙ, что невозможно для ненулевого многочлена.

#В качестве примера интерполяционного многочлена можно привести Интерполяционный многочлен Лагранжа.


import numpy as np

# Базисный многочлен Лагранжа
def lagrange_basis(x, x_points, i):
    result = 1
    for j in range(len(x_points)):
        if j != i:
            result *= (x - x_points[j]) / (x_points[i] - x_points[j])
    return result

# Интерполяционный многочлен Лагранжа
def lagrange_interpolation(x, x_points, y_points):
    n = len(x_points)
    result = 0
    for i in range(n):
        result += y_points[i] * lagrange_basis(x, x_points, i)
    return result

# Пример использования
x_points = np.array([0, 1, 2])
y_points = np.array([1, 2, 0])

# Точка, в которой нужно найти значение интерполяционного многочлена
x = 1.5

# Вычисление значения интерполяционного многочлена в точке x
y = lagrange_interpolation(x, x_points, y_points)
print('Значение интерполяционного многочлена в точке x = ', x, ': y = ', y)"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_5_5():
    answer = f"""
#Интерполяционный многочлен Лагранжа — многочлен минимальной степени, принимающий данные значения в данном наборе точек.

#Для n + 1 пар чисел (x₀, y₀), (x₁, y₁), ..., (xₙ, yₙ), где все xᵢ различны, существует ТОЛЬКО ОДИН интерполяционный многочлен L(x) степени не более n, для которого L(xᵢ) = yᵢ:

#F(x) = ∑ᵢ₌₀ⁿ yᵢLᵢ(x),

#В простейшем случае (n = 1) — это линейный многочлен, график которого — прямая, проходящая через две заданные точки.

#В качестве глобальной интерполяционной функции F(x) можно найти многочлен степени не больше n, такой, что:

#F(xᵢ) = yᵢ.

#Форма Лагранжа:

#Lᵢ(x) = ((x - x₀)...(x - xᵢ₋₁)(x - xᵢ₊₁)...(x - xₙ)) / ((xᵢ - x₀)...(xᵢ - xᵢ₋₁)(xᵢ - xᵢ₊₁)...(xᵢ - xₙ))

#В результате будет получен полином L(x) = A₀ + A₁x + A₂x² + ...Aₙxⁿ, значения которого в точках xᵢ будут совпадать с yᵢ.


import numpy as np

def lagrange_basis(x, x_points, i):
    "
    Вычисляет i-й базисный многочлен Лагранжа Lᵢ(x)
    "
    result = 1
    for j in range(len(x_points)):
        if j != i:
            result *= (x - x_points[j]) / (x_points[i] - x_points[j])
    return result

def lagrange_interpolation(x, x_points, y_points):
    "
    Вычисляет значение интерполяционного многочлена L(x) по формуле:
    L(x) = ∑[i=0..n] yᵢ * Lᵢ(x)
    "
    n = len(x_points)
    result = 0
    for i in range(n):
        result += y_points[i] * lagrange_basis(x, x_points, i)
    return result

# Пример использования:
# Заданные точки: (0, 1), (1, 3), (2, 2)
x_points = np.array([0, 1, 2])
y_points = np.array([1, 3, 2])

# Точка, в которой вычисляем значение многочлена
x = 1.5

# Вычисление и вывод результата
result = lagrange_interpolation(x, x_points, y_points)
print("Значение интерполяционного многочлена в точке", x, "равно", result)
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_5_6():
    answer = f"""
def cubic_spline_interpolation(x, y, new_x):
    "
    Интерполяция кубическим сплайном (натуральный сплайн).

    Параметры:
        x, y: массивы исходных данных. x должен быть отсортирован по возрастанию.
        new_x: значение или массив значений, в которых необходимо интерполировать

    Возвращает:
        new_y: интерполированные значения для new_x
    "
    # Приведем x и y в виде массивов numpy
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    n = len(x)
    if n < 3:
        raise ValueError('Для кубического сплайна необходимо минимум 3 точки')

    # Вычисляем интервалы h
    h = np.diff(x)  # длина интервалов, размер n-1

    # Вычисление коэффициентов системы для нахождения вторых производных (M_i)
    # Поскольку натуральный сплайн: M_0 = M_n-1= 0
    A = np.zeros(n)
    B = np.zeros(n)
    C = np.zeros(n)
    D = np.zeros(n)

    # Заполняем коэффициенты уравнений i = 1 ... n-2
    for i in range(1, n - 1):
        A[i] = h[i - 1]
        B[i] = 2 * (h[i - 1] + h[i])
        C[i] = h[i]
        D[i] = 6 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])

    # Применяем метод прогонки (Thomas algorithm) для системы с tridiagonal matrix.
    # Граничные условия: M_0 = 0, M_n-1 = 0
    M = np.zeros(n)
    cp = np.zeros(n)  # модифицированные коэффициенты C
    dp = np.zeros(n)  # модифицированные коэффициенты D

    # Начальное условие для прогонки (i = 1)
    cp[1] = C[1] / B[1]
    dp[1] = D[1] / B[1]
    
    for i in range(2, n - 1):
        denom = B[i] - A[i] * cp[i - 1]
        cp[i] = C[i] / denom
        dp[i] = (D[i] - A[i] * dp[i - 1]) / denom

    # Обратный ход
    for i in range(n - 2, 0, -1):
        M[i] = dp[i] - cp[i] * M[i + 1]
    # M[0] и M[n-1] остаются 0

    # Вычисляем интерполированное значение для каждого new_x
    def spline_eval(x_val):
        # Находим интервал, к которому принадлежит x_val
        if x_val < x[0] or x_val > x[-1]:
            raise ValueError('Значение x вне диапазона интерполяции')
        # Найдем индекс i такой, что x[i] <= x_val <= x[i+1]
        i = np.searchsorted(x, x_val) - 1
        if i < 0:
            i = 0
        if i >= n - 1:
            i = n - 2
        hi = x[i + 1] - x[i]
        A_i = (x[i + 1] - x_val) / hi
        B_i = (x_val - x[i]) / hi
        term1 = A_i * y[i] + B_i * y[i + 1]
        term2 = ((A_i**3 - A_i) * M[i] + (B_i**3 - B_i) * M[i + 1]) * (hi**2) / 6.0
        return term1 + term2

    # Если new_x - скаляр, то возвращаем скаляр;
    # если это массив, то возвращаем массив
    if np.isscalar(new_x) or isinstance(new_x, float) or isinstance(new_x, int):
        return spline_eval(new_x)
    else:
        new_x = np.array(new_x, dtype=float)
        return np.array([spline_eval(xi) for xi in new_x])
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_5_7():
    answer = f"""
def quadratic_interpolation(x, y, new_x):
    "
    Квадратичная интерполяция (полиномиальная интерполяция второй степени).

    Для каждого значения new_x выбираются три ближайшие точки и
    производится интерполяция с использованием формулы Лагранжа.

    Параметры:
        x, y: массивы с исходными данными (x должен быть отсортирован).
        new_x: значение или массив значений для интерполяции

    Возвращает:
        Интерполированное значение или массив значений
    "
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    n = len(x)
    
    def lagrange_quad(x_pts, y_pts, xi):
        # Три точки: x0, x1, x2
        L0 = ((xi - x_pts[1]) * (xi - x_pts[2])) / ((x_pts[0] - x_pts[1]) * (x_pts[0] - x_pts[2]))
        L1 = ((xi - x_pts[0]) * (xi - x_pts[2])) / ((x_pts[1] - x_pts[0]) * (x_pts[1] - x_pts[2]))
        L2 = ((xi - x_pts[0]) * (xi - x_pts[1])) / ((x_pts[2] - x_pts[0]) * (x_pts[2] - x_pts[1]))
        return L0 * y_pts[0] + L1 * y_pts[1] + L2 * y_pts[2]

    def interpolate_point(xi):
        # Найдем индекс, так что x[i] <= xi <= x[i+1], затем выберем 3 точки: по возможности, один до, текущий, после
        if xi < x[0] or xi > x[-1]:
            raise ValueError('Значение x вне диапазона интерполяции')
        idx = np.searchsorted(x, xi)
        if idx == 0:
            indices = [0, 1, 2]  # крайняя левая область
        elif idx >= n - 1:
            indices = [n - 3, n - 2, n - 1]  
        else:
            # Если возможно, выбираем один перед и один после
            indices = [idx - 1, idx, idx + 1]
        x_pts = x[indices]
        y_pts = y[indices]
        return lagrange_quad(x_pts, y_pts, xi)

    # Обрабатываем случаи, когда new_x скаляр или массив
    if np.isscalar(new_x) or isinstance(new_x, float) or isinstance(new_x, int):
        return interpolate_point(new_x)
    else:
        new_x = np.array(new_x, dtype=float)
        return np.array([interpolate_point(xi) for xi in new_x])
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_5_8():
    answer = f"""
def linear_spline_interpolation(x, y, new_x):
    "
    Интерполяция сплайнами с использованием линейной интерполяции.

    Для каждого нового значения x, находим соответствующий интервал и проводим линейную интерполяцию.

    Параметры:
        x, y: исходные данные (x должны быть отсортированы).
        new_x: значение или массив значений для интерполяции

    Возвращает:
        Интерполированное значение или массив значений
    "
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    n = len(x)

    def lin_interp(x_val):
        if x_val < x[0] or x_val > x[-1]:
            raise ValueError('Значение x вне диапазона интерполяции')
        i = np.searchsorted(x, x_val) - 1
        if i < 0:
            i = 0
        if i >= n - 1:
            i = n - 2
        # Прямая линия между (x[i], y[i]) и (x[i+1], y[i+1])
        t = (x_val - x[i]) / (x[i+1] - x[i])
        return y[i] + t * (y[i+1] - y[i])

    if np.isscalar(new_x) or isinstance(new_x, float) or isinstance(new_x, int):
        return lin_interp(new_x)
    else:
        new_x = np.array(new_x, dtype=float)
        return np.array([lin_interp(xi) for xi in new_x])
"""
    pyperclip.copy(answer)
    pyperclip.paste()

def z_5_9():
    answer = f"""
def least_squares_method(x, y, degree):
    "
    Метод наименьших квадратов для подбора полинома определенной степени,
    который аппроксимирует данные.

    Параметры:
        x, y: исходные данные
        degree: степень аппроксимирующего полинома

    Возвращает:
        coeffs: коэффициенты полинома (от старшей степени к нулевой)
        y_fit: значения аппроксимирующего полинома, рассчитанные в точках x
    "
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    # Формируем матрицу Вандермонде для полиномиальной аппроксимации
    # np.vander возвращает столбцы от старшей степени к нулевой
    A = np.vander(x, degree + 1)

    # Решаем уравнение А * coeffs = y по методу наименьших квадратов
    coeffs, residuals, rank, s = np.linalg.lstsq(A, y, rcond=None)

    # Вычисляем значения аппроксимирующего полинома
    y_fit = A.dot(coeffs)

    return coeffs, y_fit
  
   np.random.seed(0)
    x_data = np.linspace(0, 10, 11)
    y_data = np.sin(x_data) + np.random.normal(scale=0.1, size=x_data.shape)

    # Преобразуем в DataFrame
    df = pd.DataFrame({'x': x_data, 'y': y_data})
    print('Исходные данные:')
    print(df)

    # Генерируем новые точки для интерполяции
    x_new = np.linspace(x_data[0], x_data[-1], 100)

    # Кубический сплайн
    y_cubic = cubic_spline_interpolation(x_data, y_data, x_new)

    # Квадратичная интерполяция
    y_quadratic = quadratic_interpolation(x_data, y_data, x_new)

    # Линейная сплайн-интерполяция
    y_linear = linear_spline_interpolation(x_data, y_data, x_new)

    # Аппроксимация методом наименьших квадратов (полином 3-й степени)
    coeffs, y_ls = least_squares_method(x_data, y_data, degree=3)
    print('\nКоэффициенты полинома (метод наименьших квадратов, степень 3):')
    print(coeffs)

    # График результатов
    plt.figure(figsize=(10, 8))
    plt.plot(x_data, y_data, 'ko', label='Исходные данные')
    plt.plot(x_new, y_cubic, 'b-', label='Кубический сплайн')
    plt.plot(x_new, y_quadratic, 'r--', label='Квадратичная интерполяция')
    plt.plot(x_new, y_linear, 'g-.', label='Линейная интерполяция')
    plt.plot(x_data, y_ls, 'ms', label='Метод наименьших квадратов (только узлы)')
    plt.legend()
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Различные методы интерполяции и аппроксимации')
    plt.grid(True)
    plt.show()
"""
    pyperclip.copy(answer)
    pyperclip.paste()


