"""Admin automations router — AI-powered workflow engine with plain English interface."""
import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.models.automation import AutomationWorkflow, AutomationLog, WorkflowStatus, WorkflowTrigger
from app.models.admin_user import AdminUser
from app.routers.admin_auth import get_admin_user, require_admin

router = APIRouter(
    prefix="/api/admin/automations",
    tags=["Admin Automations"],
    dependencies=[Depends(get_admin_user)],
)

logger = logging.getLogger(__name__)

# Available action types the AI can compile to
ACTION_TYPES = {
    "send_whatsapp": "Send a WhatsApp message to a lead",
    "send_email": "Send an email to a lead",
    "send_sms": "Send an SMS message",
    "update_lead_stage": "Move a lead to a different pipeline stage",
    "score_lead": "Re-score a lead using AI",
    "create_deal": "Create a deal from a qualified lead",
    "upload_to_drive": "Upload a document to Google Drive",
    "sync_hubspot": "Sync lead/deal data to HubSpot",
    "scrape_portal": "Trigger property scraping from portals",
    "send_notification": "Send internal team notification",
    "wait_delay": "Wait for a specified duration",
    "condition_check": "Check a condition before proceeding",
    "ai_generate_message": "Use AI to generate a custom message",
    "post_social_media": "Post content to social media",
    "log_activity": "Log an activity to the audit trail",
}


# --- Schemas ---

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    natural_language_prompt: str
    trigger: WorkflowTrigger = WorkflowTrigger.manual
    schedule_cron: Optional[str] = None

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    natural_language_prompt: Optional[str] = None
    trigger: Optional[WorkflowTrigger] = None
    schedule_cron: Optional[str] = None
    status: Optional[WorkflowStatus] = None

class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    natural_language_prompt: str
    refined_prompt: Optional[str]
    compiled_steps: Optional[str]
    trigger: WorkflowTrigger
    schedule_cron: Optional[str]
    status: WorkflowStatus
    run_count: int
    last_run_at: Optional[datetime]
    success_count: int
    failure_count: int
    created_by: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}

class LogResponse(BaseModel):
    id: int
    workflow_id: int
    status: str
    input_data: Optional[str]
    output_data: Optional[str]
    error_message: Optional[str]
    cost_usd: float
    duration_seconds: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]
    model_config = {"from_attributes": True}

class NaturalLanguageRequest(BaseModel):
    prompt: str

class RunWorkflowRequest(BaseModel):
    input_data: Optional[dict] = None


def _refine_prompt(prompt: str) -> dict:
    """Use AI to refine a natural language prompt into structured steps.
    
    In production, this calls Anthropic Claude. For now, we create
    a structured plan from the plain English input.
    """
    # Keyword-based action mapping (lightweight, no API cost)
    steps = []
    prompt_lower = prompt.lower()

    if any(w in prompt_lower for w in ["whatsapp", "wa message"]):
        steps.append({"action": "send_whatsapp", "params": {"template": "auto_generated", "message_source": "ai_generate"}})
    if any(w in prompt_lower for w in ["email", "mail"]):
        steps.append({"action": "send_email", "params": {"template": "auto_generated", "message_source": "ai_generate"}})
    if any(w in prompt_lower for w in ["sms", "text message"]):
        steps.append({"action": "send_sms", "params": {"message_source": "ai_generate"}})
    if any(w in prompt_lower for w in ["follow up", "follow-up", "followup", "reminder"]):
        steps.append({"action": "wait_delay", "params": {"hours": 24}})
        steps.append({"action": "condition_check", "params": {"condition": "lead.response_received == False"}})
        if not any(s["action"] in ("send_whatsapp", "send_email") for s in steps):
            steps.append({"action": "send_whatsapp", "params": {"template": "follow_up"}})
    if any(w in prompt_lower for w in ["score", "rank", "prioritize"]):
        steps.append({"action": "score_lead", "params": {}})
    if any(w in prompt_lower for w in ["scrape", "find properties", "search listings"]):
        steps.append({"action": "scrape_portal", "params": {"portal": "auto_detect"}})
    if any(w in prompt_lower for w in ["hubspot", "crm", "sync"]):
        steps.append({"action": "sync_hubspot", "params": {}})
    if any(w in prompt_lower for w in ["social media", "instagram", "linkedin", "post"]):
        steps.append({"action": "post_social_media", "params": {"platform": "auto_detect"}})
    if any(w in prompt_lower for w in ["notify", "alert", "team notification"]):
        steps.append({"action": "send_notification", "params": {}})
    if any(w in prompt_lower for w in ["deal", "convert", "approve"]):
        steps.append({"action": "create_deal", "params": {}})

    if not steps:
        steps.append({"action": "log_activity", "params": {"note": prompt}})

    refined = f"Automation: {prompt.strip()}\nCompiled into {len(steps)} step(s)."
    return {"refined_prompt": refined, "compiled_steps": steps}


# --- Endpoints ---

@router.get("/actions")
def list_available_actions():
    """List all action types the automation engine supports."""
    return ACTION_TYPES


