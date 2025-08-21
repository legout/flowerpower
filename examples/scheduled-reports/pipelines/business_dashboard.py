"""
Business Dashboard Report Pipeline

This pipeline generates comprehensive business reports combining sales, inventory,
and customer data. It creates HTML/PDF reports with KPI tracking, visualizations,
and automated alerts when metrics fall below thresholds.
"""

import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from hamilton import function
from hamilton.function_modifiers import parameterize, config

from flowerpower.cfg import Config

logger = logging.getLogger(__name__)

# Load configuration parameters
BASE_DIR = Path(__file__).parent.parent
PARAMS = Config.load(str(BASE_DIR), {}).run.inputs


def sales_data(sales_file: str) -> pd.DataFrame:
    """Load sales data from CSV file."""
    file_path = BASE_DIR / sales_file
    logger.info(f"Loading sales data from {file_path}")
    
    df = pd.read_csv(file_path)
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    df['revenue'] = df['quantity'] * df['unit_price']
    
    logger.info(f"Loaded {len(df)} sales records")
    return df


def inventory_data(inventory_file: str) -> pd.DataFrame:
    """Load inventory data from CSV file."""
    file_path = BASE_DIR / inventory_file
    logger.info(f"Loading inventory data from {file_path}")
    
    df = pd.read_csv(file_path)
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    
    logger.info(f"Loaded {len(df)} inventory records")
    return df


def customer_data(customer_file: str) -> pd.DataFrame:
    """Load customer data from CSV file."""
    file_path = BASE_DIR / customer_file
    logger.info(f"Loading customer data from {file_path}")
    
    df = pd.read_csv(file_path)
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    df['last_purchase'] = pd.to_datetime(df['last_purchase'])
    
    logger.info(f"Loaded {len(df)} customer records")
    return df


def filtered_sales_data(
    sales_data: pd.DataFrame,
    current_date: str,
    start_date: str,
    end_date: str,
    report_frequency: str
) -> pd.DataFrame:
    """Filter sales data based on reporting period and frequency."""
    current = pd.to_datetime(current_date)
    
    if report_frequency == "daily":
        start_filter = current
        end_filter = current
    elif report_frequency == "weekly":
        start_filter = current - timedelta(days=7)
        end_filter = current
    elif report_frequency == "monthly":
        start_filter = current.replace(day=1)
        end_filter = current
    elif report_frequency == "quarterly":
        quarter = (current.month - 1) // 3 + 1
        start_filter = pd.to_datetime(f"{current.year}-{(quarter-1)*3+1:02d}-01")
        end_filter = current
    else:
        start_filter = pd.to_datetime(start_date)
        end_filter = pd.to_datetime(end_date)
    
    filtered = sales_data[
        (sales_data['sale_date'] >= start_filter) &
        (sales_data['sale_date'] <= end_filter)
    ]
    
    logger.info(f"Filtered to {len(filtered)} sales records for {report_frequency} report")
    return filtered


def sales_kpis(filtered_sales_data: pd.DataFrame) -> Dict[str, Any]:
    """Calculate key sales performance indicators."""
    total_revenue = filtered_sales_data['revenue'].sum()
    total_orders = len(filtered_sales_data)
    avg_order_value = filtered_sales_data['revenue'].mean() if total_orders > 0 else 0
    
    # Daily breakdown
    daily_sales = filtered_sales_data.groupby(
        filtered_sales_data['sale_date'].dt.date
    )['revenue'].sum()
    
    # Product performance
    product_sales = filtered_sales_data.groupby('product_name').agg({
        'revenue': 'sum',
        'quantity': 'sum'
    }).sort_values('revenue', ascending=False)
    
    kpis = {
        'total_revenue': float(total_revenue),
        'total_orders': int(total_orders),
        'avg_order_value': float(avg_order_value),
        'daily_sales': daily_sales.to_dict(),
        'top_products': product_sales.head(10).to_dict(),
        'best_selling_product': product_sales.index[0] if len(product_sales) > 0 else None
    }
    
    logger.info(f"Calculated sales KPIs: Revenue=${total_revenue:,.2f}, Orders={total_orders}")
    return kpis


def inventory_kpis(
    inventory_data: pd.DataFrame,
    low_inventory_threshold: int
) -> Dict[str, Any]:
    """Calculate inventory key performance indicators."""
    total_products = len(inventory_data)
    total_stock_value = (inventory_data['quantity'] * inventory_data['unit_cost']).sum()
    
    # Low stock analysis
    low_stock_items = inventory_data[
        inventory_data['quantity'] <= low_inventory_threshold
    ]
    
    # Stock by category
    category_stock = inventory_data.groupby('category').agg({
        'quantity': 'sum',
        'unit_cost': 'mean'
    })
    
    kpis = {
        'total_products': int(total_products),
        'total_stock_value': float(total_stock_value),
        'low_stock_count': int(len(low_stock_items)),
        'low_stock_items': low_stock_items[['product_name', 'quantity']].to_dict('records'),
        'stock_by_category': category_stock.to_dict(),
        'avg_stock_level': float(inventory_data['quantity'].mean())
    }
    
    logger.info(f"Calculated inventory KPIs: {total_products} products, {len(low_stock_items)} low stock")
    return kpis


