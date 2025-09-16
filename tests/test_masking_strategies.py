#!/usr/bin/env python3
"""
Tests for PII masking strategies
"""

import unittest
import json
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docling.document_converter import DocumentConverter
from cloakpivot import CloakEngine
from cloakpivot.core.policies import MaskingPolicy
from cloakpivot.core.strategies import Strategy, StrategyKind


class TestMaskingStrategies(unittest.TestCase):
    """Test different PII masking strategies"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests"""
        # Convert test PDF once
        pdf_path = Path("data/pdf/email.pdf")
        if not pdf_path.exists():
            raise FileNotFoundError(f"Test PDF not found: {pdf_path}")

        converter = DocumentConverter()
        result = converter.convert(str(pdf_path))
        cls.docling_doc = result.document

    def test_redact_strategy(self):
        """Test that redact strategy uses static placeholders"""
        # Configure redact policy
        policy = MaskingPolicy(
            default_strategy=Strategy(
                kind=StrategyKind.TEMPLATE,
                parameters={"template": "[REDACTED]"}
            )
        )
        policy = policy.with_entity_strategy("EMAIL_ADDRESS",
            Strategy(kind=StrategyKind.TEMPLATE, parameters={"template": "[EMAIL]"}))
        policy = policy.with_entity_strategy("PERSON",
            Strategy(kind=StrategyKind.TEMPLATE, parameters={"template": "[NAME]"}))
        policy = policy.with_entity_strategy("DATE_TIME",
            Strategy(kind=StrategyKind.TEMPLATE, parameters={"template": "[DATE]"}))

        # Apply masking
        cloak_engine = CloakEngine(default_policy=policy)
        result = cloak_engine.mask_document(self.docling_doc)

        # Verify masking occurred
        self.assertGreater(result.entities_found, 0)
        self.assertEqual(result.entities_found, result.entities_masked)

        # Check that masked document contains expected placeholders
        if result.document and hasattr(result.document, 'texts'):
            masked_text = ' '.join([t.text for t in result.document.texts if hasattr(t, 'text')])
            self.assertIn('[NAME]', masked_text)
            self.assertIn('[EMAIL]', masked_text)
            self.assertIn('[DATE]', masked_text)

        # Verify cloakmap contains template strategy
        if result.cloakmap:
            cloakmap_dict = result.cloakmap.to_dict()
            self.assertIn('anchors', cloakmap_dict)
            if cloakmap_dict['anchors']:
                first_anchor = cloakmap_dict['anchors'][0]
                self.assertEqual(first_anchor.get('strategy_used'), 'template')

    def test_replace_strategy(self):
        """Test that replace strategy uses surrogate/asterisk masking"""
        # Configure replace policy
        policy = MaskingPolicy(
            default_strategy=Strategy(
                kind=StrategyKind.SURROGATE,
                parameters={}
            ),
            seed="test-seed"
        )

        # Apply masking
        cloak_engine = CloakEngine(default_policy=policy)
        result = cloak_engine.mask_document(self.docling_doc)

        # Verify masking occurred
        self.assertGreater(result.entities_found, 0)
        self.assertEqual(result.entities_found, result.entities_masked)

        # Check that masked document contains asterisks
        if result.document and hasattr(result.document, 'texts'):
            masked_text = ' '.join([t.text for t in result.document.texts if hasattr(t, 'text')])
            self.assertIn('*', masked_text)
            # Should not contain template placeholders
            self.assertNotIn('[NAME]', masked_text)
            self.assertNotIn('[EMAIL]', masked_text)

        # Verify cloakmap contains surrogate strategy
        if result.cloakmap:
            cloakmap_dict = result.cloakmap.to_dict()
            self.assertIn('anchors', cloakmap_dict)
            if cloakmap_dict['anchors']:
                first_anchor = cloakmap_dict['anchors'][0]
                self.assertEqual(first_anchor.get('strategy_used'), 'surrogate')

    def test_consistent_entity_detection(self):
        """Test that both strategies detect the same entities"""
        # Redact strategy
        policy_redact = MaskingPolicy(
            default_strategy=Strategy(
                kind=StrategyKind.TEMPLATE,
                parameters={"template": "[REDACTED]"}
            )
        )
        cloak_redact = CloakEngine(default_policy=policy_redact)
        result_redact = cloak_redact.mask_document(self.docling_doc)

        # Replace strategy
        policy_replace = MaskingPolicy(
            default_strategy=Strategy(
                kind=StrategyKind.SURROGATE,
                parameters={}
            ),
            seed="test-seed"
        )
        cloak_replace = CloakEngine(default_policy=policy_replace)
        result_replace = cloak_replace.mask_document(self.docling_doc)

        # Both should detect the same number of entities
        self.assertEqual(result_redact.entities_found, result_replace.entities_found)
        self.assertEqual(result_redact.entities_masked, result_replace.entities_masked)

    def test_cloakmap_structure(self):
        """Test that cloakmap has expected structure"""
        policy = MaskingPolicy(
            default_strategy=Strategy(
                kind=StrategyKind.TEMPLATE,
                parameters={"template": "[REDACTED]"}
            )
        )
        cloak_engine = CloakEngine(default_policy=policy)
        result = cloak_engine.mask_document(self.docling_doc)

        self.assertIsNotNone(result.cloakmap)
        cloakmap_dict = result.cloakmap.to_dict()

        # Check required fields
        self.assertIn('version', cloakmap_dict)
        self.assertIn('anchors', cloakmap_dict)
        self.assertIn('policy_snapshot', cloakmap_dict)
        self.assertIn('created_at', cloakmap_dict)

        # Check anchor structure
        if cloakmap_dict['anchors']:
            anchor = cloakmap_dict['anchors'][0]
            required_fields = ['entity_type', 'masked_value', 'strategy_used', 'metadata']
            for field in required_fields:
                self.assertIn(field, anchor, f"Missing field: {field}")


if __name__ == '__main__':
    unittest.main()