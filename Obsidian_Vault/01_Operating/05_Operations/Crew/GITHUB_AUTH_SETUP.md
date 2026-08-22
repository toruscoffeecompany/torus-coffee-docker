# PINKCADY GitHub Auth Setup for toruscoffeecompany Repos

Goal: enable Git operations from PINKCADY without password prompts.

Options:
1. SSH key: add PINKCADY public key to toruscoffeecompany GitHub account
2. PAT: store in Windows Credential Manager or `~/.git-credentials`
3. Git Credential Manager Core: use OAuth flow

Recommended free path:
- Use Git Credential Manager Core (`gcm`)
- Run `gh auth login` on PINKCADY for GitHub CLI access

Next actions:
1. Generate or reuse existing SSH key on PINKCADY
2. Add to GitHub account under toruscoffeecompany
3. Test `git clone git@github.com:toruscoffeecompany/Torus_Ops.git`
