import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import math
from .material_database import get_material_properties, get_all_materials
from .utils import validate_positive_input, calculate_safety_factor
from .export_utils import export_shaft_results

def show_shaft_design_page():
    st.header("🔧 Shaft Design Calculator")
    st.markdown("Calculate shaft dimensions, stresses, and deflections")
    
    # Create tabs for different calculations
    tab1, tab2, tab3, tab4 = st.tabs(["Basic Design", "Stress Analysis", "Deflection Analysis", "Results Summary"])
    
    with tab1:
        show_basic_shaft_design()
    
    with tab2:
        show_stress_analysis()
    
    with tab3:
        show_deflection_analysis()
    
    with tab4:
        show_results_summary()

def show_basic_shaft_design():
    st.subheader("Basic Shaft Design Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Loading Conditions**")
        torque = st.number_input("Torque (N⋅m)", min_value=0.0, value=1000.0, step=10.0)
        bending_moment = st.number_input("Bending Moment (N⋅m)", min_value=0.0, value=500.0, step=10.0)
        axial_force = st.number_input("Axial Force (N)", min_value=0.0, value=0.0, step=10.0)
        
        st.markdown("**Shaft Properties**")
        shaft_length = st.number_input("Shaft Length (mm)", min_value=1.0, value=1000.0, step=10.0)
        hollow_shaft = st.checkbox("Hollow Shaft")
        
        if hollow_shaft:
            inner_diameter = st.number_input("Inner Diameter (mm)", min_value=0.0, value=20.0, step=1.0)
        else:
            inner_diameter = 0.0
    
    with col2:
        st.markdown("**Material Selection**")
        materials = get_all_materials()
        selected_material = st.selectbox("Select Material", materials)
        material_props = get_material_properties(selected_material)
        
        st.markdown("**Safety Requirements**")
        target_safety_factor = st.number_input("Target Safety Factor", min_value=1.0, value=2.0, step=0.1)
        
        st.markdown("**Design Approach**")
        design_approach = st.radio(
            "Design Method",
            ["Calculate required diameter", "Verify given diameter"]
        )
        
        if design_approach == "Verify given diameter":
            given_diameter = st.number_input("Outer Diameter (mm)", min_value=1.0, value=50.0, step=1.0)
        else:
            given_diameter = 50.0  # Default value for calculation
    
    # Calculations
    if st.button("Calculate Shaft Design", type="primary"):
        try:
            if design_approach == "Calculate required diameter":
                diameter = calculate_required_diameter(torque, bending_moment, axial_force, 
                                                    material_props, target_safety_factor, inner_diameter)
                st.session_state.shaft_diameter = diameter
                st.success(f"Required outer diameter: {diameter:.2f} mm")
            else:
                diameter = given_diameter
                safety_factor = verify_shaft_diameter(diameter, inner_diameter, torque, bending_moment, 
                                                    axial_force, material_props)
                st.session_state.shaft_diameter = diameter
                if safety_factor >= target_safety_factor:
                    st.success(f"Design is safe! Safety factor: {safety_factor:.2f}")
                else:
                    st.warning(f"Design may be unsafe. Safety factor: {safety_factor:.2f}")
            
            # Store calculation results in session state
            st.session_state.shaft_params = {
                'torque': torque,
                'bending_moment': bending_moment,
                'axial_force': axial_force,
                'shaft_length': shaft_length,
                'outer_diameter': diameter,
                'inner_diameter': inner_diameter,
                'material': selected_material,
                'material_props': material_props,
                'target_safety_factor': target_safety_factor
            }
            
        except Exception as e:
            st.error(f"Calculation error: {str(e)}")

