import pyperclip


def p1():
    answer = """
    import numpy as np

    def fixed_point_iteration(g, x0, tol=1e-9, max_iter=100):
        \"\"\"
        Находит неподвижную точку уравнения x = g(x) методом простой итерации.
        Метод сходится, если |g'(x)| < 1 в окрестности корня.

        Аргументы:
            g: Итерационная функция, x_{k+1} = g(x_k).
            x0: Начальное приближение.
            tol: Желаемая точность.
            max_iter: Максимальное число итераций.
        \"\"\"
        x = x0
        for i in range(max_iter):
            x_next = g(x)
            if abs(x_next - x) < tol:
                return x_next
            x = x_next

        print("Достигнуто максимальное число итераций.")
        return x

    # Решаем уравнение x = cos(x). Здесь g(x) = cos(x).
    g_func = lambda x: np.cos(x)

    root = fixed_point_iteration(g_func, x0=0.5)
    print("\\n--- 2. Метод функциональной итерации ---")
    print(f"Найденный корень (решение x = cos(x)): {root:.7f}")"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1t():
    answer = f"""
## 1. Метод половинного деления (бисекции)

### Теоретическое описание:
Метод половинного деления — это простейший и самый надежный численный метод для нахождения корня нелинейного уравнения f(x) = 0.

**Основная идея:**
Метод основан на теореме о промежуточных значениях (теореме Больцано-Коши). Если непрерывная функция f(x) на отрезке [a, b] принимает на концах значения разных знаков (т.е. f(a) * f(b) < 0), то на этом отрезке существует как минимум один корень.

**Алгоритм:**
1.  **Начальный шаг:** Выбирается отрезок [a, b], на концах которого функция имеет разные знаки.
2.  **Итерация:** Отрезок делится пополам, вычисляется середина c = (a + b) / 2.
3.  **Проверка:**
    -   Если |f(c)| меньше заданной точности (tol), то c — искомый корень.
    -   Если знаки f(a) и f(c) совпадают, то корень находится на отрезке [c, b]. Новый отрезок для поиска становится [c, b].
    -   Если знаки f(b) и f(c) совпадают, то корень находится на отрезке [a, c]. Новый отрезок для поиска становится [a, c].
4.  **Повторение:** Процесс повторяется, сужая отрезок поиска вдвое на каждом шаге, до тех пор, пока не будет достигнута требуемая точность.

**Преимущества:**
-   Метод всегда сходится для любой непрерывной функции, если выполнены начальные условия.
-   Прост в реализации и очень надежен.

**Недостатки:**
-   Относительно медленная скорость сходимости (линейная).
-   Неприменим для отыскания корней четного порядка (например, в точке минимума/максимума, касающейся оси), когда график функции не пересекает ось.
"""
    pyperclip.copy(answer)
    pyperclip.paste()


def p2():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p3():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()

def p1():
    answer = f"""

"""
    pyperclip.copy(answer)
    pyperclip.paste()



