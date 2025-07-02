def finance_revenue_to_plot_data(revenue_response):
    """Convert RevenueAnalysisResponse to a list of dicts for plotting."""
    if not revenue_response or not hasattr(revenue_response, "revenue_timeseries"):
        return []
    return [
        {
            "period_start": pt.period_start,
            "period_end": pt.period_end,
            "value": pt.value,
            "currency": pt.currency,
        }
        for pt in revenue_response.revenue_timeseries
    ]


# Add more converters as needed for other response models
