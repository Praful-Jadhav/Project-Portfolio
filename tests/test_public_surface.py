import unittest
from scripts.verify_public_surface import validate_packet, check_site

PACKET = """# Portfolio Evidence Packet

Task ID: PORT-ZTG-001
Status: IN_PROGRESS
Accountable owner: Portfolio maintainer
Risk tier: R1

## Claim and risk
Add static integrity and evidence checks to the public portfolio.

## Scope and acceptance criteria
Validate page structure, page title, main landmark, local stylesheet, internal anchor targets and material content packet.

## Verification plan and results
CI runs these test cases and executes the static page checker against the exact revision.

## Validation plan and results
The intended result is a structurally valid public page. A human must still open the rendered page and verify readability, responsive layout, accessibility and public claims.

## Public safety and privacy
No private client data, personal secrets or unsupported testimonials are published.

## Limitations and open items
Static checks do not verify external URLs or establish whether capability claims are true.

## Recovery and rollback
Revert the gate or page change if it blocks valid HTML or misses a verified local-navigation defect.

## Evidence and tested revision
The exact candidate SHA and workflow output are read back after CI. No acceptance is claimed here.
"""

class PortfolioIntegrityTests(unittest.TestCase):
 def test_current_public_page_is_structurally_valid(self):
  self.assertEqual(check_site(),[])
 def test_packet_passes_in_progress(self):
  self.assertEqual(validate_packet(PACKET),[])
 def test_missing_section_fails(self):
  text=PACKET.replace("## Public safety and privacy\nNo private client data, personal secrets or unsupported testimonials are published.\n","")
  self.assertTrue(any("missing section" in e for e in validate_packet(text)))
 def test_accepted_without_readback_fails(self):
  text=PACKET.replace("Status: IN_PROGRESS","Status: ACCEPTED")
  self.assertTrue(any("Independent read-back: PASS" in e for e in validate_packet(text)))
if __name__=="__main__": unittest.main()
