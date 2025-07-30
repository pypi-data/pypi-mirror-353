from __future__ import annotations

import inspect
import random
from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING
from typing import ClassVar
from typing import Literal

from rich.pretty import Pretty
from rich.syntax import Syntax
from textual import on
from textual.app import App
from textual.app import ComposeResult
from textual.containers import Container
from textual.containers import Horizontal
from textual.containers import ScrollableContainer
from textual.events import Mount
from textual.message import Message
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Label
from textual.widgets import Static
from textual.widgets import TabbedContent
from textual.widgets import TabPane

from textual_timepiece.__about__ import __version__
from textual_timepiece._activity_heatmap import ActivityHeatmap
from textual_timepiece._activity_heatmap import HeatmapManager
from textual_timepiece.pickers import DatePicker
from textual_timepiece.pickers import DateRangePicker
from textual_timepiece.pickers import DateTimeDurationPicker
from textual_timepiece.pickers import DateTimePicker
from textual_timepiece.pickers import DateTimeRangePicker
from textual_timepiece.pickers import DurationPicker
from textual_timepiece.pickers import TimePicker
from textual_timepiece.pickers._date_picker import DateSelect
from textual_timepiece.pickers._time_picker import DurationSelect
from textual_timepiece.pickers._time_picker import TimeSelect
from textual_timepiece.timeline._timeline_manager import (
    RuledHorizontalTimeline,
)
from textual_timepiece.timeline._timeline_manager import RuledVerticalTimeline

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.events import Mount


