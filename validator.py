"""
CSC481 Module 2 Critical Thinking
Email and Phone Number Validator
GTK3 GUI — multi-instance CSV sync via watchdog file watching

Dependencies: python-gobject, python-watchdog
  sudo pacman -S python-gobject
  pip install watchdog --break-system-packages
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

import re
import csv
import os
import threading
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ── CSV path (shared across all instances) ────────────────────────────────────
CSV_PATH = os.path.expanduser("~/Pictures/Screenshots/../validator_results.csv")
CSV_PATH = os.path.expanduser("~/validator_results.csv")
CSV_HEADERS = ["timestamp", "email", "phone", "email_valid", "phone_valid"]

# ── Dracula palette ───────────────────────────────────────────────────────────
COLORS = {
    "bg":      "#282a36",
    "bg_alt":  "#44475a",
    "fg":      "#f8f8f2",
    "comment": "#6272a4",
    "cyan":    "#8be9fd",
    "green":   "#50fa7b",
    "orange":  "#ffb86c",
    "pink":    "#ff79c6",
    "purple":  "#bd93f9",
    "red":     "#ff5555",
    "yellow":  "#f1fa8c",
}

# ── Regex patterns ─────────────────────────────────────────────────────────────
#
# Email rule (from assignment spec):
#   - starts with one or more lowercase letters or digits
#   - optionally followed by a period or underscore, then more lowercase letters/digits
#   - @ symbol
#   - one or more alphanumeric characters
#   - a literal period
#   - two to three alphanumeric characters
#
EMAIL_PATTERN = re.compile(
    r'^[a-z0-9]+'           # one or more lowercase letters or digits
    r'([._][a-z0-9]+)*'     # optionally: (period or underscore + more letters/digits), repeated
    r'@'                    # literal @
    r'[a-z0-9]+'            # domain name: one or more alphanumeric
    r'\.'                   # literal period
    r'[a-z0-9]{2,3}$',     # TLD: exactly two or three alphanumeric characters
    re.ASCII
)

#
# Phone rule (from assignment spec):
#   Format 1: XXX-XXX-XXXX  (hyphen or space separators, optional)
#   Format 2: (XXX) XXX-XXXX or (XXX)-XXX-XXXX
#   Also accepts: 1234567890 (no separators)
#   Separators between groups: hyphen or single space (not double space)
#
PHONE_PATTERN = re.compile(
    r'^'
    r'(?:'
        r'\(\d{3}\)'        # (XXX)
        r'[-\s]?'           # optional hyphen or space after closing paren
    r'|'
        r'\d{3}'            # XXX
        r'[-\s]?'           # optional hyphen or space
    r')'
    r'\d{3}'                # XXX
    r'[-\s]?'               # optional hyphen or space
    r'\d{4}'                # XXXX
    r'$'
)


def validate_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email.strip()))


def validate_phone(phone: str) -> bool:
    return bool(PHONE_PATTERN.match(phone.strip()))


def ensure_csv():
    """Create CSV with headers if it doesn't exist."""
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()


def append_csv(row: dict):
    """Append one result row to the shared CSV."""
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(row)


def read_csv() -> list[dict]:
    """Read all rows from the CSV, return as list of dicts."""
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


# ── CSS styling ───────────────────────────────────────────────────────────────
CSS = b"""
window {
    background-color: #282a36;
    color: #f8f8f2;
}
.title-label {
    font-size: 18px;
    font-weight: bold;
    color: #bd93f9;
    padding: 12px 0 4px 0;
}
.subtitle-label {
    font-size: 11px;
    color: #6272a4;
    padding-bottom: 12px;
}
entry {
    background-color: #44475a;
    color: #f8f8f2;
    border: 1px solid #6272a4;
    border-radius: 4px;
    padding: 6px 10px;
    font-family: monospace;
    font-size: 13px;
}
entry:focus {
    border-color: #bd93f9;
}
.validate-btn {
    background-color: #bd93f9;
    color: #282a36;
    font-weight: bold;
    border-radius: 4px;
    padding: 8px 20px;
    font-size: 13px;
    border: none;
}
.validate-btn:hover {
    background-color: #cfa9ff;
}
.valid-label {
    color: #50fa7b;
    font-weight: bold;
    font-family: monospace;
    font-size: 13px;
}
.invalid-label {
    color: #ff5555;
    font-weight: bold;
    font-family: monospace;
    font-size: 13px;
}
.neutral-label {
    color: #6272a4;
    font-family: monospace;
    font-size: 13px;
}
.section-label {
    color: #8be9fd;
    font-size: 12px;
    font-weight: bold;
    padding: 8px 0 2px 0;
}
.history-view {
    background-color: #21222c;
    color: #f8f8f2;
    font-family: monospace;
    font-size: 12px;
}
.history-frame {
    border: 1px solid #44475a;
    border-radius: 4px;
}
.row-valid {
    color: #50fa7b;
}
.row-invalid {
    color: #ff5555;
}
scrolledwindow {
    background-color: #21222c;
}
"""


