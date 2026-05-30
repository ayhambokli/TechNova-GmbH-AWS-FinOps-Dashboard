import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TechNova FinOps Dashboard",
    page_icon="☁️",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-label { font-size: 13px; color: #666; margin-bottom: 4px; }
    .metric-value { font-size: 24px; font-weight: 600; color: #1a1a1a; }
    .metric-delta-red { font-size: 12px; color: #E24B4A; }
    .metric-delta-green { font-size: 12px; color: #1D9E75; }
    .finding-box {
        background-color: #fff8f0;
        border-left: 4px solid #EF9F27;
        border-radius: 4px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .rec-box {
        background-color: #f0f9f4;
        border-left: 4px solid #1D9E75;
        border-radius: 4px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    div[data-testid="stTabs"] button {
        font-size: 15px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ── Load & prepare data ───────────────────────────────────────────────────────
@st.cache_data
def load_data():
    billing   = pd.read_csv('aws_billing.csv')
    usage     = pd.read_csv('ec2_usage_metrics.csv')
    inventory = pd.read_csv('resource_inventory.csv')

    billing['usage_start_date'] = pd.to_datetime(billing['usage_start_date'])
    billing['usage_end_date']   = pd.to_datetime(billing['usage_end_date'])
    inventory['created_date']   = pd.to_datetime(inventory['created_date'])

    env_map = {'dev':'development','development':'development',
               'prod':'production','production':'production','staging':'staging'}
    billing['tag_environment']  = billing['tag_environment'].map(env_map)
    inventory['environment']    = inventory['environment'].map(env_map)

    billing['tag_team']         = billing['tag_team'].fillna('untagged')
    billing['tag_environment']  = billing['tag_environment'].fillna('untagged')
    billing['tag_project']      = billing['tag_project'].fillna('untagged')
    inventory['team']           = inventory['team'].fillna('untagged')
    inventory['owner_email']    = inventory['owner_email'].fillna('no-owner')
    inventory['cost_center']    = inventory['cost_center'].fillna('unassigned')
    inventory['environment']    = inventory['environment'].fillna('unknown')

    billing['cost_eur'] = (billing['unblended_cost'] * 0.92).round(2)

    df = billing.merge(
        inventory[['resource_id','team','owner_email','cost_center','environment']],
        on='resource_id', how='left')
    df = df.merge(
        usage[['resource_id','billing_period','avg_cpu_utilization_pct',
               'max_cpu_utilization_pct','avg_memory_utilization_pct',
               'running_hours_total','running_on_weekends']],
        on=['resource_id','billing_period'], how='left')
    return df

df = load_data()

# ── Pre-compute dataframes ────────────────────────────────────────────────────
monthly = df.groupby('billing_period')['cost_eur'].sum().round(2).reset_index()
monthly.columns = ['month', 'total_cost_eur']

by_service = df.groupby('service')['cost_eur'].sum().sort_values(ascending=True)

by_team = df.groupby(['billing_period','tag_team'])['cost_eur'].sum().round(2).reset_index()

untagged = df[df['tag_team'] == 'untagged'].groupby('service')['cost_eur'].sum().round(2).reset_index()
untagged = untagged.sort_values('cost_eur', ascending=False)
untagged['pct_of_total'] = (untagged['cost_eur'] / df['cost_eur'].sum() * 100).round(1)

idle = df[(df['service'] == 'Amazon EC2') &
          (df['avg_cpu_utilization_pct'] < 10)].dropna(subset=['avg_cpu_utilization_pct'])
idle_summary = idle.groupby('resource_id').agg(
    avg_cpu=('avg_cpu_utilization_pct','mean'),
    total_cost=('cost_eur','sum')
).reset_index()

s3 = df[df['service'] == 'Amazon S3'].groupby(
    ['billing_period','resource_id'])['cost_eur'].sum().round(2).reset_index()
raw_logs = s3[s3['resource_id'] == 'technova-raw-logs']

# ── Header ────────────────────────────────────────────────────────────────────
st.title("☁️ TechNova GmbH — AWS FinOps Dashboard")
st.caption("Prepared by Cortex Reply FinOps Team · Jan–Mar 2024 · AWS (eu-central-1)")
st.divider()

# ── Top KPI cards ─────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown("""<div class="metric-card">
        <div class="metric-label">Total 3-Month Spend</div>
        <div class="metric-value">€24,145</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown("""<div class="metric-card">
        <div class="metric-label">Monthly Avg Spend</div>
        <div class="metric-value">€8,048</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown("""<div class="metric-card">
        <div class="metric-label">Untagged Spend</div>
        <div class="metric-value" style="color:#E24B4A">€7,542</div>
        <div class="metric-delta-red">31% of total</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown("""<div class="metric-card">
        <div class="metric-label">Savings Potential</div>
        <div class="metric-value" style="color:#1D9E75">€7,737</div>
        <div class="metric-delta-green">32% reduction</div>
    </div>""", unsafe_allow_html=True)
with k5:
    st.markdown("""<div class="metric-card">
        <div class="metric-label">RI Coverage</div>
        <div class="metric-value" style="color:#E24B4A">0%</div>
        <div class="metric-delta-red">100% On-Demand</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview",
    "👥 Team Analysis",
    "💻 EC2 Idle Instances",
    "🪣 S3 Storage",
    "💰 Savings Summary"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Monthly Cost Trend")
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(7, 4))
        colors = ['#378ADD', '#E24B4A', '#E24B4A']
        ax.bar(monthly['month'], monthly['total_cost_eur'], color=colors, width=0.5)
        ax.set_ylabel('Cost (EUR)')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'€{x:,.0f}'))
        for i, row in monthly.iterrows():
            ax.text(i, row['total_cost_eur'] + 80, f"€{row['total_cost_eur']:,.0f}",
                    ha='center', fontsize=10, fontweight='bold')
        ax.set_title('Monthly AWS Spend', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.barh(by_service.index, by_service.values, color='#378ADD')
        ax.set_xlabel('Cost (EUR)')
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'€{x:,.0f}'))
        for i, val in enumerate(by_service.values):
            ax.text(val + 30, i, f'€{val:,.0f}', va='center', fontsize=8)
        ax.set_title('Total Cost by Service', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("""<div class="finding-box">
        <b>Key Finding:</b> AWS spend jumped 69% from January to February (€5,744 → €9,682).
        EC2 is the top cost driver at €9,759 over 3 months, followed by S3 at €7,313.
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — TEAM ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Cost by Team")
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(7, 4))
        team_pivot = by_team.pivot(index='billing_period', columns='tag_team', values='cost_eur').fillna(0)
        team_pivot.plot(kind='bar', ax=ax, width=0.7,
                        color=['#378ADD','#E24B4A','#EF9F27','#1D9E75'])
        ax.set_ylabel('Cost (EUR)')
        ax.set_xlabel('')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'€{x:,.0f}'))
        ax.legend(fontsize=8)
        ax.tick_params(axis='x', rotation=0)
        ax.set_title('Monthly Cost by Team', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.barh(untagged['service'], untagged['cost_eur'], color='#E24B4A')
        ax.set_xlabel('Cost (EUR)')
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'€{x:,.0f}'))
        for i, (val, pct) in enumerate(zip(untagged['cost_eur'], untagged['pct_of_total'])):
            ax.text(val + 20, i, f'€{val:,.0f} ({pct}%)', va='center', fontsize=8)
        ax.set_title(f'Untagged Spend by Service\nTotal: €{untagged["cost_eur"].sum():,.0f} (31%)',
                     fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("""<div class="finding-box">
        <b>Key Finding:</b> €7,542 (31%) of total spend has no team tag — finance cannot
        allocate this cost to any team or cost center. Untagged spend spiked to €4,753 in February.
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div class="rec-box">
        <b>Recommendation:</b> Enforce mandatory tagging policy using AWS Config Rules.
        Block untagged deployments in CI/CD pipeline. Target: 100% tag coverage in 30 days.
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — EC2 IDLE INSTANCES
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Idle EC2 Instances (avg CPU < 10%)")
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.bar(idle_summary['resource_id'], idle_summary['total_cost'],
                      color='#E24B4A', width=0.5)
        ax.set_ylabel('Total Cost (EUR)')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'€{x:,.0f}'))
        for bar, cpu in zip(bars, idle_summary['avg_cpu']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                    f'{cpu:.1f}% CPU', ha='center', fontsize=9, fontweight='bold')
        ax.set_title('Idle EC2 Cost by Instance', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown("#### Idle Instance Details")
        st.dataframe(
            idle_summary.rename(columns={
                'resource_id': 'Instance ID',
                'avg_cpu': 'Avg CPU %',
                'total_cost': 'Total Cost (€)'
            }).style.format({'Avg CPU %': '{:.1f}%', 'Total Cost (€)': '€{:,.2f}'}),
            use_container_width=True
        )
        st.metric("Annual Waste Estimate", "€1,958", delta="-€1,958 savings potential",
                  delta_color="inverse")

    st.markdown("""<div class="finding-box">
        <b>Key Finding:</b> 4 EC2 instances running at less than 10% avg CPU — all running
        on weekends with nobody using them. Worst offender: i-00c5a62 at 3.1% CPU.
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div class="rec-box">
        <b>Recommendation:</b> Implement AWS Instance Scheduler to auto-shutdown dev/test
        instances outside business hours (Mon–Fri 08:00–20:00 CET). Saving: €1,958/year.
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — S3 STORAGE
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("S3 Storage Cost Analysis")
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(7, 4))
        s3_pivot = s3.pivot(index='billing_period', columns='resource_id', values='cost_eur').fillna(0)
        s3_pivot.plot(kind='bar', ax=ax, width=0.7)
        ax.set_ylabel('Cost (EUR)')
        ax.set_xlabel('')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'€{x:,.0f}'))
        ax.legend(fontsize=7, bbox_to_anchor=(1, 1))
        ax.tick_params(axis='x', rotation=0)
        ax.set_title('S3 Cost by Bucket per Month', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(raw_logs['billing_period'], raw_logs['cost_eur'],
               color=['#378ADD','#E24B4A','#E24B4A'], width=0.5)
        ax.set_ylabel('Cost (EUR)')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'€{x:,.0f}'))
        for i, row in raw_logs.reset_index().iterrows():
            ax.text(i, row['cost_eur'] + 30, f"€{row['cost_eur']:,.0f}",
                    ha='center', fontsize=10, fontweight='bold')
        ax.set_title('technova-raw-logs Growth\n(No lifecycle policy)', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("""<div class="finding-box">
        <b>Key Finding:</b> technova-raw-logs accounts for 90% of all S3 spend (€6,594).
        Growing +77% in 3 months with no archiving or cleanup policy — will keep growing indefinitely.
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div class="rec-box">
        <b>Recommendation:</b> Add S3 lifecycle policy — move logs older than 30 days to
        Glacier, delete after 90 days. Estimated saving: €3,956 over next 3 months.
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — SAVINGS SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.subheader("Savings Opportunity Summary")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(7, 4))
        savings_data = {
            'Fix untagged resources': 7542.90,
            'S3 lifecycle policy': 3956.75,
            'Weekend idle EC2 shutdown': 1958.52,
            'Reserved Instances (EC2+RDS)': 1822.69,
        }
        labels = list(savings_data.keys())
        values = list(savings_data.values())
        bars = ax.barh(labels, values,
                       color=['#E24B4A','#EF9F27','#378ADD','#1D9E75'])
        ax.set_xlabel('Estimated Savings (EUR)')
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'€{x:,.0f}'))
        for i, val in enumerate(values):
            ax.text(val + 50, i, f'€{val:,.0f}', va='center', fontsize=9, fontweight='bold')
        ax.set_title('Savings by Optimization Action', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown("#### Optimization Actions")
        savings_df = pd.DataFrame({
            'Finding': ['Untagged resources', 'S3 lifecycle policy',
                        'Weekend idle EC2', 'Reserved Instances'],
            'Saving (€)': [7542.90, 3956.75, 1958.52, 1822.69],
            'Effort': ['Medium', 'Low', 'Low', 'Medium'],
            'Timeline': ['30 days', '1 week', '1 week', '30 days']
        })
        st.dataframe(savings_df.style.format({'Saving (€)': '€{:,.2f}'}),
                     use_container_width=True)

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Spend", "€24,145")
        c2.metric("Potential Saving", "€7,737", delta="+32%")
        c3.metric("Optimized Spend", "€16,407", delta="-€7,737", delta_color="inverse")

    st.divider()
    st.markdown("#### Conclusion")
    st.markdown("""<div class="rec-box">
        TechNova GmbH is in the early <b>Crawl</b> stage of FinOps maturity. The cost spike was not
        caused by business growth — it was caused by lack of governance, visibility, and cloud cost
        awareness. All 4 recommendations can be implemented within 2–4 weeks with minimal engineering
        effort. The immediate priority is <b>tagging</b> — without it, none of the other optimizations
        can be measured or attributed to a team. Once enforced, TechNova can move from the
        <b>Inform</b> phase into the <b>Optimize</b> phase of the FinOps lifecycle.
    </div>""", unsafe_allow_html=True)
