import streamlit as st
import pandas as pd
import io
from datetime import datetime
import json

def export_shaft_results(parameters, summary_df, format_type='csv'):
    """Export shaft calculation results"""
    try:
        if format_type.lower() == 'csv':
            return export_to_csv(summary_df, 'shaft_design_results')
        elif format_type.lower() == 'json':
            return export_to_json(parameters, 'shaft_design_results')
        elif format_type.lower() == 'pdf':
            return export_to_text_report(parameters, summary_df, 'Shaft Design Report')
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    except Exception as e:
        st.error(f"Export error: {str(e)}")
        return None

def export_gear_results(parameters, summary_df, format_type='csv'):
    """Export gear calculation results"""
    try:
        if format_type.lower() == 'csv':
            return export_to_csv(summary_df, 'gear_design_results')
        elif format_type.lower() == 'json':
            return export_to_json(parameters, 'gear_design_results')
        elif format_type.lower() == 'pdf':
            return export_to_text_report(parameters, summary_df, 'Gear Design Report')
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    except Exception as e:
        st.error(f"Export error: {str(e)}")
        return None

def export_to_csv(dataframe, filename_base):
    """Export DataFrame to CSV format"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_base}_{timestamp}.csv"
    
    csv_buffer = io.StringIO()
    dataframe.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    st.download_button(
        label="Download CSV Report",
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        key=f"csv_download_{timestamp}"
    )
    
    return csv_data

def export_to_json(parameters, filename_base):
    """Export parameters to JSON format"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_base}_{timestamp}.json"
    
    # Convert numpy types and other non-serializable types
    def convert_types(obj):
        if hasattr(obj, 'item'):  # numpy types
            return obj.item()
        elif hasattr(obj, 'tolist'):  # numpy arrays
            return obj.tolist()
        elif isinstance(obj, (int, float, str, bool, list, dict, type(None))):
            return obj
        else:
            return str(obj)
    
    # Create export data structure
    export_data = {
        'export_info': {
            'timestamp': timestamp,
            'export_type': 'mechanical_engineering_calculation',
            'version': '1.0'
        },
        'parameters': {k: convert_types(v) for k, v in parameters.items()},
        'calculation_metadata': {
            'units': 'SI (metric)',
            'calculation_date': datetime.now().isoformat(),
            'software': 'Mechanical Engineering Design Tool'
        }
    }
    
    json_data = json.dumps(export_data, indent=2)
    
    st.download_button(
        label="Download JSON Report",
        data=json_data,
        file_name=filename,
        mime="application/json",
        key=f"json_download_{timestamp}"
    )
    
    return json_data

