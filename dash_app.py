from pathlib import Path
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# File paths
APP_DIR = Path(__file__).resolve().parent
COMPANY_FILE = APP_DIR / "sp500_companies.csv"
PRICE_FILE = APP_DIR / "sp500_data.csv"

PLOT_BG = "#141b2d"
PLOT_TEXT = "#edf2f7"

# creatae helper functions for mapping state abbreviations to names and centers for the map visualization
def state_abbrev_to_name():
    return {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
        "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
        "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
        "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
        "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
        "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
        "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
        "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
        "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
        "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
        "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
    }


def state_centers():
    return {
        "AL": (32.806671, -86.791130),
        "AK": (61.370716, -152.404419),
        "AZ": (33.729759, -111.431221),
        "AR": (34.969704, -92.373123),
        "CA": (36.116203, -119.681564),
        "CO": (39.059811, -105.311104),
        "CT": (41.597782, -72.755371),
        "DE": (39.318523, -75.507141),
        "FL": (27.766279, -81.686783),
        "GA": (33.040619, -83.643074),
        "HI": (21.094318, -157.498337),
        "ID": (44.240459, -114.478828),
        "IL": (40.349457, -88.986137),
        "IN": (39.849426, -86.258278),
        "IA": (42.011539, -93.210526),
        "KS": (38.526600, -96.726486),
        "KY": (37.668140, -84.670067),
        "LA": (31.169546, -91.867805),
        "ME": (44.693947, -69.381927),
        "MD": (39.063946, -76.802101),
        "MA": (42.230171, -71.530106),
        "MI": (43.326618, -84.536095),
        "MN": (45.694454, -93.900192),
        "MS": (32.741646, -89.678696),
        "MO": (38.456085, -92.288368),
        "MT": (46.921925, -110.454353),
        "NE": (41.125370, -98.268082),
        "NV": (38.313515, -117.055374),
        "NH": (43.452492, -71.563896),
        "NJ": (40.298904, -74.521011),
        "NM": (34.840515, -106.248482),
        "NY": (42.165726, -74.948051),
        "NC": (35.630066, -79.806419),
        "ND": (47.528912, -99.784012),
        "OH": (40.388783, -82.764915),
        "OK": (35.565342, -96.928917),
        "OR": (44.572021, -122.070938),
        "PA": (40.590752, -77.209755),
        "RI": (41.680893, -71.511780),
        "SC": (33.856892, -80.945007),
        "SD": (44.299782, -99.438828),
        "TN": (35.747845, -86.692345),
        "TX": (31.054487, -97.563461),
        "UT": (40.150032, -111.862434),
        "VT": (44.045876, -72.710686),
        "VA": (37.769337, -78.169968),
        "WA": (47.400902, -121.490494),
        "WV": (38.491226, -80.954453),
        "WI": (44.268543, -89.616508),
        "WY": (42.755966, -107.302490),
        "DC": (38.9072, -77.0369),
    }


def shorten_company_name(name: str, max_len: int = 28) -> str:
    if pd.isna(name):
        return ""
    name = str(name)
    replacements = {
        "Corporation": "Corp.",
        "Incorporated": "Inc.",
        "Company": "Co.",
        "Technologies": "Tech.",
        "International": "Intl.",
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name if len(name) <= max_len else name[: max_len - 1] + "…"


def safe_company_name(company, ticker):
    if pd.notna(company) and str(company).strip():
        return str(company)
    return str(ticker)


def wrap_company_list(names, per_line=4):
    if not names:
        return "No S&P 500 headquarters in this state"
    rows = []
    for i in range(0, len(names), per_line):
        rows.append(", ".join(names[i:i + per_line]))
    return "<br>".join(rows)


def format_billions(value):
    if pd.isna(value):
        return "N/A"
    return f"${value / 1_000_000_000:,.1f}B"


def format_millions(value):
    if pd.isna(value):
        return "N/A"
    return f"${value / 1_000_000:,.1f}M"


def format_percent(value):
    if pd.isna(value):
        return "N/A"
    return f"{value * 100:,.1f}%"


def format_volume(value):
    if pd.isna(value):
        return "N/A"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:,.1f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:,.1f}M"
    return f"{value:,.0f}"