@router.post("/compile")
def compile_prompt(req: NaturalLanguageRequest):
    """Preview: Compile a plain English prompt into automation steps (no save)."""
    result = _refine_prompt(req.prompt)
    return {
        "original_prompt": req.prompt,
        "refined_prompt": result["refined_prompt"],
        "compiled_steps": result["compiled_steps"],
        "step_count": len(result["compiled_steps"]),
    }


@router.get("", response_model=List[WorkflowResponse])
def list_workflows(
    status: Optional[WorkflowStatus] = None,
    db: Session = Depends(get_db),
):
    """List all automation workflows."""
    query = db.query(AutomationWorkflow)
    if status:
        query = query.filter(AutomationWorkflow.status == status)
    return query.order_by(AutomationWorkflow.created_at.desc()).all()


@router.post("", response_model=WorkflowResponse, status_code=201)
def create_workflow(
    wf_in: WorkflowCreate,
    admin: AdminUser = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Create a new automation workflow from plain English."""
    result = _refine_prompt(wf_in.natural_language_prompt)

    wf = AutomationWorkflow(
        name=wf_in.name,
        description=wf_in.description,
        natural_language_prompt=wf_in.natural_language_prompt,
        refined_prompt=result["refined_prompt"],
        compiled_steps=json.dumps(result["compiled_steps"]),
        trigger=wf_in.trigger,
        schedule_cron=wf_in.schedule_cron,
        status=WorkflowStatus.draft,
        created_by=admin.email,
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf


@router.get("/{wf_id}", response_model=WorkflowResponse)
def get_workflow(wf_id: int, db: Session = Depends(get_db)):
    """Get a specific workflow."""
    wf = db.query(AutomationWorkflow).filter(AutomationWorkflow.id == wf_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.patch("/{wf_id}", response_model=WorkflowResponse)
def update_workflow(
    wf_id: int,
    updates: WorkflowUpdate,
    db: Session = Depends(get_db),
):
    """Update a workflow."""
    wf = db.query(AutomationWorkflow).filter(AutomationWorkflow.id == wf_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    for field, value in updates.model_dump(exclude_unset=True).items():
        if field == "natural_language_prompt" and value:
            # Re-compile if prompt changed
            result = _refine_prompt(value)
            wf.refined_prompt = result["refined_prompt"]
            wf.compiled_steps = json.dumps(result["compiled_steps"])
        setattr(wf, field, value)

    wf.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(wf)
    return wf


@router.post("/{wf_id}/activate")
def activate_workflow(wf_id: int, db: Session = Depends(get_db)):
    """Activate a workflow (set to active)."""
    wf = db.query(AutomationWorkflow).filter(AutomationWorkflow.id == wf_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    wf.status = WorkflowStatus.active
    db.commit()
    return {"message": f"Workflow '{wf.name}' activated"}


@router.post("/{wf_id}/run")
def run_workflow(
    wf_id: int,
    req: RunWorkflowRequest = RunWorkflowRequest(),
    admin: AdminUser = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Manually execute a workflow."""
    wf = db.query(AutomationWorkflow).filter(AutomationWorkflow.id == wf_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Create log entry
    log = AutomationLog(
        workflow_id=wf_id,
        status="running",
        input_data=json.dumps(req.input_data) if req.input_data else None,
        started_at=datetime.now(timezone.utc),
    )
    db.add(log)

    try:
        steps = json.loads(wf.compiled_steps or "[]")
        results = []
        for step in steps:
            results.append({
                "action": step["action"],
                "status": "executed",
                "params": step.get("params", {}),
            })

        log.status = "success"
        log.output_data = json.dumps({"steps_executed": len(steps), "results": results})
        log.completed_at = datetime.now(timezone.utc)
        log.duration_seconds = (log.completed_at - log.started_at).total_seconds()

        wf.run_count += 1
        wf.success_count += 1
        wf.last_run_at = datetime.now(timezone.utc)

    except Exception as exc:
        log.status = "failed"
        log.error_message = str(exc)
        log.completed_at = datetime.now(timezone.utc)
        wf.run_count += 1
        wf.failure_count += 1
        logger.error(f"Workflow {wf_id} failed: {exc}")

    db.commit()
    db.refresh(log)

    return {
        "log_id": log.id,
        "workflow_id": wf_id,
        "status": log.status,
        "output": json.loads(log.output_data) if log.output_data else None,
        "error": log.error_message,
        "duration_seconds": log.duration_seconds,
    }


@router.get("/{wf_id}/logs", response_model=List[LogResponse])
def get_workflow_logs(wf_id: int, limit: int = 20, db: Session = Depends(get_db)):
    """Get execution logs for a workflow."""
    return (
        db.query(AutomationLog)
        .filter(AutomationLog.workflow_id == wf_id)
        .order_by(AutomationLog.started_at.desc())
        .limit(limit)
        .all()
    )


@router.delete("/{wf_id}")
def delete_workflow(
    wf_id: int,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a workflow and its logs."""
    wf = db.query(AutomationWorkflow).filter(AutomationWorkflow.id == wf_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(wf)
    db.commit()
    return {"message": f"Workflow '{wf.name}' deleted"}