def customer_kpis(
    customer_data: pd.DataFrame,
    current_date: str,
    customer_retention_target: float
) -> Dict[str, Any]:
    """Calculate customer key performance indicators."""
    current = pd.to_datetime(current_date)
    
    # Active customers (purchased in last 90 days)
    active_threshold = current - timedelta(days=90)
    active_customers = customer_data[
        customer_data['last_purchase'] >= active_threshold
    ]
    
    # Retention calculation
    retention_rate = len(active_customers) / len(customer_data) if len(customer_data) > 0 else 0
    
    # Customer lifetime value (simplified)
    avg_customer_value = customer_data['total_spent'].mean()
    
    # New customers this month
    month_start = current.replace(day=1)
    new_customers = customer_data[
        customer_data['signup_date'] >= month_start
    ]
    
    kpis = {
        'total_customers': int(len(customer_data)),
        'active_customers': int(len(active_customers)),
        'retention_rate': float(retention_rate),
        'avg_customer_value': float(avg_customer_value),
        'new_customers_this_month': int(len(new_customers)),
        'retention_vs_target': retention_rate >= customer_retention_target
    }
    
    logger.info(f"Calculated customer KPIs: {len(customer_data)} total, {retention_rate:.2%} retention")
    return kpis


def sales_charts(
    sales_kpis: Dict[str, Any],
    include_charts: bool,
    chart_style: str
) -> Dict[str, Any]:
    """Generate sales visualization charts."""
    if not include_charts:
        return {"charts_enabled": False}
    
    charts = {}
    
    # Daily sales trend
    daily_data = list(sales_kpis['daily_sales'].items())
    if daily_data:
        dates, revenues = zip(*daily_data)
        
        fig_daily = go.Figure()
        fig_daily.add_trace(go.Scatter(
            x=dates,
            y=revenues,
            mode='lines+markers',
            name='Daily Revenue',
            line=dict(color='#1f77b4', width=3)
        ))
        fig_daily.update_layout(
            title='Daily Sales Trend',
            xaxis_title='Date',
            yaxis_title='Revenue ($)',
            template='plotly_white'
        )
        charts['daily_sales'] = fig_daily.to_html(include_plotlyjs='cdn')
    
    # Top products chart
    top_products = sales_kpis['top_products']['revenue']
    if top_products:
        products = list(top_products.keys())
        revenues = list(top_products.values())
        
        fig_products = go.Figure(data=[
            go.Bar(x=products[:5], y=revenues[:5], marker_color='#ff7f0e')
        ])
        fig_products.update_layout(
            title='Top 5 Products by Revenue',
            xaxis_title='Product',
            yaxis_title='Revenue ($)',
            template='plotly_white'
        )
        charts['top_products'] = fig_products.to_html(include_plotlyjs='cdn')
    
    logger.info(f"Generated {len(charts)} sales charts")
    return {"charts_enabled": True, "charts": charts}


def alert_analysis(
    sales_kpis: Dict[str, Any],
    inventory_kpis: Dict[str, Any],
    customer_kpis: Dict[str, Any],
    enabled: bool,
    alert_thresholds: Dict[str, Any],
    sales_target_monthly: int,
    low_inventory_threshold: int,
    customer_retention_target: float
) -> Dict[str, Any]:
    """Analyze KPIs and generate alerts for threshold violations."""
    if not enabled:
        return {"alerts_enabled": False, "alerts": []}
    
    alerts = []
    
    # Sales target alert
    if alert_thresholds.get('sales_below_target', False):
        if sales_kpis['total_revenue'] < sales_target_monthly:
            alerts.append({
                'type': 'sales_target',
                'severity': 'warning',
                'message': f"Sales revenue ${sales_kpis['total_revenue']:,.2f} below target ${sales_target_monthly:,.2f}",
                'value': sales_kpis['total_revenue'],
                'target': sales_target_monthly
            })
    
    # Low inventory alert
    if alert_thresholds.get('low_inventory', False):
        if inventory_kpis['low_stock_count'] > 0:
            alerts.append({
                'type': 'low_inventory',
                'severity': 'critical',
                'message': f"{inventory_kpis['low_stock_count']} products below minimum stock level",
                'value': inventory_kpis['low_stock_count'],
                'items': inventory_kpis['low_stock_items']
            })
    
    # Customer retention alert
    if alert_thresholds.get('poor_retention', False):
        if not customer_kpis['retention_vs_target']:
            alerts.append({
                'type': 'customer_retention',
                'severity': 'warning',
                'message': f"Customer retention {customer_kpis['retention_rate']:.2%} below target {customer_retention_target:.2%}",
                'value': customer_kpis['retention_rate'],
                'target': customer_retention_target
            })
    
    logger.info(f"Generated {len(alerts)} business alerts")
    return {"alerts_enabled": True, "alerts": alerts}


