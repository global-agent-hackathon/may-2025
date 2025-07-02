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


class PieBuilder(IBuilder):
    async def plot(self, chart_data: ChartData, company_name: str) -> str:
        fig = self._build_pie_plot(
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
    def _build_pie_plot(data, title=None, x=None, y=None, company_name=None, **kwargs):
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

        # Create the pie chart
        fig = px.pie(
            data,
            names=x,
            values=y,
            title=None,  # We'll set the title in layout for more control
            color_discrete_sequence=custom_colors,
            hole=0.5,  # Slightly larger donut hole for modern look
            **kwargs,
        )

        # Update traces for better appearance
        fig.update_traces(
            textinfo="percent+label",
            textposition="outside",  # Place text outside for cleaner look
            textfont=dict(size=12, family="Inter, Arial, sans-serif"),
            pull=[0.02] * len(data)
            if hasattr(data, "__len__")
            else None,  # Subtle pull
            marker=dict(
                line=dict(color="#fff", width=1.5),  # Thinner white borders
                pattern=dict(shape=""),  # No patterns for clean look
            ),
            hoverinfo="label+percent+value",
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>",
        )

        fig.update_layout(
            # Title configuration
            title={
                # Use string concatenation instead of problematic f-string with backslashes
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
            # Margins and background
            margin=dict(l=20, r=20, t=80, b=80),  # More space at bottom for legend
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            # Additional layout improvements
            uniformtext=dict(minsize=10, mode="hide"),  # Ensure readable text
            showlegend=False,  # Turn off legends
            annotations=[
                dict(
                    text="<b>Total</b>",
                    showarrow=False,
                    font=dict(size=14, family="Inter, Arial, sans-serif"),
                    x=0.5,
                    y=0.5,
                )
            ]
            if hasattr(data, "__len__") and len(data) > 0
            else [],
        )

        return fig


# Test function to demonstrate pie chart
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from backend.settings import get_app_settings
    from backend.agents.netlify import NetlifyAgent

    async def main():
        # Load environment variables
        load_dotenv()
        app_settings = get_app_settings()

        # Create test data
        test_data = pd.DataFrame(
            {
                "category": [
                    "Product Revenue",
                    "Service Revenue",
                    "Consulting",
                    "Training",
                ],
                "amount": [4500000, 2300000, 1800000, 980000],
            }
        )

        # Create chart data
        chart_data = ChartData(
            data=test_data,
            title="Revenue Breakdown",
            x="category",
            y="amount",
            kind="pie",
        )

        # Initialize the builder
        netlify_agent = NetlifyAgent(app_settings.netlify_config)
        pie_builder = PieBuilder(netlify_agent)

        # Generate the plot
        url = await pie_builder.plot(chart_data, company_name="Datagenie AI")
        print(f"\nPie chart generated and uploaded to: {url}")

    # Run the test
    asyncio.run(main())
