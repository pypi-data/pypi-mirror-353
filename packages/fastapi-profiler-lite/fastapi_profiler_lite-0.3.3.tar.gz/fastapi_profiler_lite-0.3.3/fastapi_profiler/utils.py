import contextvars
import time
import uuid
from typing import Any, Dict, List, Optional

# Context variable to store the current request profiler
# This ensures thread safety and async context isolation
current_profiler_ctx = contextvars.ContextVar("current_profiler", default=None)


class RequestProfiler:
    """Tracks performance metrics for a single request."""

    __slots__ = (
        "request_id",
        "path",
        "method",
        "start_time",
        "timestamp",
        "end_time",
        "total_time",
        "status_code",
        "external_calls",
        "db_queries",
        "_dict_cache",
    )

    def __init__(self, request_id: str, path: str, method: str):
        self.request_id = request_id
        self.path = path
        self.method = method
        self.start_time = time.perf_counter()
        self.timestamp = time.time()  # Unix timestamp for frontend
        self.end_time: Optional[float] = None
        self.total_time: Optional[float] = None
        self.status_code: Optional[int] = None

        # Performance data
        self.external_calls: List[tuple] = []
        self.db_queries: List[Dict[str, Any]] = []

        # Cache for dictionary representation
        self._dict_cache = None

    def set_status_code(self, status_code: int) -> None:
        """Set the response status code."""
        self.status_code = status_code

    def complete(self) -> None:
        """Mark the request as complete and calculate total time."""
        self.end_time = time.perf_counter()
        self.total_time = self.end_time - self.start_time

    def to_dict(self, include_external: bool = True) -> Dict[str, Any]:
        """Convert profiler data to a dictionary.

        Args:
            include_external: Whether to include external call details
                Set to False for memory efficiency when storing many profiles
        """
        # Return cached version if available and complete
        if self._dict_cache is not None and self.total_time is not None:
            if include_external or "external_calls" not in self._dict_cache:
                return self._dict_cache

        # Basic profile data (always included)
        result = {
            "request_id": self.request_id,
            "path": self.path,
            "method": self.method,
            "start_time": self.timestamp,
            "total_time": self.total_time,
            "status_code": self.status_code,
        }

        # Add end_time if available
        if self.end_time is not None:
            result["end_time"] = self.timestamp + (self.end_time - self.start_time)

        # Add external calls if requested
        if include_external:
            result["external_calls"] = [
                {"url": call[0], "method": call[1], "duration": call[2]}
                for call in self.external_calls
            ]
            result["external_call_count"] = len(self.external_calls)
        else:
            result["external_call_count"] = len(self.external_calls)

        # Add database query information
        db_time = sum(query["duration"] for query in self.db_queries)
        result["db_time"] = db_time
        result["db_count"] = len(self.db_queries)

        if include_external:
            result["db_queries"] = self.db_queries

        # Cache the result if profiling is complete
        if self.total_time is not None:
            self._dict_cache = result

        return result

    def add_external_call(self, url: str, method: str, duration: float) -> None:
        """Add an external API call to the profile."""
        self.external_calls.append((url, method, duration))

    def add_db_query(
        self, duration: float, statement: str, metadata: dict = None
    ) -> None:
        """Add a database query to the profile."""
        # Skip empty or None statements
        if not statement:
            return

        # Create a copy of metadata to avoid modifying the original
        metadata_copy = dict(metadata or {})

        # Add timestamp for when the query was recorded
        metadata_copy["timestamp"] = time.time()

        # Truncate very long statements to avoid memory issues
        original_length = len(statement)
        if original_length > 1000:
            statement = statement[:997] + "..."
            metadata_copy["truncated"] = True
            metadata_copy["original_length"] = original_length

        # Normalize whitespace in the statement for better display
        statement = " ".join(statement.split())

        # Add query to the list
        self.db_queries.append(
            {"duration": duration, "statement": statement, "metadata": metadata_copy}
        )


def get_current_profiler() -> Optional[RequestProfiler]:
    """Get the profiler for the current request context."""
    return current_profiler_ctx.get()


def add_external_call(url: str, method: str, duration: float) -> None:
    """Add an external API call to the current request's profile."""
    profiler = get_current_profiler()
    if profiler:
        profiler.add_external_call(url, method, duration)


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())