def calculate_required_diameter(torque, bending_moment, axial_force, material_props, safety_factor, inner_diameter=0.0):
    """Calculate required shaft diameter based on equivalent stress"""
    allowable_stress = material_props['yield_strength'] / safety_factor
    
    # Calculate equivalent moment using Soderberg criterion
    equivalent_moment = math.sqrt(bending_moment**2 + (0.75 * torque)**2)
    
    if inner_diameter == 0:  # Solid shaft
        diameter = ((32 * equivalent_moment) / (math.pi * allowable_stress)) ** (1/3)
    else:  # Hollow shaft
        # Iterative solution for hollow shaft
        diameter = inner_diameter + 10  # Initial guess
        for _ in range(100):  # Max iterations
            J = (math.pi / 32) * (diameter**4 - inner_diameter**4)
            section_modulus = J / (diameter / 2)
            stress = equivalent_moment / section_modulus
            if stress <= allowable_stress:
                break
            diameter += 0.1
    
    return diameter * 1000  # Convert to mm

def verify_shaft_diameter(outer_diameter, inner_diameter, torque, bending_moment, axial_force, material_props):
    """Verify shaft diameter and calculate safety factor"""
    outer_diameter = outer_diameter / 1000  # Convert to meters
    inner_diameter = inner_diameter / 1000
    
    # Calculate section properties
    if inner_diameter == 0:  # Solid shaft
        area = math.pi * (outer_diameter/2)**2
        I = math.pi * outer_diameter**4 / 64
        J = math.pi * outer_diameter**4 / 32
    else:  # Hollow shaft
        area = math.pi * ((outer_diameter/2)**2 - (inner_diameter/2)**2)
        I = math.pi * (outer_diameter**4 - inner_diameter**4) / 64
        J = math.pi * (outer_diameter**4 - inner_diameter**4) / 32
    
    # Calculate stresses
    axial_stress = axial_force / area if area > 0 else 0
    bending_stress = bending_moment * (outer_diameter/2) / I if I > 0 else 0
    shear_stress = torque * (outer_diameter/2) / J if J > 0 else 0
    
    # Calculate von Mises equivalent stress
    equivalent_stress = math.sqrt((axial_stress + bending_stress)**2 + 3 * shear_stress**2)
    
    # Calculate safety factor
    safety_factor = material_props['yield_strength'] / equivalent_stress if equivalent_stress > 0 else float('inf')
    
    return safety_factor

