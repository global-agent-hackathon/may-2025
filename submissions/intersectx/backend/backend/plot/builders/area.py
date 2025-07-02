import plotly.express as px
import pandas as pd
import asyncio
import tempfile
import os
import sys

# Handle imports for both module and direct execution
if __name__ == "__main__":
    # Add project root to Python path for direct execution
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    sys.path.insert(0, project_root)
    from backend.plot.types import ChartData
    from backend.plot.builders import IBuilder
else:
    # Normal import when run as part of the package
    from backend.plot.types import ChartData
    from . import IBuilder


class AreaBuilder(IBuilder):
    async def plot(self, chart_data: ChartData, company_name: str) -> str:
        fig = self._build_area_plot(
            chart_data.data,
            title=chart_data.title,
            x=chart_data.x,
            y=chart_data.y,
            company_name=company_name,
        )
        # Save to a temporary HTML file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            fig.write_html(tmp.name, include_plotlyjs="cdn", full_html=True)
            tmp_path = tmp.name
        url = await self.netlify_agent.upload_html(tmp_path)
        return url

    @staticmethod
    def _build_area_plot(data, title=None, x=None, y=None, company_name=None, **kwargs):
        # Use a professionally curated color palette
        custom_colors = [
            "#4285F4",
            "#EA4335",
            "#FBBC05",
            "#34A853",  # Google-inspired colors
            "#1E88E5",
            "#00897B",
            "#7CB342",
            "#FFB300",  # Material design
            "#6741D9",
            "#FF5A5F",
            "#00BCD4",
            "#FF9800",  # Modern web
        ]

        # Create the area chart with improved styling - using fallback if needed
        try:
            # Modern plotly versions have px.area built-in
            fig = px.area(
                data,
                x=x,
                y=y,
                title=None,  # We'll set the title in layout for more control
                template="plotly_white",
                color_discrete_sequence=custom_colors,
                line_shape="spline",  # Smooth curves for modern look
                **kwargs,
            )
        except AttributeError:
            # Fallback for older plotly versions: use line with fill
            fig = px.line(
                data,
                x=x,
                y=y,
                title=None,
                template="plotly_white",
                color_discrete_sequence=custom_colors,
                line_shape="spline",
                **kwargs,
            )
            fig.update_traces(fill="tozeroy")

        # Enhanced styling for area and line
        fig.update_traces(
            line=dict(width=2),  # Slightly thicker line
            marker=dict(
                size=6,
                line=dict(width=1, color="#ffffff"),
                opacity=0.8,
            ),
            # Use semi-transparent fill with matching color
            fillcolor="rgba(66, 133, 244, 0.2)",  # Light blue with transparency
            opacity=0.9,  # Overall opacity
            hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>",
        )

        # Create a professional layout
        fig.update_layout(
            # Title configuration
            title={
                "text": f"<b>{title}</b>",
                "x": 0.5,  # Centered
                "font": {
                    "size": 20,
                    "family": "Inter, Arial, sans-serif",
                    "color": "#212121",
                },
            },
            # Font configuration
            font=dict(family="Inter, Arial, sans-serif", size=12, color="#212121"),
            # Legend configuration
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,  # Move below the chart
                xanchor="center",
                x=0.5,  # Center aligned
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#E0E0E0",
                borderwidth=1,
                font=dict(size=11),
            ),
            # Axis styling
            xaxis=dict(
                showgrid=True,
                gridcolor="#F0F0F0",
                gridwidth=0.5,
                title=dict(
                    text=x.capitalize() if x else "",
                    font=dict(size=14, family="Inter, Arial, sans-serif"),
                ),
                tickfont=dict(size=12, family="Inter, Arial, sans-serif"),
                zeroline=False,
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#F0F0F0",
                gridwidth=0.5,
                title=dict(
                    text=y.capitalize() if y else "",
                    font=dict(size=14, family="Inter, Arial, sans-serif"),
                ),
                tickfont=dict(size=12, family="Inter, Arial, sans-serif"),
                zeroline=False,
                # Add thousands separator for large numbers
                tickformat=",.0f",
            ),
            # Other layout improvements
            hovermode="closest",
            margin=dict(l=40, r=40, t=80, b=80),  # More space for title and axis labels
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
        )

        return fig


# Test function to demonstrate area chart
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from backend.settings import get_app_settings
    from backend.agents.netlify import NetlifyAgent

    async def main():
        # Load environment variables
        load_dotenv()
        app_settings = get_app_settings()

        # Create test data with multiple series for a gradient-like effect
        dates = pd.date_range(start="2024-01-01", periods=12, freq="ME").strftime(
            "%Y-%m-%d"
        )

        # Create test data with two series by combining dataframes
        df1 = pd.DataFrame(
            {
                "date": dates,
                "metric": "Revenue",
                "value": [
                    45,
                    52,
                    61,
                    72,
                    86,
                    103,
                    125,
                    141,
                    168,
                    189,
                    210,
                    240,
                ],  # in thousands
            }
        )

        df2 = pd.DataFrame(
            {
                "date": dates,
                "metric": "Users",
                "value": [
                    12,
                    15,
                    18,
                    23,
                    29,
                    36,
                    45,
                    51,
                    62,
                    74,
                    81,
                    95,
                ],  # in hundreds
            }
        )

        # Combine the dataframes
        test_data = pd.concat([df1, df2], ignore_index=True)

        # Create chart data with color differentiation
        chart_data = ChartData(
            data=test_data,
            title="Growth Metrics",
            x="date",
            y="value",
            kind="area",
            # Additional parameters to pass to px.area
            **{
                "color": "metric",
                "color_discrete_map": {"Revenue": "#4285F4", "Users": "#34A853"},
            },
        )

        # Initialize the builder
        netlify_agent = NetlifyAgent(app_settings.netlify_config)
        area_builder = AreaBuilder(netlify_agent)

        # Generate the plot
        url = await area_builder.plot(chart_data, company_name="Datagenie AI")
        print(f"\nArea chart generated and uploaded to: {url}")

    # Run the test
    asyncio.run(main())
