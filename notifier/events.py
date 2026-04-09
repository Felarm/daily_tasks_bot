from dataclasses import dataclass


@dataclass
class DTaskNotifyEventTypes:
    notify: str = "notify"
    begin_task: str = "begin_task"
    end_task: str = "end_task"
