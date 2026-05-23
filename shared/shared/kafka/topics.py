"""Kafka topic definitions."""


class Topics:
    ALERT_RAW = "alert.raw"
    ALERT_ENRICHED = "alert.enriched"
    ALERT_DEDUPED = "alert.deduped"
    ALERT_NOTIFY = "alert.notify"
    ALERT_LIFECYCLE = "alert.lifecycle"
    RULE_RESULT = "rule.result"

    @classmethod
    def all(cls) -> list[str]:
        return [
            cls.ALERT_RAW, cls.ALERT_ENRICHED, cls.ALERT_DEDUPED,
            cls.ALERT_NOTIFY, cls.ALERT_LIFECYCLE, cls.RULE_RESULT,
        ]
