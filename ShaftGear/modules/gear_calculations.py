import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import math
from .material_database import get_material_properties, get_all_materials
from .utils import validate_positive_input, calculate_safety_factor
from .export_utils import export_gear_results

def show_gear_design_page():
    st.header("⚙️ Gear Design Calculator")
    st.markdown("Calculate gear dimensions, strength, and contact stresses")
    
    # Create tabs for different calculations
    tab1, tab2, tab3, tab4 = st.tabs(["Basic Design", "Tooth Strength", "Contact Stress", "Results Summary"])
    
    with tab1:
        show_basic_gear_design()
    
    with tab2:
        show_tooth_strength_analysis()
    
    with tab3:
        show_contact_stress_analysis()
    
    with tab4:
        show_gear_results_summary()

def show_basic_gear_design():
    st.subheader("Basic Gear Design Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Gear Pair Configuration**")
        gear_type = st.selectbox("Gear Type", ["Spur Gear", "Helical Gear"])
        
        pinion_teeth = st.number_input("Pinion Teeth (Z₁)", min_value=12, value=20, step=1)
        gear_teeth = st.number_input("Gear Teeth (Z₂)", min_value=12, value=40, step=1)
        
        module = st.number_input("Module (mm)", min_value=0.5, value=3.0, step=0.25)
        
        if gear_type == "Helical Gear":
            helix_angle = st.number_input("Helix Angle (degrees)", min_value=0.0, max_value=45.0, value=20.0, step=1.0)
        else:
            helix_angle = 0.0
        
        face_width = st.number_input("Face Width (mm)", min_value=5.0, value=50.0, step=5.0)
        
        st.markdown("**Operating Conditions**")
        power = st.number_input("Power Transmitted (kW)", min_value=0.1, value=10.0, step=0.1)
        pinion_rpm = st.number_input("Pinion Speed (RPM)", min_value=1.0, value=1500.0, step=10.0)
    
    with col2:
        st.markdown("**Material Selection**")
        materials = get_all_materials()
        pinion_material = st.selectbox("Pinion Material", materials, key="pinion_material")
        gear_material = st.selectbox("Gear Material", materials, key="gear_material")
        
        pinion_props = get_material_properties(pinion_material)
        gear_props = get_material_properties(gear_material)
        
        st.markdown("**Design Requirements**")
        safety_factor_bending = st.number_input("Safety Factor (Bending)", min_value=1.0, value=2.0, step=0.1)
        safety_factor_contact = st.number_input("Safety Factor (Contact)", min_value=1.0, value=1.5, step=0.1)
        
        service_factor = st.number_input("Service Factor (Ks)", min_value=1.0, value=1.25, step=0.05)
        quality_factor = st.selectbox("Quality Grade", [6, 7, 8, 9, 10, 11, 12], index=3)
    
    # Basic calculations
    if st.button("Calculate Gear Parameters", type="primary"):
        try:
            # Calculate basic geometry
            gear_ratio = gear_teeth / pinion_teeth
            gear_rpm = pinion_rpm / gear_ratio
            
            # Pitch diameters
            pinion_pitch_diameter = module * pinion_teeth
            gear_pitch_diameter = module * gear_teeth
            center_distance = (pinion_pitch_diameter + gear_pitch_diameter) / 2
            
            # Torques
            pinion_torque = (power * 1000 * 60) / (2 * math.pi * pinion_rpm)  # N⋅m
            gear_torque = pinion_torque * gear_ratio
            
            # Pitch line velocity
            pitch_line_velocity = (math.pi * pinion_pitch_diameter * pinion_rpm) / (60 * 1000)  # m/s
            
            # Store results in session state
            st.session_state.gear_params = {
                'gear_type': gear_type,
                'pinion_teeth': pinion_teeth,
                'gear_teeth': gear_teeth,
                'module': module,
                'helix_angle': helix_angle,
                'face_width': face_width,
                'power': power,
                'pinion_rpm': pinion_rpm,
                'gear_ratio': gear_ratio,
                'gear_rpm': gear_rpm,
                'pinion_pitch_diameter': pinion_pitch_diameter,
                'gear_pitch_diameter': gear_pitch_diameter,
                'center_distance': center_distance,
                'pinion_torque': pinion_torque,
                'gear_torque': gear_torque,
                'pitch_line_velocity': pitch_line_velocity,
                'pinion_material': pinion_material,
                'gear_material': gear_material,
                'pinion_props': pinion_props,
                'gear_props': gear_props,
                'safety_factor_bending': safety_factor_bending,
                'safety_factor_contact': safety_factor_contact,
                'service_factor': service_factor,
                'quality_factor': quality_factor
            }
            
            # Display results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Gear Ratio", f"{gear_ratio:.2f}")
                st.metric("Center Distance", f"{center_distance:.1f} mm")
                st.metric("Pitch Line Velocity", f"{pitch_line_velocity:.2f} m/s")
            
            with col2:
                st.metric("Pinion Pitch Diameter", f"{pinion_pitch_diameter:.1f} mm")
                st.metric("Gear Pitch Diameter", f"{gear_pitch_diameter:.1f} mm")
                st.metric("Gear Speed", f"{gear_rpm:.0f} RPM")
            
            with col3:
                st.metric("Pinion Torque", f"{pinion_torque:.0f} N⋅m")
                st.metric("Gear Torque", f"{gear_torque:.0f} N⋅m")
                st.metric("Module", f"{module:.1f} mm")
            
            st.success("✅ Basic gear parameters calculated successfully!")
            
        except Exception as e:
            st.error(f"Calculation error: {str(e)}")

