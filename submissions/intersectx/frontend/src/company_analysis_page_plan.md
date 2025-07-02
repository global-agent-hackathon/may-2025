## Complete Page Layout Structure for Company Analysis

### 1. **Root Container Structure**
```
CompanyAnalysisPage
├── PageWrapper (min-h-screen bg-gray-50 p-6)
│   ├── MainContainer (max-w-7xl mx-auto space-y-8)
│   │   ├── CompanyHeader Section
│   │   └── BentoGridContainer (grid grid-cols-1 lg:grid-cols-12 gap-6)
│   │   │   ├── FinanceSection (if finance data exists)
│   │   │   ├── TeamSection (if linkedin_team data exists)
│   │   │   ├── MarketSection (if market_analysis data exists)
│   │   │   ├── RiskSection (if risk_analysis data exists)
│   │   │   ├── SentimentSection (if customer_sentiment data exists)
│   │   │   ├── PartnershipSection (if partnership_network data exists)
│   │   │   └── ComplianceSection (if regulatory_compliance data exists)
```

### 2. **Company Header Section Layout**
```
CompanyHeader
├── Card (bg-white border-0 shadow-sm)
│   └── CardContent (p-8)
│       └── HeaderContent (flex items-center space-x-4)
│           ├── CompanyLogo (w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center)
│           │   └── LogoFallback (text-2xl font-bold text-gray-600)
│           └── CompanyInfo
│               ├── CompanyName (text-3xl font-bold text-gray-900)
│               ├── CompanyDescription (text-gray-600)
│               └── CompanyMetadata (flex space-x-4 mt-2)
│                   ├── IndustryBadge
│                   ├── FoundedDate
│                   └── HeadquartersLocation
```

### 3. **Finance Section Layout (lg:col-span-8)**
```
FinanceSection
├── Card (bg-white border-0 shadow-sm h-fit)
│   ├── CardHeader (pb-4)
│   │   └── HeaderRow (flex items-center justify-between)
│   │       ├── HeaderLeft (flex items-center space-x-2)
│   │       │   ├── DollarSignIcon (w-5 h-5 text-green-600)
│   │       │   └── SectionTitle (text-lg font-semibold)
│   │       └── ExpandToggleButton
│   └── CardContent
│       ├── SummaryView (always visible)
│       │   ├── MetricsGrid (grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4)
│       │   │   ├── RevenueCard (text-center p-4 bg-green-50 rounded-lg)
│       │   │   │   ├── Value (text-2xl font-bold text-green-700)
│       │   │   │   └── Label (text-sm text-green-600)
│       │   │   ├── ValuationCard (text-center p-4 bg-blue-50 rounded-lg)
│       │   │   ├── FundingCard (text-center p-4 bg-purple-50 rounded-lg)
│       │   │   └── ExpensesCard (text-center p-4 bg-orange-50 rounded-lg)
│       │   └── QuickInsights (flex space-x-2)
│       │       ├── GrowthBadge
│       │       ├── ProfitabilityBadge
│       │       └── FundingStageBadge
│       └── ExpandedView (visible when expanded, border-t pt-4)
│           ├── ChartsSection (grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6)
│           │   ├── RevenueChart
│           │   │   ├── ChartHeader
│           │   │   └── LineChart (revenue over time)
│           │   ├── FundingChart
│           │   │   ├── ChartHeader
│           │   │   └── BarChart (funding rounds)
│           │   ├── ExpenseBreakdown
│           │   │   ├── ChartHeader
│           │   │   └── PieChart (expense categories)
│           │   └── MarginsChart
│           │       ├── ChartHeader
│           │       └── LineChart (margins over time)
│           └── DetailedMetrics (grid grid-cols-1 md:grid-cols-3 gap-4)
│               ├── RevenueDetails
│               ├── FundingDetails
│               └── ExpenseDetails
```

