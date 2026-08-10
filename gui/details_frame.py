import customtkinter as ctk

from data_models.run_metadata import RunMetadata


class DetailsFrame(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.build_ui()

    def build_ui(self):

        details_label = ctk.CTkLabel(
            self,
            text="Run Details",
            font=("Segoe UI", 16, "bold")
        )
        details_label.pack(
            anchor="w",
            padx=10,
            pady=(10, 0)
        )

        self.date_label = ctk.CTkLabel(
            self,
            text="Date: -"
        )
        self.date_label.pack(
            anchor="w",
            padx=10
        )

        self.character_label = ctk.CTkLabel(
            self,
            text="Character: -"
        )
        self.character_label.pack(
            anchor="w",
            padx=10
        )

        self.ascension_label = ctk.CTkLabel(
            self,
            text="Ascension: -"
        )
        self.ascension_label.pack(
            anchor="w",
            padx=10
        )

        self.result_label = ctk.CTkLabel(
            self,
            text="Result: -"
        )
        self.result_label.pack(
            anchor="w",
            padx=10
        )

    def show_run(self, run: RunMetadata):

        self.date_label.configure(
            text=f"Date: {run.start_time:%Y-%m-%d}"
        )

        self.character_label.configure(
            text=f"Character: {run.character}"
        )

        self.ascension_label.configure(
            text=f"Ascension: {run.ascension}"
        )

        self.result_label.configure(
            text=f"Result: {'Victory' if run.victory else 'Defeat'}"
        )

    def clear(self):

        self.date_label.configure(
            text="Date: -"
        )

        self.character_label.configure(
            text="Character: -"
        )

        self.ascension_label.configure(
            text="Ascension: -"
        )

        self.result_label.configure(
            text="Result: -"
        )