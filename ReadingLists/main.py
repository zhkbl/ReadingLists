import tkinter as tk
from gui import BookTracker


def main() -> None:

    window = tk.Tk()
    window.title("Reading Lists")
    window.geometry("500x510")
    app = BookTracker(window)
    window.mainloop()


if __name__ == "__main__":
    main()