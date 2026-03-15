"""Preferences window for configuring application settings."""

import customtkinter as ctk
from tkinter import filedialog

from app.ui.styles import *
from app.ui.components import StyledButton, StyledLabel, StyledEntry, StatusIndicator
from app.core.config_manager import get_templates_folder, set_templates_folder
from app.core.template_loader import check_templates_folder, EXPECTED_FILES


class PreferencesWindow(ctk.CTkToplevel):
    """Preferences dialog for application settings."""

    def __init__(self, master, on_save_callback=None, **kwargs):
        super().__init__(master, **kwargs)

        self.title("Preferências")
        self.geometry("600x300")
        self.configure(fg_color=BG_MAIN)
        self.resizable(False, False)
        self.on_save_callback = on_save_callback

        # Make modal
        self.transient(master)
        self.grab_set()

        # Title
        StyledLabel(self, text="Preferências", is_title=True).pack(
            anchor="w", padx=20, pady=(20, 10),
        )

        # Templates folder
        folder_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        folder_frame.pack(fill="x", padx=20, pady=5)

        StyledLabel(folder_frame, text="Pasta de templates padrão:").pack(anchor="w")

        input_row = ctk.CTkFrame(folder_frame, fg_color=BG_MAIN)
        input_row.pack(fill="x", pady=5)

        self.folder_entry = StyledEntry(input_row, width=350)
        self.folder_entry.pack(side="left", fill="x", expand=True)

        current_folder = get_templates_folder()
        if current_folder:
            self.folder_entry.insert(0, current_folder)

        StyledButton(
            input_row, text="Selecionar...", primary=False, width=110,
            command=self._select_folder,
        ).pack(side="left", padx=(10, 0))

        # Status
        self.status = StatusIndicator(self)
        self.status.pack(anchor="w", padx=20, pady=5)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        btn_frame.pack(fill="x", padx=20, pady=(15, 20))

        StyledButton(
            btn_frame, text="Testar pasta", primary=False, width=120,
            command=self._test_folder,
        ).pack(side="left")

        StyledButton(
            btn_frame, text="Salvar", primary=True, width=100,
            command=self._save,
        ).pack(side="right")

        StyledButton(
            btn_frame, text="Cancelar", primary=False, width=100,
            command=self.destroy,
        ).pack(side="right", padx=(0, 10))

    def _select_folder(self):
        path = filedialog.askdirectory(title="Selecionar pasta de templates")
        if path:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, path)

    def _test_folder(self):
        folder = self.folder_entry.get().strip()
        if not folder:
            self.status.set_warning("Informe o caminho da pasta")
            return

        found = check_templates_folder(folder)
        missing = [name for doc_type, name in EXPECTED_FILES.items() if found[doc_type] is None]

        if not missing:
            self.status.set_ok("Todos os 3 templates encontrados e válidos")
        else:
            self.status.set_warning(f"Arquivos ausentes: {', '.join(missing)}")

    def _save(self):
        folder = self.folder_entry.get().strip()
        set_templates_folder(folder)
        self.status.set_ok("Configurações salvas")

        if self.on_save_callback:
            self.on_save_callback()

        self.after(500, self.destroy)
