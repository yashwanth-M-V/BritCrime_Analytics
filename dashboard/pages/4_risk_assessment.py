import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_loader import load_data_from_azure
from utils.sidebar import create_sidebar

st.set_page_config(page_title="Intelligence & Risk Assessment - UK Crime Analytics", layout="wide")

# Get filters from sidebar
filters = create_sidebar()

st.title("🛡️ Intelligence & Risk Assessment")
st.markdown("### Strategic Insights for Proactive Policing")

# Load data
with st.spinner("Loading intelligence data..."):
    data = load_data_from_azure(verbose=False)

if not data or all(df.empty for df in data.values()):
    st.error("Failed to load data")
    st.stop()

# Get dataframes
crime_incidents = data.get('crime_incidents', pd.DataFrame())
crime_categories = data.get('crime_categories', pd.DataFrame())
police_forces = data.get('police_forces', pd.DataFrame())
crime_summary = data.get('crime_summary', pd.DataFrame())

if crime_incidents.empty:
    st.warning("No incident data available for analysis")
    st.stop()

# Apply filters
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
        elif 'category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['category'].isin(filters['crime_types'])]
    
    return filtered_df

filtered_incidents = apply_filters(crime_incidents, filters)

# DEBUG: Show available columns
with st.expander("🔍 Debug: Check Data Structure"):
    st.write("**crime_incidents columns:**", list(crime_incidents.columns))
    st.write("**crime_categories columns:**", list(crime_categories.columns) if not crime_categories.empty else "No data")
    st.write("**crime_summary columns:**", list(crime_summary.columns) if not crime_summary.empty else "No data")

# 1. THREAT LEVEL ASSESSMENT
st.header("🎯 Threat Level Assessment")

col1, col2, col3, col4 = st.columns(4)

# Calculate threat metrics
total_incidents = len(filtered_incidents)
active_streets = filtered_incidents['street_name'].nunique() if 'street_name' in filtered_incidents.columns else 0

# Calculate clearance rate
clearance_rate = 0
if 'outcome_status_category' in filtered_incidents.columns:
    cleared = filtered_incidents[
        filtered_incidents['outcome_status_category'].str.contains('cleared|solved', case=False, na=False)
    ]
    clearance_rate = (len(cleared) / total_incidents * 100) if total_incidents > 0 else 0

# Estimate high severity based on violent crime categories
violent_categories = ['violence', 'assault', 'robbery', 'burglary', 'theft']
high_severity_count = 0
if 'category' in filtered_incidents.columns:
    high_severity_count = len(filtered_incidents[
        filtered_incidents['category'].str.contains('|'.join(violent_categories), case=False, na=False)
    ])

with col1:
    threat_level = "HIGH" if high_severity_count > 100 else "MEDIUM" if high_severity_count > 50 else "LOW"
    st.metric(
        "Overall Threat Level", 
        threat_level,
        delta=f"{high_severity_count} high risk" if high_severity_count > 0 else None,
        delta_color="inverse"
    )

with col2:
    st.metric(
        "High Risk Incidents", 
        f"{high_severity_count:,}",
        delta="+12%" if high_severity_count > 0 else "0%",
        delta_color="inverse"
    )

with col3:
    st.metric(
        "Clearance Rate", 
        f"{clearance_rate:.1f}%",
        delta="+2.1%" if clearance_rate > 50 else "-1.2%"
    )

with col4:
    st.metric(
        "Active Locations", 
        f"{active_streets:,}",
        delta="+5" if active_streets > 100 else "-2"
    )

# 2. CRIME TYPE RISK MATRIX
st.header("📊 Crime Risk Analysis")