class DemoWidget(Widget):
    """Displays each widget with additional information."""

    @dataclass
    class Toggle(Message):
        """Sent when the user presses one of the buttons."""

        widget: type[Widget]
        preview: Literal[
            "docstring", "tcss", "code", "docs", "source", "bindings"
        ]

    def __init__(
        self,
        widget_call: type[Widget],
        *,
        notes: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self._notes = notes
        self._widget_type = widget_call

    def _compose_navigation_bar(self) -> ComposeResult:
        with Horizontal(id="navigation"):
            yield Button("Docstring", id="docstring", classes="nav")
            yield Label(self._widget_type.__name__, classes="title")
            if (
                hasattr(self._widget_type, "DEFAULT_CSS")
                and self._widget_type.DEFAULT_CSS
            ):
                yield Button("Default CSS", id="default-css", classes="nav")
            if (
                hasattr(self._widget_type, "BINDINGS")
                and self._widget_type.BINDINGS
            ):
                yield Button("Bindings", id="bindings", classes="nav")

            yield Button("Code Preview", id="code", classes="nav")

    def compose(self) -> ComposeResult:
        """Compose the layout for the widget."""
        yield from self._compose_navigation_bar()
        yield self._widget_type()

    @on(Button.Pressed, "#docstring")
    def _open_docstring(self, message: Button.Pressed) -> None:
        self.post_message(self.Toggle(self._widget_type, "docstring"))

    @on(Button.Pressed, "#default-css")
    def _open_default_css(self, message: Button.Pressed) -> None:
        self.post_message(self.Toggle(self._widget_type, "tcss"))

    @on(Button.Pressed, "#code")
    def _open_source(self, message: Button.Pressed) -> None:
        self.post_message(self.Toggle(self._widget_type, "code"))

    @on(Button.Pressed, "#bindings")
    def _open_bindings(self, message: Button.Pressed) -> None:
        self.post_message(self.Toggle(self._widget_type, "bindings"))


class PreviewScreen(ModalScreen[None]):
    """Preview screen that pops up to display associated widget info."""

    BINDINGS: ClassVar = [
        ("escape", "hide_preview", "Close Preview"),
    ]

    def __init__(
        self,
        renderable: RenderableType,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self._renderable = renderable

    def _on_mount(self, event: Mount) -> None:
        self.refresh_bindings()

    def compose(self) -> ComposeResult:
        """Generate the layout for the screen."""
        with Container():
            with ScrollableContainer():
                yield Static(self._renderable, id="preview")

            with Horizontal():
                yield Button(
                    r"Quit\[esc]",
                    "warning",
                    action="screen.hide_preview",
                    classes="nav",
                )

    def _action_hide_preview(self) -> None:
        self.dismiss()


class TimepieceDemo(App[None]):
    """Main demo app that displays the widgets."""

    CSS: ClassVar[str] = """
    Screen {
        layout: horizontal;
        align: center middle;

        TabbedContent {
            padding: 1 0;
            min-width: 135;
            width: 65%;

            TabPane {
                height: auto;
            }

            Container.previews {
                layout: vertical;
                overflow-y: auto;
                content-align-horizontal: center;
                align-horizontal: center;
            }
        }
    }

    .title {
        background: $panel;
        content-align-horizontal: center;
        text-align: center;
        width: 1fr;
        text-style: bold;
    }

    DemoWidget {
        height: auto;
        margin: 2 0;
        padding: 0 2;

        Horizontal#navigation {
            height: auto;
            margin-bottom: 1;
        }
    }

    Button.nav {
        border: none;
        height: 1;
        width: 10%;
        min-width: 13;
    }

    .widget_container {
        height: auto;
        width: 100%;
        align: center middle;
    }

    PreviewScreen {
        align: center middle;

        Container {
            border: round $primary;
            width: 50%;
            min-width: 125;
            height: 90%;

            ScrollableContainer {
                Static#preview {
                    margin: 1 2;
                }
            }

            Horizontal {
                height: 1;
                margin-top: 1;
                align-horizontal: center;
            }

        }
    }
    """

    TITLE = "Textual Timepiece"
    SUB_TITLE = __version__

    def compose(self) -> ComposeResult:
        """Generate the main layout for the demo app."""
        yield Header(show_clock=True)

        with TabbedContent(initial="pickers"):
            with (
                TabPane("Pickers", id="pickers"),
                Container(id="Pickers", classes="previews"),
            ):
                for item in (
                    DatePicker,
                    DurationPicker,
                    TimePicker,
                    DateTimePicker,
                    DateRangePicker,
                    DateTimeRangePicker,
                    DateTimeDurationPicker,
                ):
                    yield DemoWidget(item)

            with (
                TabPane("Select"),
                Container(id="Pickers", classes="previews"),
            ):
                for select in (
                    DateSelect,
                    TimeSelect,
                    DurationSelect,
                ):
                    yield DemoWidget(select)

            with (
                TabPane("Heatmap"),
                Container(id="heatmap", classes="previews"),
            ):
                for i in (ActivityHeatmap, HeatmapManager):
                    yield DemoWidget(i)

            with (
                TabPane("Timeline"),
                Container(id="timeline", classes="previews"),
            ):
                for timeline in (
                    RuledVerticalTimeline,
                    RuledHorizontalTimeline,
                ):
                    yield DemoWidget(timeline)

        yield Footer()

    def _on_mount(self, event: Mount) -> None:
        for widget in self.query(ActivityHeatmap):
            self._set_data(widget)

    @on(DemoWidget.Toggle)
    def _open_tab(self, message: DemoWidget.Toggle) -> None:
        data: RenderableType
        if message.preview == "tcss":
            data = message.widget.DEFAULT_CSS

        elif message.preview == "bindings":
            data = Pretty(message.widget.BINDINGS)

        elif message.preview == "docstring":
            data = str(message.widget.__doc__)

        elif message.preview == "code":
            data = Syntax(
                inspect.getsource(message.widget),
                "python",
                line_numbers=True,
                padding=1,
            )

        self.app.push_screen(PreviewScreen(data))

    def _set_data(self, widget: ActivityHeatmap) -> None:
        random.seed(widget.year)
        template = ActivityHeatmap.generate_empty_activity(widget.year)
        widget.values = defaultdict(
            lambda: 0,
            {
                day: random.randint(6000, 20000)  # noqa: S311
                for week in template
                for day in week
                if day
            },
        )

    @on(HeatmapManager.YearChanged)
    def _change_heat_year(self, message: HeatmapManager.YearChanged) -> None:
        message.stop()
        self._set_data(message.widget.heatmap)

    @cached_property
    def preview_panel(self) -> Static:
        """Panel for displaying information about a widget."""
        return self.query_one("#preview", Static)


def main() -> None:
    """Main entry point for the demo application."""
    TimepieceDemo().run()


if __name__ == "__main__":
    main()
