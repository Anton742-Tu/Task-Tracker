from typing import Any, List, Optional


def init(
    dsn: Optional[str] = None,
    integrations: Optional[List[Any]] = None,
    traces_sample_rate: float = 1.0,
    send_default_pii: bool = False,
    environment: Optional[str] = None,
    **kwargs: Any
) -> None: ...
