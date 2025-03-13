import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# Function to get a fresh database connection

def get_db_connection():
    
    try:
        conn = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="NanDha@12345",
            database="sports_radar_api",
            auth_plugin='mysql_native_password'
        )
        return conn

    except mysql.connector.Error as e:
        st.error(f"Failed to connect to the database: {e}")
        return None

# Load data with a fresh connection every time

def load_data(query, params=None):
    
    conn = None
    df = pd.DataFrame()  
    try:
        conn = get_db_connection()
        if conn:
            df = pd.read_sql_query(query, conn, params=params)

    # Display MySQL error in Streamlit        

    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")  
    
    # Display any other errors

    except Exception as e:
        st.error(f"Unexpected error: {e}")  

    # Finally Close connection

    finally:
        if conn:
            conn.close()  
    return df

# Streamlit UI

st.set_page_config(page_title="Tennis Analytics Dashboard", layout="wide")
st.title("🎾Tennis Analytics Dashboard")
st.sidebar.title("Filters & Navigation")

# Sidebar navigation

menu = ["Competitions", "Venues", "Rankings"]
choice = st.sidebar.selectbox("Select a Category", menu)

# COMPETITIONS

if choice == "Competitions":
    st.subheader("Competition Insights")
    
    # Sidebar filters for competitions

    competition_type = st.sidebar.selectbox("Competition Type", ["All", "Singles", "Doubles"])
    gender = st.sidebar.selectbox("Gender", ["All", "Men", "Women"])
    
    # Build the query dynamically based on filters

    query = """
        SELECT c.competition_name, c.type, c.gender, cat.category_name
        FROM Competitions c
        JOIN Categories cat ON c.category_id = cat.category_id
    """
    conditions = []
    params = []
    
    if competition_type != "All":
        conditions.append("c.type = %s")
        params.append(competition_type)
    
    if gender != "All":
        conditions.append("c.gender = %s")
        params.append(gender)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    df = load_data(query, params=params)
    st.dataframe(df)
    
    # Plot histogram

    if not df.empty:
        fig = px.histogram(df, x='category_name', title="Competitions by Category")
        st.plotly_chart(fig)
    else:
        st.warning("No data found for the selected filters.")

#COMPLEXES 

elif choice == "Venues":
    st.subheader("Venues Insights")
    
    # Fetch unique country names for the list box

    country_query = "SELECT DISTINCT country_name FROM Venues"
    countries = load_data(country_query)["country_name"].tolist()
    
    # Sidebar filters for venues

    country_filter = st.sidebar.selectbox("Select Country", ["All"] + countries)
    
    # Build the query dynamically based on filters

    query = """
        SELECT v.venue_name, v.city_name, v.country_name, c.complex_name
        FROM Venues v
        JOIN Complexes c ON v.complex_id = c.complex_id
    """
    conditions = []
    params = []
    
    if country_filter != "All":
        conditions.append("v.country_name = %s")
        params.append(country_filter)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    df = load_data(query, params=params)
    st.dataframe(df)

    # Plot Bar chart

    if not df.empty:
        fig = px.bar(df, x='country_name', color='city_name', title="Venues by Country")
        st.plotly_chart(fig)
    else:
        st.warning("No data found for the selected filters.")

# DOUBLE RANKING COMPETITORS

elif choice == "Rankings":
    st.subheader("Competitor Rankings")
    
    # Fetch unique country names for the list box

    country_query = "SELECT DISTINCT country FROM Competitors"
    countries = load_data(country_query)["country"].tolist()
    
    # Sidebar filters for rankings

    country_filter = st.sidebar.selectbox("Select Country", ["All"] + countries)
    
    # Rank range filter
    
    min_rank, max_rank = st.sidebar.slider(
        "Select Rank Range",
        min_value=1,
        max_value=1000,  # Adjust max_value based on your data
        value=(1, 100)   # Default range
    )
    
    # Build the query dynamically based on filters

    query = """
        SELECT r.ranks, r.points, c.name, c.country
        FROM Competitor_Rankings r
        JOIN Competitors c ON r.competitor_id = c.competitor_id
    """
    conditions = []
    params = []
    
    if country_filter != "All":
        conditions.append("c.country = %s")
        params.append(country_filter)

    # Add rank range filter

    conditions.append("r.ranks BETWEEN %s AND %s")
    params.extend([min_rank, max_rank])
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    df = load_data(query, params=params)
    st.dataframe(df)

    #Plot scatter plot

    if not df.empty:
        fig = px.scatter(df, x='ranks', y='points', color='country', title="Competitor Rankings")
        st.plotly_chart(fig)
    else:
        st.warning("No data found for the selected filters.")
