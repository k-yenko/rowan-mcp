"""
Advanced molecule lookup using PubChemPy + SQLite Cache + RDKit validation.
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
import os

# Set up logging
logger = logging.getLogger(__name__)

# Import dependencies with fallbacks
try:
    import pubchempy as pcp
    PUBCHEMPY_AVAILABLE = True
except ImportError:
    logger.warning("pubchempy not available - install with: pip install pubchempy")
    PUBCHEMPY_AVAILABLE = False

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors
    RDKIT_AVAILABLE = True
except ImportError:
    logger.warning("rdkit not available - install with: pip install rdkit")
    RDKIT_AVAILABLE = False

class MoleculeLookup:
    """Advanced molecule lookup with PubChem API, SQLite caching, and RDKit validation."""
    
    def __init__(self, cache_db: str = 'molecule_cache.db', cache_expiry_days: int = 30):
        """Initialize the molecule lookup system."""
        self.cache_expiry_days = cache_expiry_days
        
        # Create cache database
        cache_path = os.path.join(os.path.dirname(__file__), cache_db)
        self.conn = sqlite3.connect(cache_path, check_same_thread=False)
        
        # Create tables if they don't exist
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS molecules (
                identifier TEXT PRIMARY KEY,
                smiles TEXT,
                canonical_smiles TEXT,
                name TEXT,
                iupac_name TEXT,
                formula TEXT,
                molecular_weight REAL,
                cid INTEGER,
                retrieved_at TIMESTAMP,
                source TEXT
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS lookup_stats (
                date TEXT PRIMARY KEY,
                cache_hits INTEGER DEFAULT 0,
                api_calls INTEGER DEFAULT 0,
                failed_lookups INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
        logger.info("Molecule lookup cache initialized")
    
    def validate_smiles(self, smiles: str) -> Optional[str]:
        """Validate and canonicalize SMILES using RDKit."""
        if not RDKIT_AVAILABLE:
            logger.warning("RDKit not available - returning SMILES as-is")
            return smiles
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is not None:
                canonical = Chem.MolToSmiles(mol, canonical=True)
                logger.debug(f"SMILES validated: {smiles} -> {canonical}")
                return canonical
        except Exception as e:
            logger.warning(f"SMILES validation failed for {smiles}: {e}")
        
        return None
    
    def get_molecular_properties(self, smiles: str) -> dict:
        """Calculate molecular properties using RDKit."""
        if not RDKIT_AVAILABLE:
            return {}
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is not None:
                return {
                    'molecular_weight': round(Descriptors.MolWt(mol), 2),
                    'logp': round(Descriptors.MolLogP(mol), 2),
                    'hbd': Descriptors.NumHDonors(mol),
                    'hba': Descriptors.NumHAcceptors(mol),
                    'rotatable_bonds': Descriptors.NumRotatableBonds(mol),
                    'aromatic_rings': Descriptors.NumAromaticRings(mol)
                }
        except Exception as e:
            logger.warning(f"Property calculation failed for {smiles}: {e}")
        
        return {}
    
    def _is_cache_valid(self, retrieved_at: str) -> bool:
        """Check if cache entry is still valid."""
        try:
            cache_time = datetime.fromisoformat(retrieved_at)
            expiry_time = datetime.now() - timedelta(days=self.cache_expiry_days)
            return cache_time > expiry_time
        except:
            return False
    
    def _update_stats(self, stat_type: str):
        """Update lookup statistics."""
        today = datetime.now().date().isoformat()
        
        # Insert or update today's stats
        self.conn.execute(f'''
            INSERT OR IGNORE INTO lookup_stats (date, {stat_type}) VALUES (?, 1)
        ''', (today,))
        
        self.conn.execute(f'''
            UPDATE lookup_stats SET {stat_type} = {stat_type} + 1 WHERE date = ?
        ''', (today,))
        
        self.conn.commit()
    
    def get_smiles(self, identifier: str) -> Tuple[Optional[str], str, dict]:
        """Get canonical SMILES for a molecule identifier."""
        identifier = identifier.strip()
        identifier_lower = identifier.lower()
        
        # 1. Check cache first
        cursor = self.conn.execute('''
            SELECT smiles, canonical_smiles, name, iupac_name, formula, 
                   molecular_weight, cid, retrieved_at, source 
            FROM molecules WHERE identifier = ?
        ''', (identifier_lower,))
        
        result = cursor.fetchone()
        if result:
            retrieved_at = result[7]
            if self._is_cache_valid(retrieved_at):
                self._update_stats('cache_hits')
                logger.info(f"Cache hit for: {identifier}")
                
                metadata = {
                    'name': result[2],
                    'iupac_name': result[3],
                    'formula': result[4],
                    'molecular_weight': result[5],
                    'cid': result[6],
                    'source': result[8],
                    'cached': True
                }
                
                return result[1], result[8], metadata  # Return canonical_smiles
        
        # 2. Check if input is already a valid SMILES
        validated_smiles = self.validate_smiles(identifier)
        if validated_smiles and validated_smiles != identifier:
            logger.info(f"Input was valid SMILES, canonicalized: {identifier} -> {validated_smiles}")
            
            # Cache the result
            metadata = {'source': 'input_smiles', 'cached': False}
            properties = self.get_molecular_properties(validated_smiles)
            metadata.update(properties)
            
            self._cache_result(identifier_lower, identifier, validated_smiles, 
                             "User Input SMILES", "", "", 
                             properties.get('molecular_weight'), None, 'input_smiles')
            
            return validated_smiles, 'input_smiles', metadata
        
        # 3. Fetch from PubChem using PubChemPy
        if not PUBCHEMPY_AVAILABLE:
            logger.error("PubChemPy not available for API lookup")
            self._update_stats('failed_lookups')
            return None, 'error', {'error': 'PubChemPy not available'}
        
        try:
            self._update_stats('api_calls')
            logger.info(f"PubChem API lookup for: {identifier}")
            
            # Try name lookup first
            compounds = pcp.get_compounds(identifier, 'name')
            
            # If name lookup fails, try as SMILES/InChI
            if not compounds:
                compounds = pcp.get_compounds(identifier, 'smiles')
            
            if compounds:
                compound = compounds[0]
                
                # Validate the SMILES from PubChem
                pubchem_smiles = compound.canonical_smiles
                validated_smiles = self.validate_smiles(pubchem_smiles)
                
                if validated_smiles:
                    # Get additional properties
                    properties = self.get_molecular_properties(validated_smiles)
                    
                    # Cache the successful result
                    self._cache_result(
                        identifier_lower,
                        pubchem_smiles,
                        validated_smiles,
                        getattr(compound, 'iupac_name', '') or identifier,
                        getattr(compound, 'iupac_name', ''),
                        getattr(compound, 'molecular_formula', ''),
                        properties.get('molecular_weight') or getattr(compound, 'molecular_weight', None),
                        getattr(compound, 'cid', None),
                        'pubchem'
                    )
                    
                    metadata = {
                        'name': identifier,
                        'iupac_name': getattr(compound, 'iupac_name', ''),
                        'formula': getattr(compound, 'molecular_formula', ''),
                        'molecular_weight': properties.get('molecular_weight') or getattr(compound, 'molecular_weight', None),
                        'cid': getattr(compound, 'cid', None),
                        'source': 'pubchem',
                        'cached': False
                    }
                    metadata.update(properties)
                    
                    logger.info(f"PubChem lookup successful: {identifier} -> {validated_smiles}")
                    return validated_smiles, 'pubchem', metadata
        
        except Exception as e:
            logger.error(f"PubChem lookup failed for {identifier}: {e}")
            self._update_stats('failed_lookups')
            return None, 'error', {'error': str(e)}
        
        # 4. No results found
        logger.warning(f"No results found for: {identifier}")
        self._update_stats('failed_lookups')
        return None, 'not_found', {'error': 'No results found'}
    
    def _cache_result(self, identifier: str, original_smiles: str, canonical_smiles: str,
                     name: str, iupac_name: str, formula: str, 
                     molecular_weight: Optional[float], cid: Optional[int], source: str):
        """Cache a successful lookup result."""
        try:
            self.conn.execute('''
                INSERT OR REPLACE INTO molecules 
                (identifier, smiles, canonical_smiles, name, iupac_name, formula, 
                 molecular_weight, cid, retrieved_at, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (identifier, original_smiles, canonical_smiles, name, iupac_name,
                  formula, molecular_weight, cid, datetime.now().isoformat(), source))
            
            self.conn.commit()
            logger.debug(f"Cached result for: {identifier}")
        except Exception as e:
            logger.error(f"Failed to cache result: {e}")
    
    def get_cache_stats(self) -> dict:
        """Get cache usage statistics."""
        cursor = self.conn.execute('''
            SELECT COUNT(*) as total_entries,
                   COUNT(CASE WHEN source = 'pubchem' THEN 1 END) as pubchem_entries,
                   COUNT(CASE WHEN source = 'input_smiles' THEN 1 END) as smiles_entries
            FROM molecules
        ''')
        
        cache_stats = cursor.fetchone()
        
        cursor = self.conn.execute('''
            SELECT SUM(cache_hits) as total_hits,
                   SUM(api_calls) as total_calls,
                   SUM(failed_lookups) as total_failures
            FROM lookup_stats
        ''')
        
        usage_stats = cursor.fetchone()
        
        return {
            'total_cached_molecules': cache_stats[0] or 0,
            'pubchem_entries': cache_stats[1] or 0,
            'smiles_entries': cache_stats[2] or 0,
            'total_cache_hits': usage_stats[0] or 0,
            'total_api_calls': usage_stats[1] or 0,
            'total_failures': usage_stats[2] or 0
        }

# Global instance
_lookup_instance = None

def get_lookup_instance():
    """Get or create the global MoleculeLookup instance."""
    global _lookup_instance
    if _lookup_instance is None:
        _lookup_instance = MoleculeLookup()
    return _lookup_instance

def rowan_molecule_lookup(molecule_name: str, show_properties: bool = False) -> str:
    """Advanced molecule lookup with PubChem API, SQLite caching, and RDKit validation.
    
    Features:
    - PubChemPy integration for reliable API access
    - SQLite caching for faster repeated lookups
    - RDKit validation and canonicalization
    - Comprehensive molecular properties
    - Usage statistics and cache management
    
    Args:
        molecule_name: Name of the molecule (e.g., "aspirin", "taxol", "remdesivir")
        show_properties: Include molecular properties in output
    
    Returns:
        Comprehensive molecule information with canonical SMILES
    """
    
    if not molecule_name.strip():
        lookup = get_lookup_instance()
        stats = lookup.get_cache_stats()
        
        formatted = "**Advanced Molecule SMILES Lookup**\n\n"
        formatted += "**Features:**\n"
        formatted += "• PubChemPy integration - Official PubChem API access\n"
        formatted += "• SQLite caching - Faster repeated lookups\n"
        formatted += "• RDKit validation - Canonical SMILES standardization\n"
        formatted += "• Molecular properties - MW, LogP, H-bond donors/acceptors\n\n"
        
        formatted += "**Usage Examples:**\n"
        formatted += "• rowan_molecule_lookup('aspirin') - Look up pharmaceuticals\n"
        formatted += "• rowan_molecule_lookup('taxol') - Complex natural products\n"
        formatted += "• rowan_molecule_lookup('remdesivir') - Modern drugs\n"
        formatted += "• rowan_molecule_lookup('SMILES_STRING') - Validate existing SMILES\n\n"
        
        formatted += "**Cache Statistics:**\n"
        formatted += f"• Cached molecules: {stats['total_cached_molecules']}\n"
        formatted += f"• Cache hits: {stats['total_cache_hits']}\n"
        formatted += f"• API calls made: {stats['total_api_calls']}\n"
        formatted += f"• Failed lookups: {stats['total_failures']}\n\n"
        
        formatted += "**Dependencies Status:**\n"
        formatted += f"• PubChemPy: {'✓ Available' if PUBCHEMPY_AVAILABLE else '✗ Missing (pip install pubchempy)'}\n"
        formatted += f"• RDKit: {'✓ Available' if RDKIT_AVAILABLE else '✗ Missing (pip install rdkit)'}\n"
        
        return formatted
    
    lookup = get_lookup_instance()
    smiles, source, metadata = lookup.get_smiles(molecule_name)
    
    if source == 'error':
        formatted = f"**Lookup Error for '{molecule_name}'**\n\n"
        formatted += f"**Error:** {metadata.get('error', 'Unknown error')}\n\n"
        formatted += "**Troubleshooting:**\n"
        formatted += "• Check internet connection for PubChem access\n"
        formatted += "• Verify molecule name spelling\n"
        formatted += "• Try alternative names or systematic names\n"
        return formatted
    
    elif source == 'not_found':
        formatted = f"**No results found for '{molecule_name}'**\n\n"
        formatted += "**Searched in:**\n"
        formatted += "• PubChem database (via PubChemPy)\n"
        formatted += "• Local SQLite cache\n\n"
        formatted += "**Suggestions:**\n"
        formatted += "• Check spelling of molecule name\n"
        formatted += "• Try alternative names (e.g., 'acetaminophen' vs 'paracetamol')\n"
        formatted += "• Try systematic IUPAC name\n"
        formatted += "• Try CAS registry number\n"
        formatted += "• If you have a SMILES string, it will be validated automatically\n"
        return formatted
    
    else:
        source_names = {
            'pubchem': 'PubChem Database (via PubChemPy)',
            'input_smiles': 'Input SMILES Validation (RDKit)',
            'cache': 'Local Cache'
        }
        
        formatted = f"**SMILES lookup successful!** {'(Cached)' if metadata.get('cached') else ''}\n\n"
        formatted += f"**Molecule:** {molecule_name}\n"
        formatted += f"**Canonical SMILES:** {smiles}\n"
        formatted += f"**Source:** {source_names.get(source, source)}\n\n"
        
        # Add molecular information if available
        if metadata.get('name') and metadata['name'] != molecule_name:
            formatted += f"**Common Name:** {metadata['name']}\n"
        
        if metadata.get('iupac_name'):
            formatted += f"**IUPAC Name:** {metadata['iupac_name']}\n"
        
        if metadata.get('formula'):
            formatted += f"**Formula:** {metadata['formula']}\n"
        
        if metadata.get('cid'):
            formatted += f"**PubChem CID:** {metadata['cid']}\n"
        
        # Add molecular properties if requested or available
        if show_properties or any(key in metadata for key in ['molecular_weight', 'logp', 'hbd', 'hba']):
            formatted += "\n**Molecular Properties:**\n"
            
            if metadata.get('molecular_weight'):
                formatted += f"• Molecular Weight: {metadata['molecular_weight']:.2f} g/mol\n"
            
            if metadata.get('logp') is not None:
                formatted += f"• LogP: {metadata['logp']:.2f}\n"
            
            if metadata.get('hbd') is not None:
                formatted += f"• H-bond Donors: {metadata['hbd']}\n"
            
            if metadata.get('hba') is not None:
                formatted += f"• H-bond Acceptors: {metadata['hba']}\n"
            
            if metadata.get('rotatable_bonds') is not None:
                formatted += f"• Rotatable Bonds: {metadata['rotatable_bonds']}\n"
            
            if metadata.get('aromatic_rings') is not None:
                formatted += f"• Aromatic Rings: {metadata['aromatic_rings']}\n"
        
        formatted += f"\n**Usage:** Use '{smiles}' in Rowan calculations for consistent results\n"
        
        return formatted

def test_rowan_molecule_lookup():
    """Test the advanced molecule lookup function."""
    try:
        print("Testing advanced molecule lookup...")
        
        # Test common molecule
        print("1. Testing phenol...")
        result1 = rowan_molecule_lookup("phenol")
        print("✓ Phenol lookup successful")
        
        # Test cache stats
        print("2. Testing cache statistics...")
        result2 = rowan_molecule_lookup("")
        print("✓ Cache statistics successful")
        
        print("Advanced molecule lookup test successful!")
        return True
    except Exception as e:
        print(f"Advanced molecule lookup test failed: {e}")
        return False

if __name__ == "__main__":
    test_rowan_molecule_lookup() 

