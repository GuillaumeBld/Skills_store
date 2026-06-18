---
name: power-automate-mcp-preflight
description: Use when setting up powerautomate-mcp (or any Entra-app-based Power Automate / Power Platform MCP server) against a Microsoft 365 tenant, or when az login keeps returning "Please run az login" on a tenant with no Azure subscription. Determines, before building anything, whether the agent-driven MCP route is viable or whether you must fall back to native connectors.
---

# Power Automate MCP Pre-flight

## Overview
Before investing time wiring an AI/MCP server (e.g. `powerautomate-mcp`) to drive Power Automate, run a 2-minute `az` pre-flight to get a **go/no-go**. The MCP needs its own Entra app registration with **admin-consent-required** delegated scopes (`Files.ReadWrite.All`, `Sites.ReadWrite.All`, `Flows.Manage.All`). A regular user being *able to create an app* does **not** mean they can *consent* to those scopes — that is a separate tenant policy and the usual silent dead-end.

## The two gotchas a fresh agent misses
1. **`az login --allow-no-subscriptions`.** On a tenant with no Azure *subscription* (common for universities / M365-only orgs), a plain `az login` succeeds in the browser but does **not** persist the session — every later `az` call returns `Please run 'az login' to setup account`. The flag persists tenant-level access. Use it.
2. **Create-app ≠ consent.** `allowedToCreateApps: true` is necessary but not sufficient. Check the consent policy too.

## Pre-flight (run in order)
```bash
# 1. Authenticate (the flag is the fix for "no subscriptions")
az login --allow-no-subscriptions

# 2. Can this user register an app at all?
az rest --method GET --url "https://graph.microsoft.com/v1.0/policies/authorizationPolicy" \
  --query "defaultUserRolePermissions.allowedToCreateApps" -o tsv

# 3. What can this user CONSENT to?  (the real gate)
az rest --method GET --url "https://graph.microsoft.com/v1.0/policies/authorizationPolicy" \
  --query "defaultUserRolePermissions.permissionGrantPoliciesAssigned" -o json

# 4. Is there a Power Platform environment to manage?
az rest --method GET \
  --url "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/environments?api-version=2020-06-01" \
  --resource "https://service.powerapps.com/" \
  --query "value[].properties.displayName" -o tsv
```

## Verdict
| Result | Meaning |
|---|---|
| `allowedToCreateApps: false` | Can't register the app. MCP route dead unless an admin registers it. |
| `allowedToCreateApps: true` **+** consent policies are only `*-recommended` / low-impact | You can create the app but **cannot consent** to `Files/Sites/Flows.*`. A tenant admin must grant admin consent. Non-admin → **MCP blocked**. |
| No environment returned | Nothing for the MCP to manage — user likely lacks a Power Automate license. |
| Create-apps true **and** consent policy includes a matching grant for the scopes | MCP route is viable. Proceed with `powerautomate-mcp --setup`. |

## When MCP is blocked: the fallback needs zero admin
Build the flow in the Power Automate web designer with **first-party connectors** (Office 365 Outlook, Excel Online Business). These are pre-consented org-wide and need **no app registration and no admin consent** — only a Power Automate license. Author/test in a tenant you control, then **export as a Solution `.zip`** and import into the target tenant, re-mapping connections. The MCP never bypasses Microsoft's permission model; the manual route sidesteps it entirely.

## Common mistakes
- Running `powerautomate-mcp --setup` before the pre-flight, then hitting the consent wall after creating an orphan app.
- Reading `allowedToCreateApps: true` as "the MCP will work." It won't, for a non-admin, without admin consent.
- Plain `az login` on a no-subscription tenant, then chasing the recurring "Please run az login" error.
