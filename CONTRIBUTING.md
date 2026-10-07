# Contributing

## Branches

| Branch      | Purpose                                         | Deployed to |
|-------------|-------------------------------------------------|-------------|
| `main`      | Production. Always releasable.                  | Production  |
| `staging`   | Release candidates under test.                  | Staging     |
| `dev`       | Integration branch. Default target for work.    | —           |
| `feature/*` | New features, branched from `dev`.              | —           |
| `fix/*`     | Bug fixes, branched from `dev`.                 | —           |
| `hotfix/*`  | Urgent production fixes, branched from `main`.  | —           |

Never commit directly to `main`, `staging` or `dev`. All changes arrive through a merge.

## Workflow

```
feature/* --squash--> dev --merge--> staging --merge--> main
```

### 1. Start a feature

```bash
git switch dev
git pull
git switch -c feature/short-description
```

Name branches in lowercase with hyphens, e.g. `feature/conversation-search`, `fix/login-redirect`.

### 2. Work and commit

Commit as often as you like on the feature branch; these commits are squashed later.
Keep the branch up to date with `dev`:

```bash
git fetch
git rebase origin/dev
```

### 3. Squash merge into `dev`

Run the tests first (`pytest`), then:

```bash
git switch dev
git pull
git merge --squash feature/short-description
git commit            # write one clear commit message for the whole feature
git push
git branch -D feature/short-description
```

On GitHub, open a pull request into `dev` and use **Squash and merge** instead.

### 4. Promote to `staging` for testing

```bash
git switch staging
git pull
git merge --no-ff dev
git push
```

### 5. Release to `main`

Once `staging` has been tested:

```bash
git switch main
git pull
git merge --no-ff staging
git tag -a v0.2.0 -m "v0.2.0"
git push --follow-tags
```

Versions follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

### Hotfixes

```bash
git switch main
git switch -c hotfix/short-description
# fix, commit, test
git switch main && git merge --no-ff hotfix/short-description
git switch dev && git merge --no-ff hotfix/short-description
git branch -d hotfix/short-description
```

Merge the hotfix back into `staging` too if a release is in progress.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short summary, imperative, no full stop>

<optional body explaining what and why>

<optional trailers>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`.

Examples:

```
feat: add conversation search to chat page
fix: redirect to login when session expires
docs: document MongoDB indexes
```

Credit AI assistance with a `Co-authored-by:` trailer on the last line:

```
Co-authored-by: Claude Opus 5.5 <noreply@anthropic.com>
```
