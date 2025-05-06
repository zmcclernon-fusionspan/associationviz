import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from io import StringIO

# ----------------------------
# SIMPLE LOGIN SETUP
# ----------------------------
USERNAME = "fusionspansales"
PASSWORD = "fusionSpan!123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.form("login_form"):
        st.subheader("🔐 Secure Login")
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if user == USERNAME and pw == PASSWORD:
                st.session_state.authenticated = True
                st.success("✅ Login successful")
            else:
                st.error("❌ Invalid credentials")
    st.stop()

# ----------------------------
# MAIN APP LOGIC (MAP + FILTERS)
# ----------------------------
# Load data
st.title("📍 Association Map Viewer")
df = pd.read_csv("AssociationList_Geocoded.csv")
df = df.dropna(subset=['Lat', 'Lon'])

# Sidebar filters
st.sidebar.title("🔍 Filter Associations")
filter_type = st.sidebar.radio("Choose a filter type:", ["AE Layer", "RVP", "AE"])

filtered_df = df.copy()

if filter_type == "AE Layer":
    ae_layer = st.sidebar.selectbox("AE Layer", ["All"] + sorted(df['AE_Layer'].dropna().unique().tolist()))
    if ae_layer != "All":
        filtered_df = filtered_df[filtered_df['AE_Layer'] == ae_layer]

elif filter_type == "RVP":
    all_rvps = sorted(df['RVP'].dropna().unique())
    selected_rvp = st.sidebar.selectbox("RVP", ["All"] + all_rvps)
    if selected_rvp != "All":
        filtered_df = filtered_df[filtered_df['RVP'] == selected_rvp]

elif filter_type == "AE":
    if 'AE' in df.columns:
        all_aes = sorted(df['AE'].dropna().unique())
        selected_ae = st.sidebar.selectbox("Account Executive", ["All"] + all_aes)
        if selected_ae != "All":
            filtered_df = filtered_df[filtered_df['AE'] == selected_ae]

# Summary
st.markdown(f"**{len(filtered_df):,} associations match your filters.**")

# Download button
csv_buffer = StringIO()
filtered_df.to_csv(csv_buffer, index=False)
st.download_button(
    label="📥 Download Filtered List",
    data=csv_buffer.getvalue(),
    file_name="filtered_associations.csv",
    mime="text/csv"
)

# Map creation
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
marker_cluster = MarkerCluster().add_to(m)

for _, row in filtered_df.iterrows():
    popup_html = f"""
    <b>{row['Account Name']}</b><br>
    {row['City']}, {row['State']}<br>
    AE Layer: {row.get('AE_Layer', 'N/A')}<br>
    RVP: {row.get('RVP', 'N/A')}<br>
    AE: {row.get('AE', 'N/A')}
    """
    folium.Marker(
        location=[row['Lat'], row['Lon']],
        tooltip=row['Account Name'],
        popup=folium.Popup(popup_html, max_width=250)
    ).add_to(marker_cluster)

st_folium(m, width=1400, height=700)