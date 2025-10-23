import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import calendar
from utils.data_loader import load_data_from_azure
from utils.sidebar import create_sidebar

st.set_page_config(page_title="Trend Analysis - UK Crime Analytics", layout="wide")

# Get filters from sidebar
filters = create_sidebar()

st.title("📈 Crime Trends & Time Analysis")

# Load data
with st.spinner("Loading time series data..."):
    data = load_data_from_azure(verbose=False)

if not data or all(df.empty for df in data.values()):
    st.error("Failed to load data")
    st.stop()

# Apply filters function
def apply_filters(df, filters):
    filtered_df = df.copy()
    
    if filters.get('police_force') and filters['police_force'] != "All Forces":
        if 'force_name' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['force_name'] == filters['police_force']]
    
    if filters.get('time_period') and filters['time_period'] != "All Periods":
        if 'month' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['month'] == filters['time_period']]
    
    if filters.get('crime_types'):
        if 'crime_type' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['crime_type'].isin(filters['crime_types'])]
    
    if filters.get('severity_level'):
        if 'severity_level' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['severity_level'].isin(filters['severity_level'])]
    
    return filtered_df

# Get and filter data
crime_incidents = data.get('crime_incidents', pd.DataFrame())
crime_trends = data.get('crime_trends', pd.DataFrame())

if crime_incidents.empty:
    st.warning("No incident data available for trend analysis")
    st.stop()

filtered_incidents = apply_filters(crime_incidents, filters)

st.success(f"📊 Analyzing {len(filtered_incidents):,} incidents over time")

# Time series analysis controls
st.sidebar.markdown("---")
st.sidebar.subheader("📈 Analysis Settings")

time_granularity = st.sidebar.selectbox(
    "Time Granularity",
    ["Daily", "Weekly", "Monthly"],
    index=2
)

show_forecast = st.sidebar.checkbox("Show 30-day forecast", value=False)
show_moving_avg = st.sidebar.checkbox("Show Moving Averages", value=True)

# Prepare time series data
def prepare_time_series_data(df):
    """Convert incident data to time series format"""
    
    # Ensure we have a date column
    date_column = None
    for col in ['date', 'reported_date', 'month', 'incident_date']:
        if col in df.columns:
            date_column = col
            break
    
    if not date_column:
        st.error("No date column found in data")
        return pd.DataFrame()
    
    # Convert to datetime
    df['date'] = pd.to_datetime(df[date_column], errors='coerce')
    df = df.dropna(subset=['date'])
    
    return df

ts_data = prepare_time_series_data(filtered_incidents)

if ts_data.empty:
    st.error("No valid time series data available after filtering")
    st.stop()

# 1. TIME SERIES AREA CHART WITH MOVING AVERAGES
st.subheader("📈 Crime Trends Over Time")

# Aggregate by selected granularity
if time_granularity == "Daily":
    ts_agg = ts_data.groupby('date').size().reset_index(name='incidents')
    ts_agg = ts_agg.sort_values('date')
    
    # Calculate moving averages
    if show_moving_avg:
        ts_agg['7_day_ma'] = ts_agg['incidents'].rolling(window=7, min_periods=1).mean()
        ts_agg['28_day_ma'] = ts_agg['incidents'].rolling(window=28, min_periods=1).mean()
    
elif time_granularity == "Weekly":
    ts_agg = ts_data.copy()
    ts_agg['week'] = ts_agg['date'].dt.to_period('W').dt.start_time
    ts_agg = ts_agg.groupby('week').size().reset_index(name='incidents')
    ts_agg = ts_agg.rename(columns={'week': 'date'})
    ts_agg = ts_agg.sort_values('date')
    
    if show_moving_avg:
        ts_agg['4_week_ma'] = ts_agg['incidents'].rolling(window=4, min_periods=1).mean()
        
else:  # Monthly
    ts_agg = ts_data.copy()
    ts_agg['month'] = ts_agg['date'].dt.to_period('M').dt.start_time
    ts_agg = ts_agg.groupby('month').size().reset_index(name='incidents')
    ts_agg = ts_agg.rename(columns={'month': 'date'})
    ts_agg = ts_agg.sort_values('date')
    
    if show_moving_avg:
        ts_agg['3_month_ma'] = ts_agg['incidents'].rolling(window=3, min_periods=1).mean()

# Create time series chart
fig_timeseries = go.Figure()

# Main area chart
fig_timeseries.add_trace(go.Scatter(
    x=ts_agg['date'],
    y=ts_agg['incidents'],
    fill='tozeroy',
    mode='lines',
    name=f'{time_granularity} Incidents',
    line=dict(color='#1f77b4', width=2),
    fillcolor='rgba(31, 119, 180, 0.2)'
))

