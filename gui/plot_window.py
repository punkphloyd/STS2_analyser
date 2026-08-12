import customtkinter as ctk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PlotWindow(ctk.CTkToplevel):

    def __init__(
        self,
        master,
        figure,
        title="Quick Plot"
    ):
        super().__init__(master)

        self.title(title)
        self.geometry("800x600")

        self.figure = figure

        self.build_ui()

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

    def build_ui(self):

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=self
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    def close(self):
        self.destroy()