"""
Variant Parser Module
---------------------
Parses VCF files and extracts relevant variant information for downstream
ML-based pathogenicity prediction and clinical annotation.

NOTES:
- Supports multi-allelic variants (one record per ALT allele)
- INFO-field allele frequency (AF) is treated as cohort-level, NOT population
- Does NOT perform variant normalization or left-alignment
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import os


class VariantParser:
    """Parse VCF files and extract variant information"""

    def __init__(self, vcf_path: str):
        self.vcf_path = vcf_path
        self.variants: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Main VCF Parsing
    # ------------------------------------------------------------------
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

                parsed = self._parse_variant_line(fields)
                variants.extend(parsed)

        self.variants = variants
        return variants

    # ------------------------------------------------------------------
    # Line Parsing
    # ------------------------------------------------------------------
    def _parse_variant_line(self, fields: List[str]) -> List[Dict[str, Any]]:
        """
        Parse individual VCF record.
        Handles multi-allelic ALT fields by emitting one variant per ALT.
        """

        chrom = fields[0]
        pos = int(fields[1])
        ref = fields[3]
        alts = fields[4].split(',')  # Multi-allelic support
        qual = fields[5]
        filter_status = fields[6]
        info = fields[7]

        info_dict = self._parse_info_field(info)

        gene = (
            info_dict.get('GENE')
            or self._extract_from_annotation(info_dict.get('CSQ'))
            or self._extract_from_annotation(info_dict.get('ANN'))
            or 'Unknown'
        )

        consequence = (
            info_dict.get('CONSEQUENCE')
            or self._extract_from_annotation(info_dict.get('CSQ'))
            or self._extract_from_annotation(info_dict.get('ANN'))
            or 'Unknown'
        )

        variants = []
        for alt in alts:
            variant_id = f"{chrom}:{pos}:{ref}>{alt}"

            variants.append({
                'id': variant_id,
                'chromosome': chrom,
                'position': pos,
                'reference': ref,
                'alternate': alt,
                'quality': qual,
                'filter': filter_status,
                'gene': gene,
                'consequence': consequence,
                # AF here is cohort-level frequency (NOT population / gnomAD)
                'cohort_allele_frequency': float(info_dict.get('AF', '0.0')),
                'depth': info_dict.get('DP'),
                'zygosity': info_dict.get('GT', 'Unknown'),
                'info': info_dict
            })

        return variants

    # ------------------------------------------------------------------
    # INFO Field Utilities
    # ------------------------------------------------------------------
    def _parse_info_field(self, info: str) -> Dict[str, Any]:
        """Parse VCF INFO field into dictionary"""
        info_dict: Dict[str, Any] = {}

        for item in info.split(';'):
            if '=' in item:
                key, value = item.split('=', 1)
                info_dict[key] = value
            else:
                info_dict[item] = True

        return info_dict

    def _extract_from_annotation(self, annotation: Optional[str]) -> Optional[str]:
        """
        Extract first field from VEP/SnpEff-style annotations (CSQ / ANN).
        This is a lightweight parser for prototype use.
        """
        if not annotation:
            return None
        return annotation.split('|')[0]

    # ------------------------------------------------------------------
    # Data Accessors
    # ------------------------------------------------------------------
    def to_dataframe(self) -> pd.DataFrame:
        """Convert parsed variants to pandas DataFrame"""
        if not self.variants:
            self.parse_vcf()
        return pd.DataFrame(self.variants)

    # ------------------------------------------------------------------
    # Filtering Logic
    # ------------------------------------------------------------------
    def filter_variants(
        self,
        min_quality: float = 20.0,
        max_allele_freq: float = 0.5,
        pass_filter_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Filter variants based on quality and frequency criteria.

        Args:
            min_quality: Minimum QUAL score ('.' treated as fail)
            max_allele_freq: Maximum cohort allele frequency
            pass_filter_only: Require FILTER == PASS or '.'

        Returns:
            Filtered list of variants
        """
        filtered = []

        for variant in self.variants:
            # Quality filter (missing quality fails)
            if variant['quality'] == '.' or float(variant['quality']) < min_quality:
                continue

            # FILTER column handling (PASS or no filter)
            if pass_filter_only and variant['filter'] not in ['PASS', '.']:
                continue

            # Cohort allele frequency filter
            if variant['cohort_allele_frequency'] > max_allele_freq:
                continue

            filtered.append(variant)

        return filtered


# ----------------------------------------------------------------------
# Standalone Test
# ----------------------------------------------------------------------
if __name__ == "__main__":
    vcf_path = 'data/sample_variants.vcf'

    if os.path.exists(vcf_path):
        print(f"Parsing {vcf_path}...")
        parser = VariantParser(vcf_path)
        variants = parser.parse_vcf()

        print(f"\n✓ Parsed {len(variants)} variants")

        if variants:
            print("\nFirst 5 variants:")
            for i, v in enumerate(variants[:5]):
                print(
                    f"  {i+1}. {v['gene']:12s} | "
                    f"{v['consequence']:25s} | "
                    f"AF: {v['cohort_allele_frequency']:.6f}"
                )

            # Gene distribution
            genes = {}
            for v in variants:
                genes[v['gene']] = genes.get(v['gene'], 0) + 1

            print(f"\nGene distribution ({len(genes)} unique genes):")
            for gene, count in sorted(genes.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {gene:12s}: {count} variants")

            # Filtering
            filtered = parser.filter_variants(min_quality=30.0)
            print(f"\n✓ {len(filtered)} variants passed quality filters (Q ≥ 30)")
    else:
        print(f"Error: {vcf_path} not found!")