def apply_dark_figure_style(fig, title=None):
    if title is not None:
        fig.update_layout(title=title)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font_color=PLOT_TEXT,
        margin=dict(l=30, r=30, t=70, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=12),
        ),
        title_font=dict(size=24),
        hoverlabel=dict(
            bgcolor="#111827",
            bordercolor="#3b4252",
            font=dict(color="white", size=13),
        ),
    )
    return fig


def empty_figure(message):
    fig = px.scatter(title=message)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return apply_dark_figure_style(fig)


# Load and clean data
companies = pd.read_csv(
    COMPANY_FILE,
    usecols=[
        "Exchange", "Symbol", "Shortname", "Longname", "Sector", "Industry",
        "Currentprice", "Marketcap", "Ebitda", "Revenuegrowth",
        "City", "State", "Country", "Fulltimeemployees",
        "Longbusinesssummary", "Weight"
    ],
    low_memory=False
)

companies = companies.rename(columns={
    "Exchange": "exchange",
    "Symbol": "ticker",
    "Shortname": "company",
    "Longname": "longname",
    "Sector": "sector",
    "Industry": "industry",
    "Currentprice": "current_price",
    "Marketcap": "market_cap",
    "Ebitda": "ebitda",
    "Revenuegrowth": "revenue_growth",
    "City": "city",
    "State": "state",
    "Country": "country",
    "Fulltimeemployees": "full_time_employees",
    "Longbusinesssummary": "business_summary",
    "Weight": "weight",
})

prices = pd.read_csv(
    PRICE_FILE,
    usecols=[
        "Date", "Ticker", "Adj Close", "Close",
        "High", "Low", "Open", "Volume 1962-01-02"
    ],
    low_memory=False
)

prices = prices.rename(columns={
    "Date": "date",
    "Ticker": "ticker",
    "Adj Close": "adj_close",
    "Close": "close",
    "High": "high",
    "Low": "low",
    "Open": "open",
    "Volume 1962-01-02": "volume",
})

prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
prices["ticker"] = prices["ticker"].astype(str).str.strip()
companies["ticker"] = companies["ticker"].astype(str).str.strip()

for col in ["adj_close", "close", "high", "low", "open", "volume"]:
    prices[col] = pd.to_numeric(prices[col], errors="coerce")

for col in ["current_price", "market_cap", "ebitda", "revenue_growth", "full_time_employees", "weight"]:
    companies[col] = pd.to_numeric(companies[col], errors="coerce")

companies["state"] = companies["state"].astype(str).str.upper().str.strip()
companies["company"] = companies["company"].fillna(companies["longname"])
companies["company_display"] = companies.apply(
    lambda row: safe_company_name(row["company"], row["ticker"]), axis=1
)
companies["company_short"] = companies["company_display"].apply(shorten_company_name)

prices = prices.dropna(subset=["date", "ticker", "adj_close"]).copy()

df = prices.merge(companies, on="ticker", how="left")
df = df.sort_values(["ticker", "date"]).copy()
df["daily_return"] = df.groupby("ticker")["adj_close"].pct_change()
df["normalized_price"] = 100 * df["adj_close"] / df.groupby("ticker")["adj_close"].transform("first")
df["year"] = df["date"].dt.year
df["company_display"] = df.apply(lambda row: safe_company_name(row["company"], row["ticker"]), axis=1)
df["company_short"] = df["company_display"].apply(shorten_company_name)

yearly_last = (
    df.sort_values(["ticker", "year", "date"])
      .groupby(["ticker", "year"], as_index=False)
      .tail(1)
      .copy()
)

all_sectors = sorted(df["sector"].dropna().unique().tolist())
all_tickers = sorted(df["ticker"].dropna().unique().tolist())
default_tickers = [t for t in ["AAPL", "MSFT", "AMZN", "GOOGL", "NVDA"] if t in all_tickers]
if len(default_tickers) < 5:
    default_tickers = all_tickers[:5]

min_date = df["date"].min()
max_date = df["date"].max()
default_start = max(min_date, pd.Timestamp("1990-01-01"))

ticker_options = []
for t in all_tickers:
    match = companies.loc[companies["ticker"] == t, "company_display"]
    company_name = match.iloc[0] if not match.empty else t
    ticker_options.append({"label": f"{company_name} ({t})", "value": t})

