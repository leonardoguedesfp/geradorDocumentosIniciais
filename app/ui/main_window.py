"""Main application window."""

import os
import locale
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.ui.styles import *
from app.ui.components import StyledButton, StyledLabel, StatusIndicator
from app.ui.section_templates import SectionTemplates
from app.ui.tab_excel import TabExcel
from app.ui.tab_qualificacao import TabQualificacao
from app.ui.tab_manual import TabManual
from app.ui.preferences_window import PreferencesWindow
from app.core.placeholder_engine import generate_document
from app.core.pdf_converter import convert_to_pdf
from app.core.validators import validate_cpf, normalize_cep, normalize_name, normalize_filename


MONTHS_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro",
}


def data_extenso() -> str:
    """Generate current date in Portuguese extended format."""
    today = date.today()
    return f"{today.day} de {MONTHS_PT[today.month]} de {today.year}"


DOC_TYPES = {
    "procuracao": "Procuração",
    "declaracao": "Declaração de Hipossuficiência",
    "contrato": "Contrato de Prestação de Serviços",
}

DOC_SUFFIXES = {
    "procuracao": "Procuracao",
    "declaracao": "Declaracao_Hipossuficiencia",
    "contrato": "Contrato",
}


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.title("Ricardo Passos Advocacia — Gerador de Documentos")
        self.geometry("900x750")
        self.configure(fg_color=BG_MAIN)
        self.minsize(800, 650)

        ctk.set_appearance_mode("light")

        self._create_header()
        self._create_template_section()
        self._create_data_tabs()
        self._create_generation_section()

    def _create_header(self):
        """Create the fixed header with firm name and gear icon."""
        header = ctk.CTkFrame(self, fg_color=HEADER_BG, corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="Ricardo Passos Advocacia",
            text_color=HEADER_FG,
            font=(FONT_FAMILY, FONT_SIZE_HEADER, "bold"),
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            header, text="Gerador de Documentos",
            text_color="#aec6d6",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        ).pack(side="left", padx=(0, 10))

        StyledButton(
            header, text="⚙ Preferências", primary=False, width=130,
            command=self._open_preferences,
        ).pack(side="right", padx=20)

    def _create_template_section(self):
        """Create template status section."""
        self.section_templates = SectionTemplates(self)
        self.section_templates.pack(fill="x", padx=10, pady=(10, 5))

    def _create_data_tabs(self):
        """Create the tabbed data input section."""
        StyledLabel(self, text="Fonte de Dados do Cliente", is_title=True).pack(
            anchor="w", padx=15, pady=(10, 2),
        )

        self.tabview = ctk.CTkTabview(
            self, fg_color=BG_MAIN,
            segmented_button_fg_color=NEUTRAL_TEXT,
            segmented_button_selected_color=BLUE_PRIMARY,
            segmented_button_selected_hover_color=HOVER_COLOR,
            segmented_button_unselected_color="#c5c2b9",
            segmented_button_unselected_hover_color="#b5b2a9",
            text_color=HEADER_FG,
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)

        tab1 = self.tabview.add("Excel / Forms")
        tab2 = self.tabview.add("Qualificação")
        tab3 = self.tabview.add("Manual")

        self.tab_excel = TabExcel(tab1)
        self.tab_excel.pack(fill="both", expand=True)

        self.tab_qualificacao = TabQualificacao(tab2)
        self.tab_qualificacao.pack(fill="both", expand=True)

        self.tab_manual = TabManual(tab3)
        self.tab_manual.pack(fill="both", expand=True)

    def _create_generation_section(self):
        """Create document selection, destination, and generate button."""
        gen_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        gen_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Document checkboxes
        StyledLabel(gen_frame, text="Documentos a gerar", is_title=True).pack(
            anchor="w", padx=5, pady=(5, 2),
        )

        cb_frame = ctk.CTkFrame(gen_frame, fg_color=BG_MAIN)
        cb_frame.pack(fill="x", padx=5)

        self.doc_vars = {}
        for doc_type, label in DOC_TYPES.items():
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(
                cb_frame, text=label, variable=var,
                font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                text_color=BODY_TEXT,
                fg_color=BLUE_PRIMARY,
                hover_color=HOVER_COLOR,
            )
            cb.pack(side="left", padx=(0, 20))
            self.doc_vars[doc_type] = (var, cb)

        # Destination selector
        dest_frame = ctk.CTkFrame(gen_frame, fg_color=BG_MAIN)
        dest_frame.pack(fill="x", padx=5, pady=(10, 5))

        StyledLabel(dest_frame, text="Destino:").pack(side="left")

        self.dest_var = ctk.StringVar(value="auto")
        ctk.CTkRadioButton(
            dest_frame, text="Automático", variable=self.dest_var, value="auto",
            font=(FONT_FAMILY, FONT_SIZE_SMALL), text_color=BODY_TEXT,
            fg_color=BLUE_PRIMARY, hover_color=HOVER_COLOR,
        ).pack(side="left", padx=(10, 5))

        ctk.CTkRadioButton(
            dest_frame, text="Escolher pasta", variable=self.dest_var, value="custom",
            font=(FONT_FAMILY, FONT_SIZE_SMALL), text_color=BODY_TEXT,
            fg_color=BLUE_PRIMARY, hover_color=HOVER_COLOR,
        ).pack(side="left", padx=5)

        self.custom_dest_btn = StyledButton(
            dest_frame, text="Selecionar...", primary=False, width=100,
            command=self._select_dest_folder,
        )
        self.custom_dest_btn.pack(side="left", padx=5)

        self.dest_label = ctk.CTkLabel(
            dest_frame, text="", font=(FONT_FAMILY, FONT_SIZE_SMALL),
            text_color=NEUTRAL_TEXT,
        )
        self.dest_label.pack(side="left", padx=5)

        self.custom_dest_path = ""

        # Progress bar
        self.progress = ctk.CTkProgressBar(gen_frame, fg_color="#d5d2c9", progress_color=GREEN_DARK)
        self.progress.pack(fill="x", padx=5, pady=5)
        self.progress.set(0)

        # Generate button and status
        bottom_frame = ctk.CTkFrame(gen_frame, fg_color=BG_MAIN)
        bottom_frame.pack(fill="x", padx=5, pady=(0, 5))

        self.generate_btn = StyledButton(
            bottom_frame, text="Gerar Documentos", primary=True, width=180, height=40,
            command=self._generate_documents,
        )
        self.generate_btn.pack(side="left")

        self.gen_status = StatusIndicator(bottom_frame)
        self.gen_status.pack(side="left", padx=15)

        self.open_folder_btn = StyledButton(
            bottom_frame, text="Abrir pasta", primary=False, width=110,
            command=self._open_output_folder,
        )
        self.open_folder_btn.pack(side="right")
        self.open_folder_btn.pack_forget()  # Hidden until generation completes

        self.last_output_dir = ""

    def _select_dest_folder(self):
        path = filedialog.askdirectory(title="Selecionar pasta de destino")
        if path:
            self.custom_dest_path = path
            self.dest_var.set("custom")
            self.dest_label.configure(text=path)

    def _open_preferences(self):
        PreferencesWindow(self, on_save_callback=self._on_preferences_saved)

    def _on_preferences_saved(self):
        self.section_templates.reload_templates()
        self._update_doc_checkboxes()

    def _update_doc_checkboxes(self):
        """Enable/disable document checkboxes based on template availability."""
        for doc_type, (var, cb) in self.doc_vars.items():
            available = self.section_templates.is_template_available(doc_type)
            if available:
                cb.configure(state="normal")
            else:
                cb.configure(state="disabled")
                var.set(False)

    def _get_output_dir(self) -> str:
        """Determine the output directory."""
        if self.dest_var.get() == "custom" and self.custom_dest_path:
            return self.custom_dest_path

        # Auto: use source dir for Excel, or user documents dir
        current_tab = self.tabview.get()
        if current_tab == "Excel / Forms" and self.tab_excel.get_source_dir():
            return self.tab_excel.get_source_dir()

        # Default to user documents
        docs = Path.home() / "Documents"
        if docs.exists():
            return str(docs)
        return str(Path.home())

    def _resolve_output_path(self, output_dir: str, name_normalized: str, doc_suffix: str, ext: str, used_names: set) -> str:
        """Resolve output path, handling duplicates with _v2, _v3... suffix."""
        base = f"{name_normalized}_{doc_suffix}"
        candidate = base
        version = 1
        while candidate in used_names:
            version += 1
            candidate = f"{base}_v{version}"
        used_names.add(candidate)
        return os.path.join(output_dir, f"{candidate}.{ext}")

    def _generate_documents(self):
        """Generate selected documents for the current data source."""
        # Determine which documents to generate
        selected_docs = [dt for dt, (var, _) in self.doc_vars.items() if var.get()]
        if not selected_docs:
            self.gen_status.set_warning("Selecione ao menos um documento para gerar")
            return

        # Check template availability
        active_templates = self.section_templates.get_active_templates()
        for dt in selected_docs:
            if active_templates.get(dt) is None:
                self.gen_status.set_warning(f"Template não disponível para {DOC_TYPES[dt]}")
                return

        # Get clients from current tab
        current_tab = self.tabview.get()
        clients = []

        if current_tab == "Excel / Forms":
            if not self.tab_excel.has_data():
                self.gen_status.set_warning("Selecione um arquivo Excel e ao menos um cliente")
                return
            clients = self.tab_excel.get_selected_clients()
        elif current_tab == "Qualificação":
            missing = self.tab_qualificacao.validate_and_highlight()
            if missing:
                self.gen_status.set_warning("Preencha os campos obrigatórios destacados")
                return
            client = self.tab_qualificacao.get_client()
            if client:
                clients = [client]
        elif current_tab == "Manual":
            missing = self.tab_manual.validate_and_highlight()
            if missing:
                self.gen_status.set_warning("Preencha os campos obrigatórios destacados")
                return
            clients = [self.tab_manual.get_client()]

        if not clients:
            self.gen_status.set_warning("Nenhum cliente para processar")
            return

        # CPF validation warnings
        for c in clients:
            if c.cpf and not validate_cpf(c.cpf):
                proceed = messagebox.askyesno(
                    "Aviso de CPF",
                    f"O CPF de {c.nome_completo} ({c.cpf}) parece inválido.\nDeseja continuar mesmo assim?",
                )
                if not proceed:
                    return

        output_dir = self._get_output_dir()
        os.makedirs(output_dir, exist_ok=True)

        date_str = data_extenso()
        total_tasks = len(clients) * len(selected_docs) * 2  # docx + pdf
        completed = 0
        successes = []
        failures = []
        used_names: set[str] = set()

        self.progress.set(0)
        self.generate_btn.configure(state="disabled")
        self.update_idletasks()

        for client in clients:
            # Normalize name
            client.nome_completo = normalize_name(client.nome_completo)
            if client.cep:
                client.cep = normalize_cep(client.cep)

            name_norm = normalize_filename(client.nome_completo)
            placeholders = client.to_placeholders(date_str)

            for doc_type in selected_docs:
                template_path = active_templates[doc_type]
                doc_suffix = DOC_SUFFIXES[doc_type]

                # Generate .docx
                docx_path = self._resolve_output_path(
                    output_dir, name_norm, doc_suffix, "docx", used_names,
                )
                try:
                    generate_document(template_path, placeholders, docx_path)
                    successes.append(docx_path)
                except Exception as e:
                    failures.append((f"{client.nome_completo} - {DOC_TYPES[doc_type]} (.docx)", str(e)))

                completed += 1
                self.progress.set(completed / total_tasks)
                self.update_idletasks()

                # Generate .pdf
                pdf_out = docx_path.replace(".docx", ".pdf")
                # Track the pdf name too
                pdf_base = os.path.splitext(os.path.basename(docx_path))[0]
                used_names.add(pdf_base)  # Already tracked via docx
                try:
                    convert_to_pdf(docx_path, output_dir)
                    pdf_path = os.path.join(output_dir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")
                    if os.path.exists(pdf_path):
                        successes.append(pdf_path)
                    else:
                        failures.append((f"{client.nome_completo} - {DOC_TYPES[doc_type]} (.pdf)", "PDF não gerado"))
                except Exception as e:
                    failures.append((f"{client.nome_completo} - {DOC_TYPES[doc_type]} (.pdf)", str(e)))

                completed += 1
                self.progress.set(completed / total_tasks)
                self.update_idletasks()

        self.progress.set(1)
        self.generate_btn.configure(state="normal")
        self.last_output_dir = output_dir

        # Show results
        if failures and successes:
            msg = f"Gerados: {len(successes)} arquivo(s)\nFalhas: {len(failures)}\n\n"
            msg += "Falhas:\n" + "\n".join(f"  • {name}: {err}" for name, err in failures)
            messagebox.showwarning("Geração parcial", msg)
            self.gen_status.set_warning(f"{len(successes)} gerado(s), {len(failures)} falha(s)")
        elif failures:
            msg = "Todas as gerações falharam:\n" + "\n".join(f"  • {name}: {err}" for name, err in failures)
            messagebox.showerror("Erro", msg)
            self.gen_status.set_error("Falha na geração")
        else:
            files_list = "\n".join(f"  • {os.path.basename(p)}" for p in successes)
            messagebox.showinfo("Sucesso", f"Documentos gerados com sucesso:\n{files_list}")
            self.gen_status.set_ok(f"{len(successes)} arquivo(s) gerado(s)")

        # Show "Open folder" button
        self.open_folder_btn.pack(side="right")

    def _open_output_folder(self):
        """Open the output folder in the system file manager."""
        if self.last_output_dir and os.path.isdir(self.last_output_dir):
            import subprocess, sys
            if sys.platform == "win32":
                os.startfile(self.last_output_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.last_output_dir])
            else:
                subprocess.Popen(["xdg-open", self.last_output_dir])
