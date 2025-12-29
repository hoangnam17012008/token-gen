from dataclasses import dataclass, field
from collections import deque
from typing import Optional, Tuple
from time import time


@dataclass
class AccountContext:
    fingerprint: str
    username: str
    password: str
    email: str
    birthday: Tuple[int, int, int]
    proxy: str

    captcha_key: Optional[str] = None
    token: Optional[str] = None
    upn: Optional[str] = None


@dataclass
class TitleBarStats:
    token_generated: int = 0
    ev_tokens: int = 0
    invalid_tokens: int = 0
    locked_tokens: int = 0

    start_time: float = field(default_factory=time)
    _token_times: deque = field(default_factory=deque, init=False, repr=False)

    def mark_token(self):
        now = time()
        self.token_generated += 1
        self._token_times.append(now)

        while self._token_times and now - self._token_times[0] > 60:
            self._token_times.popleft()

    @property
    def tokens_per_minute(self) -> int:
        return len(self._token_times)

    @property
    def time_elapsed(self) -> int:
        return int(time() - self.start_time)

    def format_title(self) -> str:
        m, s = divmod(self.time_elapsed, 60)
        return (
            f"??? │ "
            f"Gen: {self.token_generated} │ "
            f"EV: {self.ev_tokens} │ "
            f"Inv: {self.invalid_tokens} │ "
            f"Lock: {self.locked_tokens} │ "
            f"CPM: {self.tokens_per_minute} │ "
            f"Time: {m:02}:{s:02}"
        )
