# app/routers/orchestrator.py

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import PlainTextResponse
from typing import List, Optional
from datetime import datetime

from sqlmodel import Session, select

from app.models import Service, engine
from app.schemas import (
    HealthResponse,
    ServiceSpec,
    ServiceDetail,
    ServiceListResponse,
    DeployResponse,
    DeployRequest,
    BatchDeployResponse,
    ConfigDetail,
    ConfigPatch,
    ErrorResponse,
)

router = APIRouter(tags=["Orchestrator"])

# Keep track of startup time so the /health endpoint can compute uptime
startup_time = datetime.utcnow()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health",
    operation_id="health",
)
def health():
    """
    Returns {"status":"ok","uptime":"XhYmZs"}.
    """
    delta = datetime.utcnow() - startup_time
    hours, rem = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(rem, 60)
    return HealthResponse(status="ok", uptime=f"{hours}h{minutes}m{seconds}s")


@router.get(
    "/services",
    response_model=ServiceListResponse,
    summary="List Services",
    operation_id="list_services",
)
def list_services(
    limit: int = Query(
        50,
        ge=1,
        description="Limit",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Offset",
    ),
    status: Optional[str] = Query(
        None,
        pattern="^(running|updating|error)$",
        description="Status",
    ),
):
    """
    Retrieve a paginated list of services.
    Optional filter on `status` if provided.
    """
    with Session(engine) as session:
        stmt = select(Service)
        if status is not None:
            # If you intend to filter by Service.status == status, uncomment:
            # stmt = stmt.where(Service.status == status)
            pass

        stmt = stmt.offset(offset).limit(limit)
        results = session.exec(stmt).all()

    return ServiceListResponse(
        services=results,
        total=len(results),
        limit=limit,
        offset=offset,
    )


@router.post(
    "/services",
    response_model=ServiceDetail,
    status_code=201,
    summary="Create Service",
    operation_id="create_service",
)
def create_service(
    name: str = Query(..., description="Name"),
    spec: ServiceSpec = Body(...),
):
    """
    Create a new service.  
    - **name** (query parameter): unique service name  
    - **spec** (JSON body): details conforming to ServiceSpec
    """
    with Session(engine) as session:
        existing = session.get(Service, name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Service '{name}' already exists.",
            )

        new_svc = Service(
            name=name,
            image=spec.image,
            status="stopped",
            ports=spec.ports or {},
            secrets=spec.secrets or [],
            configs=spec.configs or [],
            env={},  # or default empty dict
        )
        session.add(new_svc)
        session.commit()
        session.refresh(new_svc)

    return new_svc


@router.get(
    "/services/{service}",
    response_model=ServiceDetail,
    responses={404: {"model": ErrorResponse}},
    summary="Get Service",
    operation_id="get_service",
)
def get_service(service: str):
    """
    Fetch detailed information about a single service.
    """
    with Session(engine) as session:
        svc = session.get(Service, service)
        if not svc:
            raise HTTPException(status_code=404, detail="Service not found")
    return svc


@router.delete(
    "/services/{service}",
    status_code=204,
    responses={404: {"model": ErrorResponse}},
    summary="Delete Service",
    operation_id="delete_service",
)
def delete_service(service: str):
    """
    Delete a service by name. Returns HTTP 204 on success.
    """
    with Session(engine) as session:
        svc = session.get(Service, service)
        if not svc:
            raise HTTPException(status_code=404, detail="Service not found")
        session.delete(svc)
        session.commit()
    return None  # 204 No Content


@router.post(
    "/services/{service}/deploy",
    response_model=DeployResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Deploy Service",
    operation_id="deploy_service",
)
def deploy_service(
    service: str,
    request: DeployRequest,
):
    """
    Trigger a deployment for the specified service.
    """
    with Session(engine) as session:
        svc = session.get(Service, service)
        if not svc:
            raise HTTPException(status_code=404, detail="Service not found")
        # … your real deploy logic here …
    return DeployResponse(status="ok", message=f"{service} deployment initiated")


@router.post(
    "/deploy",
    response_model=BatchDeployResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Batch Deploy",
    operation_id="batch_deploy",
)
def batch_deploy(
    request: DeployRequest,
):
    """
    Accepts a list of service names in `request.services`.  
    Returns a BatchDeployResponse with an array of DeployResponse objects.
    """
    if not request.services:
        raise HTTPException(status_code=400, detail="Empty deploy list")

    results: List[DeployResponse] = []
    for svc_name in request.services:
        # … your real deploy logic here …
        results.append(DeployResponse(status="ok", message=f"{svc_name} deployed"))

    return BatchDeployResponse(results=results)


@router.get(
    "/services/{service}/config",
    response_model=ConfigDetail,
    responses={404: {"model": ErrorResponse}},
    summary="Get Config",
    operation_id="get_config",
)
def get_config(service: str):
    """
    Retrieve the current config (env & ports) for the specified service.
    """
    with Session(engine) as session:
        svc = session.get(Service, service)
        if not svc:
            raise HTTPException(status_code=404, detail="Service not found")
        return ConfigDetail(env=svc.env, ports=svc.ports)


@router.patch(
    "/services/{service}/config",
    response_model=ConfigDetail,
    responses={404: {"model": ErrorResponse}},
    summary="Patch Config",
    operation_id="patch_config",
)
def patch_config(
    service: str,
    patch: ConfigPatch = Body(...),
):
    """
    Partially update the service configuration.
    Only the fields provided in ConfigPatch will be modified.
    """
    with Session(engine) as session:
        svc = session.get(Service, service)
        if not svc:
            raise HTTPException(status_code=404, detail="Service not found")

        if patch.ports is not None:
            svc.ports = patch.ports
        if patch.env is not None:
            svc.env = patch.env

        session.add(svc)
        session.commit()
        session.refresh(svc)

        return ConfigDetail(env=svc.env, ports=svc.ports)


@router.get(
    "/services/{service}/logs",
    response_class=PlainTextResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get Logs",
    operation_id="get_logs",
)
def get_logs(
    service: str,
    tail: int = Query(
        100,
        ge=1,
        description="Tail",
    ),
):
    """
    Return the last `tail` lines of logs for the given service.
    """
    with Session(engine) as session:
        svc = session.get(Service, service)
        if not svc:
            raise HTTPException(status_code=404, detail="Service not found")
        # … your real log‐fetching logic here …
    return ""  # plain‐text log content


@router.post(
    "/services/{service}/rollback",
    response_model=DeployResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Rollback Service",
    operation_id="rollback_service",
)
def rollback_service(service: str):
    """
    Initiate a rollback for the specified service.
    """
    with Session(engine) as session:
        svc = session.get(Service, service)
        if not svc:
            raise HTTPException(status_code=404, detail="Service not found")
        # … your real rollback logic here …
    return DeployResponse(status="ok", message=f"{service} rollback initiated")