def export_to_text_report(parameters, summary_df, report_title):
    """Export comprehensive text report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"{report_title.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append(f"{report_title.upper()}")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {timestamp}")
    report_lines.append(f"Software: Mechanical Engineering Design Tool")
    report_lines.append("")
    
    # Executive Summary
    report_lines.append("EXECUTIVE SUMMARY")
    report_lines.append("-" * 40)
    if 'gear_ratio' in parameters:
        report_lines.append(f"Gear Design Analysis")
        report_lines.append(f"Gear Ratio: {parameters.get('gear_ratio', 'N/A'):.2f}")
        report_lines.append(f"Power Rating: {parameters.get('power', 'N/A'):.1f} kW")
        report_lines.append(f"Center Distance: {parameters.get('center_distance', 'N/A'):.1f} mm")
    elif 'outer_diameter' in parameters:
        report_lines.append(f"Shaft Design Analysis")
        report_lines.append(f"Required Diameter: {parameters.get('outer_diameter', 'N/A'):.1f} mm")
        report_lines.append(f"Applied Torque: {parameters.get('torque', 'N/A'):.0f} N⋅m")
        report_lines.append(f"Material: {parameters.get('material', 'N/A')}")
    
    report_lines.append("")
    
    # Design Parameters
    report_lines.append("DESIGN PARAMETERS")
    report_lines.append("-" * 40)
    for key, value in parameters.items():
        if isinstance(value, dict):
            continue  # Skip nested dictionaries
        if isinstance(value, (int, float)):
            if abs(value) > 1000:
                report_lines.append(f"{key.replace('_', ' ').title()}: {value:.0f}")
            else:
                report_lines.append(f"{key.replace('_', ' ').title()}: {value:.3f}")
        else:
            report_lines.append(f"{key.replace('_', ' ').title()}: {value}")
    
    report_lines.append("")
    
    # Results Summary
    report_lines.append("CALCULATION RESULTS")
    report_lines.append("-" * 40)
    for _, row in summary_df.iterrows():
        parameter = str(row['Parameter'])
        value = str(row['Value'])
        report_lines.append(f"{parameter}: {value}")
    
    report_lines.append("")
    
    # Material Properties (if available)
    if 'material_props' in parameters:
        report_lines.append("MATERIAL PROPERTIES")
        report_lines.append("-" * 40)
        props = parameters['material_props']
        report_lines.append(f"Yield Strength: {props.get('yield_strength', 0)/1e6:.0f} MPa")
        report_lines.append(f"Ultimate Strength: {props.get('ultimate_strength', 0)/1e6:.0f} MPa")
        report_lines.append(f"Elastic Modulus: {props.get('elastic_modulus', 0)/1e9:.0f} GPa")
        report_lines.append(f"Density: {props.get('density', 0):.0f} kg/m³")
        report_lines.append("")
    
    # Safety Assessment
    report_lines.append("SAFETY ASSESSMENT")
    report_lines.append("-" * 40)
    
    # Check for safety factors in session state
    safety_factors = []
    if 'bending_results' in st.session_state:
        bending = st.session_state.bending_results
        safety_factors.append(f"Pinion Bending Safety Factor: {bending.get('pinion_safety_bending', 'N/A'):.2f}")
        safety_factors.append(f"Gear Bending Safety Factor: {bending.get('gear_safety_bending', 'N/A'):.2f}")
    
    if 'contact_results' in st.session_state:
        contact = st.session_state.contact_results
        safety_factors.append(f"Contact Safety Factor: {contact.get('pinion_safety_contact', 'N/A'):.2f}")
    
    # Generic safety factor check
    target_sf = parameters.get('target_safety_factor', parameters.get('safety_factor_bending', 'N/A'))
    if target_sf != 'N/A':
        report_lines.append(f"Target Safety Factor: {target_sf:.1f}")
    
    for sf in safety_factors:
        report_lines.append(sf)
    
    if not safety_factors:
        report_lines.append("Safety factor analysis not available")
    
    report_lines.append("")
    
    # Design Recommendations
    report_lines.append("DESIGN RECOMMENDATIONS")
    report_lines.append("-" * 40)
    report_lines.append("• Verify all safety factors meet or exceed minimum requirements")
    report_lines.append("• Consider manufacturing tolerances in final design")
    report_lines.append("• Review material selection for operating environment")
    report_lines.append("• Validate assumptions with detailed FEA if critical application")
    report_lines.append("• Consider fatigue analysis for cyclic loading conditions")
    report_lines.append("")
    
    # Disclaimer
    report_lines.append("DISCLAIMER")
    report_lines.append("-" * 40)
    report_lines.append("This analysis is based on simplified engineering calculations.")
    report_lines.append("For critical applications, detailed finite element analysis")
    report_lines.append("and professional engineering review are recommended.")
    report_lines.append("Verify all results against applicable design codes and standards.")
    report_lines.append("")
    report_lines.append("=" * 80)
    
    report_text = "\n".join(report_lines)
    
    st.download_button(
        label="Download Text Report",
        data=report_text,
        file_name=filename,
        mime="text/plain",
        key=f"txt_download_{timestamp}"
    )
    
    return report_text

def create_calculation_backup():
    """Create a backup of all calculation data in session state"""
    backup_data = {}
    
    # Collect all calculation-related session state data
    calculation_keys = [
        'shaft_params', 'gear_params', 'bending_results', 
        'contact_results', 'material_selection'
    ]
    
    for key in calculation_keys:
        if key in st.session_state:
            backup_data[key] = st.session_state[key]
    
    backup_data['backup_timestamp'] = datetime.now().isoformat()
    backup_data['session_info'] = {
        'user_agent': 'Streamlit App',
        'calculation_count': len([k for k in backup_data.keys() if k.endswith('_params')])
    }
    
    return backup_data

def restore_calculation_backup(backup_data):
    """Restore calculation data from backup"""
    try:
        for key, value in backup_data.items():
            if key not in ['backup_timestamp', 'session_info']:
                st.session_state[key] = value
        
        st.success("Calculation backup restored successfully!")
        return True
    except Exception as e:
        st.error(f"Failed to restore backup: {str(e)}")
        return False

def export_all_calculations():
    """Export all calculations from current session"""
    all_data = create_calculation_backup()
    
    if not all_data or len(all_data) <= 2:  # Only timestamp and session_info
        st.warning("No calculations available to export")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"all_calculations_{timestamp}.json"
    
    json_data = json.dumps(all_data, indent=2, default=str)
    
    st.download_button(
        label="Export All Calculations",
        data=json_data,
        file_name=filename,
        mime="application/json",
        key=f"export_all_{timestamp}"
    )
    
    return json_data

def generate_calculation_summary_table(calculation_type):
    """Generate summary table for specific calculation type"""
    if calculation_type == 'shaft' and 'shaft_params' in st.session_state:
        params = st.session_state.shaft_params
        data = []
        
        # Basic parameters
        basic_params = ['torque', 'bending_moment', 'axial_force', 'outer_diameter', 'material']
        for param in basic_params:
            if param in params:
                value = params[param]
                if isinstance(value, (int, float)):
                    if param in ['torque', 'bending_moment']:
                        data.append({'Parameter': param.replace('_', ' ').title(), 'Value': f"{value:.0f} N⋅m"})
                    elif param == 'outer_diameter':
                        data.append({'Parameter': param.replace('_', ' ').title(), 'Value': f"{value:.1f} mm"})
                    elif param == 'axial_force':
                        data.append({'Parameter': param.replace('_', ' ').title(), 'Value': f"{value:.0f} N"})
                    else:
                        data.append({'Parameter': param.replace('_', ' ').title(), 'Value': f"{value}"})
                else:
                    data.append({'Parameter': param.replace('_', ' ').title(), 'Value': str(value)})
        
        return pd.DataFrame(data)
    
    elif calculation_type == 'gear' and 'gear_params' in st.session_state:
        params = st.session_state.gear_params
        data = []
        
        # Basic parameters
        basic_params = ['pinion_teeth', 'gear_teeth', 'module', 'power', 'gear_ratio', 'center_distance']
        for param in basic_params:
            if param in params:
                value = params[param]
                if isinstance(value, (int, float)):
                    if param == 'power':
                        data.append({'Parameter': param.replace('_', ' ').title(), 'Value': f"{value:.1f} kW"})
                    elif param == 'center_distance':
                        data.append({'Parameter': param.replace('_', ' ').title(), 'Value': f"{value:.1f} mm"})
                    elif param in ['pinion_teeth', 'gear_teeth']:
                        data.append({'Parameter': param.replace('_', ' ').title(), 'Value': f"{int(value)}"})
                    else:
                        data.append({'Parameter': param.replace('_', ' ').title(), 'Value': f"{value:.2f}"})
                else:
                    data.append({'Parameter': param.replace('_', ' ').title(), 'Value': str(value)})
        
        return pd.DataFrame(data)
    
    return pd.DataFrame({'Parameter': ['No data'], 'Value': ['N/A']})
