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
                       max_allele_freq: float = 0.01,
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


def create_sample_vcf(output_path: str = 'data/sample_variants.vcf'):
    """Create a sample VCF file for testing"""
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write("##fileformat=VCFv4.2\n")
        f.write("##reference=GRCh38\n")
        f.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        f.write("chr1\t12345\t.\tA\tG\t50.0\tPASS\tGENE=BRCA1;CONSEQUENCE=missense_variant;AF=0.0001\n")
        f.write("chr2\t67890\t.\tC\tT\t45.0\tPASS\tGENE=TP53;CONSEQUENCE=nonsense_variant;AF=0.0002\n")
        f.write("chr7\t55242464\t.\tG\tA\t60.0\tPASS\tGENE=EGFR;CONSEQUENCE=missense_variant;AF=0.001\n")
        f.write("chr17\t43044295\t.\tT\tC\t55.0\tPASS\tGENE=BRCA1;CONSEQUENCE=splice_site_variant;AF=0.0003\n")
        f.write("chr13\t32315474\t.\tG\tT\t48.0\tPASS\tGENE=BRCA2;CONSEQUENCE=frameshift_variant;AF=0.0001\n")
    
    print(f"Sample VCF created at {output_path}")


if __name__ == "__main__":
    create_sample_vcf()
    
    parser = VariantParser('data/sample_variants.vcf')
    variants = parser.parse_vcf()
    
    print(f"Parsed {len(variants)} variants")
    if variants:
        print("\nFirst variant:")
        print(variants[0])
        
        filtered = parser.filter_variants(min_quality=45.0)
        print(f"\n{len(filtered)} variants passed filters")
        
        df = parser.to_dataframe()
        print("\nVariants DataFrame:")
        print(df[['id', 'gene', 'consequence', 'quality']])
    else:
        print("No variants parsed. Check VCF file format.")
