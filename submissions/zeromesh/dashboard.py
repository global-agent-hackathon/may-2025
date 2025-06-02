import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import random
import time
from pathlib import Path

# Set page config with custom theme
st.set_page_config(
    page_title="ZeroMesh Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agents' not in st.session_state:
    st.session_state.agents = {
        f'agent_{i}': {
            'id': f'agent_{i}',
            'name': f'Agent {i}',
            'status': random.choice(['active', 'quarantined']),
            'trust_score': random.uniform(50, 100),
            'last_seen': (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat(),
            'type': random.choice(['service', 'user', 'system']),
            'permissions': random.choice(['admin', 'user', 'readonly']),
            'location': random.choice(['us-east', 'us-west', 'eu-central', 'ap-south'])
        } for i in range(1, 11)
    }

if 'alerts' not in st.session_state:
    st.session_state.alerts = []
    alert_types = ['security_breach', 'policy_violation', 'unauthorized_access', 'trust_score_drop', 'system_error']
    severities = ['critical', 'high', 'medium', 'low']
    for i in range(10):
        st.session_state.alerts.append({
            'id': f'alert_{i}',
            'type': random.choice(alert_types),
            'severity': random.choice(severities),
            'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 120))).isoformat(),
            'details': {
                'message': f'Sample alert message {i}',
                'source': random.choice(list(st.session_state.agents.keys())),
                'affected_systems': random.sample(list(st.session_state.agents.keys()), k=random.randint(1, 3))
            }
        })

if 'audit_logs' not in st.session_state:
    st.session_state.audit_logs = []
    event_types = ['authentication', 'policy_change', 'trust_score_update', 'agent_status_change', 'system_config']
    for i in range(20):
        st.session_state.audit_logs.append({
            'id': f'log_{i}',
            'type': random.choice(event_types),
            'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 240))).isoformat(),
            'details': {
                'message': f'Sample audit log {i}',
                'agent_id': random.choice(list(st.session_state.agents.keys())),
                'action': random.choice(['create', 'update', 'delete', 'view']),
                'status': random.choice(['success', 'failure'])
            }
        })

# Sidebar navigation
with st.sidebar:
    st.title("ZeroMesh")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["Dashboard", "Agents", "Alerts", "Audit Logs", "Settings"]
    )
    st.markdown("---")
    st.markdown("### System Status")
    system_health = random.uniform(0, 100)
    st.progress(system_health/100, f"System Health: {system_health:.1f}%")
    
    # Quick filters
    st.markdown("### Quick Filters")
    if page == "Agents":
        st.multiselect("Agent Type", ['service', 'user', 'system'], default=['service', 'user', 'system'])
    elif page == "Alerts":
        st.multiselect("Alert Severity", ['critical', 'high', 'medium', 'low'], default=['critical', 'high'])

# Helper functions
def get_alert_color(severity):
    return {
        'critical': 'darkred',
        'high': 'red',
        'medium': 'orange',
        'low': 'blue'
    }.get(severity, 'gray')

def get_trust_score_color(score):
    if score >= 80:
        return 'green'
    elif score >= 60:
        return 'orange'
    return 'red'

# Dashboard page
if page == "Dashboard":
    st.title("System Overview")
    
    # Key metrics in a grid
    col1, col2, col3, col4 = st.columns(4)
    
    active_agents = len([a for a in st.session_state.agents.values() if a['status'] == 'active'])
    quarantined_agents = len([a for a in st.session_state.agents.values() if a['status'] == 'quarantined'])
    avg_trust_score = sum(a['trust_score'] for a in st.session_state.agents.values()) / len(st.session_state.agents)
    critical_alerts = len([a for a in st.session_state.alerts if a['severity'] in ['critical', 'high']])
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Active Agents", active_agents, "+2")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Quarantined Agents", quarantined_agents, "-1")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Average Trust Score", f"{avg_trust_score:.2f}", "+0.5")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Critical Alerts", critical_alerts, "+3")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Trust Score Distribution
    st.markdown("### Trust Score Distribution")
    trust_scores = pd.DataFrame([
        {'Agent': a['name'], 'Trust Score': a['trust_score'], 'Status': a['status']}
        for a in st.session_state.agents.values()
    ])
    
    fig = px.bar(trust_scores, x='Agent', y='Trust Score',
                 color='Status', color_discrete_map={'active': 'green', 'quarantined': 'red'},
                 title="Agent Trust Scores by Status")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent Activity Timeline
    st.markdown("### Recent Activity")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Latest Alerts")
        recent_alerts = sorted(st.session_state.alerts, 
                             key=lambda x: x['timestamp'], 
                             reverse=True)[:5]
        for alert in recent_alerts:
            severity_color = get_alert_color(alert['severity'])
            st.markdown(
                f"""
                <div style='padding: 10px; border-left: 5px solid {severity_color}; margin-bottom: 10px;'>
                    <h4>{alert['type'].replace('_', ' ').title()}</h4>
                    <p><strong>Severity:</strong> {alert['severity'].upper()}</p>
                    <p><small>Time: {alert['timestamp']}</small></p>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    with col2:
        st.markdown("#### System Health Trends")
        # Generate sample health data
        dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
        health_data = pd.DataFrame({
            'Date': dates,
            'System Health': [random.uniform(80, 100) for _ in range(7)],
            'Network Latency': [random.uniform(10, 50) for _ in range(7)]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=health_data['Date'], y=health_data['System Health'],
                                mode='lines+markers', name='System Health'))
        fig.add_trace(go.Scatter(x=health_data['Date'], y=health_data['Network Latency'],
                                mode='lines+markers', name='Network Latency'))
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

# Agents page
elif page == "Agents":
    st.title("Agent Management")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            ['active', 'quarantined'],
            default=['active', 'quarantined']
        )
    with col2:
        type_filter = st.multiselect(
            "Filter by Type",
            ['service', 'user', 'system'],
            default=['service', 'user', 'system']
        )
    with col3:
        location_filter = st.multiselect(
            "Filter by Location",
            ['us-east', 'us-west', 'eu-central', 'ap-south'],
            default=['us-east', 'us-west', 'eu-central', 'ap-south']
        )
    
    # Agent list with filters applied
    filtered_agents = [
        agent for agent in st.session_state.agents.values()
        if agent['status'] in status_filter
        and agent['type'] in type_filter
        and agent['location'] in location_filter
    ]
    
    for agent in filtered_agents:
        with st.expander(f"{agent['name']} - Trust Score: {agent['trust_score']:.2f}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Status:** {agent['status'].title()}")
                st.write(f"**Type:** {agent['type'].title()}")
                st.write(f"**Location:** {agent['location']}")
            
            with col2:
                st.write(f"**Permissions:** {agent['permissions']}")
                st.write(f"**Last Seen:** {agent['last_seen']}")
            
            with col3:
                if agent['status'] == 'active':
                    if st.button('Quarantine', key=f"quarantine_{agent['id']}"):
                        st.session_state.agents[agent['id']]['status'] = 'quarantined'
                        st.session_state.audit_logs.append({
                            'id': f'log_{len(st.session_state.audit_logs)}',
                            'type': 'agent_status_change',
                            'timestamp': datetime.now().isoformat(),
                            'details': {
                                'message': f'Agent {agent["name"]} quarantined',
                                'agent_id': agent['id']
                            }
                        })
                        st.experimental_rerun()
                else:
                    if st.button('Activate', key=f"activate_{agent['id']}"):
                        st.session_state.agents[agent['id']]['status'] = 'active'
                        st.session_state.audit_logs.append({
                            'id': f'log_{len(st.session_state.audit_logs)}',
                            'type': 'agent_status_change',
                            'timestamp': datetime.now().isoformat(),
                            'details': {
                                'message': f'Agent {agent["name"]} activated',
                                'agent_id': agent['id']
                            }
                        })
                        st.experimental_rerun()

# Alerts page
elif page == "Alerts":
    st.title("Security Alerts")
    
    # Filter alerts
    severity_filter = st.multiselect(
        "Filter by Severity",
        ['critical', 'high', 'medium', 'low'],
        default=['critical', 'high', 'medium', 'low']
    )
    
    type_filter = st.multiselect(
        "Filter by Type",
        ['security_breach', 'policy_violation', 'unauthorized_access', 'trust_score_drop', 'system_error'],
        default=['security_breach', 'policy_violation', 'unauthorized_access', 'trust_score_drop', 'system_error']
    )
    
    filtered_alerts = [
        alert for alert in sorted(
            st.session_state.alerts,
            key=lambda x: x['timestamp'],
            reverse=True
        )
        if alert['severity'] in severity_filter
        and alert['type'] in type_filter
    ]
    
    # Display alerts
    for alert in filtered_alerts:
        color = get_alert_color(alert['severity'])
        with st.container():
            st.markdown(
                f"""
                <div style='padding: 15px; border-left: 5px solid {color}; margin-bottom: 15px; background-color: rgba({255 if color == 'red' else 0}, 0, 0, 0.05);'>
                    <h4>{alert['type'].replace('_', ' ').title()}</h4>
                    <p><strong>Severity:</strong> {alert['severity'].upper()}</p>
                    <p><strong>Message:</strong> {alert['details']['message']}</p>
                    <p><strong>Affected Systems:</strong> {', '.join(alert['details']['affected_systems'])}</p>
                    <p><small>Time: {alert['timestamp']}</small></p>
                </div>
                """,
                unsafe_allow_html=True
            )

# Audit Logs page
elif page == "Audit Logs":
    st.title("Audit Logs")
    
    # Date filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Event type filter
    event_type_filter = st.multiselect(
        "Filter by Event Type",
        ['authentication', 'policy_change', 'trust_score_update', 'agent_status_change', 'system_config'],
        default=['authentication', 'policy_change', 'trust_score_update', 'agent_status_change', 'system_config']
    )
    
    # Filter logs
    filtered_logs = [
        log for log in sorted(
            st.session_state.audit_logs,
            key=lambda x: x['timestamp'],
            reverse=True
        )
        if start_date <= datetime.fromisoformat(log['timestamp']).date() <= end_date
        and log['type'] in event_type_filter
    ]
    
    # Display logs in a table
    if filtered_logs:
        df = pd.DataFrame([
            {
                'Timestamp': datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                'Event Type': log['type'].replace('_', ' ').title(),
                'Agent': log['details']['agent_id'],
                'Action': log['details']['action'].title(),
                'Status': log['details']['status'].title(),
                'Message': log['details']['message']
            }
            for log in filtered_logs
        ])
        
        # Add color coding based on status
        def color_status(val):
            color = 'green' if val == 'Success' else 'red'
            return f'color: {color}'
        
        st.dataframe(
            df.style.applymap(color_status, subset=['Status']),
            use_container_width=True
        )
    else:
        st.info("No audit logs found for the selected date range.")

# Settings page
elif page == "Settings":
    st.title("System Settings")
    
    # System Configuration
    st.header("System Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Trust Score Settings")
        st.slider("Minimum Trust Score Threshold", 0, 100, 60)
        st.slider("Trust Score Decay Rate", 0.0, 1.0, 0.1)
        
    with col2:
        st.subheader("Alert Settings")
        st.multiselect(
            "Alert Notifications",
            ['Email', 'Slack', 'Teams', 'SMS'],
            default=['Email']
        )
        st.number_input("Alert Retention Days", min_value=1, value=30)
    
    # Backup & Maintenance
    st.header("Backup & Maintenance")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Backup Settings")
        st.selectbox("Backup Frequency", ['Daily', 'Weekly', 'Monthly'])
        st.text_input("Backup Location", "/backup/zeromesh")
        
    with col2:
        st.subheader("Maintenance Window")
        st.time_input("Start Time", datetime.strptime("22:00", "%H:%M"))
        st.time_input("End Time", datetime.strptime("05:00", "%H:%M"))
    
    # Save Settings
    if st.button("Save Settings"):
        st.success("Settings saved successfully!") 