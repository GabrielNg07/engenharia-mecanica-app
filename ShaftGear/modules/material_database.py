import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Engineering materials database
MATERIALS_DATABASE = {
    'AISI 1020 Steel': {
        'yield_strength': 250e6,  # Pa
        'ultimate_strength': 380e6,  # Pa
        'elastic_modulus': 200e9,  # Pa
        'poisson_ratio': 0.29,
        'density': 7850,  # kg/m³
        'fatigue_strength': 190e6,  # Pa (at 10^6 cycles)
        'hardness_hb': 111,
        'category': 'Carbon Steel'
    },
    'AISI 1045 Steel': {
        'yield_strength': 310e6,
        'ultimate_strength': 565e6,
        'elastic_modulus': 200e9,
        'poisson_ratio': 0.29,
        'density': 7850,
        'fatigue_strength': 282e6,
        'hardness_hb': 163,
        'category': 'Carbon Steel'
    },
    'AISI 4140 Steel': {
        'yield_strength': 415e6,
        'ultimate_strength': 655e6,
        'elastic_modulus': 200e9,
        'poisson_ratio': 0.29,
        'density': 7850,
        'fatigue_strength': 380e6,
        'hardness_hb': 197,
        'category': 'Alloy Steel'
    },
    'AISI 4340 Steel': {
        'yield_strength': 470e6,
        'ultimate_strength': 745e6,
        'elastic_modulus': 200e9,
        'poisson_ratio': 0.29,
        'density': 7850,
        'fatigue_strength': 425e6,
        'hardness_hb': 217,
        'category': 'Alloy Steel'
    },
    'AISI 316 Stainless Steel': {
        'yield_strength': 205e6,
        'ultimate_strength': 515e6,
        'elastic_modulus': 200e9,
        'poisson_ratio': 0.30,
        'density': 8000,
        'fatigue_strength': 240e6,
        'hardness_hb': 149,
        'category': 'Stainless Steel'
    },
    'AISI 17-4 PH Stainless Steel': {
        'yield_strength': 1170e6,
        'ultimate_strength': 1310e6,
        'elastic_modulus': 196e9,
        'poisson_ratio': 0.27,
        'density': 7750,
        'fatigue_strength': 550e6,
        'hardness_hb': 388,
        'category': 'Precipitation Hardening Steel'
    },
    'Aluminum 6061-T6': {
        'yield_strength': 276e6,
        'ultimate_strength': 310e6,
        'elastic_modulus': 69e9,
        'poisson_ratio': 0.33,
        'density': 2700,
        'fatigue_strength': 96e6,
        'hardness_hb': 95,
        'category': 'Aluminum Alloy'
    },
    'Aluminum 7075-T6': {
        'yield_strength': 503e6,
        'ultimate_strength': 572e6,
        'elastic_modulus': 71.7e9,
        'poisson_ratio': 0.33,
        'density': 2810,
        'fatigue_strength': 159e6,
        'hardness_hb': 150,
        'category': 'Aluminum Alloy'
    },
    'Titanium Ti-6Al-4V': {
        'yield_strength': 880e6,
        'ultimate_strength': 950e6,
        'elastic_modulus': 114e9,
        'poisson_ratio': 0.32,
        'density': 4430,
        'fatigue_strength': 510e6,
        'hardness_hb': 334,
        'category': 'Titanium Alloy'
    },
    'Brass C36000': {
        'yield_strength': 124e6,
        'ultimate_strength': 310e6,
        'elastic_modulus': 100e9,
        'poisson_ratio': 0.33,
        'density': 8500,
        'fatigue_strength': 110e6,
        'hardness_hb': 85,
        'category': 'Copper Alloy'
    },
    'Bronze C93200': {
        'yield_strength': 172e6,
        'ultimate_strength': 310e6,
        'elastic_modulus': 103e9,
        'poisson_ratio': 0.34,
        'density': 8800,
        'fatigue_strength': 124e6,
        'hardness_hb': 75,
        'category': 'Copper Alloy'
    },
    'Cast Iron ASTM A48 Class 30': {
        'yield_strength': 200e6,
        'ultimate_strength': 207e6,
        'elastic_modulus': 100e9,
        'poisson_ratio': 0.26,
        'density': 7200,
        'fatigue_strength': 68e6,
        'hardness_hb': 187,
        'category': 'Cast Iron'
    },
    'Ductile Iron ASTM A536 65-45-12': {
        'yield_strength': 310e6,
        'ultimate_strength': 448e6,
        'elastic_modulus': 169e9,
        'poisson_ratio': 0.29,
        'density': 7100,
        'fatigue_strength': 220e6,
        'hardness_hb': 149,
        'category': 'Cast Iron'
    },
    'Inconel 718': {
        'yield_strength': 1240e6,
        'ultimate_strength': 1380e6,
        'elastic_modulus': 200e9,
        'poisson_ratio': 0.29,
        'density': 8190,
        'fatigue_strength': 620e6,
        'hardness_hb': 388,
        'category': 'Superalloy'
    },
    'Tool Steel D2': {
        'yield_strength': 520e6,
        'ultimate_strength': 690e6,
        'elastic_modulus': 210e9,
        'poisson_ratio': 0.27,
        'density': 7700,
        'fatigue_strength': 345e6,
        'hardness_hb': 217,
        'category': 'Tool Steel'
    }
}

