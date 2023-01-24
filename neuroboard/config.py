from dataclasses import dataclass
import os
import toml


class AppConfig:
    cycle_time_ms: int
    highlight_time_ms: int
    pass_count: int
    delay_time: int

    def __init__(
        self,
        cycle_time_ms: int = -1,
        highlight_time_ms: int = -1,
        pass_count: int = -1,
        delay_time: int = -1,
    ):
        self.cycle_time_ms = cycle_time_ms
        self.highlight_time_ms = highlight_time_ms
        self.pass_count = pass_count
        self.delay_time = delay_time


def load_config() -> AppConfig:
    if not os.path.exists("nbdata/config.toml"):
        # os.makedirs("nbdata")
        default = AppConfig(
            500,
            100,
            2,
            2000,
        )
        save_config(default)
        return default
    return toml.loads(open("nbdata/config.toml", "r"))


def save_config(cfg: AppConfig):
    with open("nbdata/config.toml", "w+") as f:
        f.write(
            toml.dumps(
                {
                    "cycle_time_ms": cfg.cycle_time_ms,
                    "highlight_time_ms": cfg.highlight_time_ms,
                    "pass_count": cfg.pass_count,
                    "delay_time": cfg.delay_time,
                }
            )
        )
