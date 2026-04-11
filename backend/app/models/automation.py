"""Automation models — AI-driven workflow engine."""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class WorkflowStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"
    failed = "failed"


class WorkflowTrigger(str, enum.Enum):
    manual = "manual"
    scheduled = "scheduled"          # cron-based
    event_new_lead = "event_new_lead"
    event_response = "event_response"
    event_stage_change = "event_stage_change"
    event_doc_uploaded = "event_doc_uploaded"
    webhook = "webhook"


class AutomationWorkflow(Base):
    __tablename__ = "automation_workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # User writes plain English, AI refines it
    natural_language_prompt = Column(Text, nullable=False)
    refined_prompt = Column(Text, nullable=True)

    # AI compiles into executable steps (JSON)
    compiled_steps = Column(Text, nullable=True)  # JSON array of actions

    trigger = Column(Enum(WorkflowTrigger), default=WorkflowTrigger.manual)
    schedule_cron = Column(String(100), nullable=True)  # for scheduled triggers
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.draft)

    # Stats
    run_count = Column(Integer, default=0)
    last_run_at = Column(DateTime, nullable=True)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)

    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    logs = relationship("AutomationLog", back_populates="workflow", cascade="all, delete-orphan")


class AutomationLog(Base):
    __tablename__ = "automation_logs"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("automation_workflows.id"), nullable=False)
    status = Column(String(50), nullable=False, default="running")  # running, success, failed
    input_data = Column(Text, nullable=True)  # JSON
    output_data = Column(Text, nullable=True)  # JSON
    error_message = Column(Text, nullable=True)
    cost_usd = Column(Float, default=0.0)
    duration_seconds = Column(Float, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    workflow = relationship("AutomationWorkflow", back_populates="logs")
