"""Template status section: shows active templates and allows per-session overrides."""

import customtkinter as ctk
from tkinter import filedialog

from app.ui.styles import *
from app.ui.components import StyledLabel, StatusIndicator, StyledButton
from app.core.template_loader import (
    EXPECTED_FILES,
    check_templates_folder,
    validate_template,
)
from app.core.config_manager import get_templates_folder


class SectionTemplates(ctk.CTkFrame):
    """Template management section for the main window."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG_MAIN, **kwargs)

        self.template_paths = {"procuracao": None, "declaracao": None, "contrato": None}
        self.session_overrides = {"procuracao": None, "declaracao": None, "contrato": None}
        self.warnings = {"procuracao": [], "declaracao": [], "contrato": []}

        # Status indicator
        self.status_indicator = StatusIndicator(self)
        self.status_indicator.pack(anchor="w", padx=10, pady=(5, 0))

        # Detail status per document
        self.detail_label = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, FONT_SIZE_SMALL),
            text_color=BODY_TEXT, justify="left",
        )
        self.detail_label.pack(anchor="w", padx=10, pady=(0, 5))

        # Expandable override section
        self.override_visible = ctk.BooleanVar(value=False)
        self.toggle_btn = ctk.CTkButton(
            self,
            text="Usar modelo diferente nesta sessão ▾",
            command=self._toggle_overrides,
            fg_color="transparent",
            text_color=BLUE_PRIMARY,
            hover_color="#d5d2c9",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            anchor="w",
        )
        self.toggle_btn.pack(anchor="w", padx=10, pady=(0, 5))

        # Override frame (hidden by default)
        self.override_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        self._create_override_selectors()

        # Load templates
        self.reload_templates()

    def _create_override_selectors(self):
        doc_labels = {
            "procuracao": "Procuração",
            "declaracao": "Declaração de Hipossuficiência",
            "contrato": "Contrato de Prestação de Serviços",
        }
        self.override_labels = {}
        self.override_status = {}

        for doc_type, label_text in doc_labels.items():
            row = ctk.CTkFrame(self.override_frame, fg_color=BG_MAIN)
            row.pack(fill="x", padx=10, pady=2)

            ctk.CTkLabel(
                row, text=f"{label_text}:", font=(FONT_FAMILY, FONT_SIZE_SMALL),
                text_color=BODY_TEXT, width=250, anchor="w",
            ).pack(side="left")

            status = ctk.CTkLabel(
                row, text="Usando padrão", font=(FONT_FAMILY, FONT_SIZE_SMALL),
                text_color=NEUTRAL_TEXT, width=200, anchor="w",
            )
            status.pack(side="left", padx=(5, 0))
            self.override_status[doc_type] = status

            StyledButton(
                row, text="Selecionar...", primary=False, width=100,
                command=lambda dt=doc_type: self._select_override(dt),
            ).pack(side="left", padx=5)

            StyledButton(
                row, text="Resetar", primary=False, width=70,
                command=lambda dt=doc_type: self._reset_override(dt),
            ).pack(side="left")

    def _toggle_overrides(self):
        if self.override_visible.get():
            self.override_frame.pack_forget()
            self.toggle_btn.configure(text="Usar modelo diferente nesta sessão ▾")
            self.override_visible.set(False)
        else:
            self.override_frame.pack(fill="x", after=self.toggle_btn)
            self.toggle_btn.configure(text="Usar modelo diferente nesta sessão ▴")
            self.override_visible.set(True)

    def _select_override(self, doc_type: str):
        path = filedialog.askopenfilename(
            title=f"Selecionar template alternativo",
            filetypes=[("Documento Word", "*.docx")],
        )
        if path:
            self.session_overrides[doc_type] = path
            is_valid, warns = validate_template(path, doc_type)
            if is_valid:
                self.override_status[doc_type].configure(
                    text=path.split("/")[-1].split("\\")[-1],
                    text_color=STATUS_OK,
                )
                self.warnings[doc_type] = warns
            else:
                self.override_status[doc_type].configure(
                    text="Template inválido",
                    text_color=ERROR_BORDER,
                )
                self.session_overrides[doc_type] = None
            self._update_status()

    def _reset_override(self, doc_type: str):
        self.session_overrides[doc_type] = None
        self.override_status[doc_type].configure(
            text="Usando padrão", text_color=NEUTRAL_TEXT,
        )
        self._update_status()

    def reload_templates(self):
        """Reload templates from the configured folder."""
        folder = get_templates_folder()
        if not folder:
            self.template_paths = {k: None for k in self.template_paths}
            self.status_indicator.set_warning(
                "Pasta de templates não configurada — configure em Preferências"
            )
            self.detail_label.configure(text="")
            return

        found = check_templates_folder(folder)
        self.template_paths = found

        # Validate each found template
        self.warnings = {k: [] for k in self.template_paths}
        for doc_type, path in found.items():
            if path:
                is_valid, warns = validate_template(path, doc_type)
                if not is_valid:
                    self.template_paths[doc_type] = None
                self.warnings[doc_type] = warns

        self._update_status()

    def _update_status(self):
        """Update the status indicator based on current state."""
        active = self.get_active_templates()
        all_loaded = all(v is not None for v in active.values())
        any_override = any(v is not None for v in self.session_overrides.values())

        if all_loaded and not any_override:
            self.status_indicator.set_ok("Usando modelos padrão")
            self.detail_label.configure(text="")
        elif all_loaded:
            doc_names = {"procuracao": "Procuração", "declaracao": "Declaração", "contrato": "Contrato"}
            parts = []
            for dt, name in doc_names.items():
                if self.session_overrides[dt]:
                    parts.append(f"{name}: modelo personalizado")
                else:
                    parts.append(f"{name}: padrão")
            self.status_indicator.set_ok(" | ".join(parts))
            self.detail_label.configure(text="")
        else:
            missing = [dt for dt, path in active.items() if path is None]
            names = {"procuracao": "Procuração", "declaracao": "Declaração", "contrato": "Contrato"}
            missing_names = [names[m] for m in missing]
            self.status_indicator.set_warning(
                f"Templates faltando: {', '.join(missing_names)}"
            )
            self.detail_label.configure(
                text="Configure a pasta em Preferências ou carregue manualmente.",
                text_color=STATUS_WARN,
            )

        # Show warnings
        all_warns = []
        for doc_type, warns in self.warnings.items():
            names = {"procuracao": "Procuração", "declaracao": "Declaração", "contrato": "Contrato"}
            for w in warns:
                all_warns.append(f"{names[doc_type]}: {w}")
        if all_warns:
            current = self.detail_label.cget("text")
            warn_text = "\n".join(all_warns)
            if current:
                self.detail_label.configure(text=f"{current}\n{warn_text}")
            else:
                self.detail_label.configure(text=warn_text, text_color=STATUS_WARN)

    def get_active_templates(self) -> dict[str, str | None]:
        """Return the active template path for each document type.

        Session overrides take priority over defaults.
        """
        result = {}
        for doc_type in self.template_paths:
            override = self.session_overrides[doc_type]
            result[doc_type] = override if override else self.template_paths[doc_type]
        return result

    def is_template_available(self, doc_type: str) -> bool:
        """Check if a template is available for the given document type."""
        return self.get_active_templates().get(doc_type) is not None
