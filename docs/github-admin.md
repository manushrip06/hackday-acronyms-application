# Branch protection (repo owner / Admin)

Collaborators with Write cannot enable protection. As the repo **owner**, run:

1. GitHub → Settings → Branches → Add rule for `main`
2. Enable **Require a pull request before merging**
3. Require **1** approving review
4. Optionally: dismiss stale reviews

Or via API (owner token):

```bash
gh api repos/manushrip06/hackday-acronyms-application/branches/main/protection \
  -X PUT -H "Accept: application/vnd.github+json" \
  --input - <<'EOF'
{
  "required_status_checks": null,
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1
  },
  "restrictions": null
}
EOF
```

## Collaborators

Settings → Collaborators → invite teammates with **Write**. Keep **Admin** for the owner.
