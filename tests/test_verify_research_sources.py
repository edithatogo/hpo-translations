import hashlib
import io
import unittest

from scripts.validate_research_validation import load_json
from scripts.verify_research_sources import DEFAULT_CATALOG, catalog_pins, hash_stream


class VerifyResearchSourcesTests(unittest.TestCase):
    def test_catalog_exposes_all_pinned_assets(self) -> None:
        pins = catalog_pins(load_json(DEFAULT_CATALOG))
        self.assertEqual(len(pins), 11)
        self.assertEqual(len({pin.source_id for pin in pins}), 11)
        self.assertTrue(all(pin.url.startswith("https://") for pin in pins))

    def test_hash_stream_counts_and_hashes_without_retention(self) -> None:
        content = b"payload-safe synthetic source"
        size, digest = hash_stream(io.BytesIO(content))
        self.assertEqual(size, len(content))
        self.assertEqual(digest, hashlib.sha256(content).hexdigest())


if __name__ == "__main__":
    unittest.main()
