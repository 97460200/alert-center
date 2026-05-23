"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2026-05-23
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- tenants ---
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer, autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("status", sa.Enum("active", "disabled", name="tenantstatus"), nullable=False),
        sa.Column("config", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, autoincrement=True, nullable=False),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("role", sa.Enum("admin", "operator", "viewer", name="userrole"), nullable=False),
        sa.Column("oncall", sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- alert_rules ---
    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Integer, autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("condition", sa.Text, nullable=False, server_default="{}"),
        sa.Column("severity", sa.String(2), nullable=False, server_default="P3"),
        sa.Column("labels", sa.Text, nullable=False, server_default="{}"),
        sa.Column("annotations", sa.Text, nullable=False, server_default="{}"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- alerts ---
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("status", sa.Enum("pending", "firing", "resolved", "silenced", "acknowledged", name="alertstatus"), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("severity", sa.Enum("P0", "P1", "P2", "P3", "P4", name="alertseverity"), nullable=False),
        sa.Column("labels", sa.Text, nullable=False, server_default="{}"),
        sa.Column("annotations", sa.Text, nullable=False, server_default="{}"),
        sa.Column("rule_id", sa.Integer, sa.ForeignKey("alert_rules.id"), nullable=True),
        sa.Column("assignee", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("dedup_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("notification_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("started_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_at", sa.DateTime, nullable=True),
        sa.Column("last_notified_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_fingerprint", "alerts", ["fingerprint"])
    op.create_index("ix_alerts_status", "alerts", ["status"])
    op.create_index("ix_alerts_severity", "alerts", ["severity"])
    op.create_index("ix_alerts_started_at", "alerts", ["started_at"])
    op.create_index("ix_alerts_tenant_status", "alerts", ["tenant_id", "status"])
    op.create_index("ix_alerts_tenant_severity", "alerts", ["tenant_id", "severity"])
    op.create_index("ix_alerts_tenant_started", "alerts", ["tenant_id", "started_at"])

    # --- alert_events ---
    op.create_table(
        "alert_events",
        sa.Column("id", sa.Integer, autoincrement=True, nullable=False),
        sa.Column("alert_id", sa.String(36), sa.ForeignKey("alerts.id"), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("operator", sa.String(100), nullable=True),
        sa.Column("detail", sa.Text, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alert_events_alert_id", "alert_events", ["alert_id"])

    # --- route_policies ---
    op.create_table(
        "route_policies",
        sa.Column("id", sa.Integer, autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("match_labels", sa.Text, nullable=False, server_default="{}"),
        sa.Column("priority", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("targets", sa.Text, nullable=False, server_default="{}"),
        sa.Column("channel_ids", sa.Text, nullable=False, server_default="[]"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- notify_channels ---
    op.create_table(
        "notify_channels",
        sa.Column("id", sa.Integer, autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("type", sa.Enum("dingtalk", "wechat", "feishu", "sms", "phone", "email", "webhook", name="channeltype"), nullable=False),
        sa.Column("config", sa.Text, nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- silence_policies ---
    op.create_table(
        "silence_policies",
        sa.Column("id", sa.Integer, autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("match_labels", sa.Text, nullable=False, server_default="{}"),
        sa.Column("start_time", sa.DateTime, nullable=False),
        sa.Column("end_time", sa.DateTime, nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("creator", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- alert_stats ---
    op.create_table(
        "alert_stats",
        sa.Column("id", sa.Integer, autoincrement=True, nullable=False),
        sa.Column("stat_date", sa.Date, nullable=False),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(2), nullable=False),
        sa.Column("total_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("resolved_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("avg_resolve_seconds", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("notify_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("dedup_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alert_stats_stat_date", "alert_stats", ["stat_date"])


def downgrade() -> None:
    op.drop_table("alert_stats")
    op.drop_table("silence_policies")
    op.drop_table("notify_channels")
    op.drop_table("route_policies")
    op.drop_table("alert_events")
    op.drop_table("alerts")
    op.drop_table("alert_rules")
    op.drop_table("users")
    op.drop_table("tenants")