# Add moving averages
if show_moving_avg:
    if time_granularity == "Daily":
        fig_timeseries.add_trace(go.Scatter(
            x=ts_agg['date'], y=ts_agg['7_day_ma'],
            mode='lines', name='7-Day Moving Avg',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))
        fig_timeseries.add_trace(go.Scatter(
            x=ts_agg['date'], y=ts_agg['28_day_ma'],
            mode='lines', name='28-Day Moving Avg',
            line=dict(color='#2ca02c', width=2, dash='dash')
        ))
    elif time_granularity == "Weekly":
        fig_timeseries.add_trace(go.Scatter(
            x=ts_agg['date'], y=ts_agg['4_week_ma'],
            mode='lines', name='4-Week Moving Avg',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))
    else:  # Monthly
        fig_timeseries.add_trace(go.Scatter(
            x=ts_agg['date'], y=ts_agg['3_month_ma'],
            mode='lines', name='3-Month Moving Avg',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))

# Simple forecasting (linear trend for demo)
if show_forecast and len(ts_agg) > 10:
    last_date = ts_agg['date'].max()
    forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=30, freq='D')
    
    # Simple linear regression for demo
    x = np.arange(len(ts_agg))
    y = ts_agg['incidents'].values
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    
    forecast_values = p(np.arange(len(ts_agg), len(ts_agg) + 30))
    
    fig_timeseries.add_trace(go.Scatter(
        x=forecast_dates, y=forecast_values,
        mode='lines', name='30-Day Forecast',
        line=dict(color='#d62728', width=2, dash='dot')
    ))

fig_timeseries.update_layout(
    height=400,
    xaxis_title="Date",
    yaxis_title="Number of Incidents",
    hovermode='x unified'
)

st.plotly_chart(fig_timeseries, use_container_width=True)


# 2. SEASONAL BREAKDOWN - SMALL MULTIPLES
st.subheader("🔄 Seasonal Patterns by Crime Category")

# Check for available category columns
category_column = None
possible_category_columns = ['crime_type', 'category', 'crime_category', 'type', 'offence_type']

for col in possible_category_columns:
    if col in ts_data.columns:
        category_column = col
        break

if category_column:
    # Prepare monthly data by category
    monthly_data = ts_data.copy()
    monthly_data['year'] = monthly_data['date'].dt.year
    monthly_data['month'] = monthly_data['date'].dt.month
    monthly_data['month_name'] = monthly_data['date'].dt.month_name()
    
    # Get top categories for small multiples (limit to 6 for readability)
    top_categories = monthly_data[category_column].value_counts().head(6)
    
    if len(top_categories) > 0:
        monthly_agg = monthly_data[monthly_data[category_column].isin(top_categories.index)]
        monthly_agg = monthly_agg.groupby(['year', 'month', 'month_name', category_column]).size().reset_index(name='count')
        
        # Create small multiples
        fig_seasonal = px.line(
            monthly_agg, 
            x='month', 
            y='count', 
            color='year',
            facet_col=category_column,
            facet_col_wrap=3,
            title="Monthly Patterns by Crime Category",
            labels={
                'month': 'Month', 
                'count': 'Incidents', 
                'year': 'Year',
                category_column: 'Crime Category'
            }
        )
        
        # Improve x-axis labels
        fig_seasonal.update_xaxes(
            tickvals=list(range(1, 13)), 
            ticktext=list(calendar.month_abbr)[1:],
            title_text=""
        )
        
        # Adjust layout
        fig_seasonal.update_layout(
            height=500,
            showlegend=True
        )
        
        # Update y-axes to have consistent titles
        for annotation in fig_seasonal.layout.annotations:
            annotation.text = annotation.text.split("=")[-1]
        
        st.plotly_chart(fig_seasonal, use_container_width=True)
        
        # Show category summary
        with st.expander("View Category Summary"):
            st.write(f"**Top {len(top_categories)} Crime Categories Analyzed:**")
            for category, count in top_categories.items():
                st.write(f"- {category}: {count:,} incidents")
    else:
        st.info("No category data available for seasonal analysis after filtering")
else:
    # If no category data, show alternative analysis
    st.info("🔍 Crime category data not available for seasonal analysis")
    
    # Alternative: Show monthly trends overall
    st.subheader("📈 Monthly Trends (All Crimes)")
    
    monthly_overall = ts_data.copy()
    monthly_overall['year'] = monthly_overall['date'].dt.year
    monthly_overall['month'] = monthly_overall['date'].dt.month
    monthly_overall['month_name'] = monthly_overall['date'].dt.month_name()
    
    monthly_agg = monthly_overall.groupby(['year', 'month', 'month_name']).size().reset_index(name='count')
    
    if not monthly_agg.empty:
        fig_monthly = px.line(
            monthly_agg,
            x='month',
            y='count',
            color='year',
            title="Monthly Crime Trends (All Categories)",
            labels={'month': 'Month', 'count': 'Incidents', 'year': 'Year'}
        )
        
        fig_monthly.update_xaxes(
            tickvals=list(range(1, 13)),
            ticktext=list(calendar.month_abbr)[1:]
        )
        
        fig_monthly.update_layout(height=400)
        st.plotly_chart(fig_monthly, use_container_width=True)
    else:
        st.info("Insufficient data for monthly trend analysis")

