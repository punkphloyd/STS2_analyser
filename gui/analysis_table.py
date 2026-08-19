import customtkinter as ctk


class AnalysisTable(ctk.CTkFrame):

    def __init__(
        self,
        master,
        columns,
        rows,
        percentage_columns=None,
        column_weights=None,
    ):
        super().__init__(
            master,
            fg_color="#D9E2EC",
            corner_radius=8,
        )

        if percentage_columns is None:
            percentage_columns = set()

        self.columns = columns
        self.rows = rows
        self.percentage_columns = percentage_columns
        self.column_weights = column_weights

        self.build_table()

    def build_table(self):

        weights = self.get_column_weights()

        for column, weight in enumerate(weights):
            self.grid_columnconfigure(
                column,
                weight=weight,
            )

        self.build_header(weights)

        for row_index, row in enumerate(
            self.rows,
            start=1,
        ):
            self.build_row(
                row_index,
                row,
                weights,
            )

    def get_column_weights(self):

        if self.column_weights is not None:
            return self.column_weights

        if len(self.columns) == 4:
            return [
                1,
                4,
                1,
                2,
            ]

        return [
            3,
            1,
            1,
            1,
            1,
            1,
        ]

    def build_header(self, weights):

        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        header_frame.grid(
            row=0,
            column=0,
            columnspan=len(self.columns),
            sticky="ew",
        )

        for column, heading in enumerate(
            self.columns
        ):

            anchor = (
                "w"
                if column == 0
                else "e"
            )

            label = ctk.CTkLabel(
                header_frame,
                text=heading,
                font=ctk.CTkFont(
                    size=13,
                    weight="bold",
                ),
                anchor=anchor,
                text_color="#202020",
            )

            label.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=10,
                pady=8,
            )

            header_frame.grid_columnconfigure(
                column,
                weight=weights[column],
            )

    def build_row(
        self,
        row_index,
        row,
        weights,
    ):

        background = (
            "#EAF2F8"
            if row_index % 2 == 0
            else "#F5F5F5"
        )

        row_frame = ctk.CTkFrame(
            self,
            fg_color=background,
            corner_radius=0,
        )

        row_frame.grid(
            row=row_index,
            column=0,
            columnspan=len(self.columns),
            sticky="ew",
        )

        for column, value in enumerate(row):

            text = self.format_value(
                column,
                value,
            )

            anchor = (
                "w"
                if column == 0
                else "e"
            )

            label = ctk.CTkLabel(
                row_frame,
                text=text,
                anchor=anchor,
                text_color="#202020",
            )

            label.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=10,
                pady=6,
            )

            row_frame.grid_columnconfigure(
                column,
                weight=weights[column],
            )

    def format_value(
        self,
        column,
        value,
    ):

        if (
            column in self.percentage_columns
            and isinstance(value, (int, float))
        ):
            return f"{value:.1%}"

        if isinstance(value, float):
            return f"{value:.1f}"

        return str(value)