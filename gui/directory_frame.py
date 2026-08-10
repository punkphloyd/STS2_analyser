import customtkinter as ctk


class DirectoryFrame(ctk.CTkFrame):

    def __init__(
        self,
        master,
        directory,
        on_browse
    ):
        super().__init__(master)

        self.directory = directory
        self.on_browse = on_browse

        self.build_ui()

    def build_ui(self):

        self.grid_columnconfigure(0, weight=1)

        directory_label = ctk.CTkLabel(
            self,
            text="Run directory"
        )
        directory_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=15,
            pady=(15, 5)
        )

        directory_entry = ctk.CTkEntry(
            self,
            textvariable=self.directory
        )
        directory_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(15, 10),
            pady=(0, 15)
        )

        browse_button = ctk.CTkButton(
            self,
            text="Browse...",
            command=self.on_browse,
            width=120
        )
        browse_button.grid(
            row=1,
            column=1,
            padx=(0, 15),
            pady=(0, 15)
        )