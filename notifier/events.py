from dataclasses import dataclass


@dataclass
class DTaskNotifyEventTypes:
    notify: str = "notify"
    start_dialog: str = "start_dialog"
    end_dialog: str = "end_dialog"