# ── File watcher ──────────────────────────────────────────────────────────────
class CSVWatcher(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self._last_event = 0

    def on_modified(self, event):
        if not event.is_directory and event.src_path == os.path.abspath(CSV_PATH):
            # Debounce: GTK idle callback to refresh UI thread-safely
            GLib.idle_add(self.callback)


# ── Main window ───────────────────────────────────────────────────────────────
class ValidatorWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Email & Phone Validator — CSC481")
        self.set_default_size(700, 560)
        self.set_border_width(0)
        self.set_resizable(True)

        # Apply CSS
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        ensure_csv()
        self._build_ui()
        self._start_watcher()
        self._refresh_history()

    def _build_ui(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        outer.set_margin_start(24)
        outer.set_margin_end(24)
        outer.set_margin_top(8)
        outer.set_margin_bottom(16)
        self.add(outer)

        # Title
        title = Gtk.Label(label="Email & Phone Validator")
        title.get_style_context().add_class("title-label")
        title.set_halign(Gtk.Align.START)
        outer.pack_start(title, False, False, 0)

        subtitle = Gtk.Label(label="CSC481 · Module 2 · Results shared across all open instances")
        subtitle.get_style_context().add_class("subtitle-label")
        subtitle.set_halign(Gtk.Align.START)
        outer.pack_start(subtitle, False, False, 0)

        # ── Email input ───────────────────────────────────────────────────────
        email_lbl = Gtk.Label(label="EMAIL ADDRESS")
        email_lbl.get_style_context().add_class("section-label")
        email_lbl.set_halign(Gtk.Align.START)
        outer.pack_start(email_lbl, False, False, 0)

        self.email_entry = Gtk.Entry()
        self.email_entry.set_placeholder_text("e.g. farhad.bari@gmail.com")
        outer.pack_start(self.email_entry, False, False, 4)

        self.email_result = Gtk.Label(label="—")
        self.email_result.get_style_context().add_class("neutral-label")
        self.email_result.set_halign(Gtk.Align.START)
        outer.pack_start(self.email_result, False, False, 2)

        # ── Phone input ───────────────────────────────────────────────────────
        phone_lbl = Gtk.Label(label="US PHONE NUMBER")
        phone_lbl.get_style_context().add_class("section-label")
        phone_lbl.set_halign(Gtk.Align.START)
        outer.pack_start(phone_lbl, False, False, 0)

        self.phone_entry = Gtk.Entry()
        self.phone_entry.set_placeholder_text("e.g. 507-459-1234 or (807) 250-0022")
        outer.pack_start(self.phone_entry, False, False, 4)

        self.phone_result = Gtk.Label(label="—")
        self.phone_result.get_style_context().add_class("neutral-label")
        self.phone_result.set_halign(Gtk.Align.START)
        outer.pack_start(self.phone_result, False, False, 2)

        # ── Validate button ───────────────────────────────────────────────────
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        btn_box.set_margin_top(10)
        self.validate_btn = Gtk.Button(label="Validate & Save")
        self.validate_btn.get_style_context().add_class("validate-btn")
        self.validate_btn.connect("clicked", self._on_validate)
        btn_box.pack_start(self.validate_btn, False, False, 0)
        outer.pack_start(btn_box, False, False, 0)

        # ── History table ─────────────────────────────────────────────────────
        hist_lbl = Gtk.Label(label="VALIDATION HISTORY  (live — updates across all instances)")
        hist_lbl.get_style_context().add_class("section-label")
        hist_lbl.set_halign(Gtk.Align.START)
        hist_lbl.set_margin_top(16)
        outer.pack_start(hist_lbl, False, False, 0)

        # TreeView with ListStore
        # Columns: timestamp, email, email_valid, phone, phone_valid
        self.store = Gtk.ListStore(str, str, str, str, str)
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.get_style_context().add_class("history-view")
        self.tree.set_headers_visible(True)

        columns = [
            ("Timestamp",    0, 150),
            ("Email",        1, 190),
            ("E-Valid",      2, 70),
            ("Phone",        3, 130),
            ("P-Valid",      4, 70),
        ]
        for title, col_id, width in columns:
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, renderer, text=col_id)
            col.set_fixed_width(width)
            col.set_resizable(True)
            self.tree.append_column(col)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(180)
        scroll.get_style_context().add_class("history-frame")
        scroll.add(self.tree)
        outer.pack_start(scroll, True, True, 4)

        self.show_all()

    def _on_validate(self, _widget):
        email = self.email_entry.get_text().strip()
        phone = self.phone_entry.get_text().strip()

        email_ok = validate_email(email) if email else False
        phone_ok = validate_phone(phone) if phone else False

        # Update inline result labels
        self._set_result_label(self.email_result, email, email_ok)
        self._set_result_label(self.phone_result, phone, phone_ok)

        # Write to CSV
        row = {
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "email":       email,
            "phone":       phone,
            "email_valid": "VALID" if email_ok else "INVALID",
            "phone_valid": "VALID" if phone_ok else "INVALID",
        }
        append_csv(row)
        # Watcher will trigger refresh on all instances including this one

    def _set_result_label(self, label: Gtk.Label, value: str, valid: bool):
        ctx = label.get_style_context()
        ctx.remove_class("valid-label")
        ctx.remove_class("invalid-label")
        ctx.remove_class("neutral-label")
        if not value:
            label.set_text("—")
            ctx.add_class("neutral-label")
        elif valid:
            label.set_text(f"✓  {value}  —  VALID")
            ctx.add_class("valid-label")
        else:
            label.set_text(f"✗  {value}  —  INVALID")
            ctx.add_class("invalid-label")

    def _refresh_history(self):
        """Reload CSV into the TreeView store."""
        self.store.clear()
        rows = read_csv()
        for row in reversed(rows):   # newest first
            self.store.append([
                row.get("timestamp",    ""),
                row.get("email",        ""),
                row.get("email_valid",  ""),
                row.get("phone",        ""),
                row.get("phone_valid",  ""),
            ])
        return False  # GLib.idle_add expects False to not repeat

    def _start_watcher(self):
        handler = CSVWatcher(self._refresh_history)
        observer = Observer()
        watch_dir = os.path.dirname(os.path.abspath(CSV_PATH))
        observer.schedule(handler, path=watch_dir, recursive=False)
        t = threading.Thread(target=observer.start, daemon=True)
        t.start()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    win = ValidatorWindow()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()
