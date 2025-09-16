#!/usr/bin/env python3
"""
Test script to explore and compare different masking strategies in CloakPivot
"""

from pathlib import Path
from docling.document_converter import DocumentConverter
from cloakpivot import CloakEngine
from cloakpivot.core.policies import MaskingPolicy
from cloakpivot.core.strategies import Strategy, StrategyKind
import json

# Test document path
pdf_path = Path("data/pdf/email.pdf")

print("Converting PDF to DoclingDocument...")
converter = DocumentConverter()
result = converter.convert(str(pdf_path))
docling_doc = result.document

print("\n" + "="*60)
print("Testing TEMPLATE Strategy (Static Redaction)")
print("="*60)

# Default redaction strategy
policy_template = MaskingPolicy(
    default_strategy=Strategy(
        kind=StrategyKind.TEMPLATE,
        parameters={"template": "[REDACTED]"}
    )
)
# Configure specific entity templates
policy_template = policy_template.with_entity_strategy("EMAIL_ADDRESS",
    Strategy(kind=StrategyKind.TEMPLATE, parameters={"template": "[EMAIL]"}))
policy_template = policy_template.with_entity_strategy("PERSON",
    Strategy(kind=StrategyKind.TEMPLATE, parameters={"template": "[NAME]"}))
policy_template = policy_template.with_entity_strategy("DATE_TIME",
    Strategy(kind=StrategyKind.TEMPLATE, parameters={"template": "[DATE]"}))

cloak_template = CloakEngine(default_policy=policy_template)
result_template = cloak_template.mask_document(docling_doc)

print(f"Entities found: {result_template.entities_found}")
print(f"Entities masked: {result_template.entities_masked}")

# Get full text to see the result
if result_template.document and hasattr(result_template.document, 'texts'):
    print("\nMasked text preview:")
    for i, text_item in enumerate(result_template.document.texts[:10]):  # Show first 10 lines
        if hasattr(text_item, 'text'):
            print(f"  Line {i+1}: {text_item.text}")

print("\n" + "="*60)
print("Testing SURROGATE Strategy (Fake Data Replacement)")
print("="*60)

# Surrogate strategy for fake data replacement
policy_surrogate = MaskingPolicy(
    default_strategy=Strategy(
        kind=StrategyKind.SURROGATE,
        parameters={}
    ),
    seed="test-seed-42"  # For reproducibility
)

cloak_surrogate = CloakEngine(default_policy=policy_surrogate)
result_surrogate = cloak_surrogate.mask_document(docling_doc)

print(f"Entities found: {result_surrogate.entities_found}")
print(f"Entities masked: {result_surrogate.entities_masked}")

# Get full text to see the result
if result_surrogate.document and hasattr(result_surrogate.document, 'texts'):
    print("\nMasked text preview:")
    for i, text_item in enumerate(result_surrogate.document.texts[:10]):  # Show first 10 lines
        if hasattr(text_item, 'text'):
            print(f"  Line {i+1}: {text_item.text}")

# Let's also check the cloakmap to see what was actually replaced
if result_surrogate.cloakmap:
    print("\nSample replacements from cloakmap:")
    # Get the cloakmap as dict
    cloakmap_dict = result_surrogate.cloakmap.to_dict()
    if 'anchors' in cloakmap_dict and cloakmap_dict['anchors']:
        for anchor in cloakmap_dict['anchors'][:5]:  # Show first 5 replacements
            entity_type = anchor.get('entity_type', 'Unknown')
            masked_value = anchor.get('masked_value', 'N/A')
            original = anchor.get('metadata', {}).get('original_text', 'N/A')
            print(f"  {entity_type}: '{original}' -> '{masked_value}'")