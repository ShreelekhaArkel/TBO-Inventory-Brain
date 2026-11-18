"""
styles.py - Custom Modern SaaS Styling for TBO Inventory Brain
Theme: Dark Navy/Blue and Crisp White, clean typography, responsive cards,
interactive metrics, and badge components.
"""

CUSTOM_CSS = """
<style>
/* Import modern Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Primary Header bar */
.tbo-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #0369A1 100%);
    color: white;
    padding: 24px 32px;
    border-radius: 14px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(15, 23, 42, 0.15);
}

.tbo-header h1 {
    font-size: 26px;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
    color: #FFFFFF;
}

.tbo-header p {
    font-size: 14px;
    color: #BAE6FD;
    margin: 6px 0 0 0;
    font-weight: 400;
}

/* Metric Cards */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    height: 100%;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
    border-color: #CBD5E1;
}

.metric-label {
    font-size: 12px;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 26px;
    font-weight: 700;
    color: #0F172A;
    line-height: 1.2;
}

.metric-sub {
    font-size: 12px;
    color: #0284C7;
    margin-top: 6px;
    font-weight: 500;
}

/* Pipeline Flow Banner */
.pipeline-container {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}

.pipeline-step {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    color: #1E293B;
}

.pipeline-step.active {
    background: #EFF6FF;
    border-color: #3B82F6;
    color: #1D4ED8;
}

.pipeline-arrow {
    color: #94A3B8;
    font-weight: 700;
    font-size: 14px;
}

/* Badges */
.badge-tbo {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
    color: white;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    display: inline-block;
    letter-spacing: 0.3px;
}

.badge-procured {
    background: #DCFCE7;
    color: #15803D;
    border: 1px solid #86EFAC;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}

.badge-risk {
    background: #FEE2E2;
    color: #B91C1C;
    border: 1px solid #FCA5A5;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}

/* Hotel Card in Travel Agent */
.hotel-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}

.hotel-card.preferred {
    border-left: 4px solid #2563EB;
    background: #F8FAFC;
}

.hotel-title {
    font-size: 17px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 4px;
}

.hotel-meta {
    font-size: 12px;
    color: #64748B;
    margin-bottom: 8px;
}

.hotel-price {
    font-size: 20px;
    font-weight: 700;
    color: #1D4ED8;
}

/* Confirmation and Warning Banners */
.alert-box {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 4px solid #F59E0B;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 14px 0;
    color: #92400E;
    font-size: 13.5px;
}

.success-box {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-left: 4px solid #22C55E;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 14px 0;
    color: #166534;
    font-size: 13.5px;
}
</style>
"""

def render_header(title: str, subtitle: str):
    """Renders the top branding header without leading whitespace to prevent Markdown code block parsing."""
    return f'<div class="tbo-header"><h1>{title}</h1><p>{subtitle}</p></div>'

def render_pipeline_flow(current_step: str = "Overview"):
    """Renders the workflow navigation banner across all modules."""
    steps = [
        ("Supplier Data", "Raw Listings"),
        ("Clean Catalog", "Deduplicated & Merged"),
        ("Smart Buying", "Forecasted & Procured"),
        ("AI Travel Agent", "Personalized Selling"),
        ("Booking & Demand", "Real-Time Sync")
    ]
    html_parts = ['<div class="pipeline-container">']
    for i, (name, sub) in enumerate(steps):
        is_active = (current_step.lower() in name.lower())
        active_cls = "active" if is_active else ""
        html_parts.append(
            f'<div class="pipeline-step {active_cls}">'
            f'<div><div>{name}</div>'
            f'<div style="font-size: 10px; color: #64748B; font-weight: normal;">{sub}</div></div>'
            f'</div>'
        )
        if i < len(steps) - 1:
            html_parts.append('<div class="pipeline-arrow">&#10142;</div>')
    html_parts.append('</div>')
    return "".join(html_parts)

def render_metric_card(label: str, value: str, sub: str = "", tag: str = ""):
    """
    Renders an attractive SaaS metric card.
    Constructs compact HTML without leading whitespace/newlines to ensure Streamlit's
    Markdown parser renders pure HTML instead of a <pre><code> block.
    """
    tag_html = f'<span class="badge-tbo" style="float: right;">{tag}</span>' if tag else ""
    return (
        f'<div class="metric-card">'
        f'{tag_html}'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-sub">{sub}</div>'
        f'</div>'
    )
