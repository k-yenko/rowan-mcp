"""
Rowan scan analysis functions for MCP tool integration.
"""

from typing import Optional, Dict, Any, Tuple, List
import rowan


def rowan_scan_analyzer(
    scan_uuid: str,
    action: str = "analyze",
    energy_threshold: Optional[float] = None
) -> str:
    """Analyze scan results and extract key geometries.
    
    **Available Actions:**
    - **analyze**: Full analysis with energy profile and key points
    - **extract_ts**: Extract highest energy geometry (TS approximation)
    - **extract_minima**: Extract lowest energy geometries
    - **energy_profile**: Show energy vs coordinate plot data
    
    Args:
        scan_uuid: UUID of the completed scan workflow
        action: Analysis type ('analyze', 'extract_ts', 'extract_minima', 'energy_profile')
        energy_threshold: Energy threshold for identifying key points (kcal/mol above minimum)
    
    Returns:
        Analysis results with geometries and energies
    """
    
    action = action.lower()
    
    try:
        # Retrieve scan workflow results
        workflow = rowan.Workflow.retrieve(uuid=scan_uuid)
        
        # Check if workflow is completed
        status = workflow.get('object_status', -1)
        if status != 2:  # Not completed
            status_names = {0: "Queued", 1: "Running", 3: "Failed", 4: "Stopped"}
            return f"❌ Scan workflow is not completed. Status: {status_names.get(status, 'Unknown')}"
        
        # Extract scan data from object_data
        object_data = workflow.get('object_data', {})
        if not object_data:
            return "❌ No scan data found in workflow results"
        
        # Parse scan results
        scan_results = parse_scan_data(object_data)
        if not scan_results:
            return "❌ Could not parse scan data"
        
        # Perform requested analysis
        if action == "analyze":
            return format_full_analysis(scan_results, scan_uuid)
        elif action == "extract_ts":
            return extract_ts_geometry(scan_results, scan_uuid)
        elif action == "extract_minima":
            return extract_minima_geometries(scan_results, energy_threshold)
        elif action == "energy_profile":
            return format_energy_profile(scan_results)
        else:
            return f"❌ Unknown action '{action}'. Available: analyze, extract_ts, extract_minima, energy_profile"
            
    except Exception as e:
        return f"❌ Error analyzing scan: {str(e)}"


