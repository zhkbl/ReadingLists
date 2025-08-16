import tkinter as tk
import csv
import os
from typing import List, Dict


class BookTracker:
    """
    A GUI application to track books, either read or to-be-read.
    """

    def __init__(self, window: tk.Tk) -> None:
        """
        Initializes the BookTracker GUI.

        :param window: The Tkinter root window.
        """
        self._window: tk.Tk = window
        self._read_status: tk.StringVar = tk.StringVar(value="To Be Read")
        self._type_var: tk.StringVar = tk.StringVar()
        self._month_var: tk.StringVar = tk.StringVar(value="January")

        self._setup_gui()
        self._show_tbr_options()

    def _setup_gui(self) -> None:
        """Sets up the main GUI layout and top radio buttons."""
        # Top radio buttons for selecting book status
        top_frame = tk.Frame(self._window)
        top_frame.pack(pady=10)

        for text, cmd in [("Read", self._show_read_options), ("To Be Read", self._show_tbr_options)]:
            tk.Radiobutton(top_frame, text=text, variable=self._read_status, value=text, command=cmd).pack(side=tk.LEFT, padx=10)

        self._main_frame: tk.Frame = tk.Frame(self._window)
        self._main_frame.pack(padx=10, pady=10)

        self._message_label: tk.Label = tk.Label(self._main_frame, text="", fg="red")
        self._message_label.pack()

    def _show_read_options(self) -> None:
        """Displays the input fields for books that have been read."""
        self._clear_frame()
        self._add_common_fields()

        self._rating_entry: tk.Entry = self._add_labeled_entry("Rating (0-10):")
        self._genre_vars: Dict[str, tk.IntVar] = self._add_genre_checkboxes([
            "Sci-Fi", "Action", "Fantasy", "Mystery", "Thriller",
            "Horror", "Romance", "Drama", "YA", "Dystopian", "Crime",
            "Biography", "Memoir", "Self-Help", "Health", "Travel",
            "Business"
        ])
        self._add_dropdown("Month:", [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ], self._month_var)

        tk.Button(self._main_frame, text="Save", command=self._save_read_book).pack(pady=10)

    def _show_tbr_options(self) -> None:
        """Displays the input fields for books that are to be read."""
        self._clear_frame()
        self._add_common_fields()
        tk.Button(self._main_frame, text="Save", command=self._save_tbr_book).pack(pady=10)

    def _add_common_fields(self) -> None:
        """Adds input fields common to both read and to be read books."""
        self._title_entry: tk.Entry = self._add_labeled_entry("Title:")
        self._author_entry: tk.Entry = self._add_labeled_entry("Author:")

        type_frame = tk.Frame(self._main_frame)
        type_frame.pack(anchor="w")
        for text, val in [("Series", "Series"), ("Standalone", "Standalone")]:
            tk.Radiobutton(type_frame, text=text, variable=self._type_var, value=val).pack(side=tk.LEFT)

    def _add_labeled_entry(self, label_text: str) -> tk.Entry:
        """
        Adds a labeled text entry to the GUI.

        :param label_text: Text to display as the label.
        :return: The Entry widget created.
        """
        tk.Label(self._main_frame, text=label_text).pack(anchor="w")
        entry = tk.Entry(self._main_frame)
        entry.pack(fill=tk.X)
        return entry

    def _add_genre_checkboxes(self, genres: List[str]) -> Dict[str, tk.IntVar]:
        """
        Adds checkboxes for genres.

        :param genres: List of genre names.
        :return: Dictionary mapping genre name to its IntVar.
        """
        variables: Dict[str, tk.IntVar] = {genre: tk.IntVar() for genre in genres}
        for i in range(0, len(genres), 4):
            row = tk.Frame(self._main_frame)
            row.pack(anchor="w")
            for genre in genres[i:i + 4]:
                tk.Checkbutton(row, text=genre, variable=variables[genre]).pack(side=tk.LEFT)
        return variables

    def _add_dropdown(self, label: str, options: List[str], variable: tk.StringVar) -> None:
        """
        Adds a dropdown menu to the GUI.

        :param label: The label for the dropdown.
        :param options: List of options to display.
        :param variable: The StringVar linked to the selection.
        """
        tk.Label(self._main_frame, text=label).pack(anchor="w")
        tk.OptionMenu(self._main_frame, variable, *options).pack(fill=tk.X)

    def _save_read_book(self) -> None:
        """Validates input and saves a read book to CSV."""
        title = self._title_entry.get().strip()
        author = self._author_entry.get().strip()
        rating = self._rating_entry.get().strip()
        book_type = self._type_var.get()
        month = self._month_var.get()
        selected_genres = [g for g, var in self._genre_vars.items() if var.get()]

        # Input validation
        if not all([title, author, rating, book_type, month]):
            self._message_label.config(text="Fill in all fields.", fg="red")
            return
        try:
            rating_value = float(rating)
            if not (0 <= rating_value <= 10):
                raise ValueError
        except ValueError:
            self._message_label.config(text="Rating must be a number between 0 and 10.", fg="red")
            return

        self._save_csv("read_books.csv", [title, author, rating, book_type, ", ".join(selected_genres), month],
                       ["Title", "Author", "Rating", "Type", "Genres", "Month"])
        self._clear_entries()

    def _save_tbr_book(self) -> None:
        """Validates input and saves a to-be-read book to CSV."""
        title = self._title_entry.get().strip()
        author = self._author_entry.get().strip()
        book_type = self._type_var.get()

        if not all([title, author, book_type]):
            self._message_label.config(text="Fill in all fields.", fg="red")
            return

        self._save_csv("tbr.csv", [title, author, book_type], ["Title", "Author", "Type"])
        self._clear_entries()

    def _save_csv(self, filename: str, data: List[str], header: List[str]) -> None:
        """
        Saves data to a CSV file, creating the file and header if it doesn't exist.

        :param filename: CSV file name.
        :param data: List of values to write.
        :param header: CSV header row.
        """
        try:
            is_new_file = not os.path.exists(filename) or os.path.getsize(filename) == 0
            with open(filename, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if is_new_file:
                    writer.writerow(header)
                writer.writerow(data)
            self._message_label.config(text="Saved!", fg="green")
        except Exception as e:
            self._message_label.config(text=f"Error saving file: {e}", fg="red")

    def _clear_frame(self) -> None:
        """Clears all widgets from the main frame except the message label."""
        for widget in self._main_frame.winfo_children():
            if widget != self._message_label:
                widget.destroy()

    def _clear_entries(self) -> None:
        """Clears all input fields."""
        for entry in [self._title_entry, self._author_entry]:
            entry.delete(0, tk.END)
        self._type_var.set("")
        if hasattr(self, "_rating_entry"):
            self._rating_entry.delete(0, tk.END)
        if hasattr(self, "_genre_vars"):
            for var in self._genre_vars.values():
                var.set(0)
        self._month_var.set("January")