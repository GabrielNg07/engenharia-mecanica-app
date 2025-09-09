import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.shaft_calculations import show_shaft_design_page
from modules.gear_calculations import show_gear_design_page
from modules.material_database import show_material_database_page

# Configure page
st.set_page_config(
    page_title="Mechanical Engineering Design Tool",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("⚙️ Mechanical Engineering Design Tool")
    st.markdown("Professional shaft and gear design calculations and analysis")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Design Tool",
        ["Home", "Shaft Design", "Gear Design", "Material Database"]
    )
    
    if page == "Home":
        show_home_page()
    elif page == "Shaft Design":
        show_shaft_design_page()
    elif page == "Gear Design":
        show_gear_design_page()
    elif page == "Material Database":
        show_material_database_page()

def show_home_page():
    st.header("Welcome to the Mechanical Engineering Design Tool")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Shaft Design")
        st.markdown("""
        - **Diameter calculations** based on torque and bending moment
        - **Stress analysis** including von Mises stress calculations
        - **Deflection analysis** for shaft bending and torsion
        - **Safety factor** calculations with material properties
        - **Fatigue analysis** for cyclic loading conditions
        """)
        
        if st.button("Go to Shaft Design", key="shaft_btn"):
            st.rerun()
    
    with col2:
        st.subheader("⚙️ Gear Design")
        st.markdown("""
        - **Module and pitch** diameter calculations
        - **Gear ratio** optimization and analysis
        - **Tooth strength** calculations (Lewis equation)
        - **Contact stress** analysis (Hertzian stress)
        - **Power transmission** capacity calculations
        """)
        
        if st.button("Go to Gear Design", key="gear_btn"):
            st.rerun()
    
    st.subheader("📊 Features")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.metric("Material Properties", "50+", "Engineering materials")
    
    with feature_col2:
        st.metric("Safety Standards", "ASME/ISO", "Compliance ready")
    
    with feature_col3:
        st.metric("Export Formats", "PDF/CSV", "Professional reports")
    
    st.markdown("---")
    st.subheader("📋 Material Database")
    st.markdown("""
    Access comprehensive material properties including:
    - Yield strength, ultimate tensile strength
    - Elastic modulus, Poisson's ratio
    - Fatigue strength and endurance limit
    - Common engineering alloys and steels
    """)

if __name__ == "__main__":
    main()
