from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import uuid

class InvoiceItem(BaseModel):
    """Model for an individual line item on an invoice"""
    description: str
    quantity: float
    unit_price: float
    total: float
    
class EnergyConsumption(BaseModel):
    """Model for energy consumption details"""
    period_start: datetime
    period_end: datetime
    total_kwh: float
    peak_kwh: Optional[float] = None
    off_peak_kwh: Optional[float] = None
    rate_per_kwh: float
    
class Invoice(BaseModel):
    """Model for an energy invoice"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_path: str
    provider: str
    invoice_number: str
    issue_date: datetime
    due_date: datetime
    customer_name: str
    customer_id: str
    total_amount: float
    consumption: EnergyConsumption
    items: List[InvoiceItem]
    taxes: Dict[str, float]
    processed_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class InvoiceRecommendation(BaseModel):
    """Model for invoice recommendations"""
    invoice_id: str
    recommendations: List[str]
    potential_savings: Optional[float] = None
    efficiency_score: Optional[float] = None
    generated_at: datetime = Field(default_factory=datetime.now)
