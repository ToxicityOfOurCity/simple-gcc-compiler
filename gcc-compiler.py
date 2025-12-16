import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import subprocess
import threading
import json

class GCCCompilerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GCC Compiler GUI")
        self.root.geometry("700x550")

        # Set dark theme for the entire window
        self.root.config(bg="#2E2E2E")

        # Selected file paths
        self.source_file = tk.StringVar()
        self.output_file = tk.StringVar()

        # Compiler flag options
        self.flag_no_console = tk.BooleanVar()
        self.flag_optimise = tk.BooleanVar()
        self.flag_wall = tk.BooleanVar()
        self.flag_fullscreen = tk.BooleanVar()

        # Preferences storage
        self.load_preferences()

        # Create the widgets
        self.create_widgets()

        # Status bar for user feedback
        self.status_bar = tk.Label(self.root, text="Ready", bg="#444", fg="white", anchor="w")
        self.status_bar.pack(side="bottom", fill="x", padx=5)

        # Menu bar creation
        self.create_menu()

    def create_widgets(self):
        # --- Source file selection ---
        frame_top = tk.Frame(self.root, bg="#2E2E2E")
        frame_top.pack(pady=10, fill="x")

        tk.Label(frame_top, text="Source File:", bg="#2E2E2E", fg="white").pack(anchor="w")
        tk.Entry(frame_top, textvariable=self.source_file, bg="#444", fg="white", insertbackground="white").pack(fill="x", padx=5)
        tk.Button(frame_top, text="Select Source File", command=self.select_source, bg="#444", fg="white").pack(pady=5)

        # --- Output file selection ---
        frame_out = tk.Frame(self.root, bg="#2E2E2E")
        frame_out.pack(pady=10, fill="x")

        tk.Label(frame_out, text="Output EXE:", bg="#2E2E2E", fg="white").pack(anchor="w")
        tk.Entry(frame_out, textvariable=self.output_file, bg="#444", fg="white", insertbackground="white").pack(fill="x", padx=5)
        tk.Button(frame_out, text="Select Output Location", command=self.select_output, bg="#444", fg="white").pack(pady=5)

        # --- Compile button ---
        tk.Button(
            self.root,
            text="Compile Code",
            command=self.compile_code_in_background,
            bg="#273747",
            fg="white",
            height=2
        ).pack(pady=10)

        # --- Compiler flags ---
        flags_frame = tk.LabelFrame(
            self.root,
            text="Compiler Flags",
            bg="#2E2E2E",
            fg="white"
        )
        flags_frame.pack(fill="x", padx=5, pady=5)

        def flag_cb(text, var):
            return tk.Checkbutton(
                flags_frame,
                text=text,
                variable=var,
                bg="#2E2E2E",
                fg="white",
                activebackground="#2E2E2E",
                activeforeground="white",
                selectcolor="#2E2E2E"
            )

        flag_cb("No Console Window (-mwindows)", self.flag_no_console).pack(anchor="w")
        flag_cb("Enable Warnings (-Wall)", self.flag_wall).pack(anchor="w")
        flag_cb("Optimisation (-O2)", self.flag_optimise).pack(anchor="w")
        flag_cb("Fullscreen Macro (-DFULLSCREEN)", self.flag_fullscreen).pack(anchor="w")

        # --- Log area ---
        tk.Label(self.root, text="Compilation Log:", bg="#2E2E2E", fg="white").pack(anchor="w", padx=5)
        self.log_area = scrolledtext.ScrolledText(self.root, height=15, bg="black", fg="white", insertbackground="white")
        self.log_area.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Clear Log button ---
        tk.Button(self.root, text="Clear Log", command=self.clear_log, bg="#444", fg="white").pack(pady=5)

    def create_menu(self):
        menu_bar = tk.Menu(self.root, bg="#273747", fg="white")
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0, bg="#273747", fg="white")
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Preferences", command=self.open_preferences, background="#444", foreground="white")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, background="#444", foreground="white")

        help_menu = tk.Menu(menu_bar, tearoff=0, bg="#273747", fg="white")
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about, background="#444", foreground="white")

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("500x200")
        about_window.config(bg="#2E2E2E")

        about_label = tk.Label(about_window, text="GCC Compiler GUI v1.3\nDeveloped by some random in VGA class & ChatGPT,\nadds custom flags for Windows and fullscreen.", bg="#2E2E2E", fg="white", font=("Arial", 9))
        about_label.pack(pady=30)

        tk.Button(about_window, text="Close", command=about_window.destroy, bg="#444", fg="white").pack(pady=10)

    def select_source(self):
        file_path = filedialog.askopenfilename(
            title="Select C/C++ Source File",
            filetypes=[("C Files", "*.c"), ("C++ Files", "*.cpp"), ("All Files", "*.*")]
        )
        if file_path:
            self.source_file.set(file_path)

    def select_output(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Output Executable",
            defaultextension=".exe",
            filetypes=[("Executable", "*.exe")]
        )
        if file_path:
            self.output_file.set(file_path)

    def compile_code(self):
        self.update_status("Compiling...")
        self.log_area.delete(1.0, tk.END)

        src = self.source_file.get()
        out = self.output_file.get()

        if not src or not out:
            messagebox.showerror("Error", "Please select source and output files.")
            self.update_status("Ready")
            return

        if not os.path.exists(src):
            messagebox.showerror("Error", "Source file does not exist.")
            self.update_status("Ready")
            return

        # Build GCC command with flags
        flags = []
        if self.flag_no_console.get():
            flags.append("-mwindows")
        if self.flag_wall.get():
            flags.append("-Wall")
        if self.flag_optimise.get():
            flags.append("-O2")
        if self.flag_fullscreen.get():
            flags.append("-DFULLSCREEN")

        flag_string = " ".join(flags)
        command = f'gcc "{src}" {flag_string} -o "{out}"'

        self.log_area.insert(tk.END, f"Running command:\n{command}\n\n")

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True
            )

            stdout, stderr = process.communicate()

            if stdout:
                self.log_area.insert(tk.END, stdout)

            if stderr:
                self.log_area.insert(tk.END, stderr)

            if process.returncode == 0:
                self.log_area.insert(tk.END, "\nCompilation successful!\n")
                self.update_status("Compilation Successful")
            else:
                self.log_area.insert(tk.END, "\nCompilation failed.\n", 'error')
                self.update_status("Compilation Failed")

        except Exception as e:
            self.log_area.insert(tk.END, f"Error: {e}\n", 'error')
            self.update_status("Error Occurred")

    def compile_code_in_background(self):
        threading.Thread(target=self.compile_code).start()

    def clear_log(self):
        self.log_area.delete(1.0, tk.END)

    def update_status(self, status_text):
        self.status_bar.config(text=status_text)

    def highlight_errors(self, text):
        self.log_area.tag_configure("error", foreground="red")
        self.log_area.insert(tk.END, text, "error")

    def load_preferences(self):
        try:
            with open("config.json", "r") as f:
                preferences = json.load(f)
                self.source_file.set(preferences.get("source_file", ""))
                self.output_file.set(preferences.get("output_file", ""))
                # Load flags if saved
                self.flag_no_console.set(preferences.get("flag_no_console", False))
                self.flag_optimise.set(preferences.get("flag_optimise", False))
                self.flag_wall.set(preferences.get("flag_wall", False))
                self.flag_fullscreen.set(preferences.get("flag_fullscreen", False))
        except FileNotFoundError:
            pass

    def save_preferences(self):
        preferences = {
            "source_file": self.source_file.get(),
            "output_file": self.output_file.get(),
            "flag_no_console": self.flag_no_console.get(),
            "flag_optimise": self.flag_optimise.get(),
            "flag_wall": self.flag_wall.get(),
            "flag_fullscreen": self.flag_fullscreen.get()
        }
        with open("config.json", "w") as f:
            json.dump(preferences, f)

    def open_preferences(self):
        preferences_window = tk.Toplevel(self.root)
        preferences_window.title("Preferences")
        preferences_window.geometry("400x300")
        preferences_window.config(bg="#2E2E2E")

        # Source File selection
        tk.Label(preferences_window, text="Source File:", bg="#2E2E2E", fg="white").pack(pady=5)
        source_entry = tk.Entry(preferences_window, textvariable=self.source_file, bg="#444", fg="white", insertbackground="white")
        source_entry.pack(pady=5, padx=5, fill="x")
        tk.Button(preferences_window, text="Browse", command=lambda: self.select_source_in_preferences(preferences_window), bg="#444", fg="white").pack(pady=5)

        # Output File selection
        tk.Label(preferences_window, text="Output File:", bg="#2E2E2E", fg="white").pack(pady=5)
        output_entry = tk.Entry(preferences_window, textvariable=self.output_file, bg="#444", fg="white", insertbackground="white")
        output_entry.pack(pady=5, padx=5, fill="x")
        tk.Button(preferences_window, text="Browse", command=lambda: self.select_output_in_preferences(preferences_window), bg="#444", fg="white").pack(pady=5)

        # Save Preferences button
        tk.Button(preferences_window, text="Save Preferences", command=self.save_preferences, bg="#444", fg="white").pack(pady=10)

    def select_source_in_preferences(self, preferences_window):
        file_path = filedialog.askopenfilename(
            title="Select C/C++ Source File",
            filetypes=[("C Files", "*.c"), ("C++ Files", "*.cpp"), ("All Files", "*.*")]
        )
        if file_path:
            self.source_file.set(file_path)
        preferences_window.lift()

    def select_output_in_preferences(self, preferences_window):
        file_path = filedialog.asksaveasfilename(
            title="Save Output Executable",
            defaultextension=".exe",
            filetypes=[("Executable", "*.exe")]
        )
        if file_path:
            self.output_file.set(file_path)
        preferences_window.lift()

if __name__ == "__main__":
    root = tk.Tk()
    app = GCCCompilerApp(root)
    root.mainloop()