### 4. **Team Section Layout (lg:col-span-4)**
```
TeamSection
├── Card (bg-white border-0 shadow-sm h-fit)
│   ├── CardHeader (pb-4)
│   │   └── HeaderRow (flex items-center justify-between)
│   │       ├── HeaderLeft (flex items-center space-x-2)
│   │       │   ├── UsersIcon (w-5 h-5 text-blue-600)
│   │       │   └── SectionTitle
│   │       └── ExpandToggleButton
│   └── CardContent
│       ├── SummaryView
│       │   ├── EmployeeCountCard (text-center p-4 bg-blue-50 rounded-lg mb-4)
│       │   │   ├── TotalCount (text-2xl font-bold text-blue-700)
│       │   │   └── Label (text-sm text-blue-600)
│       │   ├── GrowthMetric (flex justify-between p-3 bg-gray-50 rounded)
│       │   │   ├── GrowthLabel
│       │   │   └── GrowthPercentage
│       │   └── TopRoles (space-y-2)
│       │       └── RoleItem (flex justify-between py-1) [repeat for top 3]
│       └── ExpandedView (visible when expanded, border-t pt-4)
│           ├── TeamBreakdownChart (mb-6)
│           │   ├── ChartHeader
│           │   └── DonutChart (roles distribution)
│           ├── GrowthTrendChart (mb-6)
│           │   ├── ChartHeader
│           │   └── LineChart (team growth over time)
│           ├── KeyPersonnel (grid grid-cols-1 gap-4 mb-4)
│           │   └── PersonCard [repeat for each key person]
│           │       ├── PersonAvatar
│           │       ├── PersonName
│           │       ├── PersonRole
│           │       └── PersonBackground
│           └── OrganizationChart
│               ├── ChartHeader
│               └── HierarchyVisualization
```

### 5. **Market Section Layout (lg:col-span-6)**
```
MarketSection
├── Card (bg-white border-0 shadow-sm h-fit)
│   ├── CardHeader (pb-4)
│   │   └── HeaderRow (flex items-center justify-between)
│   │       ├── HeaderLeft (flex items-center space-x-2)
│   │       │   ├── TrendingUpIcon (w-5 h-5 text-purple-600)
│   │       │   └── SectionTitle
│   │       └── ExpandToggleButton
│   └── CardContent
│       ├── SummaryView
│       │   ├── MarketMetrics (grid grid-cols-2 gap-4 mb-4)
│       │   │   ├── MarketSizeCard (p-4 bg-purple-50 rounded-lg)
│       │   │   └── GrowthRateCard (p-4 bg-indigo-50 rounded-lg)
│       │   ├── KeyTrends (space-y-2)
│       │   │   └── TrendItem (flex items-center space-x-2) [repeat for top 3]
│       │   └── CompetitivePosition (p-3 bg-gray-50 rounded)
│       └── ExpandedView (visible when expanded, border-t pt-4)
│           ├── MarketTrendsChart (mb-6)
│           │   ├── ChartHeader
│           │   └── AreaChart (market trends over time)
│           ├── CompetitiveLandscape (mb-6)
│           │   ├── ChartHeader
│           │   ├── CompetitorGrid (grid grid-cols-1 md:grid-cols-2 gap-4)
│           │   │   └── CompetitorCard [repeat for each competitor]
│           │   │       ├── CompetitorName
│           │   │       ├── MarketShare
│           │   │       ├── Strengths
│           │   │       └── Weaknesses
│           │   └── MarketShareChart (PieChart)
│           ├── GrowthProjections (mb-6)
│           │   ├── ChartHeader
│           │   └── LineChart (projected growth)
│           └── RegionalAnalysis
│               ├── ChartHeader
│               ├── RegionalGrid (grid grid-cols-1 md:grid-cols-2 gap-4)
│               └── RegionalChart (BarChart)
```

### 6. **Risk Section Layout (lg:col-span-6)**
```
RiskSection
├── Card (bg-white border-0 shadow-sm h-fit)
│   ├── CardHeader (pb-4)
│   │   └── HeaderRow (flex items-center justify-between)
│   │       ├── HeaderLeft (flex items-center space-x-2)
│   │       │   ├── AlertTriangleIcon (w-5 h-5 text-orange-600)
│   │       │   └── SectionTitle
│   │       └── ExpandToggleButton
│   └── CardContent
│       ├── SummaryView
│       │   ├── RiskOverview (grid grid-cols-2 gap-4 mb-4)
│       │   │   ├── OverallRiskScore (p-4 bg-orange-50 rounded-lg)
│       │   │   │   ├── RiskScore (text-2xl font-bold)
│       │   │   │   └── RiskLevel (text-sm)
│       │   │   └── HighestRiskCategory (p-4 bg-red-50 rounded-lg)
│       │   ├── TopRisks (space-y-2)
│       │   │   └── RiskItem (flex justify-between items-center py-2) [repeat for top 3]
│       │   │       ├── RiskName
│       │   │       └── SeverityBadge
│       │   └── RiskTrend (p-3 bg-gray-50 rounded)
│       └── ExpandedView (visible when expanded, border-t pt-4)
│           ├── RiskCategoryBreakdown (mb-6)
│           │   ├── ChartHeader
│           │   └── DonutChart (risk categories)
│           ├── RiskMatrix (mb-6)
│           │   ├── ChartHeader
│           │   └── ScatterPlot (probability vs impact)
│           ├── DetailedRisks (space-y-4)
│           │   └── RiskCategory [repeat for each category]
│           │       ├── CategoryHeader
│           │       ├── RiskList
│           │       │   └── RiskCard [repeat for each risk]
│           │       │       ├── RiskDescription
│           │       │       ├── ImpactLevel
│           │       │       ├── Probability
│           │       │       └── MitigationStrategy
│           │       └── CategoryScore
│           └── RiskTimeline
│               ├── ChartHeader
│               └── TimelineChart (risk levels over time)
```

