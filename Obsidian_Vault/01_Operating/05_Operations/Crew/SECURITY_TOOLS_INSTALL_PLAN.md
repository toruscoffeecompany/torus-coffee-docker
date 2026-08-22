# Security Tools Install Plan on PINKCADY

Free-tier tools to install on PINKCADY:
- nikto: web server scanner
- tshark: network packet capture/analysis
- yara: pattern-based malware/artifact scanning
- crowdsec: free IPS/WAF
- suricata: free NIDS (already present per inbox)

Next actions:
1. Install via `choco` or `winget` on Windows.
2. Verify each tool with `--version`.
3. Add scan results to vault under `10_Skills_Library/05_Operations/Security/`.
4. Update this card with completion evidence.

Blocker:
- Execution requires Sir Azure availability on PINKCADY.
