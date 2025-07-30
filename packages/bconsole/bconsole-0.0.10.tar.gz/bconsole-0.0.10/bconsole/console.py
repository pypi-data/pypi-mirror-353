from __future__ import annotations

from functools import partial
from getpass import getpass
from os import system as execute
from sys import stdin, stdout
from typing import Any, NoReturn, TextIO, overload

from unidecode import unidecode

from .core import (
    Erase,
    Foreground,
    Modifier,
)
from .utils import first, replace_last, surround_with

__all__ = ["Console"]


class Console:
    """A helper class to make better looking, and more consistent console output!"""

    @overload
    def __init__(
        self,
        file_out: TextIO = stdout,
        file_in: TextIO = stdin,
        *,
        prompt_color: str,
        input_color: str,
        arrow_color: str,
        error_color: str,
        hint_color: str,
        panic_color: str,
        arrow: str,
    ) -> None: ...

    @overload
    def __init__(
        self, file_out: TextIO = stdout, file_in: TextIO = stdin, **kwargs: str
    ) -> None: ...

    def __init__(
        self, file_out: TextIO = stdout, file_in: TextIO = stdin, **kwargs: str
    ) -> None:
        """
        Initializes a new instance of the Console class.

        ### Args:
            file_out (TextIO, optional): The file to write output to. Defaults to stdout.
            file_in (TextIO, optional): The file to read input from. Defaults to stdin.

        ### **kwargs:
            prompt_color (str, optional): The color to use for prompts. Defaults to Foreground.CYAN.
            input_color (str, optional): The color to use for input. Defaults to Modifier.RESET.
            arrow_color (str, optional): The color to use for arrows. Defaults to Foreground.GREEN + Modifier.BOLD.
            error_color (str, optional): The color to use for errors. Defaults to Foreground.RED.
            hint_color (str, optional): The color to use for hints. Defaults to Foreground.YELLOW.
            panic_color (str, optional): The color to use for panics. Defaults to Foreground.RED + Modifier.BOLD.
            arrow (str, optional): The arrow to use. Defaults to ">>".
        """
        self.file_out = file_out
        self.file_in = file_in

        self.prompt_color: str = kwargs.get("prompt_color", Foreground.CYAN)
        self.input_color: str = kwargs.get("input_color", Modifier.RESET)
        self.arrow_color: str = kwargs.get(
            "arrow_color", Foreground.GREEN + Modifier.BOLD
        )
        self.error_color: str = kwargs.get("error_color", Foreground.RED)
        self.hint_color: str = kwargs.get("hint_color", Foreground.YELLOW)
        self.panic_color: str = kwargs.get(
            "panic_color", Foreground.RED + Modifier.BOLD
        )
        self.arrow_ = kwargs.get("arrow", ">> ")

    def print(
        self,
        text: Any,
        color: str = Modifier.RESET,
        /,
        *,
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """
        Prints the specified text to the console with the specified color.

        ### Args:
            text (Any): The text to print.
            color (str, optional): The color to use. Defaults to Modifier.RESET.
            end (str, optional): The end to use. Defaults to "\n".
            flush (bool, optional): Whether to flush the output. Defaults to False.
        """
        self.file_out.write(
            f"{color}{str(text)}{Modifier.RESET}" + end,
        )

        if flush:
            self.file_out.flush()

    def input(
        self,
        prompt: str | None = None,
        /,
        *,
        invalid_values: list[str] | None = None,
        ensure_not_empty: bool = True,
        is_password: bool = False,
        allow_extras: bool = False,
    ) -> str:
        """
        Prompts the user for input with the specified prompt.

        ### Args:
            prompt (str): The prompt to display.
            invalid_values (list[str], optional): A list of invalid values. Defaults to None.
            ensure_not_empty (bool, optional): Whether to ensure the input is not empty. Defaults to True.
            is_password (bool, optional): Whether to hide the input. Defaults to False.
            allow_extras (bool, optional): Whether to allow extras, such as typing "clear" to clear the console, and "exit" to exit the program. Defaults to False.

        ### Returns:
            str: The user's input.
        """
        if prompt:
            self.print(prompt, self.prompt_color)
            self.arrow(flush=True)

        if is_password:
            res = getpass("")
        else:
            res = self.file_in.readline()

        res = res.strip()

        invalid_values = invalid_values or []

        if ensure_not_empty:
            invalid_values.append("")

        recur = partial(
            self.input,
            prompt,
            invalid_values=invalid_values,
            ensure_not_empty=ensure_not_empty,
            is_password=is_password,
            allow_extras=allow_extras,
        )

        match res:
            case "cls" | "clear" if allow_extras:
                self.clear()
                return recur()
            case "exit" | "quit" if allow_extras:
                exit(0)
            case res if res in invalid_values:
                self.error("Invalid value. Try again.")
                return recur()
            case _:
                return res

    def options(
        self,
        prompt: str,
        /,
        *,
        options: list[str] | None = None,
        wrapper: str | None = "[]",
        title: bool = True,
        format: bool = True,
        raw: bool = False,
    ) -> str:
        """
        Prompts the user to select an option from a list of options.

        ### Args:
            prompt (str): The prompt to display.
            options (list[str], optional): A list of options. Defaults to ["Yes", "No"].
            wrapper (str, optional): The wrapper to use around the options. Defaults to "[]". Example: "[x] or [y]". Can also be None or empty. Example: "x or y".
            title (bool, optional): Whether to make the first character in every option uppercase. Defaults to True.
            format (bool, optional): Whether to the two formatting options described above. Defaults to True.
            raw (bool, optional): Whether to return the user's input directly as opposed to the option selected from the options list. Defaults to False.

        ### Returns:
            str: The user's selection. Selected from the options list if raw is False, otherwise the user's input directly.
        """
        options = options or ["Yes", "No"]
        wrapper = wrapper or ""

        simplified_options = {unidecode(option).lower(): option for option in options}

        formatted_options = self._format_items(
            *[
                surround_with(option.title() if title else option, wrapper=wrapper)
                if format
                else option
                for option in options
            ]
        )

        while True:
            chosen = unidecode(self.input(f"{prompt} {formatted_options}.")).lower()

            possible_option = first(
                filter(
                    lambda option: option.startswith(chosen),
                    simplified_options.keys(),
                ),
                None,
            )

            if possible_option:
                original_option = simplified_options[possible_option]
                self.erase_lines()
                self.arrow(f"Chosen option: {original_option}", Foreground.MAGENTA)
                return chosen if raw else original_option

            self.error(
                "Invalid option.",
                hint=f"Choose one among the following options: {formatted_options}.",
            )

    def error(self, error: Exception | str, /, *, hint: str = "") -> None:
        """
        Prints an error message to the console.

        ### Args:
            error (Exception | str): The error to print.
            hint (str, optional): A hint to display. Defaults to "".
        """
        self.print(error, self.error_color)
        _ = hint and self.print(hint, self.hint_color)

    def panic(self, error: str, /, *, hint: str = "", code: int = -1) -> NoReturn:
        """
        Prints an error message to the console and exits the program with the specified code.

        ### Args:
            error (str): The error to print.
            hint (str, optional): A hint to display. Defaults to "".
            code (int, optional): The exit code. Defaults to -1.
        """
        self.error(error, hint=hint)
        self.enter_to_continue()
        exit(code)

    def arrow(
        self, text: str = "", color: str = Modifier.RESET, /, *, flush: bool = False
    ) -> None:
        """
        Prints an arrow to the console.

        ### Args:
            text (str, optional): The text to display after the arrow. Defaults to "".
            color (str, optional): The color to use. Defaults to Modifier.RESET.
            flush (bool, optional): Whether to flush the output. Defaults to False.
        """
        self.print(self.arrow_, self.arrow_color, end="", flush=flush)
        _ = text and self.print(text, color)

    def actions(self, *args: str) -> None:
        """
        Helper method to print multiple escape codes, joined by newlines.

        ### Args:
            *args (str): The escape codes to print.

        ### Example:
            >>> console.actions(*Erase.lines(2), Cursor.UP + Cursor.LEFT)
        """
        self.print("\n".join(args), end="")

    def enter_to_continue(self, text: str = "Press enter to continue...") -> None:
        """
        Prompts the user to press enter to continue.

        ### Args:
            text (str, optional): The text to display. Defaults to "Press enter to continue...".
        """
        self.input(text, ensure_not_empty=False, is_password=True)
        self.erase_lines(2)

    def space(self, count: int = 1, /) -> None:
        """
        Skips the specified number of lines.

        ### Args:
            count (int, optional): The number of lines to skip. Defaults to 1.
        """
        self.print("\n" * count, end="")

    def erase_lines(self, count: int = 1, /) -> None:
        """
        Erases the specified number of lines.

        ### Args:
            count (int, optional): The number of lines to erase. Defaults to 1.
        """
        self.actions(*Erase.lines(count))

    def clear(self) -> None:
        """Clears the console."""
        execute("cls||clear")

    def _format_items(
        self,
        *items: Any,
        sep: str = ", ",
        final_sep: str = " or ",
    ) -> str:
        """
        Formats a list of items into a string with the specified separator and final separator.

        ### Args:
            *items (Any): The items to format.
            sep (str, optional): The separator to use. Defaults to ", ".
            final_sep (str, optional): The final separator to use. Defaults to " or ".

        ### Returns:
            str: The formatted string.

        ### Example:
            >>> console._format_items("apple", "banana", "cherry")
            "apple, banana or cherry"
        """
        return replace_last(sep.join(map(str, items)), sep, final_sep)
