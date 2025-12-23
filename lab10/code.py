import tkinter as tk
from tkinter import ttk
import numpy as np
import math

class CurveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Алгоритмы построения кривых и поверхностей — Вариант 16")
        self.root.geometry("1000x700")

        self.control_points = []
        self.current_step = 0
        self.subdivisions = 5
        self.current_method = "Безье"

        self.setup_ui()

    # Своя реализация comb для старых версий Python
    def comb(self, n, k):
        if k < 0 or k > n:
            return 0
        if k == 0 or k == n:
            return 1
        k = min(k, n - k)
        result = 1
        for i in range(1, k + 1):
            result = result * (n - k + i) // i
        return result

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        method_frame = ttk.LabelFrame(left_frame, text="Метод построения")
        method_frame.pack(fill=tk.X, pady=(0, 10))

        self.method_var = tk.StringVar(value="Безье")
        methods = [
            ("Квадратичная кривая Безье", "Безье"),
            ("Кривая Чайкина", "Чайкин"),
            ("Поверхность Безье", "Безье_поверхность"),
            ("Поверхность Ду-Сабина", "Ду-Сабин")
        ]

        for text, value in methods:
            ttk.Radiobutton(method_frame, text=text, variable=self.method_var,
                            value=value, command=self.method_changed).pack(anchor=tk.W)

        points_frame = ttk.LabelFrame(left_frame, text="Управление точками")
        points_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(points_frame, text="Добавить точку",
                   command=self.add_point_mode).pack(fill=tk.X)
        ttk.Button(points_frame, text="Очистить все точки",
                   command=self.clear_points).pack(fill=tk.X, pady=(5, 0))

        params_frame = ttk.LabelFrame(left_frame, text="Параметры построения")
        params_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(params_frame, text="Количество разбиений:").pack(anchor=tk.W)
        self.subdivisions_var = tk.StringVar(value="5")
        subdivisions_entry = ttk.Entry(params_frame, textvariable=self.subdivisions_var)
        subdivisions_entry.pack(fill=tk.X)

        control_frame = ttk.LabelFrame(left_frame, text="Управление построением")
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(control_frame, text="Построить полностью",
                   command=self.build_full).pack(fill=tk.X)
        ttk.Button(control_frame, text="Следующий шаг",
                   command=self.next_step).pack(fill=tk.X, pady=(5, 0))
        ttk.Button(control_frame, text="Сбросить шаги",
                   command=self.reset_steps).pack(fill=tk.X, pady=(5, 0))

        display_frame = ttk.LabelFrame(left_frame, text="Отображение")
        display_frame.pack(fill=tk.X)

        self.show_control_var = tk.BooleanVar(value=True)
        self.show_refined_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(display_frame, text="Исходные точки",
                        variable=self.show_control_var,
                        command=self.redraw).pack(anchor=tk.W)
        ttk.Checkbutton(display_frame, text="Вершины уточненного полигона",
                        variable=self.show_refined_var,
                        command=self.redraw).pack(anchor=tk.W)

        info_frame = ttk.LabelFrame(left_frame, text="Информация")
        info_frame.pack(fill=tk.X, pady=(10, 0))

        self.info_text = tk.Text(info_frame, height=8, width=30)
        self.info_text.pack(fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(right_frame, bg="white", width=600, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.canvas_click)

        self.update_info()

    def method_changed(self):
        self.current_method = self.method_var.get()
        self.reset_steps()
        self.update_info()

    def add_point_mode(self):
        self.info_text.insert(tk.END, "Режим добавления точек: кликните на холсте\n")
        self.info_text.see(tk.END)

    def clear_points(self):
        self.control_points.clear()
        self.current_step = 0
        self.redraw()
        self.update_info()

    def canvas_click(self, event):
        if len(self.control_points) < 50:
            point = (event.x, event.y)
            self.control_points.append(point)
            self.reset_steps()
            self.redraw()
            self.update_info()

    def update_info(self):
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"Метод: {self.current_method}\n")
        self.info_text.insert(tk.END, f"Точек: {len(self.control_points)}\n")
        self.info_text.insert(tk.END, f"Шаг: {self.current_step}\n")
        self.info_text.insert(tk.END, f"Разбиений: {self.subdivisions}\n\n")

        if self.control_points:
            self.info_text.insert(tk.END, "Точки контроля:\n")
            for i, point in enumerate(self.control_points):
                self.info_text.insert(tk.END, f"{i}: ({point[0]}, {point[1]})\n")

    def get_subdivisions(self):
        try:
            self.subdivisions = max(1, min(20, int(self.subdivisions_var.get())))
        except ValueError:
            self.subdivisions = 5
            self.subdivisions_var.set("5")

    def build_full(self):
        self.get_subdivisions()
        self.current_step = self.subdivisions
        self.redraw()

    def next_step(self):
        self.get_subdivisions()
        if self.current_step < self.subdivisions:
            self.current_step += 1
        self.redraw()

    def reset_steps(self):
        self.current_step = 0
        self.redraw()

    # ========== Квадратичная кривая Безье ==========
    def quadratic_bezier(self, points, t):
        if len(points) < 3:
            return points

        result = []
        for i in range(len(points) - 2):
            p0 = np.array(points[i])
            p1 = np.array(points[i + 1])
            p2 = np.array(points[i + 2])

            point = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2
            result.append(tuple(point))

        return result

    # ========== Кривая Чайкина ==========
    def chaikin_curve(self, points, iterations):
        if len(points) < 2:
            return points

        current_points = points.copy()

        for _ in range(iterations):
            new_points = []
            for i in range(len(current_points) - 1):
                p0 = np.array(current_points[i])
                p1 = np.array(current_points[i + 1])

                q0 = 0.75 * p0 + 0.25 * p1
                q1 = 0.25 * p0 + 0.75 * p1

                new_points.append(tuple(q0))
                new_points.append(tuple(q1))

            current_points = new_points

        return current_points

    # ========== Поверхность Безье (бикубическая) ==========
    def bernstein(self, n, i, t):
        # Используем нашу собственную функцию comb
        return self.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

    def bezier_surface(self, points, subdivisions):
        # Для бикубической поверхности нужна сетка 4x4 (16 точек)
        if len(points) < 16:
            # Если точек меньше 16, используем только первые 16
            points = points[:16]

        # Преобразуем в сетку 4x4
        grid = []
        idx = 0
        for i in range(4):
            row = []
            for j in range(4):
                if idx < len(points):
                    row.append(np.array(points[idx]))
                    idx += 1
                else:
                    # Если точек не хватает, добавляем нулевые
                    row.append(np.array([100 + j*100, 100 + i*100]))
            grid.append(row)

        result_points = []
        # Количество точек по каждой оси зависит от количества разбиений
        resolution = 2 ** (subdivisions + 1) + 1  # Минимум 3 точки при subdivisions=0

        for i in range(resolution):
            u = i / (resolution - 1) if resolution > 1 else 0
            for j in range(resolution):
                v = j / (resolution - 1) if resolution > 1 else 0

                point = np.array([0.0, 0.0])
                for m in range(4):
                    for n in range(4):
                        bernstein_u = self.bernstein(3, m, u)
                        bernstein_v = self.bernstein(3, n, v)
                        point += bernstein_u * bernstein_v * grid[m][n]
                result_points.append(tuple(point))

        return result_points

    # ========== Поверхность Ду-Сабина ==========
    def du_sabin_surface(self, points, iterations):
        if len(points) < 3:
            return points

        current_points = points.copy()

        for _ in range(iterations):
            new_points = []
            n = len(current_points)

            for i in range(n):
                p_prev = np.array(current_points[(i - 1) % n])
                p_curr = np.array(current_points[i])
                p_next = np.array(current_points[(i + 1) % n])

                new_point = 0.25 * p_prev + 0.5 * p_curr + 0.25 * p_next
                new_points.append(tuple(new_point))

            current_points = new_points

        return current_points

    # ========== Отрисовка ==========
    def redraw(self):
        self.canvas.delete("all")

        if not self.control_points:
            return

        if self.show_control_var.get():
            for point in self.control_points:
                x, y = point
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red", outline="red")

            for i in range(len(self.control_points) - 1):
                x1, y1 = self.control_points[i]
                x2, y2 = self.control_points[i + 1]
                self.canvas.create_line(x1, y1, x2, y2, fill="red", dash=(2, 2))

        # Выбор метода отрисовки
        if self.current_method == "Безье" and len(self.control_points) >= 3:
            self.draw_bezier()
        elif self.current_method == "Чайкин" and len(self.control_points) >= 2:
            self.draw_chaikin()
        elif self.current_method == "Безье_поверхность":
            self.draw_bezier_surface()
        elif self.current_method == "Ду-Сабин" and len(self.control_points) >= 3:
            self.draw_du_sabin()

    def draw_bezier(self):
        if self.current_step == 0:
            return

        bezier_curve = []
        steps = 100

        for t in np.linspace(0, 1, steps):
            current_points = self.control_points.copy()

            for step in range(min(self.current_step, len(self.control_points) - 2)):
                current_points = self.quadratic_bezier(current_points, t)

            if current_points:
                bezier_curve.append(current_points[0])

        if len(bezier_curve) > 1:
            for i in range(len(bezier_curve) - 1):
                x1, y1 = bezier_curve[i]
                x2, y2 = bezier_curve[i + 1]
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)

        if self.show_refined_var.get() and self.current_step > 0:
            for step in range(1, min(self.current_step + 1, len(self.control_points) - 1)):
                intermediate_points = []
                for t in [0.0, 0.5, 1.0]:
                    current_points = self.control_points.copy()
                    for s in range(step):
                        current_points = self.quadratic_bezier(current_points, t)
                    intermediate_points.extend(current_points)

                for point in intermediate_points:
                    x, y = point
                    self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="green", outline="green")

    def draw_chaikin(self):
        if self.current_step == 0:
            return

        chaikin_curve = self.chaikin_curve(self.control_points, self.current_step)

        if len(chaikin_curve) > 1:
            for i in range(len(chaikin_curve) - 1):
                x1, y1 = chaikin_curve[i]
                x2, y2 = chaikin_curve[i + 1]
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)

        if self.show_refined_var.get():
            for point in chaikin_curve:
                x, y = point
                self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="green", outline="green")

    def draw_bezier_surface(self):
        if self.current_step == 0:
            return

        surface_points = self.bezier_surface(self.control_points, self.current_step)

        if len(surface_points) > 1:
            # Определяем количество точек по одной оси
            resolution = int(np.sqrt(len(surface_points)))

            # Отрисовка линий по U (горизонтальные)
            for i in range(resolution):
                for j in range(resolution - 1):
                    idx1 = i * resolution + j
                    idx2 = i * resolution + j + 1
                    if idx1 < len(surface_points) and idx2 < len(surface_points):
                        x1, y1 = surface_points[idx1]
                        x2, y2 = surface_points[idx2]
                        self.canvas.create_line(x1, y1, x2, y2, fill="purple", width=1)

            # Отрисовка линий по V (вертикальные)
            for i in range(resolution - 1):
                for j in range(resolution):
                    idx1 = i * resolution + j
                    idx2 = (i + 1) * resolution + j
                    if idx1 < len(surface_points) and idx2 < len(surface_points):
                        x1, y1 = surface_points[idx1]
                        x2, y2 = surface_points[idx2]
                        self.canvas.create_line(x1, y1, x2, y2, fill="purple", width=1)

        if self.show_refined_var.get():
            # Показываем точки поверхности
            for point in surface_points:
                x, y = point
                self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="orange", outline="orange")

            # Показываем контрольные точки сетки
            for i, point in enumerate(self.control_points[:16]):  # первые 16 точек как сетка 4x4
                x, y = point
                self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="red", outline="red")
                self.canvas.create_text(x, y-10, text=str(i), fill="black")

    def draw_du_sabin(self):
        if self.current_step == 0:
            return

        du_sabin_surface = self.du_sabin_surface(self.control_points, self.current_step)

        n = len(du_sabin_surface)
        for i in range(n):
            x1, y1 = du_sabin_surface[i]
            x2, y2 = du_sabin_surface[(i + 1) % n]
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)

        if self.show_refined_var.get():
            for point in du_sabin_surface:
                x, y = point
                self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="green", outline="green")


def main():
    root = tk.Tk()
    app = CurveApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()