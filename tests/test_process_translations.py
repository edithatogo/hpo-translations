import os
import time
import unittest
from unittest.mock import patch

from scripts.process_translations import validate_all, validation_worker_count


class ProcessTranslationsTests(unittest.TestCase):
    def test_worker_count_defaults_to_one(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(validation_worker_count(), 1)

    def test_worker_count_rejects_unsafe_values(self) -> None:
        for value in ("0", "5", "not-an-integer"):
            with (
                self.subTest(value=value),
                patch.dict(os.environ, {"HPO_VALIDATION_JOBS": value}, clear=True),
                self.assertRaises(ValueError),
            ):
                validation_worker_count()

    def test_parallel_validation_runs_every_language(self) -> None:
        completed: list[str] = []

        def record(language: str) -> None:
            time.sleep(0.01)
            completed.append(language)

        with patch("scripts.process_translations.validate_translation", side_effect=record):
            validate_all(["ja", "es", "fr"], 3)
        self.assertCountEqual(completed, ["es", "fr", "ja"])

    def test_parallel_validation_reports_failures_deterministically(self) -> None:
        def fail(language: str) -> None:
            if language in {"fr", "ja"}:
                raise RuntimeError(f"failed-{language}")

        with (
            patch("scripts.process_translations.validate_translation", side_effect=fail),
            self.assertRaisesRegex(
                RuntimeError,
                "fr: failed-fr\\nja: failed-ja",
            ),
        ):
            validate_all(["ja", "es", "fr"], 3)


if __name__ == "__main__":
    unittest.main()
