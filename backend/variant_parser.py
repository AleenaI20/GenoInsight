"""
Variant Parser Module
Parses VCF files and extracts relevant variant information
"""

import re
from typing import List, Dict, Any
import pandas as pd
import os

class VariantParser:
    """Parse VCF files and extract variant information"""
    
    def __init__(self, vcf_path: str):
        self.vcf_path = vcf_path
        self.variants = []
        
    def parse_vcf(self) -> List[Dict[str, Any]]:
        """Parse VCF file and return list of variant dictionaries"""
        variants = []
        
        with open(self.vcf_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                fields = line.split('\t')
                if len(fields) < 8:
                    continue
                
                variant = self._parse_variant_line(fields)
                variants.append(variant)
        
        self.variants = variants
        return variants
    
    def _parse_variant_line(self, fields: List[str]) -> Dict[str, Any]:
        """Parse individual variant line from VCF"""
        
        chrom = fields[0]
        pos = int(fields[1])
        ref = fields[3]
        alt = fields[4]
        qual = fields[5]
        filter_status = fields[6]
        info = fields[7]
        
        info_dict = self._parse_info_field(info)
        variant_id = f"{chrom}:{pos}:{ref}>{alt}"
        
        variant = {
            'id': variant_id,
            'chromosome': chrom,
            'position': pos,
            'reference': ref,
            'alternate': alt,
            'quality': qual,
            'filter': filter_status,
            'gene': info_dict.get('GENE', 'Unknown'),
            'consequence': info_dict.get('CONSEQUENCE', 'Unknown'),
            'allele_frequency': float(info_dict.get('AF', '0.0')),
            'info': info_dict
        }
        
        return variant
    
    def _parse_info_field(self, info: str) -> Dict[str, Any]:
        """Parse VCF INFO field into dictionary"""
        info_dict = {}
        
        for item in info.split(';'):
            if '=' in item:
                key, value = item.split('=', 1)
                info_dict[key] = value
            else:
                info_dict[item] = True
        
        return info_dict
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert parsed variants to pandas DataFrame"""
        if not self.variants:
            self.parse_vcf()
        
        return pd.DataFrame(self.variants)
    
    def filter_variants(self, 
                       min_quality: float = 20.0,
                       max_allele_freq: float = 0.5,
                       pass_filter_only: bool = True) -> List[Dict[str, Any]]:
        """Filter variants based on quality criteria"""
        filtered = []
        
        for variant in self.variants:
            if variant['quality'] != '.' and float(variant['quality']) < min_quality:
                continue
            
            if pass_filter_only and variant['filter'] != 'PASS':
                continue
            
            if variant['allele_frequency'] > max_allele_freq:
                continue
            
            filtered.append(variant)
        
        return filtered


if __name__ == "__main__":
    # Test with existing VCF - DON'T create new one
    vcf_path = 'data/sample_variants.vcf'
    
    if os.path.exists(vcf_path):
        print(f"Parsing {vcf_path}...")
        parser = VariantParser(vcf_path)
        variants = parser.parse_vcf()
        
        print(f"\n✓ Parsed {len(variants)} variants")
        
        if variants:
            print("\nFirst 5 variants:")
            for i, v in enumerate(variants[:5]):
                print(f"  {i+1}. {v['gene']:10s} - {v['consequence']:25s} - AF: {v['allele_frequency']:.6f}")
            
            # Show gene distribution
            genes = {}
            for v in variants:
                genes[v['gene']] = genes.get(v['gene'], 0) + 1
            
            print(f"\nGene distribution ({len(genes)} unique genes):")
            for gene, count in sorted(genes.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {gene:10s}: {count} variants")
            
            # Filter
            filtered = parser.filter_variants(min_quality=30.0)
            print(f"\n✓ {len(filtered)} variants passed quality filters (Q > 30)")
    else:
        print(f"Error: {vcf_path} not found!")
