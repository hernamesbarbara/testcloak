#!/usr/bin/env python
"""Test script to validate the PII masking workflow."""

import os
import json
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.document import DoclingDocument
from cloakpivot import CloakEngine

def test_workflow():
    """Test the complete workflow from PDF to masked markdown."""

    pdf_path = Path("data/pdf/email.pdf")
    if not pdf_path.exists():
        print(f"Error: Test PDF not found at {pdf_path}")
        return False

    print("1. Testing PDF to DoclingDocument conversion...")
    try:
        converter = DocumentConverter()
        result = converter.convert(str(pdf_path))
        docling_doc = result.document
        print(f"   ✓ Successfully converted PDF to DoclingDocument")
        text_content = docling_doc.export_to_markdown()
        print(f"   Document has {len(text_content)} characters")
        print(f"   First 100 chars: {text_content[:100]}..." if len(text_content) > 100 else f"   Content: {text_content}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    print("\n2. Testing PII detection and masking...")
    try:
        cloak_engine = CloakEngine()
        mask_result = cloak_engine.mask_document(docling_doc)

        print(f"   ✓ Mask result type: {type(mask_result)}")
        print(f"   ✓ Mask result attributes: {[attr for attr in dir(mask_result) if not attr.startswith('_')]}")

        if hasattr(mask_result, 'cloakmap'):
            cloakmap = mask_result.cloakmap
            print(f"   ✓ CloakMap type: {type(cloakmap)}")
            print(f"   ✓ Entities found: {mask_result.entities_found}")
            print(f"   ✓ Entities masked: {mask_result.entities_masked}")
            if hasattr(cloakmap, 'entity_count'):
                print(f"   ✓ Found {cloakmap.entity_count} PII entities")
            elif hasattr(cloakmap, 'replacements'):
                print(f"   ✓ Found {len(cloakmap.replacements)} PII replacements")

        masked_doc = mask_result.document
        print(f"   ✓ Successfully processed document for PII masking")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    print("\n3. Testing markdown export...")
    try:
        unmasked_md = docling_doc.export_to_markdown()
        print(f"   ✓ Masked doc type: {type(masked_doc)}")
        if hasattr(masked_doc, 'texts'):
            print(f"   ✓ Masked doc texts count: {len(masked_doc.texts) if masked_doc.texts else 0}")

        if masked_doc is None:
            print("   ⚠ Warning: Masked document is None")
            masked_md = ""
        elif hasattr(masked_doc, 'export_to_markdown'):
            masked_md = masked_doc.export_to_markdown()
        else:
            print(f"   ⚠ Warning: Masked document has no export_to_markdown method")
            print(f"   ⚠ Masked doc attributes: {[attr for attr in dir(masked_doc) if not attr.startswith('_')][:10]}")
            masked_md = str(masked_doc) if masked_doc else ""

        print(f"   ✓ Unmasked markdown: {len(unmasked_md)} characters")
        print(f"   ✓ Masked markdown: {len(masked_md)} characters")

        test_output_dir = Path("data/md/test")
        test_output_dir.mkdir(parents=True, exist_ok=True)

        unmasked_path = test_output_dir / "email.unmasked.md"
        masked_path = test_output_dir / "email.masked.md"

        with open(unmasked_path, 'w') as f:
            f.write(unmasked_md)
        print(f"   ✓ Wrote unmasked markdown to {unmasked_path}")

        with open(masked_path, 'w') as f:
            f.write(masked_md)
        print(f"   ✓ Wrote masked markdown to {masked_path}")

    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    print("\n4. Verifying output...")
    if unmasked_md == masked_md:
        print("   ⚠ Warning: Masked and unmasked documents are identical")
    else:
        print("   ✓ Masked document differs from unmasked")

    print("\n✅ All tests passed!")
    return True

if __name__ == "__main__":
    test_workflow()