### 7. **Customer Sentiment Section Layout (lg:col-span-4)**
```
SentimentSection
├── Card (bg-white border-0 shadow-sm h-fit)
│   ├── CardHeader (pb-4)
│   │   └── HeaderRow (flex items-center justify-between)
│   │       ├── HeaderLeft (flex items-center space-x-2)
│   │       │   ├── HeartIcon (w-5 h-5 text-pink-600)
│   │       │   └── SectionTitle
│   │       └── ExpandToggleButton
│   └── CardContent
│       ├── SummaryView
│       │   ├── SentimentScore (text-center p-4 bg-pink-50 rounded-lg mb-4)
│       │   │   ├── Score (text-2xl font-bold text-pink-700)
│       │   │   └── Label (text-sm text-pink-600)
│       │   ├── SentimentBreakdown (grid grid-cols-3 gap-2 mb-4)
│       │   │   ├── PositiveCount (text-center p-2 bg-green-50 rounded)
│       │   │   ├── NeutralCount (text-center p-2 bg-gray-50 rounded)
│       │   │   └── NegativeCount (text-center p-2 bg-red-50 rounded)
│       │   └── RecentTrend (p-3 bg-gray-50 rounded)
│       └── ExpandedView (visible when expanded, border-t pt-4)
│           ├── SentimentTrendChart (mb-6)
│           │   ├── ChartHeader
│           │   └── LineChart (sentiment over time)
│           ├── CustomerFeedback (mb-6)
│           │   ├── FeedbackHeader
│           │   └── FeedbackList (space-y-3)
│           │       └── FeedbackCard [repeat for recent feedback]
│           │           ├── CustomerType
│           │           ├── FeedbackText
│           │           ├── SentimentBadge
│           │           └── Date
│           ├── BrandReputation (mb-6)
│           │   ├── ReputationHeader
│           │   ├── ReputationScore
│           │   └── ReputationChart
│           └── SentimentSources
│               ├── SourcesHeader
│               └── SourcesList (grid grid-cols-2 gap-2)
```

### 8. **Partnership Network Section Layout (lg:col-span-4)**
```
PartnershipSection
├── Card (bg-white border-0 shadow-sm h-fit)
│   ├── CardHeader (pb-4)
│   │   └── HeaderRow (flex items-center justify-between)
│   │       ├── HeaderLeft (flex items-center space-x-2)
│   │       │   ├── NetworkIcon (w-5 h-5 text-indigo-600)
│   │       │   └── SectionTitle
│   │       └── ExpandToggleButton
│   └── CardContent
│       ├── SummaryView
│       │   ├── PartnerStats (grid grid-cols-2 gap-4 mb-4)
│       │   │   ├── TotalPartnersCard (p-4 bg-indigo-50 rounded-lg)
│       │   │   └── NetworkStrengthCard (p-4 bg-blue-50 rounded-lg)
│       │   ├── TopPartners (space-y-2)
│       │   │   └── PartnerItem (flex justify-between items-center py-1) [repeat for top 3]
│       │   └── PartnershipTypes (flex flex-wrap gap-2)
│       │       └── TypeBadge [repeat for each type]
│       └── ExpandedView (visible when expanded, border-t pt-4)
│           ├── PartnershipNetwork (mb-6)
│           │   ├── NetworkHeader
│           │   └── NetworkGraph (interactive network visualization)
│           ├── PartnersList (mb-6)
│           │   ├── PartnersHeader
│           │   └── PartnersGrid (grid grid-cols-1 gap-3)
│           │       └── PartnerCard [repeat for each partner]
│           │           ├── PartnerLogo
│           │           ├── PartnerName
│           │           ├── PartnershipType
│           │           ├── PartnershipStrength
│           │           └── StartDate
│           └── PartnershipTrends
│               ├── TrendsHeader
│               └── TrendsChart (partnership growth over time)
```

