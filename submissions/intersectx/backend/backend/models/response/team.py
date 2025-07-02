from pydantic import BaseModel, Field
from typing import Optional, List
from backend.plot.types import ChartData
from backend.models.response.base import CitationResponse


# --- Team Overview ---
class TeamRoleBreakdown(BaseModel):
    role: str = Field(..., description="Job role or function category")
    count: int = Field(..., description="Number of employees in this role category")
    percentage: Optional[float] = Field(
        None, description="Percentage of total workforce in this role category"
    )
    sources: Optional[List[int]] = Field(
        None, description="List of indices referencing sources in the parent response"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score between 0 and 1 for the accuracy of this data point",
    )


class TeamOverviewResponse(CitationResponse):
    company_name: str = Field(
        ..., description="Official name of the company being analyzed"
    )
    company_description: Optional[str] = Field(
        None, description="Brief description of the company and its business"
    )
    total_employees: int = Field(
        ..., description="Total number of employees at the company"
    )
    roles_breakdown: List[TeamRoleBreakdown] = Field(
        ..., description="Breakdown of employees by job role or function"
    )
    locations: Optional[List[str]] = Field(
        None,
        description="List of geographic locations where the company has offices or employees",
    )
    key_hiring_areas: Optional[List[str]] = Field(
        None,
        description="Areas or roles where the company is currently focusing its hiring efforts",
    )
    growth_rate: Optional[float] = Field(
        None, description="Annual team growth rate as a percentage"
    )
    sources: Optional[List[str]] = Field(
        None, description="List of sources or references for this team data"
    )
    last_updated: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp indicating when this analysis was last updated",
    )

    def get_plot_data(self) -> ChartData:
        data = [
            {
                "role": r.role,
                "count": r.count,
                "percentage": r.percentage,
            }
            for r in self.roles_breakdown
        ]
        return ChartData(
            data=data,
            title=f"Team Roles Breakdown for {self.company_name}",
            x="role",
            y="count",
            kind="pie",
        )


# --- Individual Performance ---
class IndividualPerformanceMetric(BaseModel):
    metric: str = Field(
        ..., description="Name of the performance metric being measured"
    )
    value: float = Field(
        ..., description="Value or score for the specified performance metric"
    )
    sources: Optional[List[int]] = Field(
        None, description="List of indices referencing sources in the parent response"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score between 0 and 1 for the accuracy of this data point",
    )


class PreviousCompany(BaseModel):
    name: str = Field(..., description="Name of the previous employer")
    title: str = Field(..., description="Job title held at the previous company")
    duration: Optional[str] = Field(
        None, description="Duration of employment (e.g., '2 years 3 months')"
    )
    dates: Optional[str] = Field(
        None, description="Employment period formatted as 'YYYY-MM to YYYY-MM'"
    )


class Education(BaseModel):
    institution: str = Field(..., description="Name of the educational institution")
    degree: Optional[str] = Field(
        None, description="Degree type obtained (e.g., 'Bachelor's', 'Master's', 'PhD')"
    )
    field_of_study: Optional[str] = Field(
        None, description="Major or specialization area of study"
    )
    dates: Optional[str] = Field(
        None,
        description="Period of study formatted as 'YYYY-MM to YYYY-MM' or 'YYYY to YYYY'",
    )


class IndividualPerformanceResponse(CitationResponse):
    company_name: str = Field(
        ..., description="Official name of the company where the individual works"
    )
    individual_name: Optional[str] = Field(
        None, description="Full name of the individual"
    )
    title: Optional[str] = Field(
        None, description="Current job title or position of the individual"
    )
    image_url: Optional[str] = Field(
        None, description="URL to the individual's professional profile image"
    )
    tenure_years: Optional[float] = Field(
        None, description="Number of years the individual has been with the company"
    )
    performance_metrics: List[IndividualPerformanceMetric] = Field(
        ...,
        description="List of quantifiable performance indicators for the individual",
    )
    previous_companies: Optional[List[PreviousCompany]] = Field(
        None, description="Previous employment history of the individual"
    )
    key_strengths: Optional[List[str]] = Field(
        None, description="Core competencies and strengths of the individual"
    )
    development_areas: Optional[List[str]] = Field(
        None, description="Areas where the individual has opportunities for growth"
    )
    education: Optional[List[Education]] = Field(
        None, description="Educational background and qualifications"
    )
    sources: Optional[List[str]] = Field(
        None, description="List of sources or references for this individual's data"
    )
    last_updated: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp indicating when this analysis was last updated",
    )

    def get_plot_data(self) -> ChartData:
        data = [
            {"metric": m.metric, "value": m.value} for m in self.performance_metrics
        ]
        return ChartData(
            data=data,
            title=f"Performance Metrics for {self.individual_name}",
            x="metric",
            y="value",
            kind="bar",
        )


# --- Org Structure ---
class OrgNode(BaseModel):
    name: str = Field(..., description="Full name of the employee")
    title: str = Field(..., description="Job title or position within the company")
    department: Optional[str] = Field(
        None, description="Department or functional area the employee belongs to"
    )
    linkedin_url: Optional[str] = Field(
        None, description="URL to the employee's LinkedIn profile"
    )
    reports_to: Optional[str] = Field(
        None, description="Name of the person's direct manager or supervisor"
    )
    direct_reports: Optional[List[str]] = Field(
        None, description="List of names of people who report directly to this person"
    )
    sources: Optional[List[int]] = Field(
        None, description="List of indices referencing sources in the parent response"
    )


