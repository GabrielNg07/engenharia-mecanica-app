import streamlit as st
import numpy as np
import math

def validate_positive_input(value, parameter_name):
    """Validate that input is positive"""
    if value <= 0:
        st.error(f"{parameter_name} must be greater than zero")
        return False
    return True

def validate_range_input(value, parameter_name, min_val, max_val):
    """Validate that input is within specified range"""
    if value < min_val or value > max_val:
        st.error(f"{parameter_name} must be between {min_val} and {max_val}")
        return False
    return True

def calculate_safety_factor(applied_stress, material_strength):
    """Calculate safety factor"""
    if applied_stress <= 0:
        return float('inf')
    return material_strength / applied_stress

def convert_units(value, from_unit, to_unit):
    """Convert between different units"""
    conversion_factors = {
        # Length conversions (to meters)
        'mm': 0.001,
        'cm': 0.01,
        'm': 1.0,
        'in': 0.0254,
        'ft': 0.3048,
        
        # Force conversions (to Newtons)
        'N': 1.0,
        'kN': 1000.0,
        'lbf': 4.448,
        'kgf': 9.807,
        
        # Pressure/Stress conversions (to Pascals)
        'Pa': 1.0,
        'MPa': 1e6,
        'GPa': 1e9,
        'psi': 6895,
        'ksi': 6.895e6,
        
        # Power conversions (to Watts)
        'W': 1.0,
        'kW': 1000.0,
        'hp': 745.7,
        
        # Torque conversions (to N⋅m)
        'Nm': 1.0,
        'kNm': 1000.0,
        'lbft': 1.356,
        'lbin': 0.113
    }
    
    if from_unit not in conversion_factors or to_unit not in conversion_factors:
        raise ValueError(f"Unknown unit conversion: {from_unit} to {to_unit}")
    
    # Convert to base unit, then to target unit
    base_value = value * conversion_factors[from_unit]
    return base_value / conversion_factors[to_unit]

def format_engineering_number(value, precision=2):
    """Format number in engineering notation"""
    if value == 0:
        return "0"
    
    exponent = math.floor(math.log10(abs(value)) / 3) * 3
    mantissa = value / (10 ** exponent)
    
    if exponent == 0:
        return f"{mantissa:.{precision}f}"
    else:
        return f"{mantissa:.{precision}f}e{exponent:+d}"

def calculate_von_mises_stress(sigma_x, sigma_y, sigma_z, tau_xy, tau_xz, tau_yz):
    """Calculate von Mises equivalent stress"""
    return math.sqrt(0.5 * ((sigma_x - sigma_y)**2 + (sigma_y - sigma_z)**2 + 
                           (sigma_z - sigma_x)**2) + 3 * (tau_xy**2 + tau_xz**2 + tau_yz**2))

def calculate_principal_stresses(sigma_x, sigma_y, tau_xy):
    """Calculate principal stresses for 2D stress state"""
    avg_stress = (sigma_x + sigma_y) / 2
    radius = math.sqrt(((sigma_x - sigma_y) / 2)**2 + tau_xy**2)
    
    sigma_1 = avg_stress + radius  # Maximum principal stress
    sigma_2 = avg_stress - radius  # Minimum principal stress
    
    # Principal angle
    if (sigma_x - sigma_y) != 0:
        theta_p = 0.5 * math.atan(2 * tau_xy / (sigma_x - sigma_y))
    else:
        theta_p = math.pi / 4 if tau_xy > 0 else -math.pi / 4
    
    return sigma_1, sigma_2, theta_p

def calculate_fatigue_life(stress_amplitude, ultimate_strength, yield_strength, endurance_limit=None):
    """Estimate fatigue life using simplified S-N curve"""
    if endurance_limit is None:
        endurance_limit = 0.5 * ultimate_strength  # Conservative estimate
    
    if stress_amplitude <= endurance_limit:
        return float('inf')  # Infinite life
    
    # Basquin's equation parameters (simplified)
    if stress_amplitude > yield_strength:
        return 1  # Failure in first cycle
    
    # Simplified S-N curve
    A = 0.9 * ultimate_strength  # Fatigue strength coefficient
    b = -0.12  # Fatigue strength exponent (typical for steel)
    
    N = (stress_amplitude / A) ** (1 / b)
    return max(1, N)

def calculate_stress_concentration_factor(geometry_type, dimensions):
    """Calculate stress concentration factors for common geometries"""
    Kt_factors = {
        'shaft_with_shoulder': {
            'description': 'Stepped shaft with shoulder fillet',
            'formula': lambda r_d_ratio, D_d_ratio: 1 + (0.25 * (D_d_ratio - 1)**0.5) / (r_d_ratio**0.5)
        },
        'shaft_with_keyway': {
            'description': 'Shaft with keyway',
            'formula': lambda: 2.0  # Conservative estimate
        },
        'shaft_with_hole': {
            'description': 'Shaft with transverse hole',
            'formula': lambda d_D_ratio: 3 - 3.13 * (d_D_ratio) + 3.66 * (d_D_ratio)**2 - 1.53 * (d_D_ratio)**3
        }
    }
    
    if geometry_type not in Kt_factors:
        return 1.0  # No concentration
    
    factor_data = Kt_factors[geometry_type]
    
    if geometry_type == 'shaft_with_shoulder':
        r_d_ratio = dimensions.get('fillet_radius', 1) / dimensions.get('small_diameter', 10)
        D_d_ratio = dimensions.get('large_diameter', 20) / dimensions.get('small_diameter', 10)
        return factor_data['formula'](max(r_d_ratio, 0.01), max(D_d_ratio, 1.1))
    
    elif geometry_type == 'shaft_with_keyway':
        return factor_data['formula']()
    
    elif geometry_type == 'shaft_with_hole':
        d_D_ratio = dimensions.get('hole_diameter', 5) / dimensions.get('shaft_diameter', 20)
        return factor_data['formula'](min(d_D_ratio, 0.5))
    
    return 1.0