def show_stress_analysis():
    st.subheader("Detailed Stress Analysis")
    
    if 'shaft_params' not in st.session_state:
        st.warning("Please complete the basic design calculation first.")
        return
    
    params = st.session_state.shaft_params
    
    # Calculate detailed stresses
    outer_diameter = params['outer_diameter'] / 1000  # Convert to meters
    inner_diameter = params['inner_diameter'] / 1000
    
    # Section properties
    if inner_diameter == 0:  # Solid shaft
        area = math.pi * (outer_diameter/2)**2
        I = math.pi * outer_diameter**4 / 64
        J = math.pi * outer_diameter**4 / 32
    else:  # Hollow shaft
        area = math.pi * ((outer_diameter/2)**2 - (inner_diameter/2)**2)
        I = math.pi * (outer_diameter**4 - inner_diameter**4) / 64
        J = math.pi * (outer_diameter**4 - inner_diameter**4) / 32
    
    # Stress calculations
    axial_stress = params['axial_force'] / area if area > 0 else 0
    bending_stress = params['bending_moment'] * (outer_diameter/2) / I if I > 0 else 0
    shear_stress = params['torque'] * (outer_diameter/2) / J if J > 0 else 0
    
    # von Mises equivalent stress
    equivalent_stress = math.sqrt((axial_stress + bending_stress)**2 + 3 * shear_stress**2)
    
    # Safety factor
    safety_factor = params['material_props']['yield_strength'] / equivalent_stress if equivalent_stress > 0 else float('inf')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Stress Components**")
        stress_data = pd.DataFrame({
            'Stress Type': ['Axial', 'Bending', 'Shear', 'von Mises Equivalent'],
            'Value (MPa)': [axial_stress/1e6, bending_stress/1e6, shear_stress/1e6, equivalent_stress/1e6],
            'Limit (MPa)': [params['material_props']['yield_strength']/1e6] * 4
        })
        st.dataframe(stress_data, use_container_width=True)
        
        st.metric("Safety Factor", f"{safety_factor:.2f}")
        
        if safety_factor >= params['target_safety_factor']:
            st.success("✅ Design meets safety requirements")
        else:
            st.error("❌ Design does not meet safety requirements")
    
    with col2:
        st.markdown("**Stress Distribution Visualization**")
        
        # Create stress comparison chart
        fig = go.Figure()
        
        stress_names = ['Axial', 'Bending', 'Shear', 'von Mises']
        stress_values = [axial_stress/1e6, bending_stress/1e6, shear_stress/1e6, equivalent_stress/1e6]
        
        fig.add_trace(go.Bar(
            x=stress_names,
            y=stress_values,
            name='Calculated Stress',
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Scatter(
            x=stress_names,
            y=[params['material_props']['yield_strength']/1e6] * len(stress_names),
            mode='lines',
            name='Yield Strength Limit',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title="Stress Analysis",
            xaxis_title="Stress Type",
            yaxis_title="Stress (MPa)",
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_deflection_analysis():
    st.subheader("Deflection Analysis")
    
    if 'shaft_params' not in st.session_state:
        st.warning("Please complete the basic design calculation first.")
        return
    
    params = st.session_state.shaft_params
    
    st.markdown("**Deflection Calculations**")
    
    # Simplified deflection calculations (assuming simply supported beam)
    outer_diameter = params['outer_diameter'] / 1000  # Convert to meters
    inner_diameter = params['inner_diameter'] / 1000
    length = params['shaft_length'] / 1000  # Convert to meters
    E = params['material_props']['elastic_modulus']
    G = E / (2 * (1 + params['material_props']['poisson_ratio']))
    
    # Section properties
    if inner_diameter == 0:  # Solid shaft
        I = math.pi * outer_diameter**4 / 64
        J = math.pi * outer_diameter**4 / 32
    else:  # Hollow shaft
        I = math.pi * (outer_diameter**4 - inner_diameter**4) / 64
        J = math.pi * (outer_diameter**4 - inner_diameter**4) / 32
    
    # Bending deflection (maximum at center for simply supported beam with point load)
    force_equivalent = params['bending_moment'] * 4 / length  # Approximate equivalent point load
    bending_deflection = (force_equivalent * length**3) / (48 * E * I) if I > 0 else 0
    
    # Torsional deflection (angle of twist)
    torsional_angle = (params['torque'] * length) / (G * J) if J > 0 else 0
    torsional_deflection = torsional_angle * (outer_diameter / 2)  # Linear deflection at surface
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Deflection Results**")
        deflection_data = pd.DataFrame({
            'Deflection Type': ['Bending', 'Torsional (at surface)', 'Angle of Twist'],
            'Value': [f"{bending_deflection*1000:.3f} mm", 
                     f"{torsional_deflection*1000:.3f} mm",
                     f"{math.degrees(torsional_angle):.3f}°"],
            'Limit': ['L/250', 'Variable', '1° per meter']
        })
        st.dataframe(deflection_data, use_container_width=True)
        
        # Check deflection limits
        bending_limit = length / 250  # Common design limit
        if bending_deflection <= bending_limit:
            st.success(f"✅ Bending deflection within limits ({bending_deflection*1000:.3f} mm ≤ {bending_limit*1000:.1f} mm)")
        else:
            st.warning(f"⚠️ Bending deflection exceeds recommended limit ({bending_deflection*1000:.3f} mm > {bending_limit*1000:.1f} mm)")
    
    with col2:
        st.markdown("**Deflection Profile Visualization**")
        
        # Create deflection curve visualization
        x = np.linspace(0, length, 100)
        # Simplified deflection curve for uniformly distributed load
        deflection_curve = bending_deflection * (x/length) * (1 - (x/length))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x*1000,  # Convert to mm
            y=deflection_curve*1000,  # Convert to mm
            mode='lines',
            name='Bending Deflection',
            line=dict(color='blue')
        ))
        
        fig.add_hline(y=bending_limit*1000, line_dash="dash", line_color="red", 
                     annotation_text="Deflection Limit")
        
        fig.update_layout(
            title="Shaft Deflection Profile",
            xaxis_title="Position along shaft (mm)",
            yaxis_title="Deflection (mm)",
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_results_summary():
    st.subheader("Design Results Summary")
    
    if 'shaft_params' not in st.session_state:
        st.warning("Please complete the basic design calculation first.")
        return
    
    params = st.session_state.shaft_params
    
    # Calculate summary metrics
    outer_diameter = params['outer_diameter'] / 1000
    inner_diameter = params['inner_diameter'] / 1000
    
    # Section properties
    if inner_diameter == 0:
        area = math.pi * (outer_diameter/2)**2
        I = math.pi * outer_diameter**4 / 64
        J = math.pi * outer_diameter**4 / 32
        weight_per_meter = area * 7850  # kg/m (assuming steel density)
    else:
        area = math.pi * ((outer_diameter/2)**2 - (inner_diameter/2)**2)
        I = math.pi * (outer_diameter**4 - inner_diameter**4) / 64
        J = math.pi * (outer_diameter**4 - inner_diameter**4) / 32
        weight_per_meter = area * 7850
    
    # Stresses
    axial_stress = params['axial_force'] / area if area > 0 else 0
    bending_stress = params['bending_moment'] * (outer_diameter/2) / I if I > 0 else 0
    shear_stress = params['torque'] * (outer_diameter/2) / J if J > 0 else 0
    equivalent_stress = math.sqrt((axial_stress + bending_stress)**2 + 3 * shear_stress**2)
    safety_factor = params['material_props']['yield_strength'] / equivalent_stress if equivalent_stress > 0 else float('inf')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Outer Diameter", f"{params['outer_diameter']:.1f} mm")
        if inner_diameter > 0:
            st.metric("Inner Diameter", f"{params['inner_diameter']:.1f} mm")
        st.metric("Safety Factor", f"{safety_factor:.2f}")
    
    with col2:
        st.metric("von Mises Stress", f"{equivalent_stress/1e6:.1f} MPa")
        st.metric("Material", params['material'])
        st.metric("Weight/Length", f"{weight_per_meter:.2f} kg/m")
    
    with col3:
        st.metric("Yield Strength", f"{params['material_props']['yield_strength']/1e6:.0f} MPa")
        st.metric("Elastic Modulus", f"{params['material_props']['elastic_modulus']/1e9:.0f} GPa")
        st.metric("Shaft Length", f"{params['shaft_length']:.0f} mm")
    
    # Summary table
    st.markdown("**Complete Design Summary**")
    summary_data = {
        'Parameter': [
            'Outer Diameter (mm)',
            'Inner Diameter (mm)',
            'Torque (N⋅m)',
            'Bending Moment (N⋅m)',
            'Axial Force (N)',
            'von Mises Stress (MPa)',
            'Safety Factor',
            'Material',
            'Yield Strength (MPa)',
            'Weight per meter (kg/m)'
        ],
        'Value': [
            f"{params['outer_diameter']:.2f}",
            f"{params['inner_diameter']:.2f}",
            f"{params['torque']:.0f}",
            f"{params['bending_moment']:.0f}",
            f"{params['axial_force']:.0f}",
            f"{equivalent_stress/1e6:.2f}",
            f"{safety_factor:.2f}",
            params['material'],
            f"{params['material_props']['yield_strength']/1e6:.0f}",
            f"{weight_per_meter:.2f}"
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)
    
    # Export options
    st.markdown("**Export Results**")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export to PDF", type="secondary"):
            try:
                export_shaft_results(params, summary_df, 'pdf')
                st.success("PDF export completed!")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
    
    with col2:
        if st.button("Export to CSV", type="secondary"):
            try:
                csv_data = summary_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="shaft_design_results.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
