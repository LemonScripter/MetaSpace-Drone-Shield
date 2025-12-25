# GitHub Pages Setup - Use `master` Branch

## Objective

Keep the existing `main` branch content intact, but configure GitHub Pages to use the `master` branch for the live site.

## Current Status

✅ **`main` branch:** Preserved (contains old content)  
✅ **`master` branch:** Contains new TRL-4 content with updated `index.html`  
✅ **No data loss:** Both branches are safe

## Steps to Configure GitHub Pages

### 1. Go to GitHub Repository Settings

Visit: https://github.com/LemonScripter/MetaSpace-Drone-Shield/settings/pages

### 2. Configure Source Branch

1. Under **"Source"** section:
   - Select: **`master`** (instead of `main`)
   - Select folder: **`/ (root)`**
   
2. Click **"Save"**

### 3. Wait for Deployment

- GitHub Pages will rebuild the site (usually takes 1-2 minutes)
- You'll see a notification when it's ready

### 4. Verify

Check the site: https://lemonscripter.github.io/MetaSpace-Drone-Shield/

The updated `index.html` from the `master` branch should now be live.

## What This Does

- ✅ **`main` branch:** Remains unchanged (old content preserved)
- ✅ **`master` branch:** Used for GitHub Pages (new TRL-4 content)
- ✅ **No force push needed:** Just change the GitHub Pages settings

## Alternative: Set `master` as Default Branch (Optional)

If you want `master` to be the default branch:

1. Go to: https://github.com/LemonScripter/MetaSpace-Drone-Shield/settings/branches
2. Under **"Default branch"**, click the switch icon
3. Select **`master`**
4. Click **"Update"**
5. Confirm the change

**Note:** This is optional. GitHub Pages can use `master` even if `main` is the default branch.

---

**Created:** 2025-12-25  
**Status:** Ready to configure (manual step required)

