#!/usr/bin/env python3
"""
Test script to explore different masking strategies in CloakPivot
"""

from pathlib import Path
from docling.document_converter import DocumentConverter
from cloakpivot import CloakEngine
from cloakpivot.core.policies import MaskingPolicy
from cloakpivot.core.strategies import Strategy, StrategyKind

# Test document path
pdf_path = Path("data/pdf/email.pdf")

print("Converting PDF to DoclingDocument...")
converter = DocumentConverter()
result = converter.convert(str(pdf_path))
docling_doc = result.document

print("\n=== Testing TEMPLATE Strategy (Default) ===")
# Default redaction strategy
policy_template = MaskingPolicy(
    default_strategy=Strategy(
        kind=StrategyKind.TEMPLATE,
        parameters={"template": "[REDACTED]"}
    )
)
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

# Get some text to see the result
if result_template.document and hasattr(result_template.document, 'texts'):
    sample_text = str(result_template.document.texts[0].text)[:200] if result_template.document.texts else ""
    print(f"Sample masked text: {sample_text}")

print("\n=== Testing SURROGATE Strategy (Fake Data) ===")
# Surrogate strategy for fake data replacement
policy_surrogate = MaskingPolicy(
    default_strategy=Strategy(
        kind=StrategyKind.SURROGATE,
        parameters={}
    ),
    seed="42"  # For reproducibility (must be string)
)

cloak_surrogate = CloakEngine(default_policy=policy_surrogate)
result_surrogate = cloak_surrogate.mask_document(docling_doc)
print(f"Entities found: {result_surrogate.entities_found}")
print(f"Entities masked: {result_surrogate.entities_masked}")

# Get some text to see the result
if result_surrogate.document and hasattr(result_surrogate.document, 'texts'):
    sample_text = str(result_surrogate.document.texts[0].text)[:200] if result_surrogate.document.texts else ""
    print(f"Sample masked text: {sample_text}")

print("\n=== Testing HASH Strategy ===")
# Hash strategy
policy_hash = MaskingPolicy(
    default_strategy=Strategy(
        kind=StrategyKind.HASH,
        parameters={"hash_type": "sha256"}
    )
)

cloak_hash = CloakEngine(default_policy=policy_hash)
result_hash = cloak_hash.mask_document(docling_doc)
print(f"Entities found: {result_hash.entities_found}")
print(f"Entities masked: {result_hash.entities_masked}")

# Get some text to see the result
if result_hash.document and hasattr(result_hash.document, 'texts'):
    sample_text = str(result_hash.document.texts[0].text)[:200] if result_hash.document.texts else ""
    print(f"Sample masked text: {sample_text}")