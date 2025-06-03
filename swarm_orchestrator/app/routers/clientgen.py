# app/routers/clientgen.py

from fastapi import APIRouter, HTTPException
from datetime import datetime
from sqlmodel import Session

from app.models import ClientStatus, engine
from app.schemas import ClientStatusResponse, ErrorResponse

router = APIRouter(tags=["ClientGen"])


@router.post(
    "/clientgen/{service}/regenerate",
    response_model=ClientStatusResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Regenerate Client",
    operation_id="regenerate_client",
)
def regenerate_client(service: str):
    """
    Trigger regeneration of the client SDK for the given service.
    """
    with Session(engine) as session:
        status_obj = session.get(ClientStatus, service)
        now = datetime.utcnow()

        if status_obj:
            # Update existing record
            status_obj.last_generated_at = now
            status_obj.checksum = f"new-checksum-{now.isoformat()}"
            status_obj.status = "regenerating"
            status_obj.error = None
            session.add(status_obj)
            session.commit()
            session.refresh(status_obj)
            return ClientStatusResponse(
                service=status_obj.service,
                last_generated_at=status_obj.last_generated_at,
                checksum=status_obj.checksum,
                status=status_obj.status,
                error=status_obj.error,
            )
        else:
            # Create a new ClientStatus record
            new_status = ClientStatus(
                service=service,
                last_generated_at=now,
                checksum=f"checksum-{now.isoformat()}",
                status="regenerating",
                error=None,
            )
            session.add(new_status)
            session.commit()
            session.refresh(new_status)
            return ClientStatusResponse(
                service=new_status.service,
                last_generated_at=new_status.last_generated_at,
                checksum=new_status.checksum,
                status=new_status.status,
                error=new_status.error,
            )


@router.get(
    "/clientgen/status/{service}",
    response_model=ClientStatusResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get Client Status",
    operation_id="get_client_status",
)
def get_client_status(service: str):
    """
    Return the current status of client SDK generation for the given service.
    """
    with Session(engine) as session:
        status_obj = session.get(ClientStatus, service)
        if not status_obj:
            raise HTTPException(
                status_code=404,
                detail="No client status found for this service"
            )
        return ClientStatusResponse(
            service=status_obj.service,
            last_generated_at=status_obj.last_generated_at,
            checksum=status_obj.checksum,
            status=status_obj.status,
            error=status_obj.error,
        )
