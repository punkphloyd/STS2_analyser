import customtkinter as ctk

from analysis.combat_analysis import (
    calculate_encounter_statistics,
)
from data_models.run_data import RunData
from gui.analysis_table import AnalysisTable
from gui.formatters import format_encounter_name


class CombatAnalysisWindow(ctk.CTkToplevel):

    def __init__(
        self,
        master,
        runs: list[RunData],
    ):
        super().__init__(master)

        self.title("Combat Analysis")
        self.geometry("1450x750")
        self.minsize(1100, 600)

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
            fg_color="transparent"
        )
        header_frame.pack(
            fill="x",
            padx=20,
            pady=(20, 0)
        )

        title_label = ctk.CTkLabel(
            header_frame,
            text="Combat Analysis",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )
        title_label.pack(
            anchor="w"
        )

        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text=self.get_run_summary(),
            font=ctk.CTkFont(size=14)
        )
        self.subtitle_label.pack(
            anchor="w",
            pady=(0, 15)
        )

        # ============================================================
        # Controls
        # ============================================================

        controls_frame = ctk.CTkFrame(self)
        controls_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 10)
        )

        act_label = ctk.CTkLabel(
            controls_frame,
            text="Act:"
        )
        act_label.pack(
            side="left",
            padx=(10, 5)
        )

        self.act_combo = ctk.CTkComboBox(
            controls_frame,
            values=[
                "All",
                "Act 1",
                "Act 2",
                "Act 3",
            ],
            command=self.on_filter_changed,
            width=140
        )
        self.act_combo.set("All")
        self.act_combo.pack(
            side="left",
            padx=(0, 20)
        )

        encounter_type_label = ctk.CTkLabel(
            controls_frame,
            text="Monster Type:"
        )
        encounter_type_label.pack(
            side="left",
            padx=(0, 5)
        )

        self.encounter_type_combo = ctk.CTkComboBox(
            controls_frame,
            values=[
                "All",
                "Normal",
                "Elite",
                "Boss",
            ],
            command=self.on_filter_changed,
            width=140
        )
        self.encounter_type_combo.set("All")
        self.encounter_type_combo.pack(
            side="left",
            padx=(0, 10)
        )

        # ============================================================
        # Table
        # ============================================================

        self.table_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=10,
        )
        self.table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.build_table()

    def get_run_summary(self):

        return (
            f"{len(self.runs)} runs available for analysis"
        )

    def on_filter_changed(self, _value=None):

        self.build_table()

    def get_selected_act(self):

        value = self.act_combo.get()

        if value == "All":
            return None

        return int(
            value.replace("Act ", "")
        )

    def get_selected_encounter_type(self):

        value = self.encounter_type_combo.get()

        if value == "All":
            return None

        mapping = {
            "Normal": "monster",
            "Elite": "elite",
            "Boss": "boss",
        }

        return mapping[value]

    def build_table(self):

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        statistics = calculate_encounter_statistics(
            self.runs,
            act=self.get_selected_act(),
            encounter_type=(
                self.get_selected_encounter_type()
            ),
        )

        if not statistics:
            self.build_empty_message(
                "No combat encounters match the selected filters."
            )
            return

        columns = [
            "Encounter",
            "Type",
            "Fights",
            "Wins",
            "Win Rate",
            "Avg Damage",
            "Median Damage",
            "Min Damage",
            "Max Damage",
            "Avg Turns",
            "Min Turns",
            "Max Turns",
            "Avg Dmg / Turn",
        ]

        rows = []

        for encounter, stats in sorted(
            statistics.items(),
            key=lambda item: (
                item[1].encounter_type,
                item[0],
            )
        ):

            rows.append(
                (
                    format_encounter_name(encounter),
                    self.format_encounter_type(
                        stats.encounter_type
                    ),
                    stats.fights,
                    stats.wins,
                    stats.win_rate,
                    stats.average_damage,
                    stats.median_damage,
                    stats.minimum_damage,
                    stats.maximum_damage,
                    stats.average_turns,
                    stats.minimum_turns,
                    stats.maximum_turns,
                    stats.average_damage_per_turn,
                )
            )

        table = AnalysisTable(
            self.table_frame,
            columns,
            rows,
            percentage_columns={4},
            column_weights=[
                3,  # Encounter
                2,  # Type
                1,  # Fights
                1,  # Wins
                2,  # Win Rate
                2,  # Avg Damage
                2,  # Median Damage
                2,  # Min Damage
                2,  # Max Damage
                2,  # Avg Turns
                1,  # Min Turns
                1,  # Max Turns
                2,  # Avg Damage / Turn
            ],
        )

        table.pack(
            fill="x",
            expand=True,
        )

    @staticmethod
    def format_encounter_type(
        encounter_type: str,
    ) -> str:

        mapping = {
            "monster": "Normal",
            "elite": "Elite",
            "boss": "Boss",
        }

        return mapping.get(
            encounter_type,
            encounter_type.title(),
        )

    def build_empty_message(self, text):

        label = ctk.CTkLabel(
            self.table_frame,
            text=text,
            font=ctk.CTkFont(size=14)
        )

        label.pack(
            pady=30
        )

    def update_runs(self, runs: list[RunData]):

        self.runs = runs

        self.subtitle_label.configure(
            text=self.get_run_summary()
        )

        self.build_table()

    def close(self):

        self.destroy()