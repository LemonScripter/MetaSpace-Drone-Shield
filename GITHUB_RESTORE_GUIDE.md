# GitHub Restore Guide

## Current Situation

**Local Repository:** Just initialized (commit `582065a`)  
**GitHub Repository:** `https://github.com/LemonScripter/MetaSpace-Drone-Shield` (if exists)

## Step 1: Check What's Currently on GitHub

Before pushing, we need to save the current GitHub state (if it exists):

```bash
# 1. Add remote (if not already added)
git remote add origin https://github.com/LemonScripter/MetaSpace-Drone-Shield.git

# 2. Fetch current state from GitHub
git fetch origin

# 3. Check what's on GitHub
git log origin/main --oneline -10
# OR
git log origin/master --oneline -10

# 4. Create a tag for the current GitHub state
git tag -a github-before-update-2025-12-25 origin/main
# OR
git tag -a github-before-update-2025-12-25 origin/master
```

## Step 2: Save Current GitHub State

If there's content on GitHub that you want to preserve:

```bash
# Create a backup branch from GitHub's current state
git checkout -b backup-github-state-2025-12-25 origin/main
# OR
git checkout -b backup-github-state-2025-12-25 origin/master

# Switch back to master
git checkout master

# Now you have:
# - master: Your new changes (local)
# - backup-github-state-2025-12-25: GitHub's current state (backup)
```

## Step 3: Push New Changes

After saving the GitHub state, you can safely push:

```bash
# Push your new changes
git push origin master

# Push tags too
git push origin --tags
```

## Step 4: How to Restore GitHub's Previous State

If you need to restore what was on GitHub before your push:

### Option 1: Reset Remote to Previous State
```bash
# Find the commit hash from GitHub's previous state
git log backup-github-state-2025-12-25 --oneline -1

# Reset remote to that commit (WARNING: This rewrites history)
git push origin +backup-github-state-2025-12-25:main
# OR
git push origin +backup-github-state-2025-12-25:master
```

### Option 2: Create a New Branch from Backup
```bash
# Create a branch from the backup
git checkout -b restore-github-state backup-github-state-2025-12-25

# Push this branch
git push origin restore-github-state
```

### Option 3: Revert Specific Commits
```bash
# If you want to undo specific commits
git revert <commit-hash>
git push origin master
```

## Important Notes

⚠️ **Before Pushing:**
1. ✅ Always fetch and backup GitHub's current state first
2. ✅ Create a tag or branch for the GitHub state
3. ✅ Test your changes locally
4. ✅ Review what will be pushed: `git diff origin/main..master`

✅ **After Pushing:**
- The backup branch `backup-github-state-2025-12-25` contains GitHub's previous state
- You can always restore from this branch
- The tag `github-before-update-2025-12-25` marks the GitHub state

## Quick Commands Summary

```bash
# 1. Save GitHub state
git fetch origin
git checkout -b backup-github-state-2025-12-25 origin/main
git checkout master

# 2. Push new changes
git push origin master

# 3. Restore GitHub state (if needed)
git push origin +backup-github-state-2025-12-25:main
```

---

**Created:** 2025-12-25  
**Purpose:** Guide for safely pushing updates while preserving ability to restore GitHub's previous state

