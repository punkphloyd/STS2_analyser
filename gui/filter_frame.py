import customtkinter as ctk


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
        on_custom_dates_applied
    ):
        super().__init__(master)

        self.on_character_changed = on_character_changed
        self.on_result_changed = on_result_changed
        self.on_min_ascension_changed = on_min_ascension_changed
        self.on_max_ascension_changed = on_max_ascension_changed
        self.on_date_changed = on_date_changed
        self.on_clear_filters = on_clear_filters
        self.on_custom_dates_applied = on_custom_dates_applied

        # Custom date filter variables
        self.custom_date_frame = None
        self.from_date_entry = None
        self.to_date_entry = None

        self.build_ui()

    def build_ui(self):

        filter_label = ctk.CTkLabel(
            self,
            text="Filters",
            font=("Segoe UI", 16, "bold")
        )
        filter_label.pack(
            side="left",
            padx=(10, 20)
        )

        character_label = ctk.CTkLabel(
            self,
            text="Character"
        )
        character_label.pack(
            side="left",
            padx=(0, 5)
        )

        self.character_combo = ctk.CTkComboBox(
            self,
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
            self,
            text="Result"
        )
        result_label.pack(
            side="left",
            padx=(0, 5)
        )

        self.result_combo = ctk.CTkComboBox(
            self,
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
            self,
            text="Ascension"
        )
        ascension_label.pack(
            side="left",
            padx=(0, 5)
        )

        self.min_ascension_combo = ctk.CTkComboBox(
            self,
            values=[str(i) for i in range(11)],
            width=60,
            command=self.on_min_ascension_changed
        )
        self.min_ascension_combo.set("0")
        self.min_ascension_combo.pack(
            side="left"
        )

        to_label = ctk.CTkLabel(
            self,
            text="to"
        )
        to_label.pack(
            side="left",
            padx=5
        )

        self.max_ascension_combo = ctk.CTkComboBox(
            self,
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
            self,
            text="Date"
        )
        date_label.pack(
            side="left",
            padx=(0, 5)
        )

        self.date_combo = ctk.CTkComboBox(
            self,
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
            self,
            text="Clear Filters",
            command=self.on_clear_filters,
            width=110
        )
        clear_button.pack(
            side="left",
            padx=(0, 10)
        )

        self.custom_date_frame = ctk.CTkFrame(self)

        from_label = ctk.CTkLabel(
            self.custom_date_frame,
            text="From"
        )
        from_label.pack(
            side="left",
            padx=(10, 5)
        )

        self.from_date_entry = ctk.CTkEntry(
            self.custom_date_frame,
            width=120,
            placeholder_text="DD/MM/YYYY"
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

        self.to_date_entry = ctk.CTkEntry(
            self.custom_date_frame,
            width=120,
            placeholder_text="DD/MM/YYYY"
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
        self.custom_date_frame.pack(
            side="left",
            fill="x",
            padx=(0, 10)
        )

    def hide_custom_dates(self):
        self.custom_date_frame.pack_forget()

    def apply_custom_dates(self):
        self.on_custom_dates_applied(
            self.from_date_entry.get().strip(),
            self.to_date_entry.get().strip()
        )