import customtkinter as ctk


class QuickPlotsFrame(ctk.CTkFrame):

    def __init__(
        self,
        master,
        on_plot
    ):
        super().__init__(master)

        self.on_plot = on_plot

        self.build_ui()

    def build_ui(self):

        quick_plots_label = ctk.CTkLabel(
            self,
            text="Quick Plots",
            font=("Segoe UI", 16, "bold")
        )
        quick_plots_label.pack(
            side="left",
            padx=(10, 20)
        )

        self.plot_combo = ctk.CTkComboBox(
            self,
            values=[
                "Win Rate"
            ],
            width=150
        )
        self.plot_combo.set("Win Rate")
        self.plot_combo.pack(
            side="left",
            padx=(0, 10)
        )

        plot_button = ctk.CTkButton(
            self,
            text="Plot",
            command=self.on_plot,
            width=80
        )
        plot_button.pack(
            side="left",
            padx=(0, 10)
        )