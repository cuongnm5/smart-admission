from enum import Enum


class UniversityType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class SelectivityBand(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CompetitivenessLevel(str, Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MatchBucket(str, Enum):
    REACH = "reach"
    TARGET = "target"
    LIKELY = "likely"
