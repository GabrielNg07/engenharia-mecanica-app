# Mechanical Engineering Design Tool

## Overview

This is a Streamlit-based web application for mechanical engineering design calculations, specifically focused on shaft and gear design. The tool provides comprehensive analysis capabilities including stress calculations, deflection analysis, safety factor determination, and material property lookups. It serves as a professional engineering calculator for mechanical designers and engineers working on power transmission systems.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework for rapid prototyping and deployment
- **Layout**: Multi-page application with sidebar navigation and tabbed interfaces
- **Visualization**: Plotly for interactive charts and graphs
- **UI Components**: Streamlit widgets for input forms, data display, and file downloads

### Application Structure
- **Modular Design**: Separated into distinct modules for shaft calculations, gear calculations, material database, and utility functions
- **Tab-based Interface**: Each major calculation type is organized into logical tabs (Basic Design, Stress Analysis, Deflection Analysis, Results Summary)
- **Navigation Pattern**: Sidebar-based page selection with dedicated pages for different engineering tools

### Data Management
- **In-memory Database**: Material properties stored as Python dictionaries within the application
- **Data Processing**: Pandas DataFrames for calculation results and tabular data presentation
- **Export Capabilities**: Multiple export formats (CSV, JSON, PDF-style text reports) with timestamped filenames

### Calculation Engine
- **Mathematical Libraries**: NumPy for numerical calculations and mathematical operations
- **Engineering Calculations**: Custom calculation modules for:
  - Shaft stress analysis (von Mises stress, torsional stress, bending stress)
  - Gear design parameters (tooth strength, contact stress, geometric calculations)
  - Safety factor analysis and fatigue calculations
- **Input Validation**: Utility functions for parameter validation and unit conversion

### Material Database System
- **Static Database**: Hardcoded material properties for common engineering materials
- **Material Categories**: Organized by steel types (Carbon Steel, Alloy Steel, Stainless Steel)
- **Properties Included**: Yield strength, ultimate strength, elastic modulus, Poisson's ratio, density, fatigue strength, hardness

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework for the user interface
- **NumPy**: Numerical computing and mathematical operations
- **Pandas**: Data manipulation and analysis for results processing
- **Plotly**: Interactive plotting and data visualization (both graph_objects and express modules)

### Python Standard Library
- **Math**: Mathematical functions and constants
- **IO**: String and file I/O operations for export functionality
- **DateTime**: Timestamp generation for exported files
- **JSON**: Data serialization for export capabilities

### Engineering Standards
- **Material Properties**: Based on AISI steel standards and common engineering materials
- **Calculation Methods**: Following standard mechanical engineering design practices for shaft and gear analysis
- **Safety Factors**: Industry-standard approaches to stress analysis and fatigue evaluation