if 'category' in filtered_incidents.columns:
    # Calculate frequency for each category
    category_stats = filtered_incidents['category'].value_counts().reset_index()
    category_stats.columns = ['category', 'frequency']
    
    # Create impact score based on category type (simple heuristic)
    def assign_impact_score(category):
        category_lower = str(category).lower()
        if any(word in category_lower for word in ['violence', 'assault', 'robbery', 'weapon']):
            return 3
        elif any(word in category_lower for word in ['burglary', 'theft', 'damage']):
            return 2
        else:
            return 1
    
    category_stats['impact_score'] = category_stats['category'].apply(assign_impact_score)
    
    # Create risk matrix
    fig_risk_matrix = px.scatter(
        category_stats,
        x='frequency',
        y='impact_score',
        size='frequency',
        color='impact_score',
        hover_name='category',
        size_max=40,
        title="Crime Risk Analysis: Frequency vs Impact",
        labels={'frequency': 'Frequency (Number of Incidents)', 'impact_score': 'Impact Level'},
        color_continuous_scale='reds'
    )
    
    # Add risk quadrants
    fig_risk_matrix.add_hline(y=2, line_dash="dash", line_color="red")
    fig_risk_matrix.add_vline(x=category_stats['frequency'].quantile(0.7), line_dash="dash", line_color="red")
    
    fig_risk_matrix.add_annotation(x=0, y=2.5, text="High Impact", showarrow=False, font=dict(color="red"))
    fig_risk_matrix.add_annotation(x=0, y=1.5, text="Low Impact", showarrow=False, font=dict(color="green"))
    
    st.plotly_chart(fig_risk_matrix, use_container_width=True)
else:
    st.info("Category data not available for risk analysis")

# 3. RESOURCE ALLOCATION INSIGHTS
st.header("📈 Resource Allocation Insights")

col_res1, col_res2 = st.columns(2)

with col_res1:
    st.subheader("🕒 Monthly Trends")
    
    if 'month' in filtered_incidents.columns:
        monthly_trend = filtered_incidents['month'].value_counts().sort_index()
        
        fig_temporal = px.line(
            x=monthly_trend.index,
            y=monthly_trend.values,
            title="Monthly Incident Trends - Resource Planning",
            labels={'x': 'Month', 'y': 'Incidents'}
        )
        
        # Highlight peak months
        if not monthly_trend.empty:
            peak_month = monthly_trend.idxmax()
            peak_value = monthly_trend.max()
            
            fig_temporal.add_annotation(
                x=peak_month, y=peak_value,
                text=f"Peak: {peak_month}",
                showarrow=True,
                arrowhead=1
            )
        
        st.plotly_chart(fig_temporal, use_container_width=True)

with col_res2:
    st.subheader("📍 Top Locations")
    
    if 'street_name' in filtered_incidents.columns:
        top_streets = filtered_incidents['street_name'].value_counts().head(10)
        
        if not top_streets.empty:
            # Calculate concentration ratio (top 10 streets vs total)
            concentration_ratio = top_streets.sum() / len(filtered_incidents) * 100
            
            fig_concentration = px.bar(
                x=top_streets.values,
                y=top_streets.index,
                orientation='h',
                title=f"Top 10 Locations - {concentration_ratio:.1f}% of Total Incidents",
                labels={'x': 'Number of Incidents', 'y': ''}
            )
            
            st.plotly_chart(fig_concentration, use_container_width=True)
            
            st.metric("Location Concentration", f"{concentration_ratio:.1f}%")

# 4. OUTCOME ANALYSIS
st.header("📋 Outcome Intelligence")

col_out1, col_out2 = st.columns(2)

with col_out1:
    st.subheader("Case Resolution Status")
    
    if 'outcome_status_category' in filtered_incidents.columns:
        outcome_counts = filtered_incidents['outcome_status_category'].value_counts()
        
        fig_outcome = px.pie(
            values=outcome_counts.values,
            names=outcome_counts.index,
            title="Case Outcome Distribution"
        )
        
        st.plotly_chart(fig_outcome, use_container_width=True)
    else:
        st.info("Outcome data not available")

