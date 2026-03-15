"""Tab 2: Parse qualification text from petição inicial."""

import customtkinter as ctk

from app.ui.styles import *
from app.ui.components import StyledButton, StyledLabel, StyledEntry, StyledTextbox, StatusIndicator
from app.core.parser import parse_qualificacao
from app.core.validators import validate_cpf, normalize_cep, normalize_name
from app.models.cliente import Cliente


# Fields that can be extracted from qualification text
EXTRACTABLE = {"nome_completo", "nacionalidade", "estado_civil", "rg", "cpf", "endereco"}

# Additional fields not in qualification text
MANUAL_FIELDS = [
    ("email", "E-mail *", True),
    ("telefone", "Telefone *", True),
    ("profissao", "Profissão *", True),
    ("parte_contraria", "Parte Contrária / Réu *", True),
    ("tipo_acao", "Tipo de Ação *", True),
]

REQUIRED_FIELDS = {
    "nome_completo", "nacionalidade", "estado_civil", "rg", "cpf",
    "logradouro_numero", "email", "telefone", "profissao",
    "parte_contraria", "tipo_acao",
}


class TabQualificacao(ctk.CTkFrame):
    """Qualification text parsing tab."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG_MAIN, **kwargs)

        self.field_entries: dict[str, StyledEntry] = {}
        self.extracted_fields: list[str] = []

        # Text input area
        StyledLabel(self, text="Cole o texto da qualificação:", is_title=False).pack(
            anchor="w", padx=10, pady=(10, 2),
        )
        self.text_input = StyledTextbox(self, height=100)
        self.text_input.pack(fill="x", padx=10, pady=(0, 5))

        btn_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        btn_frame.pack(fill="x", padx=10, pady=(0, 5))

        StyledButton(
            btn_frame, text="Processar texto", primary=True,
            command=self._parse_text, width=140,
        ).pack(side="left")

        StyledButton(
            btn_frame, text="Limpar", primary=False,
            command=self._clear_all, width=80,
        ).pack(side="left", padx=10)

        self.status = StatusIndicator(btn_frame)
        self.status.pack(side="left", padx=10)

        # Scrollable fields area
        self.fields_frame = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN, height=250)
        self.fields_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self._create_extracted_fields()
        self._create_manual_fields()

    def _create_extracted_fields(self):
        """Create fields for data extracted from qualification text."""
        StyledLabel(self.fields_frame, text="Dados extraídos", is_title=True).pack(
            anchor="w", pady=(5, 2),
        )

        extracted_defs = [
            ("nome_completo", "Nome Completo *"),
            ("nacionalidade", "Nacionalidade *"),
            ("estado_civil", "Estado Civil *"),
            ("rg", "RG *"),
            ("cpf", "CPF *"),
            ("logradouro_numero", "Endereço Completo *"),
        ]

        for field_name, label_text in extracted_defs:
            row = ctk.CTkFrame(self.fields_frame, fg_color=BG_MAIN)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                row, text=label_text, font=(FONT_FAMILY, FONT_SIZE_SMALL),
                text_color=BODY_TEXT, width=180, anchor="w",
            ).pack(side="left")
            entry = StyledEntry(row, width=400)
            entry.pack(side="left", fill="x", expand=True)
            self.field_entries[field_name] = entry

    def _create_manual_fields(self):
        """Create fields for data that must be entered manually."""
        StyledLabel(self.fields_frame, text="Campos adicionais (preencha manualmente)", is_title=True).pack(
            anchor="w", pady=(15, 2),
        )

        for field_name, label_text, required in MANUAL_FIELDS:
            row = ctk.CTkFrame(self.fields_frame, fg_color=BG_MAIN)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                row, text=label_text, font=(FONT_FAMILY, FONT_SIZE_SMALL),
                text_color=BODY_TEXT, width=180, anchor="w",
            ).pack(side="left")
            entry = StyledEntry(row, width=400)
            entry.pack(side="left", fill="x", expand=True)
            self.field_entries[field_name] = entry

    def _parse_text(self):
        """Parse the qualification text and populate fields."""
        text = self.text_input.get("1.0", "end").strip()
        if not text:
            self.status.set_warning("Cole o texto da qualificação primeiro")
            return

        cliente, extracted = parse_qualificacao(text)
        self.extracted_fields = extracted

        # Populate extracted fields
        field_map = {
            "nome_completo": cliente.nome_completo,
            "nacionalidade": cliente.nacionalidade,
            "estado_civil": cliente.estado_civil,
            "rg": cliente.rg,
            "cpf": cliente.cpf,
            "logradouro_numero": cliente.logradouro_numero,
        }

        for field_name, value in field_map.items():
            entry = self.field_entries[field_name]
            entry.delete(0, "end")
            if value:
                entry.insert(0, value)
                entry.set_error(False)
            else:
                entry.set_error(True)

        # Highlight manual fields in red
        for field_name, _, _ in MANUAL_FIELDS:
            self.field_entries[field_name].set_error(True)

        n_extracted = len(extracted)
        self.status.set_ok(f"{n_extracted} campo(s) extraído(s)")

    def _clear_all(self):
        """Clear all fields and text input."""
        self.text_input.delete("1.0", "end")
        for entry in self.field_entries.values():
            entry.delete(0, "end")
            entry.set_error(False)
        self.status.configure(text="")
        self.extracted_fields = []

    def get_client(self) -> Cliente | None:
        """Build a Cliente from the form fields. Returns None if required fields are missing."""
        values = {}
        for field_name, entry in self.field_entries.items():
            values[field_name] = entry.get().strip()

        return Cliente(
            nome_completo=normalize_name(values.get("nome_completo", "")),
            nacionalidade=values.get("nacionalidade", ""),
            estado_civil=values.get("estado_civil", ""),
            profissao=values.get("profissao", ""),
            rg=values.get("rg", ""),
            cpf=values.get("cpf", ""),
            logradouro_numero=values.get("logradouro_numero", ""),
            email=values.get("email", ""),
            telefone=values.get("telefone", ""),
            parte_contraria=values.get("parte_contraria", ""),
            tipo_acao=values.get("tipo_acao", ""),
        )

    def has_data(self) -> bool:
        """Check if required fields are filled."""
        for field_name in REQUIRED_FIELDS:
            entry = self.field_entries.get(field_name)
            if entry and not entry.get().strip():
                return False
        return True

    def validate_and_highlight(self) -> list[str]:
        """Validate fields and highlight errors. Returns list of missing field names."""
        missing = []
        for field_name in REQUIRED_FIELDS:
            entry = self.field_entries.get(field_name)
            if entry:
                if not entry.get().strip():
                    entry.set_error(True)
                    missing.append(field_name)
                else:
                    entry.set_error(False)
        return missing
