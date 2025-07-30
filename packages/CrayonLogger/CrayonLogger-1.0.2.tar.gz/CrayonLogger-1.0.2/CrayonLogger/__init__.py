import functools
import inspect
import datetime
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import time  # necessário para temporização

class Logger:
    def __init__(self, log_file=None, enable_terminal=True, gui_title="Logger - Interface Gráfica"):
        self.enabled = True
        self.enable_terminal = enable_terminal
        self.log_file = log_file
        self.gui_enabled = False
        self.gui_window = None
        self.gui_textbox = None
        self.gui_title = gui_title
        self._timers = {}  # Armazena tempos de início para medir duração

    def graphical(self, enable=True, title=None):
        self.gui_enabled = enable
        if title:
            self.gui_title = title
        if enable:
            threading.Thread(target=self._start_gui, daemon=True).start()

    def _start_gui(self):
        self.gui_window = tk.Tk()
        self.gui_window.title(self.gui_title)
        self.gui_window.geometry("700x400")
        self.gui_textbox = ScrolledText(self.gui_window, font=("Consolas", 10))
        self.gui_textbox.pack(expand=True, fill=tk.BOTH)
        self.gui_textbox.configure(state="disabled")

        # Tags de cor
        self.gui_textbox.tag_configure("default", foreground="black")
        self.gui_textbox.tag_configure("func", foreground="blue")
        self.gui_textbox.tag_configure("return", foreground="green")
        self.gui_textbox.tag_configure("error", foreground="red")
        self.gui_textbox.tag_configure("warn", foreground="orange")
        self.gui_textbox.tag_configure("success", foreground="green")
        self.gui_textbox.tag_configure("id", foreground="purple")
        self.gui_textbox.tag_configure("time", foreground="cyan")

        self.gui_window.mainloop()

    def _wait_gui_ready(self, timeout=5):
        for _ in range(int(timeout * 10)):
            if self.gui_textbox:
                return True
            time.sleep(0.1)
        return False

    def _write_gui(self, text, tag="default"):
        if not self._wait_gui_ready():
            return
        self.gui_textbox.configure(state="normal")
        self.gui_textbox.insert(tk.END, text + "\n", tag)
        self.gui_textbox.see(tk.END)
        self.gui_textbox.configure(state="disabled")

    def _write_log(self, msg, tag="default"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_msg = f"[{timestamp}] {msg}"

        if self.enable_terminal:
            if tag == "time":
                print(f"\033[96m{full_msg}\033[0m")
            elif tag == "error":
                print(f"\033[91m{full_msg}\033[0m")
            elif tag == "warn":
                print(f"\033[93m{full_msg}\033[0m")
            elif tag == "success":
                print(f"\033[92m{full_msg}\033[0m")
            elif tag == "func":
                print(f"\033[94m{full_msg}\033[0m")
            elif tag == "return":
                print(f"\033[92m{full_msg}\033[0m")
            else:
                print(full_msg)

        if self.gui_enabled:
            self._write_gui(full_msg, tag)
        if self.log_file:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(full_msg + "\n")
            except Exception as e:
                print(f"[Logger ERRO]: Falha ao salvar no arquivo: {e}")

    def log_func(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return func(*args, **kwargs)

            func_name = func.__name__
            self._write_log(f"[FUNÇÃO] Chamando '{func_name}' com:", tag="func")

            arg_names = inspect.getfullargspec(func).args
            for name, val in zip(arg_names, args):
                self._write_log(f"   - {name} = {val}", tag="func")
            for name, val in kwargs.items():
                self._write_log(f"   - {name} = {val} (kwarg)", tag="func")

            try:
                result = func(*args, **kwargs)
                self._write_log(f"[RETORNO] {func_name}: {result}", tag="return")
                return result
            except Exception as e:
                self._write_log(f"[EXCEÇÃO] {func_name}: {e}", tag="error")
                raise
        return wrapper

    def point(self, *args, **vars):
        if not args:
            return

        if len(args) == 1:
            msg = args[0]
            tag = "default"
        else:
            tag = args[0].lower()
            msg = args[1]

            if tag not in {"error", "warn", "success", "id", "func", "return", "time"}:
                msg = f"{tag}: {msg}"
                tag = "default"

        self._write_log(msg, tag=tag)

        for k, v in vars.items():
            self._write_log(f"   - {k} = {v}", tag=tag)
            
    def timeit(self, label=None):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                name = label or func.__name__
                self.start(name)
                try:
                    return func(*args, **kwargs)
                finally:
                    self.end(name)
            return wrapper
        return decorator

    def start(self, label=""):
        self._timers[label] = time.time()
        self.point("func", f"Iniciando temporizador '{label}'")

    def end(self, label=""):
        inicio = self._timers.get(label)
        if inicio is None:
            self.point("error", f"Nenhum temporizador iniciado com label '{label}'")
            return
        duracao = time.time() - inicio
        self.point(f"Tempo decorrido para '{label}': {duracao:.4f} segundos")
        del self._timers[label]
