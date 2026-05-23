"""Alert management router."""
from __future__ import annotations

import structlog
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Alert, AlertEvent, AlertStatus

from app.dependencies import get_db
from app.schemas.alert import (
    AlertAcknowledgeRequest,
    AlertListResponse,
    AlertResolveRequest,
    AlertResponse,
)

logger = structlog.get_logger()
router = APIRouter()


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    tenant_id: int = Query(...),
    status: str | None = None,
    severity: str | None = None,
    source: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Alert).where(Alert.tenant_id == tenant_id)
    if status:
        query = query.where(Alert.status == status)
    if severity:
        query = query.where(Alert.severity == severity)
    if source:
        query = query.where(Alert.source == source)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(Alert.started_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    alerts = result.scalars().all()

    return AlertListResponse(
        items=[AlertResponse.model_validate(a) for a in alerts],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    request: AlertAcknowledgeRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = AlertStatus.ACKNOWLEDGED
    if request.assignee:
        alert.assignee = request.assignee

    event = AlertEvent(
        alert_id=alert_id,
        action="acknowledged",
        operator=str(request.assignee) if request.assignee else None,
        detail="{}",
    )
    db.add(event)
    await db.commit()
    logger.info("alert_acknowledged", alert_id=alert_id)
    return {"status": "ok"}


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    request: AlertResolveRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.now()

    event = AlertEvent(
        alert_id=alert_id,
        action="resolved",
        detail='{"reason": "' + (request.reason or "") + '"}',
    )
    db.add(event)
    await db.commit()
    logger.info("alert_resolved", alert_id=alert_id)
    return {"status": "ok"}
