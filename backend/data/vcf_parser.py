import re

class VCFParser:
    """Parse VCF files for variant analysis"""
    
    def parse_vcf(self, vcf_content):
        """Parse VCF file content"""
        variants = []
        lines = vcf_content.split('\n')
        
        for line in lines:
            if line.startswith('#') or not line.strip():
                continue
                
            parts = line.split('\t')
            if len(parts) < 8:
                continue
                
            variant = {
                'chrom': parts[0],
                'pos': parts[1],
                'id': parts[2] if parts[2] != '.' else f"var_{parts[0]}_{parts[1]}",
                'ref': parts[3],
                'alt': parts[4],
                'qual': parts[5],
                'filter': parts[6],
                'info': parts[7]
            }
            
            variants.append(variant)
        
        return variants
    
    def annotate_variants(self, variants, variant_db):
        """Annotate uploaded variants with ClinVar data"""
        annotated = []
        
        for var in variants:
            # Try to match with known variants
            matched = False
            for known_var in variant_db:
                if (var['chrom'] in known_var.get('position', '') and 
                    var['ref'] == known_var.get('ref', '') and
                    var['alt'] == known_var.get('alt', '')):
                    annotated.append({**var, **known_var, 'matched': True})
                    matched = True
                    break
            
            if not matched:
                # Unknown variant - mark for further analysis
                annotated.append({
                    **var,
                    'disease': 'Unknown Clinical Significance',
                    'pathogenicity': 'Uncertain',
                    'matched': False
                })
        
        return annotated
