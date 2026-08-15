import customtkinter as ctk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from plots.win_rate import (
    plot_overall_win_rate,
    plot_win_rate_by_character,
    plot_win_rate_by_ascension,
    plot_win_rate_by_character_and_ascension,
    plot_win_rate_over_time,
)


class PlotWindow(ctk.CTkToplevel):

    def __init__(
        self,
        master,
        runs,
        title="Quick Plot",
        plot_type="Win Rate"
    ):
        super().__init__(master)

        self.title(title)
        self.geometry("800x600")

        self.runs = runs
        self.figure = None
        self.canvas = None
        self.plot_type = plot_type
        self.build_ui()

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

    def build_ui(self):

        controls_frame = ctk.CTkFrame(self)
        controls_frame.pack(
            fill="x",
            padx=10,
            pady=(10, 0)
        )

        if self.plot_type == "Win Rate":
            view_label = ctk.CTkLabel(
                controls_frame,
                text="View:"
            )
            view_label.pack(
                side="left",
                padx=(10, 5)
            )

            self.view_combo = ctk.CTkComboBox(
                controls_frame,
                values=[
                    "Overall",
                    "By Character",
                    "By Ascension",
                    "By Character & Ascension",
                ],
                command=self.on_view_changed,
                width=200
            )
            self.view_combo.set("Overall")
            self.view_combo.pack(
                side="left",
                padx=(0, 10)
            )

        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        if self.plot_type == "Win Rate":
            self.update_plot("Overall")
        elif self.plot_type == "Win Rate Over Time":
            self.update_plot("Win Rate Over Time")

    def on_view_changed(self, value):

        self.update_plot(value)

    def update_plot(self, view):

        if view == "Overall":
            figure = plot_overall_win_rate(self.runs)

        elif view == "By Character":
            figure = plot_win_rate_by_character(self.runs)

        elif view == "By Ascension":
            figure = plot_win_rate_by_ascension(self.runs)

        elif view == "By Character & Ascension":
            figure = plot_win_rate_by_character_and_ascension(
                self.runs
            )
        elif view == "Win Rate Over Time":
            figure = plot_win_rate_over_time(self.runs)
        else:
            return

        if figure is None:
            return

        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()

        if self.figure is not None:
            self.figure.clear()

        self.figure = figure

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=self.plot_frame
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    def update_runs(self, runs):

        self.runs = runs

        if self.plot_type == "Win Rate":
            self.update_plot(self.view_combo.get())

        elif self.plot_type == "Win Rate Over Time":
            self.update_plot("Win Rate Over Time")

    def close(self):

        self.master.plot_window = None

        self.destroy()