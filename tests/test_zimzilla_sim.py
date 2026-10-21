"""Tests for the offline ZimZilla research simulator."""
import unittest

from hermes_mesh.zimzilla_sim import crystal_lane, fusion_lane, merge_findings, report


class ZimZillaSimulatorTests(unittest.TestCase):
    def test_both_independent_lanes_exist(self):
        self.assertEqual(len(crystal_lane()), 3)
        self.assertEqual(len(fusion_lane()), 3)
        self.assertEqual({f.lane for f in merge_findings(crystal_lane(), fusion_lane())},
                         {"CRYSTAL", "FUSION"})

    def test_report_is_deterministic_for_same_seed(self):
        self.assertEqual(report(1859), report(1859))
        self.assertNotEqual(report(1859)["seed"], report(1860)["seed"])

    def test_report_never_claims_proof(self):
        result = report()
        self.assertEqual(result["summary"]["proof_status"], "NOT_PROVED")
        self.assertEqual(result["summary"]["disproof_status"], "NOT_ESTABLISHED")
        self.assertTrue(result["evidence_policy"]["numerical_checks_are_not_proofs"])
        self.assertEqual(result["summary"]["findings"], 6)

    def test_duplicate_finding_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            merge_findings(crystal_lane(), crystal_lane())


if __name__ == "__main__":
    unittest.main()