def calculate_surface_finish_factor(surface_finish, ultimate_strength):
    """Calculate surface finish factor for fatigue analysis"""
    finish_factors = {
        'mirror_polished': {'a': 1.58, 'b': -0.085},
        'polished': {'a': 4.51, 'b': -0.265},
        'machined': {'a': 4.51, 'b': -0.265},
        'hot_rolled': {'a': 57.7, 'b': -0.718},
        'as_forged': {'a': 272, 'b': -0.995}
    }
    
    if surface_finish not in finish_factors:
        surface_finish = 'machined'  # Default
    
    factors = finish_factors[surface_finish]
    Sut_ksi = ultimate_strength / 6.895e6  # Convert Pa to ksi
    
    Ka = factors['a'] * (Sut_ksi ** factors['b'])
    return min(Ka, 1.0)  # Surface factor should not exceed 1.0

def calculate_size_factor(diameter_mm, loading_type='bending'):
    """Calculate size factor for fatigue analysis"""
    diameter_in = diameter_mm / 25.4  # Convert to inches
    
    if loading_type == 'bending' or loading_type == 'torsion':
        if diameter_in <= 0.3:
            Kb = 1.0
        elif diameter_in <= 2.0:
            Kb = (diameter_in / 0.3) ** (-0.107)
        elif diameter_in <= 10.0:
            Kb = 0.91 * (diameter_in ** (-0.157))
        else:
            Kb = 0.91 * (10.0 ** (-0.157))  # Cap at 10 inches
    else:  # Axial loading
        Kb = 1.0
    
    return Kb

def display_calculation_help(calculation_type):
    """Display help information for calculations"""
    help_texts = {
        'shaft_design': """
        **Shaft Design Help:**
        - **Torque**: Rotational moment applied to the shaft (N⋅m)
        - **Bending Moment**: Maximum bending moment due to transverse loads (N⋅m)
        - **Safety Factor**: Ratio of material strength to applied stress (typically 2-4)
        - **von Mises Stress**: Equivalent stress combining all stress components
        """,
        
        'gear_design': """
        **Gear Design Help:**
        - **Module**: Ratio of pitch diameter to number of teeth (mm)
        - **Pressure Angle**: Angle between tooth profile and radial line (typically 20°)
        - **Lewis Form Factor**: Tooth geometry factor for bending stress calculation
        - **Contact Stress**: Hertzian stress between meshing teeth
        """,
        
        'material_selection': """
        **Material Selection Help:**
        - **Yield Strength**: Stress at which permanent deformation begins
        - **Ultimate Strength**: Maximum stress material can withstand
        - **Fatigue Strength**: Stress amplitude for infinite fatigue life
        - **Elastic Modulus**: Measure of material stiffness
        """
    }
    
    if calculation_type in help_texts:
        with st.expander("📚 Calculation Help"):
            st.markdown(help_texts[calculation_type])

def create_calculation_summary(parameters, results, calculation_type):
    """Create a standardized calculation summary"""
    summary = {
        'calculation_type': calculation_type,
        'timestamp': st.session_state.get('timestamp', 'Unknown'),
        'parameters': parameters,
        'results': results,
        'units': get_standard_units(calculation_type)
    }
    return summary

def get_standard_units(calculation_type):
    """Get standard units for different calculation types"""
    unit_sets = {
        'shaft_design': {
            'length': 'mm',
            'force': 'N',
            'moment': 'N⋅m',
            'stress': 'MPa',
            'pressure': 'MPa'
        },
        'gear_design': {
            'length': 'mm',
            'force': 'N',
            'moment': 'N⋅m',
            'stress': 'MPa',
            'power': 'kW',
            'speed': 'RPM'
        }
    }
    
    return unit_sets.get(calculation_type, unit_sets['shaft_design'])

def validate_engineering_inputs(inputs, calculation_type):
    """Validate engineering inputs for different calculation types"""
    errors = []
    
    if calculation_type == 'shaft_design':
        if inputs.get('torque', 0) < 0:
            errors.append("Torque cannot be negative")
        if inputs.get('diameter', 0) <= 0:
            errors.append("Diameter must be positive")
        if inputs.get('safety_factor', 0) < 1:
            errors.append("Safety factor must be at least 1.0")
    
    elif calculation_type == 'gear_design':
        if inputs.get('module', 0) <= 0:
            errors.append("Module must be positive")
        if inputs.get('teeth', 0) < 6:
            errors.append("Number of teeth must be at least 6")
        if inputs.get('power', 0) <= 0:
            errors.append("Power must be positive")
    
    return errors