def show_tooth_strength_analysis():
    st.subheader("Tooth Bending Strength Analysis (Lewis Equation)")
    
    if 'gear_params' not in st.session_state:
        st.warning("Please complete the basic design calculation first.")
        return
    
    params = st.session_state.gear_params
    
    # Lewis form factors (approximate values for standard teeth)
    lewis_factors = {
        12: 0.245, 13: 0.261, 14: 0.277, 15: 0.290, 16: 0.296,
        17: 0.303, 18: 0.309, 19: 0.314, 20: 0.322, 22: 0.331,
        24: 0.337, 26: 0.346, 28: 0.353, 30: 0.359, 34: 0.371,
        38: 0.384, 43: 0.397, 50: 0.409, 60: 0.422, 75: 0.435,
        100: 0.447, 150: 0.460, 300: 0.472
    }
    
    def get_lewis_factor(teeth):
        if teeth in lewis_factors:
            return lewis_factors[teeth]
        else:
            # Interpolate for values not in table
            teeth_list = sorted(lewis_factors.keys())
            if teeth < min(teeth_list):
                return lewis_factors[min(teeth_list)]
            elif teeth > max(teeth_list):
                return lewis_factors[max(teeth_list)]
            else:
                # Linear interpolation
                for i in range(len(teeth_list) - 1):
                    if teeth_list[i] <= teeth <= teeth_list[i + 1]:
                        t1, t2 = teeth_list[i], teeth_list[i + 1]
                        y1, y2 = lewis_factors[t1], lewis_factors[t2]
                        return y1 + (y2 - y1) * (teeth - t1) / (t2 - t1)
    
    # Calculate Lewis form factors
    pinion_lewis_factor = get_lewis_factor(params['pinion_teeth'])
    gear_lewis_factor = get_lewis_factor(params['gear_teeth'])
    
    # Dynamic factor (velocity factor)
    v = params['pitch_line_velocity']
    if v <= 5:
        Kv = 1.0
    elif v <= 10:
        Kv = (5.56 + math.sqrt(v)) / (5.56)
    else:
        Kv = (5.56 + math.sqrt(v)) / (5.56)
    
    # Size factor (assumed)
    Ks = 1.0  # For standard gears
    
    # Calculate transmitted load
    Wt = params['pinion_torque'] * 2000 / params['pinion_pitch_diameter']  # N
    
    # Calculate bending stresses
    pinion_bending_stress = (Wt * params['service_factor'] * Kv * Ks) / (params['face_width'] * params['module'] * pinion_lewis_factor)
    gear_bending_stress = (Wt * params['service_factor'] * Kv * Ks) / (params['face_width'] * params['module'] * gear_lewis_factor)
    
    # Calculate safety factors
    pinion_safety_bending = (params['pinion_props']['yield_strength'] / 1e6) / (pinion_bending_stress / 1e6)
    gear_safety_bending = (params['gear_props']['yield_strength'] / 1e6) / (gear_bending_stress / 1e6)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Pinion Bending Analysis**")
        pinion_data = pd.DataFrame({
            'Parameter': ['Lewis Form Factor', 'Bending Stress (MPa)', 'Material Strength (MPa)', 'Safety Factor'],
            'Value': [f"{pinion_lewis_factor:.3f}", 
                     f"{pinion_bending_stress/1e6:.1f}",
                     f"{params['pinion_props']['yield_strength']/1e6:.0f}",
                     f"{pinion_safety_bending:.2f}"]
        })
        st.dataframe(pinion_data, use_container_width=True)
        
        if pinion_safety_bending >= params['safety_factor_bending']:
            st.success(f"✅ Pinion bending strength adequate (SF = {pinion_safety_bending:.2f})")
        else:
            st.error(f"❌ Pinion bending strength insufficient (SF = {pinion_safety_bending:.2f})")
    
    with col2:
        st.markdown("**Gear Bending Analysis**")
        gear_data = pd.DataFrame({
            'Parameter': ['Lewis Form Factor', 'Bending Stress (MPa)', 'Material Strength (MPa)', 'Safety Factor'],
            'Value': [f"{gear_lewis_factor:.3f}", 
                     f"{gear_bending_stress/1e6:.1f}",
                     f"{params['gear_props']['yield_strength']/1e6:.0f}",
                     f"{gear_safety_bending:.2f}"]
        })
        st.dataframe(gear_data, use_container_width=True)
        
        if gear_safety_bending >= params['safety_factor_bending']:
            st.success(f"✅ Gear bending strength adequate (SF = {gear_safety_bending:.2f})")
        else:
            st.error(f"❌ Gear bending strength insufficient (SF = {gear_safety_bending:.2f})")
    
    # Visualization
    st.markdown("**Bending Stress Comparison**")
    
    fig = go.Figure()
    
    components = ['Pinion', 'Gear']
    stresses = [pinion_bending_stress/1e6, gear_bending_stress/1e6]
    limits = [params['pinion_props']['yield_strength']/1e6, params['gear_props']['yield_strength']/1e6]
    
    fig.add_trace(go.Bar(
        x=components,
        y=stresses,
        name='Bending Stress',
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        x=components,
        y=limits,
        name='Yield Strength',
        marker_color='lightcoral',
        opacity=0.7
    ))
    
    fig.update_layout(
        title="Bending Stress Analysis",
        xaxis_title="Component",
        yaxis_title="Stress (MPa)",
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Store results
    st.session_state.bending_results = {
        'pinion_bending_stress': pinion_bending_stress,
        'gear_bending_stress': gear_bending_stress,
        'pinion_safety_bending': pinion_safety_bending,
        'gear_safety_bending': gear_safety_bending,
        'dynamic_factor': Kv
    }

def show_contact_stress_analysis():
    st.subheader("Contact Stress Analysis (Hertzian Stress)")
    
    if 'gear_params' not in st.session_state:
        st.warning("Please complete the basic design calculation first.")
        return
    
    params = st.session_state.gear_params
    
    # Calculate contact stress using Hertzian formula for gears
    # Simplified approach for spur gears
    
    # Transmitted load
    Wt = params['pinion_torque'] * 2000 / params['pinion_pitch_diameter']  # N
    
    # Dynamic factor (same as bending analysis)
    v = params['pitch_line_velocity']
    if v <= 5:
        Kv = 1.0
    elif v <= 10:
        Kv = (5.56 + math.sqrt(v)) / (5.56)
    else:
        Kv = (5.56 + math.sqrt(v)) / (5.56)
    
    # Geometry factor for contact stress
    gear_ratio = params['gear_ratio']
    I = (math.cos(math.radians(params['helix_angle'])) * math.sin(math.radians(20))) / 2 * (gear_ratio / (gear_ratio + 1))  # Simplified
    if I <= 0:
        I = 0.1  # Minimum value to avoid division by zero
    
    # Elastic coefficient
    E1 = params['pinion_props']['elastic_modulus']
    E2 = params['gear_props']['elastic_modulus']
    nu1 = params['pinion_props']['poisson_ratio']
    nu2 = params['gear_props']['poisson_ratio']
    
    Cp = math.sqrt(1 / (math.pi * ((1 - nu1**2) / E1 + (1 - nu2**2) / E2)))
    
    # Contact stress calculation
    contact_stress = Cp * math.sqrt((Wt * params['service_factor'] * Kv) / (params['face_width'] * params['pinion_pitch_diameter'] * I))
    
    # Contact fatigue strength (approximate)
    # Using surface hardness correlation for contact strength
    pinion_contact_strength = 2.8 * params['pinion_props']['yield_strength'] / 1e6  # MPa (approximate)
    gear_contact_strength = 2.8 * params['gear_props']['yield_strength'] / 1e6  # MPa (approximate)
    
    # Safety factors
    pinion_safety_contact = pinion_contact_strength / (contact_stress / 1e6)
    gear_safety_contact = gear_contact_strength / (contact_stress / 1e6)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Contact Stress Parameters**")
        contact_data = pd.DataFrame({
            'Parameter': [
                'Transmitted Load (N)',
                'Dynamic Factor (Kv)',
                'Elastic Coefficient (Cp)',
                'Geometry Factor (I)',
                'Contact Stress (MPa)'
            ],
            'Value': [
                f"{Wt:.0f}",
                f"{Kv:.2f}",
                f"{Cp:.0f}",
                f"{I:.4f}",
                f"{contact_stress/1e6:.0f}"
            ]
        })
        st.dataframe(contact_data, use_container_width=True)
    
    with col2:
        st.markdown("**Safety Factor Analysis**")
        safety_data = pd.DataFrame({
            'Component': ['Pinion', 'Gear'],
            'Contact Stress (MPa)': [contact_stress/1e6, contact_stress/1e6],
            'Contact Strength (MPa)': [pinion_contact_strength, gear_contact_strength],
            'Safety Factor': [pinion_safety_contact, gear_safety_contact]
        })
        st.dataframe(safety_data, use_container_width=True)
        
        min_safety = min(pinion_safety_contact, gear_safety_contact)
        if min_safety >= params['safety_factor_contact']:
            st.success(f"✅ Contact strength adequate (Min SF = {min_safety:.2f})")
        else:
            st.error(f"❌ Contact strength insufficient (Min SF = {min_safety:.2f})")
    
    # Visualization
    st.markdown("**Contact Stress Visualization**")
    
    fig = go.Figure()
    
    components = ['Pinion', 'Gear']
    stresses = [contact_stress/1e6, contact_stress/1e6]
    limits = [pinion_contact_strength, gear_contact_strength]
    
    fig.add_trace(go.Bar(
        x=components,
        y=stresses,
        name='Contact Stress',
        marker_color='lightgreen'
    ))
    
    fig.add_trace(go.Bar(
        x=components,
        y=limits,
        name='Contact Strength',
        marker_color='lightcoral',
        opacity=0.7
    ))
    
    fig.update_layout(
        title="Contact Stress Analysis",
        xaxis_title="Component",
        yaxis_title="Stress (MPa)",
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Store results
    st.session_state.contact_results = {
        'contact_stress': contact_stress,
        'pinion_safety_contact': pinion_safety_contact,
        'gear_safety_contact': gear_safety_contact,
        'elastic_coefficient': Cp
    }

def show_gear_results_summary():
    st.subheader("Gear Design Results Summary")
    
    if 'gear_params' not in st.session_state:
        st.warning("Please complete the basic design calculation first.")
        return
    
    params = st.session_state.gear_params
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Gear Ratio", f"{params['gear_ratio']:.2f}")
        st.metric("Module", f"{params['module']:.1f} mm")
        st.metric("Center Distance", f"{params['center_distance']:.1f} mm")
    
    with col2:
        st.metric("Pinion Teeth", f"{params['pinion_teeth']}")
        st.metric("Gear Teeth", f"{params['gear_teeth']}")
        st.metric("Face Width", f"{params['face_width']:.0f} mm")
    
    with col3:
        st.metric("Power", f"{params['power']:.1f} kW")
        st.metric("Pinion Speed", f"{params['pinion_rpm']:.0f} RPM")
        st.metric("Gear Speed", f"{params['gear_rpm']:.0f} RPM")
    
    with col4:
        st.metric("Pitch Line Velocity", f"{params['pitch_line_velocity']:.2f} m/s")
        st.metric("Pinion Torque", f"{params['pinion_torque']:.0f} N⋅m")
        st.metric("Gear Torque", f"{params['gear_torque']:.0f} N⋅m")
    
    # Safety factor summary
    if 'bending_results' in st.session_state and 'contact_results' in st.session_state:
        st.markdown("**Safety Factor Summary**")
        
        bending = st.session_state.bending_results
        contact = st.session_state.contact_results
        
        safety_summary = pd.DataFrame({
            'Analysis Type': ['Bending (Pinion)', 'Bending (Gear)', 'Contact (Pinion)', 'Contact (Gear)'],
            'Safety Factor': [
                f"{bending['pinion_safety_bending']:.2f}",
                f"{bending['gear_safety_bending']:.2f}",
                f"{contact['pinion_safety_contact']:.2f}",
                f"{contact['gear_safety_contact']:.2f}"
            ],
            'Required': [
                f"{params['safety_factor_bending']:.1f}",
                f"{params['safety_factor_bending']:.1f}",
                f"{params['safety_factor_contact']:.1f}",
                f"{params['safety_factor_contact']:.1f}"
            ],
            'Status': [
                "✅ OK" if bending['pinion_safety_bending'] >= params['safety_factor_bending'] else "❌ Low",
                "✅ OK" if bending['gear_safety_bending'] >= params['safety_factor_bending'] else "❌ Low",
                "✅ OK" if contact['pinion_safety_contact'] >= params['safety_factor_contact'] else "❌ Low",
                "✅ OK" if contact['gear_safety_contact'] >= params['safety_factor_contact'] else "❌ Low"
            ]
        })
        
        st.dataframe(safety_summary, use_container_width=True)
    
    # Complete design summary
    st.markdown("**Complete Design Summary**")
    summary_data = {
        'Parameter': [
            'Gear Type',
            'Pinion Teeth',
            'Gear Teeth',
            'Module (mm)',
            'Helix Angle (°)',
            'Face Width (mm)',
            'Pinion Pitch Diameter (mm)',
            'Gear Pitch Diameter (mm)',
            'Center Distance (mm)',
            'Gear Ratio',
            'Power (kW)',
            'Pinion Speed (RPM)',
            'Gear Speed (RPM)',
            'Pinion Torque (N⋅m)',
            'Gear Torque (N⋅m)',
            'Pitch Line Velocity (m/s)',
            'Pinion Material',
            'Gear Material'
        ],
        'Value': [
            params['gear_type'],
            f"{params['pinion_teeth']}",
            f"{params['gear_teeth']}",
            f"{params['module']:.1f}",
            f"{params['helix_angle']:.1f}",
            f"{params['face_width']:.0f}",
            f"{params['pinion_pitch_diameter']:.1f}",
            f"{params['gear_pitch_diameter']:.1f}",
            f"{params['center_distance']:.1f}",
            f"{params['gear_ratio']:.2f}",
            f"{params['power']:.1f}",
            f"{params['pinion_rpm']:.0f}",
            f"{params['gear_rpm']:.0f}",
            f"{params['pinion_torque']:.0f}",
            f"{params['gear_torque']:.0f}",
            f"{params['pitch_line_velocity']:.2f}",
            params['pinion_material'],
            params['gear_material']
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
                export_gear_results(params, summary_df, 'pdf')
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
                    file_name="gear_design_results.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
