import os
import pandas as pd
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to load and validate orders data
def load_orders_data():
    """Load orders data from CSV file and validate it."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, '..', 'data', 'orders.csv')
        
        if not os.path.exists(csv_path):
            logging.error(f"File not found at {csv_path}")
            return None
        
        orders_df = pd.read_csv(csv_path, delimiter=';')
        logging.info("Orders data loaded successfully.")
        
        # Convert date column to datetime
        orders_df['date'] = pd.to_datetime(orders_df['date'], format='%d.%m.%y', errors='coerce')
        if orders_df['date'].isnull().any():
            logging.warning("Some dates could not be parsed in the 'orders.csv' file.")
        
        return orders_df
    except Exception as e:
        logging.error(f"Error loading orders data: {e}")
        return None

# Function to calculate crate distribution
def calculate_crate_distribution(df):
    """Calculate the distribution of crate types."""
    try:
        if df is None or df.empty:
            logging.warning("Data not available for calculating distribution.")
            return None
        
        # Count crate types and calculate percentages
        crate_counts = df['crate_type'].value_counts().reset_index()
        crate_counts.columns = ['crate_type', 'count']
        total_orders = crate_counts['count'].sum()
        crate_counts['percentage'] = (crate_counts['count'] / total_orders * 100).round(2)
        
        logging.info("Crate distribution calculated successfully.")
        return crate_counts
    except Exception as e:
        logging.error(f"Error calculating crate distribution: {e}")
        return None

# Function to load and validate sales performance data
def load_sales_performance():
    """Load sales performance data from CSV file and validate it."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, '..', 'output', 'sales_performance.csv')
        
        if not os.path.exists(csv_path):
            logging.error(f"File not found at {csv_path}")
            return None
        
        sales_performance_df = pd.read_csv(csv_path)
        logging.info("Sales performance data loaded successfully.")
        
        # Convert gross value to 'k' and round
        sales_performance_df['gross_per_salesowner_k'] = (sales_performance_df['gross_per_salesowner'] / 1000).round(2)
        
        return sales_performance_df
    except Exception as e:
        logging.error(f"Error loading sales performance data: {e}")
        return None

# Function to load top performers data
def load_top_performers_data():
    """Load top 5 performers data from CSV file and validate it."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, '..', 'output', 'top_5_performers.csv')
        
        if not os.path.exists(csv_path):
            logging.error(f"File not found at {csv_path}")
            return None
        
        top_performers_df = pd.read_csv(csv_path)
        logging.info("Top performers data loaded successfully.")
        
        # Format gross_rolling_3m for display
        top_performers_df['gross_rolling_3m_formatted'] = top_performers_df['gross_rolling_3m'].map("{:,.2f}".format)
        
        return top_performers_df
    except Exception as e:
        logging.error(f"Error loading top performers data: {e}")
        return None

# Function to create crate distribution plot
def create_crate_distribution_plot(crate_counts):
    """Generate the crate distribution bar plot using Plotly."""
    fig = px.bar(
        crate_counts,
        x='crate_type',
        y='count',
        title='Distribution of Orders by Crate Type',
        labels={'crate_type': 'Crate Type', 'count': 'Number of Orders', 'percentage': 'Percentage'},
        color='crate_type',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Orders: %{y}<br>Percentage: %{customdata}%',
        customdata=crate_counts['percentage']
    )
    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center'},
        xaxis_title='Crate Type',
        yaxis_title='Number of Orders',
        template='plotly_white',
        font=dict(size=16),
    )
    return fig

# Function to create sales performance plot
def create_sales_performance_plot(sales_performance_df):
    """Generate the sales performance bar plot for plastic crates using Plotly."""
    fig = px.bar(
        sales_performance_df.sort_values(by='gross_per_salesowner'),
        x='gross_per_salesowner_k',
        y='salesowners',
        orientation='h',
        title="Sales Performance for Plastic Crates (Last 12 Months)",
        labels={'salesowners': 'Sales Owners', 'gross_per_salesowner_k': 'Gross Value per Salesowner (k€)'},
        text='gross_per_salesowner_k',
        color='salesowners',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(texttemplate='%{text}k', textposition='outside', textfont_size=10)
    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center'},
        xaxis_title="Gross Value per Salesowner (k€)",
        yaxis_title="",
        xaxis=dict(tickformat=",", tickprefix="€", ticksuffix="k"),
        template='plotly_white',
        font=dict(size=16),
    )
    return fig

# Function to create top performers table
def create_top_performers_table(top_performers_df):
    """Generate a table plot of top 5 performers with formatted values."""
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=["Year-Month", "Salesowner", "Gross Rolling 3M (€)", "Rank"],
                    fill_color="lightblue",
                    align="center",
                    font=dict(size=12, color="black"),
                ),
                cells=dict(
                    values=[
                        top_performers_df["year_month"],
                        top_performers_df["salesowners"],
                        top_performers_df["gross_rolling_3m_formatted"],
                        top_performers_df["rank"].astype(int),
                    ],
                    fill_color="white",
                    align="center",
                    font=dict(size=11),
                ),
            )
        ]
    )
    fig.update_layout(
        title="Top 5 Performers Selling Plastic Crates for Each 3-Month Rolling Window",
        title_x=0.5,
        margin=dict(l=20, r=20, t=60, b=20),
        width=800,
        height=500,
    )
    return fig

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load data and create plots
orders_df = load_orders_data()
crate_counts = calculate_crate_distribution(orders_df)
crate_fig = create_crate_distribution_plot(crate_counts)

sales_performance_df = load_sales_performance()
sales_fig = create_sales_performance_plot(sales_performance_df)

top_performers_df = load_top_performers_data()
top_performers_table = create_top_performers_table(top_performers_df)

# Define the layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("IFCO Data Engineering Challenge", className="text-center text-primary mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.H4("What is the distribution of orders by crate type?", className="text-center text-secondary mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=crate_fig), width=12, className="mb-5")
    ]),
    dbc.Row([
        dbc.Col(html.H4("Which sales owners need most training to improve selling on plastic crates?", className="text-center text-secondary mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=sales_fig), width=12, className="mb-5")
    ]),
    dbc.Row([
        dbc.Col(html.H4("Top 5 Performers Selling Plastic Crates for Each 3-Month Rolling Window", className="text-center text-secondary mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=top_performers_table), width=12, className="mb-5")
    ])
], fluid=True)

if __name__ == "__main__":
    try:
        logging.info("Starting the Dash application.")
        app.run_server(host="0.0.0.0", port=8050)
    except Exception as e:
        logging.error(f"An error occurred while running the Dash app: {e}")