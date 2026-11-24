<#
.SYNOPSIS
  Applies the "Protect main" repository ruleset to Akus0ni/reglens-agent (public repo, so GitHub Free is enough).

.DESCRIPTION
  - Changes to the default branch must go through a pull request approved by a code owner (.github/CODEOWNERS).
  - Direct pushes, force-pushes and branch deletion are blocked for everyone.
  - The `evals` status check (GitHub Actions) must pass (spec 0002).
  - The Repository admin role (the owner) may bypass the approval rule only when merging a pull request
    (bypass_mode = pull_request), never for a direct push.
  Safe to re-run: updates the ruleset if it already exists.
#>
param(
    [string]$Repo = "Akus0ni/reglens-agent",
    [string]$RulesetName = "Protect main"
)

$ErrorActionPreference = "Stop"

$ruleset = @{
    name         = $RulesetName
    target       = "branch"
    enforcement  = "active"
    conditions   = @{ ref_name = @{ include = @("~DEFAULT_BRANCH"); exclude = @() } }
    rules        = @(
        @{ type = "deletion" },
        @{ type = "non_fast_forward" },
        # Spec 0002, R2.12: the evals job (.github/workflows/evals.yml) must pass before merging.
        @{
            type       = "required_status_checks"
            parameters = @{
                required_status_checks               = @(@{ context = "evals" })
                strict_required_status_checks_policy = $false
            }
        },
        @{
            type       = "pull_request"
            parameters = @{
                required_approving_review_count   = 1
                require_code_owner_review         = $true
                dismiss_stale_reviews_on_push     = $true
                require_last_push_approval        = $false
                required_review_thread_resolution = $false
            }
        }
    )
    # actor_id 5 = built-in "Repository admin" role; bypass only through a pull request
    bypass_actors = @(@{ actor_id = 5; actor_type = "RepositoryRole"; bypass_mode = "pull_request" })
}

$payload = New-TemporaryFile
try {
    $ruleset | ConvertTo-Json -Depth 10 | Out-File -FilePath $payload -Encoding ascii

    $existing = gh api "repos/$Repo/rulesets" | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) { throw "Could not list rulesets for $Repo." }
    $existingId = ($existing | Where-Object { $_.name -eq $RulesetName } | Select-Object -First 1).id

    if ($existingId) {
        gh api --method PUT "repos/$Repo/rulesets/$existingId" --input $payload | Out-Null
        $action = "Updated"
    }
    else {
        gh api --method POST "repos/$Repo/rulesets" --input $payload | Out-Null
        $action = "Created"
    }
    if ($LASTEXITCODE -ne 0) { throw "GitHub rejected the ruleset." }
    Write-Host "$action ruleset '$RulesetName' on $Repo."
}
finally {
    Remove-Item $payload -ErrorAction SilentlyContinue
}