class Department(BaseModel):
    name: str = Field(..., description="Name of the department or functional area")
    head: Optional[str] = Field(
        None, description="Name of the department head or leader"
    )
    employee_count: Optional[int] = Field(
        None, description="Total number of employees in the department"
    )
    sub_departments: Optional[List[str]] = Field(
        None, description="List of sub-departments or teams within this department"
    )


class LeadershipTeamMember(BaseModel):
    name: str = Field(..., description="Full name of the leadership team member")
    title: str = Field(..., description="Executive or leadership title")
    linkedin_url: Optional[str] = Field(
        None, description="URL to the leader's LinkedIn profile"
    )
    department: Optional[str] = Field(
        None, description="Department or functional area the leader oversees"
    )


class OrgStructureResponse(CitationResponse):
    company_name: str = Field(
        ..., description="Official name of the company being analyzed"
    )
    org_chart: List[OrgNode] = Field(
        ...,
        description="Nodes representing employees and their reporting relationships",
    )
    ceo: Optional[str] = Field(
        None, description="Name of the Chief Executive Officer or equivalent"
    )
    departments: Optional[List[Department]] = Field(
        None, description="List of departments or major organizational divisions"
    )
    leadership_team: Optional[List[LeadershipTeamMember]] = Field(
        None, description="List of executive or senior leadership team members"
    )
    sources: Optional[List[str]] = Field(
        None, description="List of sources or references for this organizational data"
    )
    last_updated: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp indicating when this analysis was last updated",
    )

    def get_plot_data(self) -> ChartData:
        if self.departments:
            data = [
                {"department": d.name, "employee_count": d.employee_count or 0}
                for d in self.departments
            ]
            return ChartData(
                data=data,
                title=f"Department Sizes for {self.company_name}",
                x="department",
                y="employee_count",
                kind="bar",
            )
        else:
            return ChartData(data=[], title="No department data", kind="bar")


# --- Team Growth ---
class TeamGrowthTimeSeriesPoint(BaseModel):
    period_start: str = Field(
        ..., description="ISO 8601 formatted start date of the reporting period"
    )
    period_end: str = Field(
        ..., description="ISO 8601 formatted end date of the reporting period"
    )
    hires: int = Field(
        ..., description="Number of new employees hired during this period"
    )
    attrition: int = Field(
        ..., description="Number of employees who left during this period"
    )
    net_growth: int = Field(
        ..., description="Net change in headcount (hires minus attrition)"
    )
    growth_rate: Optional[float] = Field(
        None, description="Growth rate as a percentage for this specific period"
    )
    sources: Optional[List[int]] = Field(
        None, description="List of indices referencing sources in the parent response"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score between 0 and 1 for the accuracy of this data point",
    )


class DepartmentAttrition(BaseModel):
    department: str = Field(
        ..., description="Name of the department or functional area"
    )
    attrition_count: int = Field(
        ..., description="Number of employees who left this department"
    )
    attrition_rate: Optional[float] = Field(
        None, description="Attrition rate as a percentage for this department"
    )


class HiringTrendSupportingData(BaseModel):
    """Supporting data for hiring trends with defined properties instead of Dict[str, Any]"""

    percentage: Optional[float] = Field(
        None, description="Percentage value related to the trend"
    )
    count: Optional[int] = Field(
        None, description="Count or numeric value related to the trend"
    )
    year_over_year_change: Optional[float] = Field(
        None, description="Annual percentage change in the metric"
    )
    previous_value: Optional[float] = Field(
        None, description="Previous period's value for comparison"
    )
    current_value: Optional[float] = Field(
        None, description="Current period's value being analyzed"
    )
    description: Optional[str] = Field(
        None, description="Textual description of the supporting data"
    )


class HiringTrend(BaseModel):
    trend: str = Field(..., description="Name or title of the hiring trend")
    description: str = Field(
        ..., description="Detailed description of the observed hiring trend"
    )
    supporting_data: Optional[HiringTrendSupportingData] = Field(
        None, description="Quantitative data supporting the trend observation"
    )


class TeamGrowthResponse(CitationResponse):
    company_name: str = Field(
        ..., description="Official name of the company being analyzed"
    )
    team_growth_timeseries: List[TeamGrowthTimeSeriesPoint] = Field(
        ...,
        description="Time series data points showing team growth over different periods",
    )
    total_hires: int = Field(
        ..., description="Total number of new hires across all analyzed periods"
    )
    total_attrition: int = Field(
        ...,
        description="Total number of employees who left across all analyzed periods",
    )
    net_growth: int = Field(
        ..., description="Net change in headcount (total_hires minus total_attrition)"
    )
    growth_rate_annualized: Optional[float] = Field(
        None, description="Annualized growth rate as a percentage"
    )
    key_hiring_areas: Optional[List[str]] = Field(
        None,
        description="Areas or roles where the company has focused its recent hiring",
    )
    attrition_by_department: Optional[List[DepartmentAttrition]] = Field(
        None, description="Breakdown of employee attrition by department"
    )
    hiring_trends: Optional[List[HiringTrend]] = Field(
        None, description="Notable trends in the company's hiring patterns"
    )
    sources: Optional[List[str]] = Field(
        None, description="List of sources or references for this team growth data"
    )
    last_updated: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp indicating when this analysis was last updated",
    )

    def get_plot_data(self) -> ChartData:
        data = [
            {"period_start": t.period_start, "net_growth": t.net_growth}
            for t in self.team_growth_timeseries
        ]
        return ChartData(
            data=data,
            title=f"Team Net Growth Over Time for {self.company_name}",
            x="period_start",
            y="net_growth",
            kind="area",
        )
