import enum


@enum.unique
class SubscriptionStatus(enum.Enum):
    FREE = "free"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    IDLE = "idle"