def get_material_properties(material_name):
    """Get material properties for a given material"""
    return MATERIALS_DATABASE.get(material_name, MATERIALS_DATABASE['AISI 1045 Steel'])

def get_all_materials():
    """Get list of all available materials"""
    return list(MATERIALS_DATABASE.keys())

def get_materials_by_category(category):
    """Get materials filtered by category"""
    return [name for name, props in MATERIALS_DATABASE.items() if props['category'] == category]

def show_material_database_page():
    st.header("📋 Material Properties Database")
    st.markdown("Comprehensive database of engineering materials for mechanical design")
    
    # Material selection and filtering
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Filters")
        categories = list(set(props['category'] for props in MATERIALS_DATABASE.values()))
        selected_category = st.selectbox("Filter by Category", ["All"] + sorted(categories))
        
        if selected_category == "All":
            filtered_materials = MATERIALS_DATABASE
        else:
            filtered_materials = {name: props for name, props in MATERIALS_DATABASE.items() 
                                if props['category'] == selected_category}
        
        st.metric("Materials Available", len(filtered_materials))
        
        # Material comparison selection
        st.subheader("Compare Materials")
        comparison_materials = st.multiselect(
            "Select materials to compare",
            list(filtered_materials.keys()),
            default=list(filtered_materials.keys())[:3] if len(filtered_materials) >= 3 else list(filtered_materials.keys())
        )
    
    with col2:
        # Display material properties table
        st.subheader("Material Properties")
        
        # Create DataFrame for display
        display_data = []
        for name, props in filtered_materials.items():
            display_data.append({
                'Material': name,
                'Category': props['category'],
                'Yield Strength (MPa)': props['yield_strength'] / 1e6,
                'Ultimate Strength (MPa)': props['ultimate_strength'] / 1e6,
                'Elastic Modulus (GPa)': props['elastic_modulus'] / 1e9,
                'Density (kg/m³)': props['density'],
                'Fatigue Strength (MPa)': props['fatigue_strength'] / 1e6,
                'Hardness (HB)': props['hardness_hb']
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export material data
        if st.button("Export Material Data"):
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="material_properties.csv",
                mime="text/csv"
            )
    
    # Material comparison charts
    if comparison_materials:
        st.subheader("Material Comparison Charts")
        
        # Prepare data for comparison
        comparison_data = []
        for material in comparison_materials:
            props = MATERIALS_DATABASE[material]
            comparison_data.append({
                'Material': material,
                'Yield Strength': props['yield_strength'] / 1e6,
                'Ultimate Strength': props['ultimate_strength'] / 1e6,
                'Elastic Modulus': props['elastic_modulus'] / 1e9,
                'Density': props['density'],
                'Fatigue Strength': props['fatigue_strength'] / 1e6,
                'Specific Strength': (props['yield_strength'] / 1e6) / (props['density'] / 1000)  # MPa/(g/cm³)
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Create comparison charts
        tab1, tab2, tab3, tab4 = st.tabs(["Strength Comparison", "Stiffness vs Density", "Fatigue Properties", "Material Radar"])
        
        with tab1:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=comparison_df['Material'],
                y=comparison_df['Yield Strength'],
                name='Yield Strength',
                marker_color='lightblue'
            ))
            
            fig.add_trace(go.Bar(
                x=comparison_df['Material'],
                y=comparison_df['Ultimate Strength'],
                name='Ultimate Strength',
                marker_color='lightcoral'
            ))
            
            fig.update_layout(
                title="Strength Comparison",
                xaxis_title="Material",
                yaxis_title="Strength (MPa)",
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            fig = px.scatter(
                comparison_df,
                x='Density',
                y='Elastic Modulus',
                text='Material',
                title="Elastic Modulus vs Density",
                labels={'Density': 'Density (kg/m³)', 'Elastic Modulus': 'Elastic Modulus (GPa)'}
            )
            
            fig.update_traces(textposition="top center", marker_size=12)
            fig.update_layout(showlegend=False)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=comparison_df['Material'],
                y=comparison_df['Fatigue Strength'],
                mode='markers+lines',
                name='Fatigue Strength',
                marker=dict(size=10, color='green')
            ))
            
            fig.update_layout(
                title="Fatigue Strength Comparison",
                xaxis_title="Material",
                yaxis_title="Fatigue Strength (MPa)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            # Radar chart for material properties
            if len(comparison_materials) <= 5:  # Limit for readability
                fig = go.Figure()
                
                # Normalize properties for radar chart (0-100 scale)
                max_yield = comparison_df['Yield Strength'].max()
                max_modulus = comparison_df['Elastic Modulus'].max()
                max_fatigue = comparison_df['Fatigue Strength'].max()
                max_specific = comparison_df['Specific Strength'].max()
                
                properties = ['Yield Strength', 'Elastic Modulus', 'Fatigue Strength', 'Specific Strength']
                
                for _, material_data in comparison_df.iterrows():
                    values = [
                        100 * material_data['Yield Strength'] / max_yield,
                        100 * material_data['Elastic Modulus'] / max_modulus,
                        100 * material_data['Fatigue Strength'] / max_fatigue,
                        100 * material_data['Specific Strength'] / max_specific
                    ]
                    
                    fig.add_trace(go.Scatterpolar(
                        r=values + [values[0]],  # Close the polygon
                        theta=properties + [properties[0]],
                        fill='toself',
                        name=material_data['Material']
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    title="Material Properties Radar Chart (Normalized)",
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Select 5 or fewer materials for radar chart visualization")
    
    # Material selection guide
    st.subheader("Material Selection Guide")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**High Strength Applications:**")
        high_strength = sorted(
            [(name, props['yield_strength']/1e6) for name, props in MATERIALS_DATABASE.items()],
            key=lambda x: x[1], reverse=True
        )[:5]
        
        for material, strength in high_strength:
            st.write(f"• {material}: {strength:.0f} MPa")
    
    with col2:
        st.markdown("**Lightweight Applications:**")
        specific_strength = sorted(
            [(name, (props['yield_strength']/1e6)/(props['density']/1000)) for name, props in MATERIALS_DATABASE.items()],
            key=lambda x: x[1], reverse=True
        )[:5]
        
        for material, spec_strength in specific_strength:
            st.write(f"• {material}: {spec_strength:.1f} MPa/(g/cm³)")
    
    # Application recommendations
    st.subheader("Application Recommendations")
    
    applications = {
        "General Purpose Shafts": ["AISI 1045 Steel", "AISI 4140 Steel"],
        "High-Speed Applications": ["AISI 4340 Steel", "Tool Steel D2"],
        "Corrosion Resistance": ["AISI 316 Stainless Steel", "AISI 17-4 PH Stainless Steel"],
        "Lightweight Design": ["Aluminum 7075-T6", "Titanium Ti-6Al-4V"],
        "High Temperature": ["Inconel 718", "AISI 17-4 PH Stainless Steel"],
        "Cost-Effective": ["AISI 1020 Steel", "Cast Iron ASTM A48 Class 30"]
    }
    
    for application, materials in applications.items():
        with st.expander(f"{application}"):
            for material in materials:
                props = MATERIALS_DATABASE[material]
                st.write(f"**{material}**")
                st.write(f"- Yield Strength: {props['yield_strength']/1e6:.0f} MPa")
                st.write(f"- Density: {props['density']} kg/m³")
                st.write(f"- Category: {props['category']}")
                st.write("")