top_metric_options = [
    {"label": "Market cap", "value": "market_cap"},
    {"label": "Return over selected period", "value": "period_return"},
    {"label": "Volatility", "value": "volatility"},
    {"label": "Average trading volume", "value": "avg_volume"},
]

map_metric_options = [
    {"label": "Company count", "value": "company_count"},
    {"label": "Total market cap", "value": "total_market_cap"},
    {"label": "Average market cap", "value": "avg_market_cap"},
]

# Apply dark style to any figures created before the app runs
app = Dash(__name__)
server = app.server
app.title = "Driving Factors of the S&P 500"

app.layout = html.Div(
    className="app-shell",
    children=[
        html.Div(
            className="hero-block",
            children=[
                html.H1("Driving Factors of the S&P 500", className="hero-title"),
                html.P("Author: Suhas Makineni", className="hero-author"),
                html.P(
                    "This dashboard explains the S&P 500 through four connected ideas: where major firms are concentrated, which companies dominate leadership over time, how firms rank by size and performance, and how risk and return differ across the market.",
                    className="hero-subtitle",
                ),
            ],
        ),

        html.Div(
            className="kpi-grid",
            children=[
                html.Div(className="kpi-card", children=[
                    html.P("Companies in view", className="kpi-label"),
                    html.H2(id="kpi-companies", className="kpi-value"),
                    html.P("Filtered by sector and date range", className="kpi-subtext"),
                ]),
                html.Div(className="kpi-card", children=[
                    html.P("Top sector in view", className="kpi-label"),
                    html.H2(id="kpi-top-sector", className="kpi-value kpi-value-small"),
                    html.P(id="kpi-top-sector-sub", className="kpi-subtext"),
                ]),
                html.Div(className="kpi-card", children=[
                    html.P("Largest company", className="kpi-label"),
                    html.H2(id="kpi-largest-company", className="kpi-value kpi-value-small"),
                    html.P(id="kpi-largest-company-sub", className="kpi-subtext"),
                ]),
                html.Div(className="kpi-card", children=[
                    html.P("Best performer", className="kpi-label"),
                    html.H2(id="kpi-best-performer", className="kpi-value kpi-value-small"),
                    html.P(id="kpi-best-performer-sub", className="kpi-subtext"),
                ]),
            ],
        ),

        html.Div(className="section-gap"),

        html.Div(
            className="card card-large",
            children=[
                html.H2("Where Is S&P 500 Influence Concentrated?", className="section-title"),
                html.P(
                    "This map opens the story by showing how market influence is concentrated across a relatively small number of states. Switch the metric to compare simple headquarters counts with total or average market capitalization by state.",
                    className="visual-description",
                ),
                html.Div(
                    className="top-controls-row",
                    children=[
                        html.Div(
                            className="top-control-box",
                            children=[
                                html.Label("Map metric", className="control-label"),
                                dcc.Dropdown(
                                    id="map-metric-dropdown",
                                    className="dash-dropdown",
                                    options=map_metric_options,
                                    value="company_count",
                                    clearable=False,
                                ),
                            ],
                        ),
                    ],
                ),
                dcc.Graph(id="state-map", style={"height": "720px"}),
            ],
        ),

        html.Div(className="section-gap"),

        html.Div(
            className="card card-large",
            children=[
                html.H2("Which Companies Lead by the Selected Metric?", className="section-title"),
                html.P(
                    "This ranking chart gives a fast read on leadership in the filtered view. It helps separate companies that dominate by sheer size from those that stand out for return, volatility, or trading activity.",
                    className="visual-description",
                ),
                html.Div(
                    className="top-controls-row",
                    children=[
                        html.Div(
                            className="top-control-box",
                            children=[
                                html.Label("Rank companies by", className="control-label"),
                                dcc.Dropdown(
                                    id="top-metric-dropdown",
                                    className="dash-dropdown",
                                    options=top_metric_options,
                                    value="market_cap",
                                    clearable=False,
                                ),
                            ],
                        ),
                    ],
                ),
                dcc.Graph(id="top-companies-bar", style={"height": "560px"}),
            ],
        ),

        html.Div(className="section-gap"),

        html.Div(
            className="story-grid",
            children=[
                html.Div(
                    className="controls-panel",
                    children=[
                        html.H3("Explore the comparison", className="panel-title"),
                        html.P(
                            "Use these filters to move from broad market structure to firm-level comparison.",
                            className="panel-description",
                        ),
                        html.P(
                            "Best use case: compare around 5–10 similarly sized companies for the clearest animation and line-chart story.",
                            className="panel-note",
                        ),

                        html.Div(
                            className="control-block",
                            children=[
                                html.Label("Sector filter", className="control-label"),
                                dcc.Dropdown(
                                    id="sector-dropdown",
                                    className="dash-dropdown",
                                    options=[{"label": "All sectors", "value": "ALL"}] +
                                            [{"label": s, "value": s} for s in all_sectors],
                                    value="ALL",
                                    clearable=False,
                                ),
                            ],
                        ),

                        html.Div(
                            className="control-block",
                            children=[
                                html.Label("Companies to compare", className="control-label"),
                                dcc.Dropdown(
                                    id="ticker-dropdown",
                                    className="dash-dropdown",
                                    options=ticker_options,
                                    value=default_tickers,
                                    multi=True,
                                    placeholder="Select companies",
                                ),
                            ],
                        ),

                    ],
                ),

                html.Div(
                    className="card card-large animation-card",
                    children=[
                        html.H2("How Do Selected Companies Trade Leadership Year by Year?", className="section-title"),
                        html.P(
                            "This animation compares selected firms on a shared indexed scale. The log x-axis is appropriate because stock growth compounds multiplicatively, so equal proportional gains are more meaningful than equal raw-value gaps.",
                            className="visual-description",
                        ),
                        dcc.Graph(id="company-animation", style={"height": "720px"}),
                        html.P(id="animation-note", className="note-text"),
                    ],
                ),
            ],
        ),

        html.Div(className="section-gap"),

        html.Div(
        className="card card-large",
        children=[
            html.H2("How Do Selected Companies Compare Over Time?", className="section-title"),
            html.P(
            "This indexed line chart shows the full path of the selected companies. It turns the animated snapshots into a continuous story of divergence, catch-up, and sustained leadership.",
            className="visual-description",
        ),

        html.Div(
            className="top-controls-row comparison-date-row",
            children=[
                html.Div(
                    className="top-control-box comparison-date-box",
                    children=[
                        html.Label("Date range", className="control-label"),
                        dcc.DatePickerRange(
                            id="date-range",
                            start_date=default_start,
                            end_date=max_date,
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            display_format="YYYY-MM-DD",
                            clearable=False,
                        ),
                    ],
                ),
            ],
        ),

        dcc.Graph(id="comparison-line", style={"height": "650px"}),
    ],
),

        html.Div(className="section-gap"),

        html.Div(
            className="card card-large",
            children=[
                html.H2("How Does Risk Relate to Return Across Firms?", className="section-title"),
                html.P(
                    "This scatter plot compares return and volatility over the selected period. A log-scaled volatility axis spreads firms out for easier reading, while bubble size reflects average trading volume and helps highlight which names attract the most market attention.",
                    className="visual-description",
                ),
                dcc.Graph(id="risk-return-scatter", style={"height": "600px"}),
            ],
        ),

        html.Div(className="section-gap"),

        html.Div(
            className="footer-note",
            children=[
                html.P(
                    "Source: S&P 500 company fundamentals and historical price data used from Kaggle. "
                    "All figures update dynamically based on the selected sector, date range, and company filters. "
                    f"Underlying price history in this dashboard spans {min_date.date()} to {max_date.date()}."
                )
            ],
        ),
    ],
)

