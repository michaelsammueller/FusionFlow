from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class SupplierPerformance(Base):
    __tablename__ = "supplier_performance"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)

    # Performance period
    evaluation_period_start = Column(DateTime, nullable=False)
    evaluation_period_end = Column(DateTime, nullable=False)
    evaluation_type = Column(String(20), default="Quarterly")  # Monthly, Quarterly, Annual, Project-based

    # Delivery performance
    total_orders_in_period = Column(Integer, default=0)
    on_time_deliveries = Column(Integer, default=0)
    early_deliveries = Column(Integer, default=0)
    late_deliveries = Column(Integer, default=0)
    on_time_delivery_rate = Column(Numeric(precision=5, scale=2))  # Percentage

    # Lead time performance
    average_quoted_lead_time_days = Column(Numeric(precision=6, scale=2))
    average_actual_lead_time_days = Column(Numeric(precision=6, scale=2))
    lead_time_variance_days = Column(Numeric(precision=6, scale=2))  # Actual - Quoted
    lead_time_consistency_scorre = Column(Numeric(precision=3, scale=2))  # 1-5 scale

    # Quality performance
    total_items_received = Column(Integer, default=0)
    items_accepted_first_time = Column(Integer, default=0)
    items_requiring_rework = Column(Integer, default=0)
    items_rejected = Column(Integer, default=0)
    first_pass_yield_rate = Column(Numeric(precision=5, scale=2))  # Percentage
    rejection_rate = Column(Numeric(precision=5, scale=2))  # Percentage

    # Cost performance
    total_order_value = Column(Numeric(precision=15, scale=2))
    cost_savings_achieved = Column(Numeric(precision=12, scale=2))
    cost_overruns = Column(Numeric(precision=12, scale=2))
    price_competitiveness_score = Column(Numeric(precision=3, scale=2))  # 1-5 scale

    # Communication performance
    average_response_time_hours = Column(Numeric(precision=6, scale=2))
    communication_quality_score = Column(Numeric(precision=3, scale=2))  # 1-5 scale
    proactive_communication_instances = Column(Integer, default=0)
    communication_issues = Column(Integer, default=0)

    # Compliance performance
    certifications_up_to_date = Column(Boolean, default=True)
    compliance_violations = Column(Integer, default=0)
    corrective_actions_required = Column(Integer, default=0)
    corrective_actions_completed = Column(Integer, default=0)
    compliance_score = Column(Numeric(precision=3, scale=2))  # 1-5 scale

    # Innovation and improvement
    improvement_suggestions_submitted = Column(Integer, default=0)
    improvement_suggestions_implemented = Column(Integer, default=0)
    technology_upgrades_introduced = Column(Integer, default=0)
    innovation_score = Column(Numeric(precision=3, scale=2))  # 1-5 scale

    # Risk assessment
    supply_chain_disruptions = Column(Integer, default=0)
    financial_stability_score = Column(Numeric(precision=3, scale=2))  # 1-5 scale
    geographic_risk_score = Column(Numeric(precision=3, scale=2))  # 1-5 scale
    overall_risk_score = Column(Numeric(precision=3, scale=2))  # 1-5 scale

    # Overall performance metrics
    overall_performance_score = Column(Numeric(precision=3, scale=2))  # Weighted average of all scores
    performance_grade = Column(String(2))  # A+, A, B+, B, C+, C, D+, D, F
    performance_trend = Column(String(10))  # Improving, Stable, Declining

    # Benchmarking
    industry_percentile = Column(Integer)  # Where this supplier ranks in the industry
    internal_ranking = Column(Integer)  # Ranking among all suppliers

    # Detailed breakdowns (JSON fields for flexibility)
    delivery_performance_details = Column(JSON)  # Monthly breakdown, by product category, etc.
    quality_issues_breakdown = Column(JSON)  # Types of issues, frequency, resolution time
    cost_analysis_details = Column(JSON)  # Price trends, cost drivers, comparison with market

    # Action items and recommendations
    improvement_areas = Column(JSON)  # ["Lead Time", "Communication", "Quality"]
    recommended_actions = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    next_review_date = Column(DateTime)

    # Evaluation details
    evaluated_by = Column(String(100))
    evaluation_methodology = Column(String(100))  # Manual, Automated, Hybrid
    evaluation_notes = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    supplier = relationship("Supplier", back_populates="performance_records")