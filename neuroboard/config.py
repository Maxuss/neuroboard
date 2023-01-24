from dataclasses import dataclass


@dataclass
class AppConfig:
    cycle_time_ms: int
    highlight_time_ms: int
    pass_count: int
    delay_time: int