# Callbacks for interactivity
@app.callback(
    Output("state-map", "figure"),
    Input("sector-dropdown", "value"),
    Input("map-metric-dropdown", "value"),
)
def update_map(selected_sector, selected_map_metric):
    company_subset = companies.copy()

    if selected_sector != "ALL":
        company_subset = company_subset[company_subset["sector"] == selected_sector]

    grouped = (
        company_subset.drop_duplicates(subset=["ticker"])
        .dropna(subset=["state"])
        .groupby("state", as_index=False)
        .agg(
            company_count=("ticker", "nunique"),
            total_market_cap=("market_cap", "sum"),
            avg_market_cap=("market_cap", "mean"),
            company_names=("company_display", lambda s: sorted(set(s.dropna().tolist())))
        )
    )

    all_states = pd.DataFrame({"state": list(state_centers().keys())})
    grouped = all_states.merge(grouped, on="state", how="left")
    grouped["company_count"] = grouped["company_count"].fillna(0).astype(int)
    grouped["total_market_cap"] = grouped["total_market_cap"].fillna(0)
    grouped["avg_market_cap"] = grouped["avg_market_cap"].fillna(0)
    grouped["company_names"] = grouped["company_names"].apply(
        lambda x: x if isinstance(x, list) else []
    )
    grouped["state_name"] = grouped["state"].map(state_abbrev_to_name())
    grouped["company_names_hover"] = grouped["company_names"].apply(
        lambda x: wrap_company_list(x) if len(x) > 0 else "No S&P 500 headquarters in this state"
    )

    centers = state_centers()
    grouped["lat"] = grouped["state"].map(lambda s: centers[s][0])
    grouped["lon"] = grouped["state"].map(lambda s: centers[s][1])

    metric_labels = {
        "company_count": "Company count",
        "total_market_cap": "Total market cap",
        "avg_market_cap": "Average market cap",
    }

    if selected_map_metric == "company_count":
        hover_metric_text = grouped["company_count"].map(lambda x: f"{x:,}")
        colorbar_title = "Company count"
        range_max = max(1, grouped["company_count"].max())
    elif selected_map_metric == "total_market_cap":
        hover_metric_text = grouped["total_market_cap"].map(format_billions)
        colorbar_title = "Total market cap"
        range_max = max(1, grouped["total_market_cap"].max())
    else:
        hover_metric_text = grouped["avg_market_cap"].map(format_billions)
        colorbar_title = "Average market cap"
        range_max = max(1, grouped["avg_market_cap"].max())

    grouped["map_metric_text"] = hover_metric_text

    fig = px.choropleth(
        grouped,
        locations="state",
        locationmode="USA-states",
        color=selected_map_metric,
        scope="usa",
        color_continuous_scale=[
            [0.00, "#e6f0ff"],
            [0.20, "#bfd7ff"],
            [0.40, "#8bbcff"],
            [0.60, "#5e9cff"],
            [0.80, "#356fd8"],
            [1.00, "#173b8f"],
        ],
        range_color=(0, range_max),
        labels={selected_map_metric: metric_labels[selected_map_metric]},
        custom_data=["state_name", "map_metric_text", "company_names_hover"],
        title=None,
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            f"{metric_labels[selected_map_metric]}: %{{customdata[1]}}<br><br>"
            "<b>Companies:</b><br>%{customdata[2]}"
            "<extra></extra>"
        )
    )

    fig.add_scattergeo(
        lon=grouped["lon"],
        lat=grouped["lat"],
        mode="markers",
        marker=dict(size=14, opacity=0),
        customdata=grouped[["state_name", "map_metric_text", "company_names_hover"]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            f"{metric_labels[selected_map_metric]}: %{{customdata[1]}}<br><br>"
            "<b>Companies:</b><br>%{customdata[2]}"
            "<extra></extra>"
        ),
        showlegend=False,
    )

    fig.update_layout(
        coloraxis_colorbar=dict(
            title=dict(
                text=colorbar_title,
                font=dict(size=14),
            ),
            tickfont=dict(size=12),
            len=0.8,
        ),
        geo=dict(
            bgcolor=PLOT_BG,
            lakecolor=PLOT_BG,
            showlakes=False,
            showframe=False,
            showcoastlines=False,
            projection_type="albers usa",
        ),
    )

    return apply_dark_figure_style(fig)


