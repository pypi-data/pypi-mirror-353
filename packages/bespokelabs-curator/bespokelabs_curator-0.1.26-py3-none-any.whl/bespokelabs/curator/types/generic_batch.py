"""Module for defining types related to generic batch requests."""

import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class GenericBatchStatus(Enum):
    """Status of a generic batch request."""

    SUBMITTED = "submitted"  # Batch has been submitted but not yet processed
    FINISHED = "finished"  # Batch processing has completed
    DOWNLOADED = "downloaded"  # Results have been downloaded


class GenericBatchRequestCounts(BaseModel):
    """Counts of requests in a batch and their status."""

    total: int  # Total number of requests in the batch
    failed: int  # Number of failed requests
    succeeded: int  # Number of successful requests
    raw_request_counts_object: dict  # Raw counts data from the API response


class GenericBatch(BaseModel):
    """Represents a batch of requests sent to an API."""

    request_file: str  # Path to the file containing the requests
    id: str  # Unique identifier for this batch
    created_at: datetime.datetime  # When the batch was created
    finished_at: Optional[datetime.datetime]  # When processing completed, if finished
    status: str  # Current status of the batch
    api_key_suffix: str  # Last few characters of the API key used
    request_counts: GenericBatchRequestCounts  # Statistics about the requests
    raw_status: str  # Raw status string from the API
    raw_batch: dict  # Complete raw batch data from the API
    attempts_left: int = 1  # Number of attempts left to download the results
    resubmitted: bool = False  # Whether the batch has been resubmitted

    model_config = {
        "json_encoders": {datetime.datetime: lambda dt: dt.isoformat()},
    }

    @property
    def is_finished(self):
        """Returns whether a batch is finished."""
        return self.status == GenericBatchStatus.FINISHED.value


class BaseState(Enum):
    """Base enum class for defining state constants with a helper method to verify if a given value exists."""

    @classmethod
    def has_value(cls, value):
        """Check if the given value exists in the enum."""
        return any(value == item.value for item in cls)
