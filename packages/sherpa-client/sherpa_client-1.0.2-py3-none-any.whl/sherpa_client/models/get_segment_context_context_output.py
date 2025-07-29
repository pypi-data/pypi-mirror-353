from enum import Enum


class GetSegmentContextContextOutput(str, Enum):
    ALL = "all"
    MERGED_SEGMENTS = "merged_segments"
    SEGMENTS = "segments"

    def __str__(self) -> str:
        return str(self.value)
