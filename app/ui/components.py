"""Reusable UI components for the application."""

import customtkinter as ctk
from app.ui.styles import *


class StyledButton(ctk.CTkButton):
    """Primary styled button."""

    def __init__(self, master, text="", command=None, primary=True, **kwargs):
        bg = BTN_PRIMARY_BG if primary else BTN_SECONDARY_BG
        fg = BTN_PRIMARY_FG if primary else BTN_SECONDARY_FG
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=bg,
            text_color=fg,
            hover_color=HOVER_COLOR,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            corner_radius=6,
            **kwargs,
        )


class StyledEntry(ctk.CTkEntry):
    """Styled text entry field."""

    def __init__(self, master, placeholder="", **kwargs):
        super().__init__(
            master,
            placeholder_text=placeholder,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=BODY_TEXT,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            corner_radius=4,
            **kwargs,
        )

    def set_error(self, error=True):
        self.configure(border_color=ERROR_BORDER if error else INPUT_BORDER)


class StyledLabel(ctk.CTkLabel):
    """Styled label."""

    def __init__(self, master, text="", is_title=False, **kwargs):
        font_size = FONT_SIZE_TITLE if is_title else FONT_SIZE_NORMAL
        color = SECTION_TITLE if is_title else BODY_TEXT
        weight = "bold" if is_title else "normal"
        super().__init__(
            master,
            text=text,
            text_color=color,
            font=(FONT_FAMILY, font_size, weight),
            **kwargs,
        )


class StyledTextbox(ctk.CTkTextbox):
    """Styled multiline text box."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=BODY_TEXT,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            corner_radius=4,
            border_width=1,
            **kwargs,
        )


class StatusIndicator(ctk.CTkLabel):
    """Status indicator with colored text."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            text="",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            **kwargs,
        )

    def set_ok(self, text: str):
        self.configure(text=f"✔ {text}", text_color=STATUS_OK)

    def set_warning(self, text: str):
        self.configure(text=f"⚠ {text}", text_color=STATUS_WARN)

    def set_error(self, text: str):
        self.configure(text=f"✖ {text}", text_color=ERROR_BORDER)


class ScrollableCheckboxFrame(ctk.CTkScrollableFrame):
    """Scrollable frame with checkboxes for selecting items."""

    def __init__(self, master, items=None, **kwargs):
        super().__init__(master, fg_color=INPUT_BG, **kwargs)
        self.checkboxes = []
        self.variables = []
        if items:
            self.set_items(items)

    def set_items(self, items: list[str]):
        for cb in self.checkboxes:
            cb.destroy()
        self.checkboxes.clear()
        self.variables.clear()
        for item in items:
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(
                self,
                text=item,
                variable=var,
                font=(FONT_FAMILY, FONT_SIZE_SMALL),
                text_color=BODY_TEXT,
                fg_color=BLUE_PRIMARY,
                hover_color=HOVER_COLOR,
            )
            cb.pack(anchor="w", padx=5, pady=2)
            self.checkboxes.append(cb)
            self.variables.append(var)

    def get_selected_indices(self) -> list[int]:
        return [i for i, var in enumerate(self.variables) if var.get()]

    def select_all(self):
        for var in self.variables:
            var.set(True)

    def deselect_all(self):
        for var in self.variables:
            var.set(False)
