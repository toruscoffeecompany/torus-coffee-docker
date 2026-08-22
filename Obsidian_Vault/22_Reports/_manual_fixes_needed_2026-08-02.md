# Manual Fixes Required

## 1. Move 11_Torus_Ops Outside Vault (REQUIRES ADMIN/Reboot)

**Problem:** `11_Torus_Ops` is a stale vault clone inside the main vault. It has its own `.git`, duplicate folders, and 3 VOID references.

**Fix:**
1. Close Obsidian completely
2. Open File Explorer as Administrator
3. Move `D:\Work\Torus Coffee Company LLC\11_Torus_Ops` to `D:\Work\Torus_Ops_Mirror`
4. Update the git remote in the new location:
   ```
   cd D:\Work\Torus_Ops_Mirror
   git remote set-url origin https://<PAT>@github.com/toruscoffeecompany/Torus_Ops.git
   ```
5. Delete the empty `11_Torus_Ops` folder from the vault

**Alternative:** Reboot pinkcady, then immediately move the folder before Obsidian starts.

## 2. Delete Empty obsidian-periodic-notes/ Folder (REQUIRES REBOOT)

**Problem:** Empty folder locked by Windows Search Indexer.

**Fix:** Reboot pinkcady, then delete:
```
D:\Work\Torus Coffee Company LLC\.obsidian\plugins\obsidian-periodic-notes\
```

## 3. Configure Templater Template Folder (DONE)

✓ Fixed: `.obsidian/plugins/Templater/data.json` created with `templates_folder: "00_Inbox/07_Templates"`

## 4. Import QuickAdd Macros (DONE)

✓ Fixed: `quickadd_macros.json` copied to `.obsidian/plugins/QuickAdd/data.json`

## 5. Add .gitignore to 11_Torus_Ops (After Move)

After moving `11_Torus_Ops` outside the vault, add a `.gitignore` to prevent binary bloat:
```
.obsidian/
node_modules/
*.zip
*.pdf
*.png
*.jpg
*.xlsx
*.docx
```