@app.callback(
    Output("kpi-companies", "children"),
    Output("kpi-top-sector", "children"),
    Output("kpi-top-sector-sub", "children"),
    Output("kpi-largest-company", "children"),
    Output("kpi-largest-company-sub", "children"),
    Output("kpi-best-performer", "children"),
    Output("kpi-best-performer-sub", "children"),
    Output("top-companies-bar", "figure"),
    Input("sector-dropdown", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("top-metric-dropdown", "value"),
)
def update_kpis_and_top_chart(selected_sector, start_date, end_date, selected_metric):
    filtered = df[
        (df["date"] >= pd.to_datetime(start_date)) &
        (df["date"] <= pd.to_datetime(end_date))
    ].copy()

    if selected_sector != "ALL":
        filtered = filtered[filtered["sector"] == selected_sector]

    summary = (
        filtered.sort_values(["ticker", "date"])
        .groupby(["ticker", "company_display", "sector"], as_index=False)
        .agg(
            period_return=("adj_close", lambda s: s.iloc[-1] / s.iloc[0] - 1 if len(s) > 1 else pd.NA),
            volatility=("daily_return", "std"),
            avg_volume=("volume", "mean"),
            market_cap=("market_cap", "last"),
        )
        .dropna(subset=["market_cap"], how="all")
    )

    n_companies = summary["ticker"].nunique() if not summary.empty else 0

    if summary.empty:
        fig = empty_figure("No company ranking data available for this selection.")
        return (
            "0",
            "N/A",
            "No sector composition available",
            "N/A",
            "No market-cap data available",
            "N/A",
            "No return data available",
            fig,
        )

    sector_counts = (
        summary.dropna(subset=["sector"])
        .groupby("sector", as_index=False)
        .agg(company_count=("ticker", "nunique"))
        .sort_values("company_count", ascending=False)
    )
    if sector_counts.empty:
        top_sector_name = "N/A"
        top_sector_sub = "No sector composition available"
    else:
        top_sector_name = sector_counts.iloc[0]["sector"]
        top_sector_sub = f"{sector_counts.iloc[0]['company_count']} companies in current view"

    largest_row = summary.dropna(subset=["market_cap"]).sort_values("market_cap", ascending=False).head(1)
    if largest_row.empty:
        largest_name = "N/A"
        largest_sub = "No market-cap data available"
    else:
        largest_name = shorten_company_name(largest_row.iloc[0]["company_display"], max_len=22)
        largest_sub = f"Market cap: {format_billions(largest_row.iloc[0]['market_cap'])}"

    best_row = summary.dropna(subset=["period_return"]).sort_values("period_return", ascending=False).head(1)
    if best_row.empty:
        best_name = "N/A"
        best_sub = "No return data available"
    else:
        best_name = shorten_company_name(best_row.iloc[0]["company_display"], max_len=22)
        best_sub = f"Return: {format_percent(best_row.iloc[0]['period_return'])}"

    metric_labels = {
        "market_cap": "Market cap",
        "period_return": "Return over selected period",
        "volatility": "Volatility",
        "avg_volume": "Average trading volume",
    }

    chart_df = summary.dropna(subset=[selected_metric]).copy()
    chart_df = chart_df.sort_values(selected_metric, ascending=False).head(10).copy()
    chart_df["company_short"] = chart_df["company_display"].apply(lambda x: shorten_company_name(x, max_len=28))
    chart_df = chart_df.sort_values(selected_metric, ascending=True)

    if chart_df.empty:
        fig = empty_figure("No ranking data available for this metric.")
    else:
        fig = px.bar(
            chart_df,
            x=selected_metric,
            y="company_short",
            color="sector",
            orientation="h",
            hover_name="company_display",
            hover_data={
                "ticker": True,
                "market_cap": ":,.0f",
                "period_return": ":.2%",
                "volatility": ":.4f",
                "avg_volume": ":,.0f",
            },
            labels={
                selected_metric: metric_labels[selected_metric],
                "company_short": "Company",
            },
            title=None,
        )

        fig.update_traces(marker_line_width=0)

        if selected_metric == "period_return":
            fig.update_xaxes(tickformat=".0%")

        fig.update_xaxes(
            gridcolor="#263042",
            tickfont=dict(size=13),
            title_font=dict(size=15),
        )
        fig.update_yaxes(
            tickfont=dict(size=13),
            title_font=dict(size=15),
        )

        fig = apply_dark_figure_style(fig)

    return (
        f"{n_companies:,}",
        top_sector_name,
        top_sector_sub,
        largest_name,
        largest_sub,
        best_name,
        best_sub,
        fig,
    )


@app.callback(
    Output("company-animation", "figure"),
    Output("animation-note", "children"),
    Input("sector-dropdown", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("ticker-dropdown", "value"),
)
def update_company_animation(selected_sector, start_date, end_date, selected_tickers):
    if not selected_tickers:
        return empty_figure("Select at least one company to animate."), (
            "This chart compares selected companies on a common indexed scale."
        )

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    anim_df = yearly_last[
        (yearly_last["date"] >= start_date) &
        (yearly_last["date"] <= end_date) &
        (yearly_last["ticker"].isin(selected_tickers))
    ].copy()

    if selected_sector != "ALL":
        anim_df = anim_df[anim_df["sector"] == selected_sector]

    if anim_df.empty:
        return empty_figure("No animation data available for the selected companies."), (
            "Try widening the date range or choosing companies within the selected sector."
        )

    first_dates = (
        anim_df.groupby("ticker", as_index=False)["date"]
        .min()
        .rename(columns={"date": "first_date"})
    )

    if first_dates.empty:
        return empty_figure("No animation data available for the selected companies."), (
            "Try widening the date range or choosing different companies."
        )

    common_start = first_dates["first_date"].max()
    anim_df = anim_df[anim_df["date"] >= common_start].copy()

    if anim_df.empty:
        return empty_figure("No overlapping date range for the selected companies."), (
            "These companies do not share enough overlapping history in the selected window."
        )

    anim_df = anim_df.sort_values(["ticker", "date"]).copy()
    anim_df["animation_index"] = (
        100 * anim_df["adj_close"] /
        anim_df.groupby("ticker")["adj_close"].transform("first")
    )

    anim_df["company_display"] = anim_df.apply(
        lambda row: safe_company_name(row["company"], row["ticker"]), axis=1
    )
    anim_df["company_short"] = anim_df["company_display"].apply(
        lambda x: shorten_company_name(x, max_len=24)
    )

    anim_df = anim_df.sort_values(
        ["year", "animation_index"], ascending=[True, False]
    ).copy()

    x_max = anim_df["animation_index"].max()
    if pd.isna(x_max) or x_max <= 0:
        x_max = 100
    x_upper = x_max * 1.20

    fig = px.bar(
        anim_df,
        x="animation_index",
        y="company_short",
        color="company_display",
        animation_frame="year",
        orientation="h",
        hover_name="company_display",
        hover_data={
            "ticker": True,
            "animation_index": ":,.0f",
            "sector": True,
            "adj_close": ":.2f",
        },
        labels={
            "animation_index": "Indexed price (common start = 100)",
            "company_short": "Company",
            "company_display": "Company",
        },
        title=None,
    )

    fig.update_traces(
        text=None,
        marker_line_width=0,
        cliponaxis=False,
    )

    tick_vals = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000]
    tick_vals = [v for v in tick_vals if v <= x_upper]

    if len(tick_vals) < 2:
        tick_vals = [100, max(200, round(x_upper))]

    tick_text_map = {
        100: "100",
        200: "200",
        500: "500",
        1000: "1k",
        2000: "2k",
        5000: "5k",
        10000: "10k",
        20000: "20k",
        50000: "50k",
        100000: "100k",
        200000: "200k",
        500000: "500k",
    }
    tick_text = [tick_text_map.get(v, f"{int(v):,}") for v in tick_vals]

    fig.update_layout(
        height=700,
        showlegend=False,
        margin=dict(l=150, r=70, t=20, b=170),
        bargap=0.18,
    )

    fig.update_xaxes(
        type="log",
        range=[np.log10(100), np.log10(x_upper)],
        tickmode="array",
        tickvals=tick_vals,
        ticktext=tick_text,
        title=dict(
            text="Indexed price (log scale, common start = 100)",
            standoff=18,
            font=dict(size=16),
        ),
        gridcolor="#263042",
        zeroline=False,
        tickfont=dict(size=14),
        minorloglabels="none",
    )

    fig.update_yaxes(
        automargin=True,
        tickfont=dict(size=15),
        title_font=dict(size=16),
    )

    if fig.layout.updatemenus:
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1200
        fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 500
        fig.layout.updatemenus[0]["x"] = 0.02
        fig.layout.updatemenus[0]["y"] = -0.22
        fig.layout.updatemenus[0]["xanchor"] = "left"
        fig.layout.updatemenus[0]["yanchor"] = "top"
        fig.layout.updatemenus[0]["pad"] = {"t": 0, "r": 10}

    if fig.layout.sliders:
        fig.layout.sliders[0]["pad"] = {"t": 58}
        fig.layout.sliders[0]["len"] = 0.76
        fig.layout.sliders[0]["x"] = 0.16
        fig.layout.sliders[0]["y"] = -0.16
        fig.layout.sliders[0]["currentvalue"] = {
            "prefix": "Year: ",
            "font": {"size": 16},
            "xanchor": "right",
            "offset": 12,
        }

    fig = apply_dark_figure_style(fig)

    note = (
        f"This animation starts at the earliest date shared by all selected companies "
        f"({common_start.date()}). Each company is re-indexed to 100 at that shared starting point. "
        f"The log scale matters because market leadership is usually driven by proportional compounding, "
        f"not raw-dollar spacing, so it preserves relative growth differences without letting one outlier flatten the rest."
    )

    return fig, note


@app.callback(
    Output("risk-return-scatter", "figure"),
    Output("comparison-line", "figure"),
    Input("sector-dropdown", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("ticker-dropdown", "value"),
)
def update_main_charts(selected_sector, start_date, end_date, selected_tickers):
    filtered = df[
        (df["date"] >= pd.to_datetime(start_date)) &
        (df["date"] <= pd.to_datetime(end_date))
    ].copy()

    if selected_sector != "ALL":
        filtered = filtered[filtered["sector"] == selected_sector]

    scatter_summary = (
        filtered.sort_values(["ticker", "date"])
        .groupby(["ticker", "company_display", "sector"], as_index=False)
        .agg(
            period_return=("adj_close", lambda s: s.iloc[-1] / s.iloc[0] - 1 if len(s) > 1 else pd.NA),
            volatility=("daily_return", "std"),
            avg_volume=("volume", "mean"),
            market_cap=("market_cap", "last"),
        )
        .dropna(subset=["period_return", "volatility"])
    )

    if scatter_summary.empty:
        scatter = empty_figure("No data available for risk versus return.")
    else:
        scatter = px.scatter(
            scatter_summary,
            x="volatility",
            y="period_return",
            color="sector",
            size="avg_volume",
            size_max=20,
            opacity=0.75,
            hover_name="company_display",
            hover_data={
                "ticker": True,
                "volatility": ":.4f",
                "period_return": ":.2%",
                "avg_volume": ":,.0f",
                "market_cap": ":,.0f",
            },
            labels={
                "volatility": "Volatility (log scale)",
                "period_return": "Return over selected period",
            },
            title=None,
        )

        scatter.update_traces(marker=dict(line=dict(width=0)))

        scatter.update_xaxes(
            type="log",
            tickfont=dict(size=13),
            title_font=dict(size=15),
            gridcolor="#263042",
        )
        scatter.update_yaxes(
            tickfont=dict(size=13),
            title_font=dict(size=15),
            gridcolor="#263042",
        )
        scatter = apply_dark_figure_style(scatter)

    if not selected_tickers:
        selected_tickers = default_tickers

    line_df = filtered[filtered["ticker"].isin(selected_tickers)].copy()

    if line_df.empty:
        line = empty_figure("No data available for the selected companies.")
    else:
        line_df = line_df.sort_values(["ticker", "date"]).copy()
        line_df["line_index"] = (
            100 * line_df["adj_close"] /
            line_df.groupby("ticker")["adj_close"].transform("first")
        )

        line = px.line(
        line_df,
        x="date",
        y="line_index",
        color="company_display",
        labels={
            "date": "Date",
            "line_index": "Indexed price (start = 100)",
            "company_display": "Company",
        },
        hover_data={"ticker": True, "adj_close": ":.2f"},
        title=None,
    )
    line.update_xaxes(tickfont=dict(size=13), title_font=dict(size=15))
    line.update_yaxes(tickfont=dict(size=13), title_font=dict(size=15))
    line = apply_dark_figure_style(line)

    return scatter, line


if __name__ == "__main__":
    app.run(debug=True)