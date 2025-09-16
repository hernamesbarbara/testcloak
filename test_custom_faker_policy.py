#!/usr/bin/env python3
"""
Test CloakPivot with a custom faker-based policy
"""

from pathlib import Path
from docling.document_converter import DocumentConverter
from cloakpivot import CloakEngine
from cloakpivot.core.policies import MaskingPolicy
from cloakpivot.core.strategies import Strategy, StrategyKind
from faker import Faker
import hashlib

# Initialize faker
faker = Faker()
faker.seed_instance("testcloak")

def create_faker_callback(entity_type):
    """Create a callback function for faker-based replacement"""
    def callback(text):
        # Use hash for consistency
        hash_val = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        faker.seed_instance(hash_val)

        if entity_type == "PERSON":
            return faker.name()
        elif entity_type == "EMAIL_ADDRESS":
            return faker.email()
        elif entity_type == "DATE_TIME":
            # Generate a date in similar format
            return faker.date_time().strftime("%Y-%m-%d")
        elif entity_type == "PHONE_NUMBER":
            return faker.phone_number()
        elif entity_type == "LOCATION":
            return faker.city()
        else:
            return f"[{entity_type}]"
    return callback

# Test document path
pdf_path = Path("data/pdf/email.pdf")

print("Converting PDF to DoclingDocument...")
converter = DocumentConverter()
result = converter.convert(str(pdf_path))
docling_doc = result.document

print("\n=== Testing Custom Faker Strategy ===")

# Create a policy with custom callbacks for each entity type
policy = MaskingPolicy(
    default_strategy=Strategy(
        kind=StrategyKind.CUSTOM,
        parameters={"callback": lambda text: f"[REDACTED-{len(text)}]"}
    ),
    seed="testcloak"
)

# Add faker callbacks for specific entities
entity_types = ["PERSON", "EMAIL_ADDRESS", "DATE_TIME", "PHONE_NUMBER", "LOCATION"]
for entity_type in entity_types:
    policy = policy.with_entity_strategy(
        entity_type,
        Strategy(
            kind=StrategyKind.CUSTOM,
            parameters={"callback": create_faker_callback(entity_type)}
        )
    )

# Create engine with custom policy
cloak_engine = CloakEngine(default_policy=policy)
mask_result = cloak_engine.mask_document(docling_doc)

print(f"Entities found: {mask_result.entities_found}")
print(f"Entities masked: {mask_result.entities_masked}")

# Get some text to see the result
if mask_result.document and hasattr(mask_result.document, 'texts'):
    print("\nMasked text preview:")
    for i, text_item in enumerate(mask_result.document.texts[:10]):  # Show first 10 lines
        if hasattr(text_item, 'text'):
            print(f"  Line {i+1}: {text_item.text}")

# Check the cloakmap to see what was replaced
if mask_result.cloakmap:
    print("\nSample replacements from cloakmap:")
    cloakmap_dict = mask_result.cloakmap.to_dict()
    if 'anchors' in cloakmap_dict and cloakmap_dict['anchors']:
        for anchor in cloakmap_dict['anchors'][:5]:  # Show first 5 replacements
            entity_type = anchor.get('entity_type', 'Unknown')
            masked_value = anchor.get('masked_value', 'N/A')
            original = anchor.get('metadata', {}).get('original_text', 'N/A')
            print(f"  {entity_type}: '{original}' -> '{masked_value}'")