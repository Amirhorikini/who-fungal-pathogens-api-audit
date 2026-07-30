from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class ProbeResult:
    """Result of a query attempt to a source, for a given pathogen.

    `attempted=False` is reserved for sources with no confirmed programmatic count
    endpoint (LILACS, DDBJ, FungiDB) -- see ../../docs/03_lessons_learned.md.
    This is deliberately distinct from `ok=False` (the endpoint exists, but the call
    failed): the recurring lesson from the previous project was to never collapse
    "not measured", "failed", and "actual zero" into a single value.
    """
    source: str
    pathogen_id: str
    pathogen_label: str
    attempted: bool
    ok: bool
    http_status: Optional[int] = None
    latency_ms: Optional[float] = None
    raw_value: Union[int, str] = "NA"
    error: Optional[str] = None
    note: str = ""
