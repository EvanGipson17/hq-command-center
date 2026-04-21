# context.ps1 — defines the `context` PowerShell function.
#
# Source this file from your PowerShell $PROFILE so `context "your note"` works
# from any terminal. The helper appends a dated entry to EVAN_BUSINESS_CONTEXT.md
# and commits + pushes to GitHub via update_context.py.
#
# To install:
#     . C:\Users\wwgip\hq-command-center\context.ps1
#
# Or add that line permanently to your profile:
#     notepad $PROFILE
#     # paste:   . C:\Users\wwgip\hq-command-center\context.ps1

function context {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
        [string[]]$Note
    )
    $joined = ($Note -join ' ').Trim()
    if ([string]::IsNullOrWhiteSpace($joined)) {
        Write-Error 'usage: context "your note"'
        return
    }
    & python 'C:\Users\wwgip\hq-command-center\update_context.py' $joined
}
