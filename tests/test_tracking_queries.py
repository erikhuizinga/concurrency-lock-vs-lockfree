import importlib.util
import pathlib
import unittest


def load_tracking_module():
    module_path = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "tracking.py"
    spec = importlib.util.spec_from_file_location("tracking_module", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TrackingQueriesTests(unittest.TestCase):
    def test_queries_include_related_terminology_baseline(self):
        tracking = load_tracking_module()

        required_queries = {
            "lockfree",
            "lock free",
            "concurrency-lock-vs-lockfree",
            "erikhuizinga/concurrency-lock-vs-lockfree",
        }

        self.assertTrue(required_queries.issubset(set(tracking.QUERIES)))


if __name__ == "__main__":
    unittest.main()
