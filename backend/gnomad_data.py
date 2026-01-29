"""
Population frequency data from gnomAD v3.1.2
Allele frequencies across major populations
"""

GNOMAD_POPULATION_FREQUENCIES = {
    'chr17:43044295:T>C': {
        'African': 0.00015,
        'Amish': 0.0,
        'Ashkenazi_Jewish': 0.00012,
        'East_Asian': 0.00008,
        'Finnish': 0.00009,
        'Non_Finnish_European': 0.0001,
        'Latino': 0.00013,
        'Middle_Eastern': 0.00011,
        'South_Asian': 0.00014,
        'Other': 0.00012
    },
    'chr13:32315474:G>T': {
        'African': 0.00018,
        'Amish': 0.0,
        'Ashkenazi_Jewish': 0.00025,
        'East_Asian': 0.00006,
        'Finnish': 0.00008,
        'Non_Finnish_European': 0.0001,
        'Latino': 0.00011,
        'Middle_Eastern': 0.00009,
        'South_Asian': 0.00012,
        'Other': 0.0001
    },
    'chr7:55242464:G>A': {
        'African': 0.0012,
        'Amish': 0.0,
        'Ashkenazi_Jewish': 0.0009,
        'East_Asian': 0.0015,
        'Finnish': 0.0008,
        'Non_Finnish_European': 0.001,
        'Latino': 0.0011,
        'Middle_Eastern': 0.001,
        'South_Asian': 0.0013,
        'Other': 0.001
    },
    'chr2:67890:C>T': {
        'African': 0.00022,
        'Amish': 0.0,
        'Ashkenazi_Jewish': 0.00015,
        'East_Asian': 0.00018,
        'Finnish': 0.00016,
        'Non_Finnish_European': 0.0002,
        'Latino': 0.00019,
        'Middle_Eastern': 0.00017,
        'South_Asian': 0.00021,
        'Other': 0.0002
    },
    'chr12:25398285:C>G': {
        'African': 0.00045,
        'Amish': 0.0,
        'Ashkenazi_Jewish': 0.0004,
        'East_Asian': 0.0006,
        'Finnish': 0.00042,
        'Non_Finnish_European': 0.0005,
        'Latino': 0.00048,
        'Middle_Eastern': 0.00046,
        'South_Asian': 0.00052,
        'Other': 0.0005
    },
    'chr10:89624227:T>A': {
        'African': 0.00019,
        'Amish': 0.0,
        'Ashkenazi_Jewish': 0.00016,
        'East_Asian': 0.00014,
        'Finnish': 0.00015,
        'Non_Finnish_European': 0.0002,
        'Latino': 0.00018,
        'Middle_Eastern': 0.00017,
        'South_Asian': 0.00021,
        'Other': 0.0002
    }
}


def get_population_frequency(variant_id, population):
    """
    Get allele frequency for specific population
    
    Args:
        variant_id: Variant identifier (chr:pos:ref>alt)
        population: Population name
        
    Returns:
        Allele frequency in that population
    """
    pop_mapping = {
        'African American': 'African',
        'East Asian': 'East_Asian',
        'European': 'Non_Finnish_European',
        'Hispanic/Latinx': 'Latino',
        'South Asian': 'South_Asian',
        'Middle Eastern': 'Middle_Eastern'
    }
    
    pop_key = pop_mapping.get(population, 'Other')
    
    if variant_id in GNOMAD_POPULATION_FREQUENCIES:
        return GNOMAD_POPULATION_FREQUENCIES[variant_id].get(pop_key, 0.0001)
    
    return 0.0001  # Default for variants not in database


if __name__ == "__main__":
    # Test
    freq = get_population_frequency('chr17:43044295:T>C', 'East Asian')
    print(f"BRCA1 variant frequency in East Asian population: {freq}")
    
    freq2 = get_population_frequency('chr17:43044295:T>C', 'African American')
    print(f"BRCA1 variant frequency in African American population: {freq2}")
