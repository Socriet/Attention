import os
import sys
import shutil
import threading
import subprocess
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
MASK_SCRIPT = BASE_DIR / "mask.py"

try:
    import customtkinter as ctk
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    USE_CTK = True
    BaseWindow = ctk.CTk
    BaseFrame = ctk.CTkFrame
    BaseButton = ctk.CTkButton
    BaseEntry = ctk.CTkEntry
    BaseLabel = ctk.CTkLabel
    BaseScrollFrame = ctk.CTkScrollableFrame
except ImportError:
    USE_CTK = False
    BaseWindow = tk.Tk
    BaseFrame = ttk.Frame
    BaseButton = ttk.Button
    BaseEntry = ttk.Entry
    BaseLabel = ttk.Label
    BaseScrollFrame = ttk.Frame


class AttentionStudioApp(BaseWindow):
    def __init__(self):
        super().__init__()
        self.title("BERT Attention Matrix Explorer & Run Manager")
        self.geometry("1300x850")
        self.minsize(1050, 700)

        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

        self.selected_folder = None
        self.selected_layer = tk.IntVar(value=1)
        self.selected_head = tk.IntVar(value=1)
        self.current_pil_image = None
        self.current_tk_image = None

        self._build_ui()
        self.refresh_folder_list()

    def _build_ui(self):
        # Master grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top Execution Bar
        if USE_CTK:
            top_frame = ctk.CTkFrame(self, corner_radius=10)
        else:
            top_frame = ttk.LabelFrame(self, text="Run Model")
        top_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        top_frame.grid_columnconfigure(1, weight=1)

        lbl_prompt = BaseLabel(top_frame, text="Sentence with [MASK]:")
        lbl_prompt.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.entry_text = BaseEntry(top_frame)
        self.entry_text.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.entry_text.insert(0, "The [MASK] jumped over the lazy dog.")

        self.btn_run = BaseButton(top_frame, text="⚡ Run mask.py", command=self.on_run_clicked)
        self.btn_run.grid(row=0, column=2, padx=10, pady=10)

        self.status_label = BaseLabel(top_frame, text="Ready")
        self.status_label.grid(row=0, column=3, padx=10, pady=10)

        # Main Split View 
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        # Left Column
        left_container = BaseFrame(main_paned)
        main_paned.add(left_container, weight=1)
        left_container.grid_rowconfigure(1, weight=1)
        left_container.grid_columnconfigure(0, weight=1)

        # Action toolbar for folders
        folder_actions_frame = BaseFrame(left_container)
        folder_actions_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        btn_refresh = BaseButton(folder_actions_frame, text="🔄 Refresh", width=70, command=self.refresh_folder_list)
        btn_refresh.pack(side=tk.LEFT, padx=3)

        btn_rename = BaseButton(folder_actions_frame, text="✏️ Rename", width=70, command=self.rename_selected_folder)
        btn_rename.pack(side=tk.LEFT, padx=3)

        btn_delete = BaseButton(folder_actions_frame, text="🗑️ Delete", width=70, command=self.delete_selected_folder)
        btn_delete.pack(side=tk.LEFT, padx=3)

        btn_open_folder = BaseButton(folder_actions_frame, text="📂 Explorer", width=75, command=self.open_in_file_explorer)
        btn_open_folder.pack(side=tk.RIGHT, padx=3)

        # Folder Listbox with Scrollbar
        list_frame = ttk.Frame(left_container)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.folder_listbox = tk.Listbox(
            list_frame, 
            bg="#1e1e1e" if USE_CTK else "#ffffff",
            fg="#ffffff" if USE_CTK else "#000000",
            selectbackground="#26588c",
            selectforeground="#ffffff",
            font=("Consolas", 10),
            highlightthickness=0,
            borderwidth=1
        )
        self.folder_listbox.grid(row=0, column=0, sticky="nsew")
        self.folder_listbox.bind("<<ListboxSelect>>", self.on_folder_selected)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.folder_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.folder_listbox.config(yscrollcommand=scrollbar.set)

        # Terminal
        self.log_text = tk.Text(
            left_container, 
            height=7,
            bg="#181818" if USE_CTK else "#f0f0f0",
            fg="#cccccc" if USE_CTK else "#111111",
            font=("Consolas", 9),
            relief=tk.FLAT
        )
        self.log_text.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.log_text.insert(tk.END, "Model inference logs will appear here...\n")
        self.log_text.config(state=tk.DISABLED)

        # Right Column
        right_container = BaseFrame(main_paned)
        main_paned.add(right_container, weight=3)
        right_container.grid_rowconfigure(1, weight=1)
        right_container.grid_columnconfigure(0, weight=1)

        # Head / Layer Selection Bar
        ctrl_frame = BaseFrame(right_container)
        ctrl_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        lbl_layer = BaseLabel(ctrl_frame, text="Layer (1-12):")
        lbl_layer.pack(side=tk.LEFT, padx=(5, 2))
        self.spin_layer = ttk.Spinbox(ctrl_frame, from_=1, to=12, width=4, textvariable=self.selected_layer, command=self.update_image_display)
        self.spin_layer.pack(side=tk.LEFT, padx=(0, 15))
        self.spin_layer.bind("<Return>", lambda e: self.update_image_display())

        lbl_head = BaseLabel(ctrl_frame, text="Head (1-12):")
        lbl_head.pack(side=tk.LEFT, padx=(5, 2))
        self.spin_head = ttk.Spinbox(ctrl_frame, from_=1, to=12, width=4, textvariable=self.selected_head, command=self.update_image_display)
        self.spin_head.pack(side=tk.LEFT, padx=(0, 15))
        self.spin_head.bind("<Return>", lambda e: self.update_image_display())

        # Quick Jump Buttons
        btn_quick1 = BaseButton(ctrl_frame, text="Prev Token (L2, H5)", command=lambda: self.jump_to(2, 5))
        btn_quick1.pack(side=tk.LEFT, padx=5)

        btn_quick3 = BaseButton(ctrl_frame, text="Next Token (L3, H10)", command=lambda: self.jump_to(3, 10))
        btn_quick3.pack(side=tk.LEFT, padx=5)

        # Image Canvas Display
        self.image_canvas = tk.Canvas(right_container, bg="#111111", highlightthickness=0)
        self.image_canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.image_canvas.bind("<Configure>", self.on_canvas_resize)

        # Image Path / Info Bar
        self.image_info_lbl = BaseLabel(right_container, text="Select an output run to view attention maps.")
        self.image_info_lbl.grid(row=2, column=0, sticky="w", padx=15, pady=5)

    # Navigation & Display
    def jump_to(self, layer, head):
        self.selected_layer.set(layer)
        self.selected_head.set(head)
        self.update_image_display()

    def refresh_folder_list(self):
        """Scans the outputs/ folder and populates the listbox."""
        self.folder_listbox.delete(0, tk.END)
        if not OUTPUTS_DIR.exists():
            return

        folders = [d for d in OUTPUTS_DIR.iterdir() if d.is_dir()]
        # Sort folders
        folders.sort(key=lambda d: d.stat().st_mtime, reverse=True)

        for folder in folders:
            num_pngs = len(list(folder.glob("*.png")))
            display_name = f"{folder.name} ({num_pngs} PNGs)"
            self.folder_listbox.insert(tk.END, display_name)

        if folders:
            self.folder_listbox.selection_set(0)
            self.selected_folder = folders[0]
            self.update_image_display()

    def on_folder_selected(self, event=None):
        selection = self.folder_listbox.curselection()
        if not selection:
            return
        item_text = self.folder_listbox.get(selection[0])
        folder_name = item_text.split(" (")[0]
        self.selected_folder = OUTPUTS_DIR / folder_name
        self.update_image_display()

    def update_image_display(self):
        """Loads and scales the PNG for the current Layer and Head selection."""
        if not self.selected_folder or not self.selected_folder.exists():
            self.image_canvas.delete("all")
            self.image_info_lbl.configure(text="No folder selected.")
            return

        layer = self.selected_layer.get()
        head = self.selected_head.get()
        image_name = f"Attention_Layer{layer}_Head{head}.png"
        image_path = self.selected_folder / image_name

        if not image_path.exists():
            self.image_canvas.delete("all")
            self.image_canvas.create_text(
                self.image_canvas.winfo_width() / 2 or 200,
                self.image_canvas.winfo_height() / 2 or 200,
                text=f"Image not found:\n{image_name}",
                fill="#888888",
                font=("Consolas", 12),
                justify=tk.CENTER
            )
            self.image_info_lbl.configure(text=f"Missing: {image_name}")
            return

        try:
            self.current_pil_image = Image.open(image_path)
            self._render_canvas_image()
            self.image_info_lbl.configure(text=f"Viewing: {self.selected_folder.name} / {image_name} ({self.current_pil_image.width}x{self.current_pil_image.height})")
        except Exception as e:
            self.image_info_lbl.configure(text=f"Error loading image: {e}")

    def on_canvas_resize(self, event):
        if self.current_pil_image:
            self._render_canvas_image()

    def _render_canvas_image(self):
        canvas_w = self.image_canvas.winfo_width()
        canvas_h = self.image_canvas.winfo_height()

        if canvas_w < 50 or canvas_h < 50:
            return

        img_w, img_h = self.current_pil_image.size
        scale = min((canvas_w - 20) / img_w, (canvas_h - 20) / img_h, 1.5)
        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))

        resized = self.current_pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.current_tk_image = ImageTk.PhotoImage(resized)

        self.image_canvas.delete("all")
        self.image_canvas.create_image(canvas_w // 2, canvas_h // 2, anchor=tk.CENTER, image=self.current_tk_image)

    # Folder Management Actions
    def rename_selected_folder(self):
        if not self.selected_folder or not self.selected_folder.exists():
            messagebox.showwarning("Rename Folder", "Please select a run folder first.")
            return

        current_name = self.selected_folder.name
        new_name = simpledialog.askstring("Rename Folder", "Enter new folder name:", initialvalue=current_name)
        if not new_name or new_name.strip() == "" or new_name == current_name:
            return

        # Sanitize name
        new_name = "".join(c for c in new_name if c.isalnum() or c in ("-", "_", " ")).strip()
        new_path = OUTPUTS_DIR / new_name

        if new_path.exists():
            messagebox.showerror("Error", f"A folder named '{new_name}' already exists.")
            return

        try:
            self.selected_folder.rename(new_path)
            self.selected_folder = new_path
            self.refresh_folder_list()
            # Reselect the renamed item
            for idx in range(self.folder_listbox.size()):
                if self.folder_listbox.get(idx).startswith(new_name):
                    self.folder_listbox.selection_clear(0, tk.END)
                    self.folder_listbox.selection_set(idx)
                    break
        except Exception as e:
            messagebox.showerror("Rename Failed", f"Could not rename folder: {e}")

    def delete_selected_folder(self):
        if not self.selected_folder or not self.selected_folder.exists():
            messagebox.showwarning("Delete Folder", "Please select a run folder first.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to permanently delete:\n'{self.selected_folder.name}' and all its images?"
        )
        if confirm:
            try:
                shutil.rmtree(self.selected_folder)
                self.selected_folder = None
                self.refresh_folder_list()
                self.image_canvas.delete("all")
            except Exception as e:
                messagebox.showerror("Delete Failed", f"Could not delete folder: {e}")

    def open_in_file_explorer(self):
        target = self.selected_folder if self.selected_folder and self.selected_folder.exists() else OUTPUTS_DIR
        if sys.platform == "win32":
            os.startfile(str(target))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(target)])
        else:
            subprocess.run(["xdg-open", str(target)])

    # Execution & Threading
    def log_append(self, text):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def on_run_clicked(self):
        sentence = self.entry_text.get().strip()
        if "[MASK]" not in sentence:
            messagebox.showwarning("Invalid Input", "The input sentence must contain the token [MASK].")
            return

        self.btn_run.configure(state="disabled")
        self.status_label.configure(text="Processing...")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log_append(f"Starting inference on: \"{sentence}\"\n")

        # Run mask.py in background
        thread = threading.Thread(target=self._run_mask_process, args=(sentence,), daemon=True)
        thread.start()

    def _run_mask_process(self, sentence):
        python_executable = sys.executable

        try:
            # Execute mask.py
            process = subprocess.Popen(
                [python_executable, str(MASK_SCRIPT)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(BASE_DIR)
            )

            stdout, _ = process.communicate(input=sentence + "\n")

            self.after(0, self._on_run_finished, stdout, process.returncode)

        except Exception as e:
            self.after(0, self._on_run_finished, f"Execution failed: {e}\n", 1)

    def _on_run_finished(self, output, return_code):
        self.btn_run.configure(state="normal")
        self.log_append(output)

        if return_code == 0:
            self.status_label.configure(text="Done! ✓")
            self.refresh_folder_list()
        else:
            self.status_label.configure(text="Error! ✗")
            messagebox.showerror("Execution Error", "mask.py exited with an error. Check the log panel for details.")


if __name__ == "__main__":
    app = AttentionStudioApp()
    app.mainloop()