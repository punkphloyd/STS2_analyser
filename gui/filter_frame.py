import customtkinter as ctk
from tkcalendar import DateEntry


class FilterFrame(ctk.CTkFrame):

    def __init__(
        self,
        master,
        on_character_changed,
        on_result_changed,
        on_min_ascension_changed,
        on_max_ascension_changed,
        on_date_changed,
        on_clear_filters,
        on_custom_dates_applied,
        on_exclude_daily_changed,
        on_exclude_custom_changed,
        on_game_version_changed
    ):
        super().__init__(master)

        self.on_character_changed = on_character_changed
        self.on_result_changed = on_result_changed
        self.on_min_ascension_changed = on_min_ascension_changed
        self.on_max_ascension_changed = on_max_ascension_changed
        self.on_date_changed = on_date_changed
        self.on_clear_filters = on_clear_filters
        self.on_custom_dates_applied = on_custom_dates_applied
        self.on_exclude_daily_changed = on_exclude_daily_changed
        self.on_exclude_custom_changed = on_exclude_custom_changed
        self.on_game_version_changed = on_game_version_changed

        # Custom date filter variables
        self.custom_date_frame = None
        self.from_date_entry = None
        self.to_date_entry = None

        self.build_ui()

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # ============================================================
        # Main filter controls
        # ============================================================

        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        filter_label = ctk.CTkLabel(
            controls_frame,
            text="Filters",
            font=("Segoe UI", 16, "bold")
        )
        filter_label.pack(
            side="left",
            padx=(10, 20)
        )

        character_label = ctk.CTkLabel(
            controls_frame,
            text="Character"
        )
        character_label.pack(
            side="left",
            padx=(0, 5)
        )

        self.character_combo = ctk.CTkComboBox(
            controls_frame,
            values=[
                "All",
                "Ironclad",
                "Silent",
                "Defect",
                "Regent",
                "Necrobinder"
            ],
            command=self.on_character_changed,
            width=130
        )
        self.character_combo.set("All")
        self.character_combo.pack(
            side="left",
            padx=(0, 15)
        )

        result_label = ctk.CTkLabel(
            controls_frame,
            text="Result"
        )
        result_label.pack(
            side="left",
            padx=(0, 5)
        )

        self.result_combo = ctk.CTkComboBox(
            controls_frame,
            values=[
                "All",
                "Wins",
                "Losses"
            ],
            command=self.on_result_changed,
            width=100
        )
        self.result_combo.set("All")
        self.result_combo.pack(
            side="left",
            padx=(0, 15)
        )

        ascension_label = ctk.CTkLabel(
            controls_frame,
            text="Ascension"
        )
        ascension_label.pack(
            side="left",
            padx=(0, 5)
        )

        self.min_ascension_combo = ctk.CTkComboBox(
            controls_frame,
            values=[str(i) for i in range(11)],
            width=60,
            command=self.on_min_ascension_changed
        )
        self.min_ascension_combo.set("0")
        self.min_ascension_combo.pack(
            side="left"
        )

        to_label = ctk.CTkLabel(
            controls_frame,
            text="to"
        )
        to_label.pack(
            side="left",
            padx=5
        )

        self.max_ascension_combo = ctk.CTkComboBox(
            controls_frame,
            values=[str(i) for i in range(11)],
            width=60,
            command=self.on_max_ascension_changed
        )
        self.max_ascension_combo.set("10")
        self.max_ascension_combo.pack(
            side="left",
            padx=(0, 15)
        )

        date_label = ctk.CTkLabel(
            controls_frame,
            text="Date"
        )
        date_label.pack(
            side="left",
            padx=(0, 5)
        )

        self.date_combo = ctk.CTkComboBox(
            controls_frame,
            values=[
                "All",
                "Last 7 days",
                "Last 30 days",
                "Last 90 days",
                "Last 365 days",
                "Custom..."
            ],
            command=self.on_date_changed,
            width=130
        )
        self.date_combo.set("All")
        self.date_combo.pack(
            side="left",
            padx=(0, 15)
        )

        clear_button = ctk.CTkButton(
            controls_frame,
            text="Clear Filters",
            command=self.on_clear_filters,
            width=110
        )
        clear_button.pack(
            side="left",
            padx=(0, 10)
        )

        # ============================================================
        # Run type (daily/standard etc) filter controls
        # ============================================================

        self.exclude_daily_checkbox = ctk.CTkCheckBox(
            controls_frame,
            text="Exclude Daily",
            command=self.on_exclude_daily_changed
        )
        self.exclude_daily_checkbox.pack(
            side="left",
            padx=(10, 10)
        )

        self.exclude_custom_checkbox = ctk.CTkCheckBox(
            controls_frame,
            text="Exclude Custom",
            command=self.on_exclude_custom_changed
        )
        self.exclude_custom_checkbox.pack(
            side="left",
            padx=(0, 10)
        )

        # ============================================================
        # Secondary frame for version filtering
        # ============================================================

        secondary_frame = ctk.CTkFrame(self)

        secondary_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(5,0)
        )

        game_version_label = ctk.CTkLabel(
            secondary_frame,
            text="Game Version"
        )
        game_version_label.pack(
            side="left",
            padx=(10, 5)
        )

        self.game_version_combo = ctk.CTkComboBox(
            secondary_frame,
            values=["All"],
            width=130,
            command=self.on_game_version_changed
        )
        self.game_version_combo.set("All")
        self.game_version_combo.pack(
            side="left",
            padx=(0, 10)
        )


        # ============================================================
        # Custom date controls
        # ============================================================

        self.custom_date_frame = ctk.CTkFrame(self)

        self.custom_date_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(5, 0)
        )

        self.custom_date_frame.grid_remove()

        from_label = ctk.CTkLabel(
            self.custom_date_frame,
            text="From"
        )
        from_label.pack(
            side="left",
            padx=(10, 5)
        )

        self.from_date_entry = DateEntry(
            self.custom_date_frame,
            width=12,
            date_pattern="dd/mm/yyyy"
        )
        self.from_date_entry.pack(
            side="left",
            padx=(0, 20)
        )

        to_label = ctk.CTkLabel(
            self.custom_date_frame,
            text="To"
        )
        to_label.pack(
            side="left",
            padx=(0, 5)
        )

        self.to_date_entry = DateEntry(
            self.custom_date_frame,
            width=12,
            date_pattern="dd/mm/yyyy"
        )
        self.to_date_entry.pack(
            side="left",
            padx=(0, 20)
        )

        apply_button = ctk.CTkButton(
            self.custom_date_frame,
            text="Apply",
            command=self.apply_custom_dates,
            width=80
        )
        apply_button.pack(
            side="left",
            padx=(0, 10)
        )
    # Functions to handle showing/hiding the custom date selection boxes
    def show_custom_dates(self):
        self.custom_date_frame.grid()

    def hide_custom_dates(self):
        self.custom_date_frame.grid_remove()

    def apply_custom_dates(self):
        self.on_custom_dates_applied(
            self.from_date_entry.get_date(),
            self.to_date_entry.get_date()
        )

    def set_game_versions(self, versions):

        values = ["All"] + versions

        self.game_version_combo.configure(
            values=values
        )

        self.game_version_combo.set("All")