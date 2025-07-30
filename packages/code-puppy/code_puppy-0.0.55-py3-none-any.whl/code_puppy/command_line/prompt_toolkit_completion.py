import os
from code_puppy.command_line.utils import list_directory
from code_puppy.config import get_puppy_name, get_config_keys, get_value

# ANSI color codes are no longer necessary because prompt_toolkit handles
# styling via the `Style` class. We keep them here commented-out in case
# someone needs raw ANSI later, but they are unused in the current code.
# RESET = '\033[0m'
# GREEN = '\033[1;32m'
# CYAN = '\033[1;36m'
# YELLOW = '\033[1;33m'
# BOLD = '\033[1m'
import asyncio
from typing import Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.completion import merge_completers
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

from code_puppy.command_line.model_picker_completion import (
    ModelNameCompleter,
    get_active_model,
    update_model_in_input,
)
from code_puppy.command_line.file_path_completion import FilePathCompleter

from prompt_toolkit.completion import Completer, Completion


class SetCompleter(Completer):
    def __init__(self, trigger: str = "~set"):
        self.trigger = trigger

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not text.strip().startswith(self.trigger):
            return
        # If the only thing typed is exactly '~set', suggest space
        if text.strip() == self.trigger:
            yield Completion(
                self.trigger + " ",
                start_position=-len(self.trigger),
                display=f"{self.trigger} ",
                display_meta="set config",
            )
        tokens = text.strip().split()
        # completion for the first arg after ~set
        if len(tokens) == 1:
            # user just typed ~set <-- suggest config keys
            base = ""
        else:
            base = tokens[1]
        # --- SPECIAL HANDLING FOR 'model' KEY ---
        if base == "model":
            # Don't return any completions -- let ModelNameCompleter handle it
            return
        for key in get_config_keys():
            if key == "model":
                continue  # exclude 'model' from regular ~set completions
            if key.startswith(base):
                prev_value = get_value(key)
                # Ensure there's a space after '~set' if it's the only thing typed
                if text.strip() == self.trigger or text.strip() == self.trigger + "":
                    prefix = self.trigger + " "  # Always enforce a space
                    insert_text = (
                        f"{prefix}{key} = {prev_value}"
                        if prev_value is not None
                        else f"{prefix}{key} = "
                    )
                    sp = -len(text)
                else:
                    insert_text = (
                        f"{key} = {prev_value}"
                        if prev_value is not None
                        else f"{key} = "
                    )
                    sp = -len(base)
                # Make it obvious the value part is from before
                yield Completion(
                    insert_text,
                    start_position=sp,
                    display_meta=f"puppy.cfg key (was: {prev_value})"
                    if prev_value is not None
                    else "puppy.cfg key",
                )


class CDCompleter(Completer):
    def __init__(self, trigger: str = "~cd"):
        self.trigger = trigger

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not text.strip().startswith(self.trigger):
            return
        tokens = text.strip().split()
        if len(tokens) == 1:
            base = ""
        else:
            base = tokens[1]
        try:
            prefix = os.path.expanduser(base)
            part = os.path.dirname(prefix) if os.path.dirname(prefix) else "."
            dirs, _ = list_directory(part)
            dirnames = [d for d in dirs if d.startswith(os.path.basename(base))]
            base_dir = os.path.dirname(base)
            for d in dirnames:
                # Build the completion text so we keep the already-typed directory parts.
                if base_dir and base_dir != ".":
                    suggestion = os.path.join(base_dir, d)
                else:
                    suggestion = d
                # Append trailing slash so the user can continue tabbing into sub-dirs.
                suggestion = suggestion.rstrip(os.sep) + os.sep
                yield Completion(
                    suggestion,
                    start_position=-len(base),
                    display=d + os.sep,
                    display_meta="Directory",
                )
        except Exception:
            # Silently ignore errors (e.g., permission issues, non-existent dir)
            pass


def get_prompt_with_active_model(base: str = ">>> "):
    puppy = get_puppy_name()
    model = get_active_model() or "(default)"
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd.startswith(home):
        cwd_display = "~" + cwd[len(home) :]
    else:
        cwd_display = cwd
    return FormattedText(
        [
            ("bold", "🐶 "),
            ("class:puppy", f"{puppy}"),
            ("", " "),
            ("class:model", "[" + str(model) + "] "),
            ("class:cwd", "(" + str(cwd_display) + ") "),
            ("class:arrow", str(base)),
        ]
    )


async def get_input_with_combined_completion(
    prompt_str=">>> ", history_file: Optional[str] = None
) -> str:
    history = FileHistory(history_file) if history_file else None
    completer = merge_completers(
        [
            FilePathCompleter(symbol="@"),
            ModelNameCompleter(trigger="~m"),
            CDCompleter(trigger="~cd"),
            SetCompleter(trigger="~set"),
        ]
    )
    # Add custom key bindings for Alt+M to insert a new line without submitting
    bindings = KeyBindings()

    @bindings.add(Keys.Escape, "m")  # Alt+M
    def _(event):
        event.app.current_buffer.insert_text("\n")

    @bindings.add(Keys.Escape)
    def _(event):
        """Cancel the current prompt when the user presses the ESC key alone."""
        event.app.exit(exception=KeyboardInterrupt)

    session = PromptSession(
        completer=completer,
        history=history,
        complete_while_typing=True,
        key_bindings=bindings,
    )
    # If they pass a string, backward-compat: convert it to formatted_text
    if isinstance(prompt_str, str):
        from prompt_toolkit.formatted_text import FormattedText

        prompt_str = FormattedText([(None, prompt_str)])
    style = Style.from_dict(
        {
            # Keys must AVOID the 'class:' prefix – that prefix is used only when
            # tagging tokens in `FormattedText`. See prompt_toolkit docs.
            "puppy": "bold magenta",
            "owner": "bold white",
            "model": "bold cyan",
            "cwd": "bold green",
            "arrow": "bold yellow",
        }
    )
    text = await session.prompt_async(prompt_str, style=style)
    possibly_stripped = update_model_in_input(text)
    if possibly_stripped is not None:
        return possibly_stripped
    return text


if __name__ == "__main__":
    print("Type '@' for path-completion or '~m' to pick a model. Ctrl+D to exit.")

    async def main():
        while True:
            try:
                inp = await get_input_with_combined_completion(
                    get_prompt_with_active_model(),
                    history_file="~/.path_completion_history.txt",
                )
                print(f"You entered: {inp}")
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
        print("\nGoodbye!")

    asyncio.run(main())
