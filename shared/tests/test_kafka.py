"""Tests for Kafka wrapper."""
from shared.kafka.topics import Topics


def test_topics_all():
    all_topics = Topics.all()
    assert Topics.ALERT_RAW in all_topics
    assert Topics.ALERT_NOTIFY in all_topics
    assert len(all_topics) == 6
