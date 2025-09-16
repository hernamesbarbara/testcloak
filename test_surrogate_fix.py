#!/usr/bin/env python3
"""
Test script to diagnose and fix the surrogate generation issue
"""

from pathlib import Path
from docling.document_converter import DocumentConverter
from cloakpivot import CloakEngine
from cloakpivot.core.policies import MaskingPolicy
from cloakpivot.core.strategies import Strategy, StrategyKind
from cloakpivot.core.surrogate import SurrogateGenerator
from cloakpivot.masking.presidio_adapter import PresidioAdapter
import inspect

# Check if the Presidio adapter is properly configured
print("Checking PresidioAdapter surrogate strategy implementation...")

# Create a test policy with surrogate strategy
policy = MaskingPolicy(
    default_strategy=Strategy(
        kind=StrategyKind.SURROGATE,
        parameters={}
    ),
    seed="test-seed"
)

# Check what parameters the surrogate strategy accepts
print("\nStrategy kind:", StrategyKind.SURROGATE.value)
print("Strategy parameters:", policy.default_strategy.parameters)

# Try different parameter configurations
print("\n=== Testing different surrogate configurations ===")

# Test 1: Default surrogate with no parameters
policy1 = MaskingPolicy(
    default_strategy=Strategy(
        kind=StrategyKind.SURROGATE,
        parameters={}
    ),
    seed="test"
)
print(f"Test 1 - Default: {policy1.default_strategy}")

# Test 2: Surrogate with fallback redaction disabled
policy2 = MaskingPolicy(
    default_strategy=Strategy(
        kind=StrategyKind.SURROGATE,
        parameters={"fallback": "asterisks", "use_faker": True}
    ),
    seed="test"
)
print(f"Test 2 - With faker: {policy2.default_strategy}")

# Test the engine with a simple text
test_text = "John Doe's email is john@example.com"
print(f"\nTest text: {test_text}")

# Convert to a document
print("\nCreating test document...")
pdf_path = Path("data/pdf/email.pdf")
converter = DocumentConverter()
result = converter.convert(str(pdf_path))
docling_doc = result.document

# Test with different engines
print("\n=== Testing with different engine configurations ===")

# Engine 1: Default surrogate
engine1 = CloakEngine(default_policy=policy1)
result1 = engine1.mask_document(docling_doc)
if result1.document and hasattr(result1.document, 'texts'):
    preview = str(result1.document.texts[2].text) if len(result1.document.texts) > 2 else ""
    print(f"Engine 1 result: {preview}")

# Let's also check what the PresidioAdapter does
print("\n=== Checking PresidioAdapter directly ===")
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer import RecognizerResult

# Create a recognizer result for testing
test_results = [
    RecognizerResult(entity_type="PERSON", start=0, end=8, score=0.85),
    RecognizerResult(entity_type="EMAIL_ADDRESS", start=20, end=37, score=1.0),
]

# Test the anonymizer with default settings
anonymizer = AnonymizerEngine()
try:
    # Try using replace operator
    result = anonymizer.anonymize(
        text=test_text,
        analyzer_results=test_results,
        operators={
            "PERSON": OperatorConfig("replace", {"new_value": "REDACTED_NAME"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "REDACTED_EMAIL"})
        }
    )
    print(f"Anonymizer with replace: {result.text}")
except Exception as e:
    print(f"Error with replace: {e}")

# Try with faker if available
try:
    from faker import Faker
    faker = Faker()
    faker.seed_instance("test")

    print(f"\nFaker is available!")
    print(f"Fake name: {faker.name()}")
    print(f"Fake email: {faker.email()}")

    # Check if presidio has faker operator
    result = anonymizer.anonymize(
        text=test_text,
        analyzer_results=test_results,
        operators={
            "PERSON": OperatorConfig("custom", {"lambda": lambda x: faker.name()}),
            "EMAIL_ADDRESS": OperatorConfig("custom", {"lambda": lambda x: faker.email()})
        }
    )
    print(f"Anonymizer with faker: {result.text}")
except Exception as e:
    print(f"Error with faker: {e}")