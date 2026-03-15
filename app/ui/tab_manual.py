"""Tab 3: Manual data entry form."""

import customtkinter as ctk

from app.ui.styles import *
from app.ui.components import StyledButton, StyledLabel, StyledEntry
from app.core.validators import normalize_name, normalize_cep
from app.models.cliente import Cliente


UF_LIST = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS",
    "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC",
    "SE", "SP", "TO",
]

FIELD_GROUPS = [
    ("Dados Pessoais", [
        ("nome_completo", "Nome Completo *", True),
        ("nacionalidade", "Nacionalidade *", True),
        ("estado_civil", "Estado Civil *", True),
        ("profissao", "Profissão *", True),
        ("rg", "RG *", True),
        ("cpf", "CPF *", True),
    ]),
    ("Endereço", [
        ("logradouro_numero", "Logradouro e Número *", True),
        ("complemento", "Complemento", False),
        ("bairro", "Bairro *", True),
        ("cidade", "Cidade *", True),
        ("uf", "UF *", True),
        ("cep", "CEP *", True),
    ]),
    ("Contato", [
        ("email", "E-mail *", True),
        ("telefone", "Telefone(s) *", True),
    ]),
    ("Dados do Caso", [
        ("parte_contraria", "Parte Contrária / Réu *", True),
        ("tipo_acao", "Tipo de Ação *", True),
    ]),
]

REQUIRED_FIELDS = {
    "nome_completo", "nacionalidade", "estado_civil", "profissao", "rg", "cpf",
    "logradouro_numero", "bairro", "cidade", "uf", "cep",
    "email", "telefone", "parte_contraria", "tipo_acao",
}


class TabManual(ctk.CTkFrame):
    """Manual data entry tab."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG_MAIN, **kwargs)

        self.field_entries: dict[str, ctk.CTkEntry | ctk.CTkComboBox] = {}

        # Scrollable form
        form = ctk.CTkScrollableFrame(self, fg_color=BG_MAIN, height=300)
        form.pack(fill="both", expand=True, padx=10, pady=5)

        for group_name, fields in FIELD_GROUPS:
            StyledLabel(form, text=group_name, is_title=True).pack(
                anchor="w", pady=(10, 2),
            )

            for field_name, label_text, required in fields:
                row = ctk.CTkFrame(form, fg_color=BG_MAIN)
                row.pack(fill="x", pady=2)

                ctk.CTkLabel(
                    row, text=label_text,
                    font=(FONT_FAMILY, FONT_SIZE_SMALL),
                    text_color=BODY_TEXT, width=180, anchor="w",
                ).pack(side="left")

                if field_name == "uf":
                    entry = ctk.CTkComboBox(
                        row, values=UF_LIST, width=100,
                        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                        fg_color=INPUT_BG, border_color=INPUT_BORDER,
                        text_color=BODY_TEXT, button_color=BTN_SECONDARY_BG,
                        dropdown_fg_color=INPUT_BG, dropdown_text_color=BODY_TEXT,
                    )
                    entry.set("")
                else:
                    entry = StyledEntry(row, width=400)
                entry.pack(side="left", fill="x", expand=True)
                self.field_entries[field_name] = entry

        # Clear button
        btn_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        btn_frame.pack(fill="x", padx=10, pady=5)
        StyledButton(
            btn_frame, text="Limpar", primary=False, width=80,
            command=self._clear_form,
        ).pack(side="left")

    def _clear_form(self):
        """Reset all form fields."""
        for field_name, entry in self.field_entries.items():
            if isinstance(entry, ctk.CTkComboBox):
                entry.set("")
            else:
                entry.delete(0, "end")
                if hasattr(entry, "set_error"):
                    entry.set_error(False)

    def get_client(self) -> Cliente:
        """Build a Cliente from the form fields."""
        values = {}
        for field_name, entry in self.field_entries.items():
            if isinstance(entry, ctk.CTkComboBox):
                values[field_name] = entry.get().strip()
            else:
                values[field_name] = entry.get().strip()

        return Cliente(
            nome_completo=normalize_name(values.get("nome_completo", "")),
            nacionalidade=values.get("nacionalidade", ""),
            estado_civil=values.get("estado_civil", ""),
            profissao=values.get("profissao", ""),
            rg=values.get("rg", ""),
            cpf=values.get("cpf", ""),
            logradouro_numero=values.get("logradouro_numero", ""),
            complemento=values.get("complemento", ""),
            bairro=values.get("bairro", ""),
            cidade=values.get("cidade", ""),
            uf=values.get("uf", ""),
            cep=normalize_cep(values.get("cep", "")),
            email=values.get("email", ""),
            telefone=values.get("telefone", ""),
            parte_contraria=values.get("parte_contraria", ""),
            tipo_acao=values.get("tipo_acao", ""),
        )

    def has_data(self) -> bool:
        """Check if all required fields are filled."""
        for field_name in REQUIRED_FIELDS:
            entry = self.field_entries.get(field_name)
            if entry:
                val = entry.get().strip() if not isinstance(entry, ctk.CTkComboBox) else entry.get().strip()
                if not val:
                    return False
        return True

    def validate_and_highlight(self) -> list[str]:
        """Validate fields and highlight errors. Returns list of missing field names."""
        missing = []
        for field_name in REQUIRED_FIELDS:
            entry = self.field_entries.get(field_name)
            if entry:
                val = entry.get().strip() if not isinstance(entry, ctk.CTkComboBox) else entry.get().strip()
                if not val:
                    if hasattr(entry, "set_error"):
                        entry.set_error(True)
                    missing.append(field_name)
                else:
                    if hasattr(entry, "set_error"):
                        entry.set_error(False)
        return missing
