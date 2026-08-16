import customtkinter as ctk

from analysis.relic_analysis import calculate_neow_relic_statistics
from data_models.run_data import RunData


class AnalysisWindow(ctk.CTkToplevel):

    def __init__(
        self,
        master,
        runs: list[RunData],
        title="Neow's Bonus Relic Analysis",
    ):
        super().__init__(master)

        self.title(title)
        self.geometry("950x650")
        self.minsize(800, 500)

        self.runs = runs

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

        self.build_ui()

    def build_ui(self):

        # ============================================================
        # Header
        # ============================================================

        header_frame = ctk.CTkFrame(
            self,
            corner_radius=10
        )
        header_frame.pack(
            fill="x",
            padx=15,
            pady=(15, 10)
        )

        title_label = ctk.CTkLabel(
            header_frame,
            text="Neow's Bonus Relics",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )
        title_label.pack(
            anchor="w",
            padx=20,
            pady=(15, 2)
        )

        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text=f"{len(self.runs)} runs analysed",
            font=ctk.CTkFont(size=14)
        )

        self.subtitle_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        # ============================================================
        # Table
        # ============================================================

        self.table_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=10,
            fg_color="#F2F3F5"
        )
        self.table_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.build_table()

    def build_table(self):

        statistics = calculate_neow_relic_statistics(
            self.runs
        )

        headers = [
            "Relic",
            "Offered",
            "Picked",
            "Pick Rate",
            "Wins",
            "Win Rate",
        ]

        # Shared column configuration.
        # The first column gets more space for relic names.
        column_weights = [
            3,
            1,
            1,
            2,
            1,
            2,
        ]

        # ============================================================
        # Header
        # ============================================================

        header_frame = ctk.CTkFrame(
            self.table_frame,
            corner_radius=6,
            fg_color="#D9E6F2"
        )
        header_frame.grid(
            row=0,
            column=0,
            columnspan=len(headers),
            sticky="ew",
            padx=5,
            pady=(5, 5)
        )

        for column, weight in enumerate(column_weights):
            header_frame.grid_columnconfigure(
                column,
                weight=weight
            )

        for column, header in enumerate(headers):

            label = ctk.CTkLabel(
                header_frame,
                text=header,
                text_color="#263746",
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                ),
                anchor="w" if column == 0 else "center"
            )

            label.grid(
                row=0,
                column=column,
                padx=15,
                pady=10,
                sticky="ew"
            )

        # ============================================================
        # Rows
        # ============================================================

        for row, (relic, stats) in enumerate(
            statistics.items(),
            start=1
        ):

            if row % 2 == 0:
                row_colour = "#E8EEF3"
            else:
                row_colour = "#F7F8F9"

            row_frame = ctk.CTkFrame(
                self.table_frame,
                corner_radius=5,
                fg_color=row_colour
            )
            row_frame.grid(
                row=row,
                column=0,
                columnspan=len(headers),
                sticky="ew",
                padx=5,
                pady=2
            )

            for column, weight in enumerate(column_weights):
                row_frame.grid_columnconfigure(
                    column,
                    weight=weight
                )

            values = [
                self.format_relic_name(relic),
                stats.offered,
                stats.picks,
                f"{stats.pick_rate:.1%}",
                stats.wins,
                (
                    f"{stats.win_rate:.1%}"
                    if stats.win_rate is not None
                    else "N/A"
                ),
            ]

            for column, value in enumerate(values):

                label = ctk.CTkLabel(
                    row_frame,
                    text=str(value),
                    text_color="#263746",
                    font=ctk.CTkFont(
                        size=13,
                        weight="bold" if column == 0 else "normal"
                    ),
                    anchor="w" if column == 0 else "center"
                )

                label.grid(
                    row=0,
                    column=column,
                    padx=15,
                    pady=9,
                    sticky="ew"
                )

    @staticmethod
    def format_relic_name(relic: str) -> str:
        return relic.replace("_", " ").title()

    def update_runs(self, runs: list[RunData]):

        self.runs = runs

        self.subtitle_label.configure(
            text=f"{len(self.runs)} runs analysed"
        )

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        self.build_table()

    def close(self):
        self.destroy()