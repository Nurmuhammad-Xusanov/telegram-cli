import asyncio
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Input, Static, OptionList, RichLog
from textual.widgets.option_list import Option
from textual.binding import Binding

class TelegramTUI(App):
    CSS = """
    /* Zero blank space, Edge-to-Edge Pure Black OLED */
    * {
        box-sizing: border-box;
    }

    Screen {
        background: #000000;
        color: #ffffff;
        padding: 0;
        margin: 0;
    }

    #main-container {
        height: 100%;
        width: 100%;
        background: #000000;
        padding: 0;
        margin: 0;
    }

    #left-panel {
        width: 30;
        min-width: 24;
        max-width: 38;
        border-right: solid #222222;
        background: #000000;
        padding: 0;
        margin: 0;
        height: 100%;
    }

    #search-input {
        height: 3;
        margin: 0;
        border: none;
        border-bottom: solid #222222;
        background: #000000;
        color: #ffffff;
        padding: 0 1;
    }

    #search-input:focus {
        border-bottom: solid #555555;
        background: #0a0a0a;
    }

    #chats-list {
        height: 1fr;
        background: #000000;
        border: none;
        padding: 0;
        margin: 0;
        scrollbar-size-vertical: 1;
    }

    OptionList > .option-list--option {
        background: #000000;
        color: #777777;
        padding: 0 1;
        height: 1;
    }

    OptionList > .option-list--option-highlighted {
        background: #161616;
        color: #ffffff;
        text-style: bold;
    }

    OptionList:focus > .option-list--option-highlighted {
        background: #242424;
        color: #ffffff;
        text-style: bold;
    }


    #right-panel {
        width: 1fr;
        height: 100%;
        background: #000000;
        padding: 0;
        margin: 0;
    }

    #chat-header {
        height: 3;
        background: #000000;
        border-bottom: solid #222222;
        color: #ffffff;
        padding: 1;
        margin: 0;
        text-style: bold;
    }

    #messages-log {
        height: 1fr;
        background: #000000;
        border: none;
        padding: 1;
        margin: 0;
        scrollbar-size-vertical: 1;
    }

    #message-input {
        height: 3;
        border: none;
        border-top: solid #222222;
        background: #000000;
        color: #ffffff;
        padding: 0 1;
        margin: 0;
    }

    #message-input:focus {
        border-top: solid #555555;
        background: #0a0a0a;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False, priority=True),
        Binding("f2", "toggle_channels", "Channels", show=False),
        Binding("f3", "open_last_media", "Open Media", show=False),
        Binding("f5", "refresh_chats", "Refresh", show=False),
        Binding("escape", "focus_chats", "Chats", show=False),
        Binding("slash", "focus_search", "Search", show=False),
    ]

    def __init__(self, tg_manager):
        super().__init__()
        self.tg = tg_manager
        self.show_channels = False
        self.all_dialogs = []
        self.filtered_dialogs = []
        self.current_dialog = None
        self.current_entity = None
        self.media_messages = []

    def compose(self) -> ComposeResult:
        with Horizontal(id="main-container"):
            with Vertical(id="left-panel"):
                yield Input(placeholder="Search (/)...", id="search-input")
                yield OptionList(id="chats-list")
            with Vertical(id="right-panel"):
                yield Static("Select a chat...", id="chat-header")
                yield RichLog(id="messages-log", wrap=True, highlight=False, markup=True)
                yield Input(placeholder="Message... (/1 to open media, F3: last media)", id="message-input")



    async def on_mount(self) -> None:
        self.tg.set_on_new_message(self.handle_incoming_message)
        self.load_dialogs()
        self.query_one("#chats-list").focus()

    @work(exclusive=True)
    async def load_dialogs(self) -> None:
        """Fetch dialogs"""
        header = self.query_one("#chat-header", Static)
        if not self.current_dialog:
            header.update("Loading chats...")
        try:
            self.all_dialogs = await self.tg.get_dialogs_list(show_channels=self.show_channels)
            self.apply_filter()
        except Exception as e:
            if not self.current_dialog:
                header.update(f"Error: {e}")
        else:
            if not self.current_dialog:
                mode = "Chats (DMs & Groups)" if not self.show_channels else "All Chats"
                header.update(f"{mode} — Select a chat")

    def apply_filter(self, search_query: str = "") -> None:
        """Filter dialogs and render single-line username list with active highlight"""
        query = search_query.strip().lower()
        self.filtered_dialogs = []
        option_list = self.query_one("#chats-list", OptionList)
        option_list.clear_options()

        active_index = None

        for d in self.all_dialogs:
            name = d["name"].strip() or "Unnamed"
            if query and query not in name.lower():
                continue
            self.filtered_dialogs.append(d)
            current_idx = len(self.filtered_dialogs) - 1

            is_active = (self.current_dialog and self.current_dialog["id"] == d["id"])
            if is_active:
                active_index = current_idx

            has_unread = d["unread_count"] > 0
            badge = " [bold white]1[/bold white]" if has_unread else ""

            max_len = 20 if has_unread else 23
            truncated_name = name[:max_len] if len(name) > max_len else name

            if is_active:
                line = f"[bold white]› {truncated_name}[/bold white]{badge}"
            elif has_unread:
                line = f"  [bold white]{truncated_name}[/bold white]{badge}"
            else:
                line = f"  [#777777]{truncated_name}[/#777777]"

            option_list.add_option(Option(line, id=str(d["id"])))

        if active_index is not None and 0 <= active_index < len(self.filtered_dialogs):
            option_list.highlighted = active_index

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self.apply_filter(event.value)

    async def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Select a chat and mark messages as read on server"""
        index = event.option_index
        if 0 <= index < len(self.filtered_dialogs):
            self.current_dialog = self.filtered_dialogs[index]
            self.current_entity = self.current_dialog["entity"]
            self.media_messages = []
            
            # Reset unread locally and send read acknowledge to Telegram servers
            self.current_dialog["unread_count"] = 0
            await self.tg.mark_as_read(self.current_entity)
            self.apply_filter(self.query_one("#search-input", Input).value)
            
            header = self.query_one("#chat-header", Static)
            header.update(f"Chat: [bold]{self.current_dialog['name']}[/bold]")
            
            self.load_messages()
            self.query_one("#message-input").focus()


    @work(exclusive=True)
    async def load_messages(self) -> None:
        """Load messages for active chat"""
        log = self.query_one("#messages-log", RichLog)
        log.clear()
        log.write("[dim]Loading messages...[/dim]")

        if not self.current_entity:
            return

        try:
            messages = await self.tg.get_chat_history(self.current_entity)
            log.clear()
            self.media_messages = []
            if not messages:
                log.write("[dim]No messages[/dim]")
                return

            for m in messages:
                self.render_message_line(m)
        except Exception as e:
            log.clear()
            log.write(f"[dim]Error: {e}[/dim]")

    def render_message_line(self, m: dict) -> None:
        """Render message in clean monochrome format"""
        log = self.query_one("#messages-log", RichLog)
        time_tag = f"[dim]{m['time']}[/dim]"
        sender_tag = f"[bold]{m['sender_name']}:[/bold]"

        raw_msg = m.get("raw_message")
        media_hint = ""
        if raw_msg and raw_msg.media:
            self.media_messages.append(raw_msg)
            idx = len(self.media_messages)
            media_hint = f" #{idx}"

        text = m['text']
        if media_hint:
            for tag in ["[Photo]", "[GIF]", "[Video]", "[Voice", "[Audio", "[Sticker]", "[File", "[Attachment]"]:
                if tag in text:
                    text = text.replace(tag, f"{tag[:-1]}{media_hint}]", 1) if tag.endswith("]") else f"{tag}{media_hint}]" if tag.startswith("[") and not tag.endswith("]") else f"{tag} {media_hint}"
                    break

        log.write(f"{time_tag} {sender_tag} {text}")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Send message or execute command"""
        if event.input.id == "message-input":
            val = event.value.strip()
            if not val:
                return

            # Check if this is a media open command: /open, /view, /o, /1, o 1
            cmd = val.lower()
            is_media_cmd = False
            target_idx = None

            if cmd == "/open" or cmd == "/view" or cmd == "/o" or cmd == "o":
                is_media_cmd = True
            elif cmd.startswith("/open ") or cmd.startswith("/view ") or cmd.startswith("/o ") or cmd.startswith("o "):
                parts = cmd.split()
                if len(parts) > 1 and parts[1].isdigit():
                    is_media_cmd = True
                    target_idx = int(parts[1])
            elif cmd.startswith("/") and cmd[1:].isdigit():
                is_media_cmd = True
                target_idx = int(cmd[1:])

            if is_media_cmd:
                event.input.value = ""
                await self.open_media_action(target_idx)
                return

            # Check if this is a file upload command: /send <path> [caption], /file, /f
            if val.startswith("/send ") or val.startswith("/file ") or val.startswith("/f "):
                event.input.value = ""
                if not self.current_entity:
                    log = self.query_one("#messages-log", RichLog)
                    log.write("[dim]Please select a chat first.[/dim]")
                    return

                rest = val.split(maxsplit=1)[1].strip()
                import shlex
                try:
                    tokens = shlex.split(rest)
                    file_path = tokens[0]
                    caption = " ".join(tokens[1:]) if len(tokens) > 1 else None
                except Exception:
                    parts = rest.split(maxsplit=1)
                    file_path = parts[0]
                    caption = parts[1] if len(parts) > 1 else None

                log = self.query_one("#messages-log", RichLog)
                log.write(f"[dim]Uploading: {file_path}...[/dim]")
                sent_msg, err = await self.tg.send_media_file(self.current_entity, file_path, caption=caption)
                if err:
                    log.write(f"[dim]Upload error: {err}[/dim]")
                elif sent_msg:
                    self.render_message_line(sent_msg)
                return

            if not self.current_entity:
                return

            event.input.value = ""
            try:
                sent_msg = await self.tg.send_text(self.current_entity, val)

                if sent_msg:
                    self.render_message_line(sent_msg)
            except Exception as e:
                log = self.query_one("#messages-log", RichLog)
                log.write(f"[dim]Failed to send: {e}[/dim]")

    async def open_media_action(self, idx: int | None = None) -> None:
        """Open media upon request"""
        log = self.query_one("#messages-log", RichLog)
        if not self.media_messages:
            log.write("[dim]No media found in this chat.[/dim]")
            return

        if idx is None:
            target_msg = self.media_messages[-1]
            idx = len(self.media_messages)
        elif 1 <= idx <= len(self.media_messages):
            target_msg = self.media_messages[idx - 1]
        else:
            log.write(f"[dim]Invalid index. Available: 1 to {len(self.media_messages)}[/dim]")
            return

        log.write(f"[dim]Downloading media #{idx}...[/dim]")
        success, msg = await self.tg.download_and_open_media(target_msg)
        if success:
            log.write(f"[dim]Media #{idx} opened.[/dim]")
        else:
            log.write(f"[dim]{msg}[/dim]")

    async def handle_incoming_message(self, chat_id, message, msg_info) -> None:
        """Handle real-time incoming messages"""
        if self.current_dialog and self.current_dialog["id"] == chat_id:
            self.render_message_line(msg_info)
            await self.tg.mark_as_read(self.current_entity, max_id=message.id)
        
        for d in self.all_dialogs:
            if d["id"] == chat_id:
                if not (self.current_dialog and self.current_dialog["id"] == chat_id):
                    d["unread_count"] = 1
                break
        self.apply_filter(self.query_one("#search-input", Input).value)


    def on_key(self, event) -> None:
        if event.key == "escape":
            self.query_one("#chats-list").focus()

    def action_toggle_channels(self) -> None:
        self.show_channels = not self.show_channels
        self.load_dialogs()

    async def action_open_last_media(self) -> None:
        await self.open_media_action()

    def action_refresh_chats(self) -> None:
        self.load_dialogs()

    def action_focus_chats(self) -> None:
        self.query_one("#chats-list").focus()

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()
