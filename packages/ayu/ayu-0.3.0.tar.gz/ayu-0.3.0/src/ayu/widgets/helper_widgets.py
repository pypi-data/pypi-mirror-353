from __future__ import annotations

from textual.reactive import reactive
from textual.widgets import Rule, Button
from textual.message import Message
from textual.containers import Vertical, Horizontal

from ayu.utils import TestOutcome


class ToggleRule(Rule):
    test_result: reactive[TestOutcome | None] = reactive(None)
    widget_is_displayed: reactive[bool] = reactive(True)

    class Toggled(Message):
        def __init__(self, togglerule: ToggleRule) -> None:
            self.togglerule: ToggleRule = togglerule
            super().__init__()

        @property
        def control(self) -> ToggleRule:
            return self.togglerule

    def __init__(self, target_widget_id: str, *args, **kwargs) -> None:
        self.target_widget_id = target_widget_id
        super().__init__(*args, **kwargs)

    def compose(self):
        yield Button("[green]Passed[/]")

    def on_button_pressed(self):
        self.widget_is_displayed = not self.widget_is_displayed
        self.post_message(self.Toggled(self))
        self.watch_test_result()

    def watch_test_result(self):
        if self.widget_is_displayed:
            hint_string = " (click to collaps)"
        else:
            hint_string = " (click to open)"

        match self.test_result:
            case TestOutcome.PASSED:
                color = "green"
                result_string = self.test_result
            case TestOutcome.FAILED:
                color = "red"
                result_string = self.test_result
            case TestOutcome.SKIPPED:
                color = "yellow"
                result_string = self.test_result
            case _:
                color = "white"
                hint_string = ""
                result_string = "Please run or select a test"

        self.query_one(
            Button
        ).label = f"[{color}]{result_string}[/][white]{hint_string}[/]"


class ButtonPanel(Vertical):
    tests_running: reactive[bool] = reactive(False, init=False)

    def compose(self):
        yield Button(label="Plugins", id="button_plugins", variant="warning")
        yield Button(label="Show Log", id="button_log", variant="primary")
        yield Button(label="Show Coverage", id="button_coverage", variant="warning")
        with Horizontal():
            yield Button(label="Run tests", id="button_run", variant="success")
            yield Button(label="Cancel Run", id="button_cancel", variant="error")

    def watch_tests_running(self):
        self.query_one("#button_run", Button).disabled = self.tests_running
        self.query_one("#button_cancel", Button).disabled = not self.tests_running