### 9. **Regulatory Compliance Section Layout (lg:col-span-4)**
```
ComplianceSection
├── Card (bg-white border-0 shadow-sm h-fit)
│   ├── CardHeader (pb-4)
│   │   └── HeaderRow (flex items-center justify-between)
│   │       ├── HeaderLeft (flex items-center space-x-2)
│   │       │   ├── ShieldIcon (w-5 h-5 text-green-600)
│   │       │   └── SectionTitle
│   │       └── ExpandToggleButton
│   └── CardContent
│       ├── SummaryView
│       │   ├── ComplianceScore (text-center p-4 bg-green-50 rounded-lg mb-4)
│       │   │   ├── Score (text-2xl font-bold text-green-700)
│       │   │   └── Label (text-sm text-green-600)
│       │   ├── KeyRegulations (space-y-2 mb-4)
│       │   │   └── RegulationItem (flex justify-between items-center py-1) [repeat for key regs]
│       │   │       ├── RegulationName
│       │   │       └── ComplianceStatus (badge)
│       │   └── LastAudit (p-3 bg-gray-50 rounded)
│       └── ExpandedView (visible when expanded, border-t pt-4)
│           ├── ComplianceBreakdown (mb-6)
│           │   ├── BreakdownHeader
│           │   ├── RegulationsList (space-y-3)
│           │   │   └── RegulationCard [repeat for each regulation]
│           │   │       ├── RegulationName
│           │   │       ├── ComplianceLevel
│           │   │       ├── LastAssessment
│           │   │       └── Requirements
│           │   └── ComplianceChart (DonutChart)
│           ├── ViolationHistory (mb-6)
│           │   ├── ViolationHeader
│           │   └── ViolationTimeline
│           ├── ComplianceRisks (mb-6)
│           │   ├── RisksHeader
│           │   └── RisksList (space-y-2)
│           │       └── RiskItem [repeat for each risk]
│           └── RegionalCompliance
│               ├── RegionalHeader
│               └── RegionalGrid (grid grid-cols-1 md:grid-cols-2 gap-3)
```

### 10. **Responsive Grid Layout Rules**
```
BentoGridContainer Classes:
- Base: "grid grid-cols-1 gap-6"
- Large screens: "lg:grid-cols-12"

Section Responsive Classes:
- FinanceSection: "lg:col-span-8" (takes 8 columns on large screens)
- TeamSection: "lg:col-span-4" (takes 4 columns on large screens)
- MarketSection: "lg:col-span-6" (takes 6 columns on large screens)
- RiskSection: "lg:col-span-6" (takes 6 columns on large screens)
- SentimentSection: "lg:col-span-4" (takes 4 columns on large screens)
- PartnershipSection: "lg:col-span-4" (takes 4 columns on large screens)
- ComplianceSection: "lg:col-span-4" (takes 4 columns on large screens)

Breakpoint Behavior:
- Mobile (< 768px): All sections stack vertically (grid-cols-1)
- Tablet (768px - 1024px): All sections stack vertically (grid-cols-1)
- Desktop (> 1024px): 12-column grid with specified spans
```

### 11. **Loading State Structure**
```
LoadingState
├── PageWrapper (min-h-screen bg-gray-50 p-6)
│   └── MainContainer (max-w-7xl mx-auto)
│       └── LoadingContent (animate-pulse space-y-6)
│           ├── HeaderSkeleton (h-32 bg-gray-200 rounded-lg)
│           └── CardsSkeleton (grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6)
│               └── CardSkeleton (h-64 bg-gray-200 rounded-lg) [repeat 6 times]
```

### 12. **Error State Structure**
```
ErrorState
├── PageWrapper (min-h-screen bg-gray-50 flex items-center justify-center)
│   └── ErrorContent (text-center)
│       ├── ErrorTitle (text-2xl font-bold text-gray-900 mb-4)
│       ├── ErrorMessage (text-gray-600 mb-6)
│       └── RetryButton (Button component)
```

This complete layout structure provides every component, container, styling class, and responsive behavior needed to implement the bento box company analysis page with no assumptions.