import subprocess
from datetime import datetime
from pathlib import Path
from typing import override

import pyperclip
import typer
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, RichLog, TextArea

CONVO_FILE = Path("conversation.txt")


def encrypt_message(plaintext: str, recipient: str) -> str:
    """Encrypt message using GPG"""
    proc = subprocess.run(
        ["gpg", "-aesr", recipient],
        input=plaintext.encode(),
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode())
    return proc.stdout.decode()


def decrypt_message(ciphertext: str) -> str:
    """Decrypt message using GPG"""
    proc = subprocess.run(
        ["gpg", "-d"],
        input=ciphertext.encode(),
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode())
    return proc.stdout.decode()


class ChatApp(App):
    """Modern chat-style GPG encryption/decryption application"""

    CSS_PATH = "app.css"
    BINDINGS = [
        ("ctrl+e", "encrypt", "Encrypt"),
        ("ctrl+d", "decrypt", "Decrypt"),
        ("ctrl+l", "clear_input", "Clear Input"),
    ]

    convo_log = reactive("")
    encrypted_output = reactive("")

    def __init__(self, recipient: str, **kwargs):
        super().__init__(**kwargs)
        self.recipient = recipient

    @override
    def compose(self) -> ComposeResult:
        """Create the application UI"""
        yield Header(show_clock=True)

        with Container(id="main-container"):
            # Conversation panel
            with VerticalScroll(id="convo-panel"):
                yield RichLog(id="convo-log", wrap=True, markup=True)

            # Input/Output panel
            with Vertical(id="io-panel"):
                # with Horizontal(id="input-panel"):
                #     yield TextArea("", id="input-box", language="markdown")
                yield TextArea("", id="input-box", language="markdown")

                with Horizontal(id="button-panel"):
                    yield Button("Encrypt", id="encrypt-btn", variant="success")
                    yield Button("Decrypt", id="decrypt-btn", variant="warning")
                    yield Button("Clear", id="clear-btn", variant="error")

        yield Footer()

    @override
    def on_mount(self) -> None:
        """Load existing conversation when app starts"""
        self.title = "Secure GPG Messenger"
        self.sub_title = f"Recipient: {self.recipient}"

        if CONVO_FILE.exists():
            with CONVO_FILE.open() as f:
                self.query_one("#convo-log").write(f.read())

    def add_to_convo_log(self, role: str, message: str) -> None:
        """Add a message to the conversation log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = (
            rf"[b cyan]\[{timestamp}] You:[/] {message}"
            if role == "me"
            else rf"[b yellow]\[{timestamp}] Other:[/] {message}"
        )

        with CONVO_FILE.open("a") as f:
            f.write(line + "\n")

        log = self.query_one("#convo-log").write(line)
        log.scroll_end(animate=False)

    def action_encrypt(self) -> None:
        """Encrypt the current message"""
        self.on_button_pressed(Button.Pressed(self.query_one("#encrypt-btn")))

    def action_decrypt(self) -> None:
        """Decrypt the current message"""
        self.on_button_pressed(Button.Pressed(self.query_one("#decrypt-btn")))

    def action_clear_input(self) -> None:
        """Clear the input field"""
        self.query_one("#input-box").text = ""
        self.query_one("#input-box").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button click events"""
        input_box = self.query_one("#input-box", TextArea)
        text = input_box.text.strip()

        if not text:
            self.notify("Please enter some text", title="Input Error", severity="error")
            return

        try:
            if event.button.id == "encrypt-btn":
                encrypted = encrypt_message(text, self.recipient)
                pyperclip.copy(encrypted)
                self.add_to_convo_log("me", text)
                self.notify("Encrypted & copied to clipboard!", title="Success")
                input_box.text = ""

            elif event.button.id == "decrypt-btn":
                decrypted = decrypt_message(text)
                self.add_to_convo_log("other", decrypted)
                self.notify("Message decrypted!", title="Success")
                input_box.text = ""

            elif event.button.id == "clear-btn":
                input_box.text = ""
                input_box.focus()

        except Exception as e:
            self.notify(f"Error: {str(e)}", title="Operation Failed", severity="error")
            self.bell()


app = typer.Typer()


@app.command()
def chat(
    recipient: str = typer.Option(..., "--recipient", "-r", help="GPG recipient username or email"),
):
    """Start the secure messaging application"""
    ChatApp(recipient).run()


if __name__ == "__main__":
    app()