# 3. HEAT TABLE - DAY OF WEEK vs HOUR OF DAY
st.subheader("🔥 Peak Times Analysis")

if all(col in ts_data.columns for col in ['date']):
    # Extract time features
    heat_data = ts_data.copy()
    heat_data['day_of_week'] = heat_data['date'].dt.day_name()
    heat_data['hour_of_day'] = heat_data['date'].dt.hour
    
    # Create pivot table
    heat_table = heat_data.groupby(['day_of_week', 'hour_of_day']).size().reset_index(name='count')
    heat_pivot = heat_table.pivot(index='day_of_week', columns='hour_of_day', values='count').fillna(0)
    
    # Order days of week properly
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heat_pivot = heat_pivot.reindex(day_order)
    
    # Create heatmap
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heat_pivot.values,
        x=list(range(24)),
        y=heat_pivot.index,
        colorscale='Viridis',
        hoverongaps=False,
        hovertemplate='Day: %{y}<br>Hour: %{x}:00<br>Incidents: %{z}<extra></extra>'
    ))
    
    fig_heatmap.update_layout(
        height=400,
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        xaxis=dict(tickvals=list(range(24))),
        title="Incident Heatmap: Day of Week vs Hour of Day"
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    st.info("Date information not available for heatmap analysis")

# 4. CUMULATIVE TREND vs PRIOR YEAR
st.subheader("📊 Year-over-Year Comparison")

if len(ts_data) > 0:
    # Prepare cumulative data
    cumulative_data = ts_data.copy()
    cumulative_data['year'] = cumulative_data['date'].dt.year
    cumulative_data['day_of_year'] = cumulative_data['date'].dt.dayofyear
    
    current_year = datetime.now().year
    years_available = cumulative_data['year'].unique()
    
    if len(years_available) >= 2:
        # Get current and previous year
        current_year_data = cumulative_data[cumulative_data['year'] == current_year]
        previous_year = current_year - 1
        previous_year_data = cumulative_data[cumulative_data['year'] == previous_year]
        
        if not current_year_data.empty and not previous_year_data.empty:
            # Calculate cumulative sums
            current_cumulative = current_year_data.groupby('day_of_year').size().cumsum().reset_index(name='cumulative_incidents')
            current_cumulative['year'] = current_year
            
            previous_cumulative = previous_year_data.groupby('day_of_year').size().cumsum().reset_index(name='cumulative_incidents')
            previous_cumulative['year'] = previous_year
            
            # Combine for plotting
            comparison_data = pd.concat([current_cumulative, previous_cumulative], ignore_index=True)
            
            fig_comparison = px.line(
                comparison_data,
                x='day_of_year',
                y='cumulative_incidents',
                color='year',
                title=f"Cumulative Incidents: {current_year} vs {previous_year}",
                labels={'day_of_year': 'Day of Year', 'cumulative_incidents': 'Cumulative Incidents'}
            )
            
            fig_comparison.update_layout(height=400)
            st.plotly_chart(fig_comparison, use_container_width=True)
        else:
            st.info("Insufficient data for year-over-year comparison")
    else:
        st.info("Need at least 2 years of data for year-over-year comparison")
else:
    st.info("No data available for cumulative trend analysis")

# Summary statistics
st.markdown("---")
st.subheader("📋 Time Analysis Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if not ts_agg.empty:
        avg_incidents = ts_agg['incidents'].mean()
        st.metric("Avg Daily Incidents", f"{avg_incidents:.1f}")

with col2:
    if not ts_agg.empty:
        peak_day = ts_agg.loc[ts_agg['incidents'].idxmax(), 'date']
        st.metric("Peak Day", peak_day.strftime('%Y-%m-%d'))

with col3:
    if 'day_of_week' in locals():
        peak_hour = heat_table.loc[heat_table['count'].idxmax(), 'hour_of_day']
        st.metric("Peak Hour", f"{peak_hour:02d}:00")

with col4:
    if len(ts_agg) > 1:
        trend = (ts_agg['incidents'].iloc[-1] - ts_agg['incidents'].iloc[0]) / ts_agg['incidents'].iloc[0] * 100
        st.metric("Overall Trend", f"{trend:+.1f}%")

# Data export
st.markdown("---")
if st.button("📥 Export Time Series Data"):
    csv = ts_agg.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="crime_time_series.csv",
        mime="text/csv"
    )

st.caption("💡 **Tips**: Use the sidebar to adjust time granularity and toggle moving averages/forecasts.")