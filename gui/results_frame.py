import customtkinter as ctk
from tkinter import ttk

from data_models.run_metadata import RunMetadata


class ResultsFrame(ctk.CTkFrame):

    def __init__(
        self,
        master,
        on_run_selected
    ):
        super().__init__(master)
        self.on_run_selected = on_run_selected
        self.run_lookup: dict[str, RunMetadata] = {}

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_ui()

    def build_ui(self):

        results_label = ctk.CTkLabel(
            self,
            text="Runs",
            font=("Segoe UI", 16, "bold")
        )
        results_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=(10, 0)
        )

        table_frame = ctk.CTkFrame(self)
        table_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=10
        )

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.results = ttk.Treeview(
            table_frame,
            columns=("date", "character", "ascension", "result", "game_version"),
            show="headings"
        )

        self.results.heading(
            "date",
            text="Date"
        )
        self.results.heading(
            "character",
            text="Character"
        )
        self.results.heading(
            "ascension",
            text="Ascension"
        )
        self.results.heading(
            "result",
            text="Result"
        )
        self.results.heading(
            "game_version",
            text="Game Version"
        )

        self.results.column(
            "date",
            width=150
        )
        self.results.column(
            "character",
            width=150
        )
        self.results.column(
            "ascension",
            width=100,
            anchor="center"
        )
        self.results.column(
            "result",
            width=100,
            anchor="center"
        )
        self.results.column(
            "game_version",
            width=110
        )

        self.results.bind(
            "<<TreeviewSelect>>",
            self.on_run_selected
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.results.yview
        )

        self.results.configure(
            yscrollcommand=scrollbar.set
        )

        self.results.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

    def set_runs(self, runs: list[RunMetadata]):

        self.clear()

        self.run_lookup = {
            str(run.file_path): run
            for run in runs
        }

        for run in runs:
            result = "Win" if run.victory else "Loss"

            self.results.insert(
                "",
                "end",
                iid=str(run.file_path),
                values=(
                    run.start_time.strftime("%Y-%m-%d"),
                    run.character,
                    run.ascension,
                    result
                )
            )

    def clear(self):

        for row in self.results.get_children():
            self.results.delete(row)

    def get_selected_run(self) -> RunMetadata | None:

        selected = self.results.selection()

        if not selected:
            return None

        return self.run_lookup.get(selected[0])