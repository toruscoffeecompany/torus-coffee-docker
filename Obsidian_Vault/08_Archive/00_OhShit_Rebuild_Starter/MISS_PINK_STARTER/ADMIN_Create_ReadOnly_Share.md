# Q1-A — Create Read-Only Vault Share (RUN AS ADMIN on SQUIDSTATION)

> Miss Pink proved the `\\SQUIDSTATION\Users` share is WRITABLE from PINKCADY — an OPSEC hole.
> This creates a DEDICATED read-only share for just the vault path, so PINKCADY can read
> the fleet source-of-truth but never write/edit it. OS-enforced, not policy-only.

## Run this in an ADMIN PowerShell / CMD on SQUIDSTATION (this PC):
```powershell
# 1. Create the share, read-only for Everyone (PINKCADY mounts anonymously/LAN user)
New-SmbShare -Name "VOIDVaultRead" `
  -Path "C:\Users\kidsm\Documents\My Docs\VOID Pirate Trading Co\Obsidian_Vault\Developer_Brain" `
  -ReadAccess "Everyone" `
  -Description "Read-only fleet vault for PINKCADY"

# 2. Harden the NTFS ACL so even with the share, writes are denied to non-owner
$acl = Get-Acl "C:\Users\kidsm\Documents\My Docs\VOID Pirate Trading Co\Obsidian_Vault\Developer_Brain"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone","Write,Modify,FullControl","ContainerInherit,ObjectInherit","None","Deny")
$acl.AddAccessRule($rule)
Set-Acl "C:\Users\kidsm\Documents\My Docs\VOID Pirate Trading Co\Obsidian_Vault\Developer_Brain" $acl
```

## Verify (from PINKCADY):
```powershell
# read should work:
dir "\\SQUIDSTATION\VOIDVaultRead\CORE_RULES.md"
# write should FAIL:
echo test > "\\SQUIDSTATION\VOIDVaultRead\_write_probe.txt"
#  -> Access is denied  (good — OPSEC enforced by OS)
```

## Notes
- The old `\\SQUIDSTATION\Users` share is left as-is (your personal share); PINKCADY should
  switch to `\\SQUIDSTATION\VOIDVaultRead` for vault reads per her build template.
- If you prefer to restrict the existing `Users` share instead, use `Set-SmbShare -Name Users -ReadAccess ...`
  but a dedicated RO share has smaller blast radius. Captain chose A (dedicated).
