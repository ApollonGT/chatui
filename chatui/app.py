import configparser
from os.path import abspath
from typing import Callable, Awaitable

from textual.app import App, ComposeResult, Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.widget import Widget
from textual.widgets import Header, Footer, Static, Input, Button
from textual.reactive import reactive

chatui_config = configparser.ConfigParser()
chatui_config.read("./config.ini")


class MessageBox(Widget):
    text = reactive("", recompose=True)
    role = reactive("")

    def set_text(self, value) -> None:
        self.text = value

    def set_role(self, value) -> None:
        self.role = value

    def compose(self) -> ComposeResult:
        yield Static(self.text, classes=f"message {self.role}")


class ChatApp(App):
    CSS_PATH = abspath(chatui_config['TUI']['CSS_PATH'])
    TITLE = chatui_config['TUI']['TITLE']
    SUB_TITLE = chatui_config['TUI']['SUB_TITLE']

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Exit the application"),
        Binding("tab", "focus_next", "Focus Next", show=False),
        Binding("escape", "focus_none", "Focus None", show=False),
    ]

    def set_callback(self, callback: Callable[[str], Awaitable[str]]) -> None:
        self.callback = callback

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)

        yield ScrollableContainer(id="conversation-box")

        with Horizontal(id="input-container"):
            yield Input(placeholder="Ask anything...", id="message-input")
            yield Button(label="Send", id="send-button")

        yield Footer()

    def on_ready(self) -> None:
        message_input = self.query_one("#message-input", Input)
        message_input.focus()

    async def on_button_pressed(self) -> None:
        await self.process_conversation()

    async def on_input_submitted(self) -> None:
        await self.process_conversation()

    async def get_response(self) -> None:
        message_input = self.query_one("#message-input", Input)
        button = self.query_one("#send-button")
        conversation_box = self.query_one("#conversation-box")

        reply_box = MessageBox()
        reply_box.set_text("Loading")
        reply_box.set_role("bot")

        conversation_box.mount(reply_box)

        query = message_input.value

        with message_input.prevent(Input.Changed):
            message_input.value = ""

        reply_box.loading = True

        text = await self.callback(query)
        text = f"A: {text}"

        reply_box.set_text(text)

        reply_box.loading = False

        self.toggle_widgets(message_input, button)
        conversation_box.scroll_end(animate=False)
        message_input.focus()

    async def process_conversation(self) -> None:
        message_input = self.query_one("#message-input", Input)

        if message_input.value == "":
            return

        button = self.query_one("#send-button")
        conversation_box = self.query_one("#conversation-box")

        self.toggle_widgets(message_input, button)

        message_box = MessageBox()
        message_box.set_text(f"Q: {message_input.value}")
        message_box.set_role("user")
        conversation_box.mount(message_box)
        conversation_box.scroll_end(animate=False)

        await self.get_response()

    def toggle_widgets(self, *widgets: Widget) -> None:
        for w in widgets:
            w.disabled = not w.disabled