def business_dashboard(
    sales_kpis: Dict[str, Any],
    inventory_kpis: Dict[str, Any],
    customer_kpis: Dict[str, Any],
    sales_charts: Dict[str, Any],
    alert_analysis: Dict[str, Any],
    current_date: str,
    output_format: str,
    output_dir: str
) -> Dict[str, Any]:
    """Generate comprehensive business dashboard report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_date = pd.to_datetime(current_date).strftime("%Y-%m-%d")
    
    # Ensure output directory exists
    output_path = BASE_DIR / output_dir
    output_path.mkdir(exist_ok=True)
    
    # Generate HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Business Dashboard - {report_date}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .kpi-section {{ margin: 20px 0; padding: 20px; background: #f5f5f5; border-radius: 5px; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
            .kpi-card {{ background: white; padding: 15px; border-radius: 5px; text-align: center; }}
            .kpi-value {{ font-size: 24px; font-weight: bold; color: #333; }}
            .kpi-label {{ font-size: 14px; color: #666; }}
            .alert {{ padding: 10px; margin: 5px 0; border-radius: 5px; }}
            .alert-warning {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
            .alert-critical {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
            .chart-container {{ margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Business Dashboard</h1>
            <h2>Report Date: {report_date}</h2>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="kpi-section">
            <h3>📊 Sales Performance</h3>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-value">${sales_kpis['total_revenue']:,.2f}</div>
                    <div class="kpi-label">Total Revenue</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{sales_kpis['total_orders']:,}</div>
                    <div class="kpi-label">Total Orders</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">${sales_kpis['avg_order_value']:,.2f}</div>
                    <div class="kpi-label">Avg Order Value</div>
                </div>
            </div>
        </div>
        
        <div class="kpi-section">
            <h3>📦 Inventory Status</h3>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-value">{inventory_kpis['total_products']:,}</div>
                    <div class="kpi-label">Total Products</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">${inventory_kpis['total_stock_value']:,.2f}</div>
                    <div class="kpi-label">Stock Value</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{inventory_kpis['low_stock_count']}</div>
                    <div class="kpi-label">Low Stock Items</div>
                </div>
            </div>
        </div>
        
        <div class="kpi-section">
            <h3>👥 Customer Metrics</h3>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-value">{customer_kpis['total_customers']:,}</div>
                    <div class="kpi-label">Total Customers</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{customer_kpis['active_customers']:,}</div>
                    <div class="kpi-label">Active Customers</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{customer_kpis['retention_rate']:.1%}</div>
                    <div class="kpi-label">Retention Rate</div>
                </div>
            </div>
        </div>
    """
    
    # Add alerts section
    if alert_analysis['alerts_enabled'] and alert_analysis['alerts']:
        html_content += """
        <div class="kpi-section">
            <h3>🚨 Business Alerts</h3>
        """
        for alert in alert_analysis['alerts']:
            severity_class = f"alert-{alert['severity']}"
            html_content += f"""
            <div class="alert {severity_class}">
                <strong>{alert['type'].replace('_', ' ').title()}:</strong> {alert['message']}
            </div>
            """
        html_content += "</div>"
    
    # Add charts if enabled
    if sales_charts['charts_enabled'] and 'charts' in sales_charts:
        html_content += """
        <div class="kpi-section">
            <h3>📈 Sales Visualizations</h3>
        """
        for chart_name, chart_html in sales_charts['charts'].items():
            html_content += f"""
            <div class="chart-container">
                <h4>{chart_name.replace('_', ' ').title()}</h4>
                {chart_html}
            </div>
            """
        html_content += "</div>"
    
    html_content += """
    </body>
    </html>
    """
    
    # Save report
    report_filename = f"business_dashboard_{timestamp}.html"
    report_path = output_path / report_filename
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Create symlink to latest report
    latest_path = output_path / "latest_dashboard.html"
    if latest_path.exists():
        latest_path.unlink()
    latest_path.symlink_to(report_filename)
    
    result = {
        'report_generated': True,
        'report_path': str(report_path),
        'report_date': report_date,
        'timestamp': timestamp,
        'format': output_format,
        'kpis': {
            'sales': sales_kpis,
            'inventory': inventory_kpis,
            'customers': customer_kpis
        },
        'alerts': alert_analysis['alerts'] if alert_analysis['alerts_enabled'] else [],
        'charts_included': sales_charts['charts_enabled']
    }
    
    logger.info(f"Generated business dashboard report: {report_path}")
    return result