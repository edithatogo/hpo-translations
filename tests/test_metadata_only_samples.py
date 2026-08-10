import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_metadata_only_samples import main, validate_track


class MetadataOnlySampleTests(unittest.TestCase):
    def test_approved_samples_are_payload_free(self) -> None:
        self.assertEqual(main(), 0)

    def test_incomplete_contract_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            track_dir = Path(temporary_directory)
            (track_dir / "maintainer_review_handoff.json").write_text(
                json.dumps({"status": "approved_bounded_metadata_only_sample"}),
                encoding="utf-8",
            )
            self.assertEqual(
                validate_track(track_dir),
                ["missing required Phase 2 artifact", "missing required Phase 4 artifact"],
            )


if __name__ == "__main__":
    unittest.main()
