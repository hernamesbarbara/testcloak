#!/usr/bin/env python3
"""
Test script to verify faker integration with presidio
"""

# Test if we can use faker with presidio directly
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from faker import Faker
import hashlib

# Initialize faker with seed for consistency
faker = Faker()
faker.seed_instance("testcloak")

# Create consistent fake data based on original value
def generate_consistent_fake(original_text, entity_type):
    """Generate consistent fake data based on original text hash"""
    # Use hash of original to select consistent fake data
    hash_val = int(hashlib.md5(original_text.encode()).hexdigest()[:8], 16)
    faker.seed_instance(hash_val)

    if entity_type == "PERSON":
        return faker.name()
    elif entity_type == "EMAIL_ADDRESS":
        return faker.email()
    elif entity_type == "DATE_TIME":
        return faker.date()
    elif entity_type == "PHONE_NUMBER":
        return faker.phone_number()
    elif entity_type == "LOCATION":
        return faker.city()
    else:
        return f"[{entity_type}]"

# Test text
test_text = "John Doe's email is john@example.com and his friend Jane Smith is at jane@company.org"
print(f"Original: {test_text}")

# Analyze text
analyzer = AnalyzerEngine()
results = analyzer.analyze(text=test_text, language="en")

print("\nDetected entities:")
for result in results:
    entity_text = test_text[result.start:result.end]
    print(f"  {result.entity_type}: '{entity_text}' (confidence: {result.score})")

# Anonymize with custom faker operator
anonymizer = AnonymizerEngine()

# Create operators for each entity type
operators = {}
for result in results:
    entity_text = test_text[result.start:result.end]
    fake_value = generate_consistent_fake(entity_text, result.entity_type)
    operators[result.entity_type] = OperatorConfig("replace", {"new_value": fake_value})

# Apply anonymization
anonymized = anonymizer.anonymize(
    text=test_text,
    analyzer_results=results,
    operators=operators
)

print(f"\nAnonymized: {anonymized.text}")

# Test again with same input to verify consistency
operators2 = {}
for result in results:
    entity_text = test_text[result.start:result.end]
    fake_value = generate_consistent_fake(entity_text, result.entity_type)
    operators2[result.entity_type] = OperatorConfig("replace", {"new_value": fake_value})

anonymized2 = anonymizer.anonymize(
    text=test_text,
    analyzer_results=results,
    operators=operators2
)

print(f"Anonymized (2nd run): {anonymized2.text}")
print(f"Consistent: {anonymized.text == anonymized2.text}")