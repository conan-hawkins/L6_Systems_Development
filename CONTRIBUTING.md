# Contributing

## Branches

| Branch      | Purpose                                          | Deployed to |
|-------------|--------------------------------------------------|-------------|
| `main`      | Production. Always releasable.                   | Production  |
| `staging`   | Release candidates under test.                   | Staging     |
| `dev`       | Integration branch. Default target for work.     | —           |
| `feature/*` | New features, branched from `dev`.               | —           |
| `fix/*`     | Bug fixes, branched from `dev`.                  | —           |
| `docs/*`    | Documentation-only changes, branched from `dev`. | —           |
| `hotfix/*`  | Urgent production fixes, branched from `main`.   | —           |

`main`, `staging` and `dev` are protected by repository rulesets: direct pushes,
force pushes and deletion are blocked. Every change arrives through a pull request.

## Issues and branch names

Every change starts with a [GitHub Issue](https://docs.github.com/en/issues) describing
what is needed and why. GitHub numbers issues automatically (`#1`, `#2`, ...).

Name the branch `<type>/<issue number>-<short-description>`, in lowercase with hyphens:

```
feature/3-add-ci
docs/4-contributing-prs
fix/7-login-redirect
hotfix/9-session-timeout
```

The type comes first so it matches the branch patterns above. Do not invent your own
numbering; always use the issue number.

In the pull request description, link the issue with a closing keyword:

```
Closes #3
```

GitHub then links the pull request to the issue and closes the issue when the pull
request is merged. See
[Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue).

## Workflow

```
feature/* --squash PR--> dev --merge PR--> staging --merge PR--> main
```

| Pull request         | Merge method on GitHub    | Why                                    |
|----------------------|---------------------------|----------------------------------------|
| `feature/*` → `dev`  | **Squash and merge**      | One clean commit per feature on `dev`. |
| `dev` → `staging`    | **Create a merge commit** | Keeps `staging` in step with `dev`.    |
| `staging` → `main`   | **Create a merge commit** | Keeps `main` in step with `staging`.   |

The rulesets only allow the method listed for each branch.

### 1. Start a branch

```bash
git switch dev
git pull
git switch -c feature/<issue>-short-description
```

Create the issue first, then use its number in the branch name, e.g. `feature/3-add-ci`
(see [Issues and branch names](#issues-and-branch-names)).

### 2. Work and commit

Commit as often as you like; the commits are squashed when the pull request is merged.
Run the tests before pushing:

```bash
pytest
```

If `dev` has moved on, bring your branch up to date:

```bash
git fetch
git rebase origin/dev
git push --force-with-lease   # only ever on your own feature branch
```

### 3. Open a pull request into `dev`

```bash
git push -u origin feature/<issue>-short-description
```

Open the pull request on GitHub (the link is printed by `git push`). The base is `dev` by default.

- **Title**: becomes the squashed commit's subject, so write it as a Conventional Commit,
  e.g. `feat: add conversation search`.
- **Description**: becomes the commit body. Say what changed and why, and end with
  `Closes #<issue>`.
- Wait for the CI checks to pass, then click **Squash and merge**.
  The branch is deleted on GitHub automatically.

Then update your local copy:

```bash
git switch dev
git pull
git branch -D feature/<issue>-short-description
```

### 4. Promote `dev` to `staging`

On GitHub, open a pull request with base `staging` and compare `dev`.
Title it e.g. `release: v0.2.0 to staging`. Once CI passes, click **Create a merge commit**.

Deploy `staging` and test it.

### 5. Release `staging` to `main`

Open a pull request with base `main` and compare `staging`. Once CI passes, click
**Create a merge commit**. Then tag the release:

```bash
git switch main
git pull
git tag -a v0.2.0 -m "v0.2.0"
git push origin v0.2.0
```

Versions follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

### Hotfixes

1. Branch from `main`: `git switch main && git pull && git switch -c hotfix/<issue>-short-description`
2. Fix, commit, test, push.
3. Open a pull request into `main` and click **Create a merge commit**. Tag a patch release.
4. Open a second pull request from `main` into `dev` (and `staging` if a release is in
   progress) so the fix isn't lost.

## Continuous integration

`.github/workflows/ci.yml` runs the test suite on pull requests into `dev`, `staging`
and `main`. A pull request cannot be merged while a required check is failing.

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

When squash merging on GitHub, add the trailer to the end of the commit message in the
merge dialog if any commit on the branch had one.