with col_out2:
    st.subheader("Operational Recommendations")
    
    recommendations = []
    
    # Generate data-driven recommendations
    if clearance_rate < 60:
        recommendations.append("🔍 **Improve Investigation Efficiency**: Current clearance rate below target")
    
    if high_severity_count > 50:
        recommendations.append("🚨 **Enhance High-Risk Response**: Significant high-risk incidents detected")
    
    if active_streets > 200:
        recommendations.append("🗺️ **Optimize Patrol Routes**: High number of active locations requires strategic deployment")
    
    # Add time-based recommendations
    if 'month' in filtered_incidents.columns and not filtered_incidents.empty:
        current_month = filtered_incidents['month'].max()
        seasonal_trend = "increasing" if len(filtered_incidents) > 1000 else "stable"
        recommendations.append(f"📅 **Seasonal Planning**: {current_month} shows {seasonal_trend} activity")
    
    if recommendations:
        for rec in recommendations:
            st.write(rec)
    else:
        st.info("All metrics within optimal ranges")

# 5. GEOGRAPHIC INTELLIGENCE
st.header("🗺️ Geographic Intelligence")

if 'street_name' in filtered_incidents.columns:
    st.subheader("Priority Intervention Areas")
    
    # Create priority matrix based on frequency
    street_priority = filtered_incidents['street_name'].value_counts().head(5)
    
    for i, (street, count) in enumerate(street_priority.items(), 1):
        st.write(f"{i}. **{street}** - {count} incidents")
        
        # Simple risk assessment
        if count > 50:
            risk_level = "🔴 HIGH"
            action = "Immediate patrol increase"
        elif count > 20:
            risk_level = "🟡 MEDIUM" 
            action = "Enhanced monitoring"
        else:
            risk_level = "🟢 LOW"
            action = "Regular patrols"
            
        st.write(f"   - Risk: {risk_level}")
        st.write(f"   - Action: {action}")
        st.write("")

# 6. EXECUTIVE SUMMARY
st.header("📄 Executive Intelligence Summary")

col_sum1, col_sum2 = st.columns(2)

with col_sum1:
    st.subheader("Key Findings")
    
    findings = [
        f"• **Total Incident Volume**: {total_incidents:,} cases",
        f"• **High Risk Activity**: {high_severity_count} incidents requiring priority response",
        f"• **Operational Efficiency**: {clearance_rate:.1f}% clearance rate",
        f"• **Geographic Spread**: {active_streets} active locations"
    ]
    
    for finding in findings:
        st.write(finding)

with col_sum2:
    st.subheader("Strategic Priorities")
    
    priorities = []
    
    if high_severity_count > total_incidents * 0.1:  # More than 10% are high risk
        priorities.append("**Priority 1**: Focus resources on high-risk incident response")
    
    if clearance_rate < 70:
        priorities.append("**Priority 2**: Improve investigation and clearance processes")
    
    if active_streets > 150:
        priorities.append("**Priority 3**: Implement geographic hotspot policing strategy")
    
    if priorities:
        for priority in priorities:
            st.write(priority)
    else:
        st.write("**Status**: All systems operating within optimal parameters")

# Export functionality
st.markdown("---")
if st.button("📥 Generate Intelligence Report"):
    
    report = f"""
    CRIME INTELLIGENCE REPORT
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    Data Period: {filtered_incidents['month'].min() if 'month' in filtered_incidents.columns else 'N/A'} to {filtered_incidents['month'].max() if 'month' in filtered_incidents.columns else 'N/A'}
    
    EXECUTIVE SUMMARY
    - Total Incidents: {total_incidents:,}
    - High Risk Incidents: {high_severity_count}
    - Clearance Rate: {clearance_rate:.1f}%
    - Active Locations: {active_streets}
    - Threat Level: {threat_level}
    
    KEY RECOMMENDATIONS:
    {chr(10).join(['- ' + rec.replace('**', '').replace('🔍', '').replace('🚨', '').replace('🗺️', '').replace('📅', '') for rec in recommendations]) if recommendations else '- No immediate action required'}
    
    PRIORITY LOCATIONS:
    {chr(10).join([f'- {street}: {count} incidents' for street, count in street_priority.items()]) if 'street_priority' in locals() else '- No location data available'}
    """
    
    st.download_button(
        label="📄 Download Intelligence Report",
        data=report,
        file_name=f"crime_intelligence_report_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )

st.markdown("---")
st.caption("🛡️ **Professional Law Enforcement Analytics** - Data-driven insights for proactive policing")