def parse_scan_data(object_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse raw scan data into structured format."""
    
    try:
        # Look for scan points in various possible locations
        scan_points = None
        
        # Try different object_data structures
        if 'scan_points' in object_data:
            scan_points = object_data['scan_points']
        elif 'results' in object_data and isinstance(object_data['results'], list):
            scan_points = object_data['results']
        elif 'calculations' in object_data:
            scan_points = object_data['calculations']
        else:
            # Try to find array-like data
            for key, value in object_data.items():
                if isinstance(value, list) and len(value) > 1:
                    scan_points = value
                    break
        
        if not scan_points:
            return None
        
        # Structure the scan data
        parsed_data = {
            'points': [],
            'energies': [],
            'coordinates': [],
            'geometries': []
        }
        
        for i, point in enumerate(scan_points):
            if isinstance(point, dict):
                # Extract energy
                energy = point.get('energy') or point.get('total_energy') or point.get('scf_energy')
                if energy is not None:
                    parsed_data['energies'].append(energy)
                
                # Extract coordinate value
                coord_val = point.get('coordinate_value') or point.get('scan_coordinate') or i
                parsed_data['coordinates'].append(coord_val)
                
                # Extract geometry (XYZ coordinates)
                geometry = extract_geometry_from_point(point)
                parsed_data['geometries'].append(geometry)
                
                parsed_data['points'].append({
                    'index': i,
                    'energy': energy,
                    'coordinate': coord_val,
                    'geometry': geometry
                })
        
        return parsed_data if parsed_data['energies'] else None
        
    except Exception as e:
        print(f"Error parsing scan data: {e}")
        return None


def extract_geometry_from_point(point_data: Dict[str, Any]) -> Optional[str]:
    """Extract XYZ geometry from a scan point."""
    
    try:
        # Look for geometry in various formats
        if 'geometry' in point_data:
            geom = point_data['geometry']
            if isinstance(geom, str):
                return geom
            elif isinstance(geom, dict) and 'xyz' in geom:
                return geom['xyz']
        
        # Look for molecule object
        if 'molecule' in point_data:
            mol = point_data['molecule']
            if isinstance(mol, dict) and 'geometry' in mol:
                return mol['geometry']
        
        # Look for atoms/coordinates
        if 'atoms' in point_data:
            atoms = point_data['atoms']
            if isinstance(atoms, list):
                return format_atoms_to_xyz(atoms)
        
        return None
        
    except Exception:
        return None


def format_atoms_to_xyz(atoms: List[Dict]) -> str:
    """Convert atoms list to XYZ format."""
    
    try:
        xyz_lines = [str(len(atoms)), ""]  # Number of atoms + comment line
        
        for atom in atoms:
            symbol = atom.get('symbol') or atom.get('element')
            coords = atom.get('coordinates') or atom.get('position') or [0, 0, 0]
            
            if symbol and len(coords) >= 3:
                xyz_lines.append(f"{symbol:2s} {coords[0]:12.6f} {coords[1]:12.6f} {coords[2]:12.6f}")
        
        return '\n'.join(xyz_lines)
        
    except Exception:
        return ""


def extract_ts_geometry(scan_results: Dict[str, Any], scan_uuid: str) -> str:
    """Extract the highest energy geometry (TS approximation)."""
    
    energies = scan_results['energies']
    geometries = scan_results['geometries']
    coordinates = scan_results['coordinates']
    
    if not energies:
        return "❌ No energy data found in scan results"
    
    # Find highest energy point
    max_energy_idx = energies.index(max(energies))
    max_energy = energies[max_energy_idx]
    max_coord = coordinates[max_energy_idx]
    ts_geometry = geometries[max_energy_idx]
    
    # Calculate relative energy (kcal/mol above minimum)
    min_energy = min(energies)
    rel_energy = (max_energy - min_energy) * 627.509  # Hartree to kcal/mol
    
    formatted = f"🎯 **Transition State Approximation Extracted**\n\n"
    formatted += f"📍 **Scan Point:** {max_energy_idx + 1} of {len(energies)}\n"
    formatted += f"📐 **Coordinate Value:** {max_coord:.3f}\n"
    formatted += f"⚡ **Energy:** {max_energy:.6f} hartree\n"
    formatted += f"🔥 **Barrier:** {rel_energy:.2f} kcal/mol above minimum\n\n"
    
    if ts_geometry:
        formatted += f"📋 **XYZ Geometry:**\n```\n{ts_geometry}\n```\n\n"
        formatted += f"💡 **Next Steps:**\n"
        formatted += f"1. Use this geometry for transition state optimization\n"
        formatted += f"2. Run: `rowan_spin_states(name='TS_opt', molecule='<geometry>', transition_state=True)`\n"
        formatted += f"3. Verify single imaginary frequency\n"
        formatted += f"4. Use optimized TS for IRC calculation\n"
    else:
        formatted += f"⚠️ **Warning:** Could not extract geometry data\n"
        formatted += f"💡 Check scan workflow {scan_uuid} manually for geometry data\n"
    
    return formatted


def extract_minima_geometries(scan_results: Dict[str, Any], energy_threshold: Optional[float] = None) -> str:
    """Extract low energy geometries (minima)."""
    
    energies = scan_results['energies']
    geometries = scan_results['geometries']
    coordinates = scan_results['coordinates']
    
    if not energies:
        return "❌ No energy data found in scan results"
    
    min_energy = min(energies)
    threshold = energy_threshold or 2.0  # Default 2 kcal/mol above minimum
    threshold_hartree = threshold / 627.509
    
    # Find all points within energy threshold
    minima_points = []
    for i, energy in enumerate(energies):
        if energy <= min_energy + threshold_hartree:
            rel_energy = (energy - min_energy) * 627.509
            minima_points.append({
                'index': i,
                'energy': energy,
                'rel_energy': rel_energy,
                'coordinate': coordinates[i],
                'geometry': geometries[i]
            })
    
    formatted = f"🌊 **Low Energy Structures** (within {threshold:.1f} kcal/mol)\n\n"
    formatted += f"Found {len(minima_points)} structures:\n\n"
    
    for point in minima_points:
        formatted += f"**Point {point['index'] + 1}:**\n"
        formatted += f"  📐 Coordinate: {point['coordinate']:.3f}\n"
        formatted += f"  ⚡ Energy: +{point['rel_energy']:.2f} kcal/mol\n"
        if point['geometry']:
            # Show first few lines of geometry
            geom_lines = point['geometry'].split('\n')[:5]
            formatted += f"  📋 Geometry: {' | '.join(geom_lines[:2])}\n"
        formatted += "\n"
    
    return formatted


def format_energy_profile(scan_results: Dict[str, Any]) -> str:
    """Format energy profile data for plotting/analysis."""
    
    energies = scan_results['energies']
    coordinates = scan_results['coordinates']
    
    if not energies:
        return "❌ No energy data found"
    
    min_energy = min(energies)
    
    formatted = f"📊 **Energy Profile Data**\n\n"
    formatted += f"Coordinate | Energy (hartree) | Rel Energy (kcal/mol)\n"
    formatted += f"-----------|------------------|--------------------\n"
    
    for coord, energy in zip(coordinates, energies):
        rel_energy = (energy - min_energy) * 627.509
        formatted += f"{coord:10.3f} | {energy:15.6f} | {rel_energy:18.2f}\n"
    
    formatted += f"\n📈 **Energy Range:** {(max(energies) - min_energy) * 627.509:.2f} kcal/mol\n"
    formatted += f"🎯 **Barrier Location:** Coordinate {coordinates[energies.index(max(energies))]:.3f}\n"
    
    return formatted


def format_full_analysis(scan_results: Dict[str, Any], scan_uuid: str) -> str:
    """Provide complete scan analysis."""
    
    energies = scan_results['energies']
    coordinates = scan_results['coordinates']
    
    if not energies:
        return "❌ No scan data to analyze"
    
    min_energy = min(energies)
    max_energy = max(energies)
    energy_range = (max_energy - min_energy) * 627.509
    
    # Find key points
    min_idx = energies.index(min_energy)
    max_idx = energies.index(max_energy)
    
    formatted = f"🔬 **Complete Scan Analysis**\n\n"
    formatted += f"📊 **Overview:**\n"
    formatted += f"  • Total Points: {len(energies)}\n"
    formatted += f"  • Energy Range: {energy_range:.2f} kcal/mol\n"
    formatted += f"  • Coordinate Range: {min(coordinates):.3f} to {max(coordinates):.3f}\n\n"
    
    formatted += f"🌊 **Global Minimum:**\n"
    formatted += f"  • Point {min_idx + 1}: {coordinates[min_idx]:.3f}\n"
    formatted += f"  • Energy: {min_energy:.6f} hartree\n\n"
    
    formatted += f"⛰️ **Energy Maximum (TS Approx):**\n"
    formatted += f"  • Point {max_idx + 1}: {coordinates[max_idx]:.3f}\n"
    formatted += f"  • Energy: {max_energy:.6f} hartree\n"
    formatted += f"  • Barrier: {energy_range:.2f} kcal/mol\n\n"
    
    formatted += f"💡 **Recommended Next Steps:**\n"
    formatted += f"1. Extract TS geometry: `rowan_scan_analyzer('{scan_uuid}', 'extract_ts')`\n"
    formatted += f"2. Optimize transition state with extracted geometry\n"
    formatted += f"3. Run IRC from optimized TS\n"
    
    return formatted


def test_rowan_scan_analyzer():
    """Test the scan analyzer function."""
    try:
        # Test with dummy UUID 
        result = rowan_scan_analyzer("test-scan-uuid", "analyze")
        print("✅ Scan analyzer test completed!")
        print(f"Result type: {type(result)}")
        return True
    except Exception as e:
        print(f"❌ Scan analyzer test failed: {e}")
        return False


if __name__ == "__main__":
    test_rowan_scan_analyzer() 