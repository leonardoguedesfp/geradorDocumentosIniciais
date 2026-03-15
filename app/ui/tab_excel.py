"""Tab 1: Excel / Microsoft Forms exported spreadsheet."""

import customtkinter as ctk
from tkinter import filedialog

from app.ui.styles import *
from app.ui.components import (
    StyledButton, StyledLabel, ScrollableCheckboxFrame, StatusIndicator,
)
from app.core.excel_reader import read_excel
from app.models.cliente import Cliente


class TabExcel(ctk.CTkFrame):
    """Excel import tab for batch client processing."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG_MAIN, **kwargs)

        self.clientes: list[Cliente] = []
        self.row_warnings: list[tuple[int, list[str]]] = []

        # File selection
        file_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        file_frame.pack(fill="x", padx=10, pady=(10, 5))

        StyledLabel(file_frame, text="Arquivo Excel:", is_title=False).pack(side="left")
        self.file_label = ctk.CTkLabel(
            file_frame, text="Nenhum arquivo selecionado",
            font=(FONT_FAMILY, FONT_SIZE_SMALL), text_color=NEUTRAL_TEXT,
        )
        self.file_label.pack(side="left", padx=10, expand=True, fill="x")

        StyledButton(
            file_frame, text="Selecionar arquivo", primary=True,
            command=self._select_file, width=150,
        ).pack(side="right")

        # Status
        self.status = StatusIndicator(self)
        self.status.pack(anchor="w", padx=10, pady=(0, 5))

        # Client list with checkboxes
        list_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = ctk.CTkFrame(list_frame, fg_color=BG_MAIN)
        btn_frame.pack(fill="x", pady=(0, 5))

        StyledButton(
            btn_frame, text="Selecionar todos", primary=False, width=130,
            command=self._select_all,
        ).pack(side="left", padx=(0, 5))

        StyledButton(
            btn_frame, text="Desmarcar todos", primary=False, width=130,
            command=self._deselect_all,
        ).pack(side="left")

        self.client_count_label = ctk.CTkLabel(
            btn_frame, text="", font=(FONT_FAMILY, FONT_SIZE_SMALL),
            text_color=BODY_TEXT,
        )
        self.client_count_label.pack(side="right")

        self.client_list = ScrollableCheckboxFrame(list_frame, height=200)
        self.client_list.pack(fill="both", expand=True)

    def _select_file(self):
        path = filedialog.askopenfilename(
            title="Selecionar planilha de clientes",
            filetypes=[("Planilha Excel", "*.xlsx"), ("Todos os arquivos", "*.*")],
        )
        if not path:
            return

        self.file_label.configure(
            text=path.split("/")[-1].split("\\")[-1],
            text_color=BODY_TEXT,
        )

        try:
            clientes, col_warnings, row_warnings = read_excel(path)
        except Exception as e:
            self.status.set_error(f"Erro ao ler arquivo: {e}")
            self.clientes = []
            self.client_list.set_items([])
            return

        self.clientes = clientes
        self.row_warnings = row_warnings
        self.file_path = path

        if col_warnings:
            self.status.set_warning("; ".join(col_warnings))
        elif row_warnings:
            warn_rows = [str(r) for r, _ in row_warnings]
            self.status.set_warning(
                f"Campos obrigatórios ausentes nas linhas: {', '.join(warn_rows)}"
            )
        elif clientes:
            self.status.set_ok(f"{len(clientes)} cliente(s) encontrado(s)")
        else:
            self.status.set_warning("Nenhum cliente encontrado na planilha")

        # Populate client list
        items = []
        for i, c in enumerate(clientes):
            label = c.nome_completo or f"(Linha {i + 1} — nome vazio)"
            # Mark rows with warnings
            has_warn = any(r == i for r, _ in row_warnings)
            if has_warn:
                label += " ⚠"
            items.append(label)

        self.client_list.set_items(items)
        self.client_count_label.configure(text=f"{len(clientes)} cliente(s)")

    def _select_all(self):
        self.client_list.select_all()

    def _deselect_all(self):
        self.client_list.deselect_all()

    def get_selected_clients(self) -> list[Cliente]:
        """Return the list of selected clients."""
        indices = self.client_list.get_selected_indices()
        return [self.clientes[i] for i in indices if i < len(self.clientes)]

    def has_data(self) -> bool:
        return len(self.clientes) > 0 and len(self.client_list.get_selected_indices()) > 0

    def get_source_dir(self) -> str:
        """Return the directory of the source Excel file."""
        if hasattr(self, "file_path"):
            import os
            return os.path.dirname(self.file_path)
        return ""
