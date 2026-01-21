from typing import Any, Dict, Optional

def config(
    default: Optional[str] = None,
    conn_max_age: int = 0,
    conn_health_checks: bool = False,
    **kwargs: Any
) -> Dict[str, Any]: ...
