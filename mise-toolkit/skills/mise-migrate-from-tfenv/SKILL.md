---
name: mise-migrate-from-tfenv
description: Migrating from tfenv to mise — reading .terraform-version, translating tfenv-installed versions, handling the terraform vs tofu fork decision, and tearing down ~/.tfenv cleanly. Use when a user is currently using tfenv for Terraform version management.
---

# Migrating from tfenv to mise

`tfenv` is a shell-based Terraform version manager, modeled after rbenv/pyenv. mise replaces it with a version-pinned, aqua-backed terraform install that cross-integrates with every other tool you use. Migration is straightforward because `.terraform-version` has exactly one format (a bare version string).

## The terraform vs opentofu decision

Before migrating, decide which tool you actually want:

- **terraform** — HashiCorp's original, now under the BSL (Business Source License). Fine for most use; licensing forbids some SaaS reseller scenarios.
- **opentofu** — the Linux Foundation fork after the BSL change. Drop-in compatible with terraform 1.5.x and below, diverging in newer features.

mise supports both:

```toml
[tools]
terraform = "1.9.8"
# or
opentofu = "1.8.4"
```

Most users want terraform still. opentofu matters if you're in a regulated/legal situation where the BSL is a problem, or if you want to commit to the open-source fork.

For this guide we'll assume terraform. The migration is identical for opentofu — just swap the tool name.

## The migration plan

1. Inventory tfenv state.
2. Create `mise.toml` per project.
3. Swap shell rc.
4. Verify.
5. Uninstall tfenv.

## Step 1 — inventory

```sh
tfenv list                 # installed versions
tfenv version-name         # current
cat .terraform-version     # project pin
grep -r tfenv ~/.zshrc ~/.bashrc 2>/dev/null
```

## Step 2 — mise.toml

For a `.terraform-version` containing `1.9.8`:

```toml
# mise.toml
[tools]
terraform = "1.9.8"
```

Or enable the idiomatic reader and let `.terraform-version` work directly:

```toml
[settings]
idiomatic_version_file_enable_tools = ["terraform"]
```

### Global default

```toml
# ~/.config/mise/config.toml
[tools]
terraform = "1.9"
```

## Step 3 — swap shell rc

Remove tfenv:

```sh
# ~/.zshrc — DELETE
export PATH="$HOME/.tfenv/bin:$PATH"
```

Add mise:

```sh
eval "$(mise activate zsh)"
```

Restart shell.

## Step 4 — verify

```sh
which terraform
# should be under ~/.local/share/mise/

terraform --version
cd <project>
terraform --version   # matches .terraform-version
```

## Step 5 — uninstall tfenv

```sh
rm -rf ~/.tfenv
# If installed via Homebrew:
brew uninstall tfenv
```

Restart shell. Verify `which tfenv` → not found.

## Common multi-tool setups

Terraform is rarely used alone. Pair with:

```toml
[tools]
terraform = "1.9.8"
"aqua:terraform-linters/tflint" = "latest"
"aqua:terraform-docs/terraform-docs" = "latest"
"aqua:aquasecurity/tfsec" = "latest"
"aqua:gruntwork-io/terragrunt" = "latest"

[tasks.init]
run = "terraform init"
sources = ["*.tf", ".terraform.lock.hcl"]

[tasks.plan]
depends = ["init"]
run = "terraform plan -out=tfplan"

[tasks.apply]
run = "terraform apply tfplan"

[tasks.lint]
run = ["tflint", "tfsec ."]

[tasks.docs]
run = "terraform-docs markdown . > README.md"
```

All of these are aqua-backed — fast, pre-built, version-pinned.

## Common issues

### Wrong version after `cd` into project

Check that the idiomatic reader is enabled, or put `terraform = "<version>"` in the project's `mise.toml` explicitly.

### `terraform init` downloads providers to the wrong place

`terraform init` creates `.terraform/` in the project dir. This is terraform's behavior, not tfenv's or mise's. It's already gitignored by default in most terraform `.gitignore` templates.

### Provider plugin cache

If you were using `TF_PLUGIN_CACHE_DIR` with tfenv, the same env var still works:

```toml
[env]
TF_PLUGIN_CACHE_DIR = "{{env.HOME}}/.cache/terraform-plugin-cache"
```

Shared across projects; saves bandwidth and disk.

### Multiple terraform versions needed simultaneously

```toml
[tools]
terraform = "1.9 1.5"
```

Both installed. `terraform` resolves to 1.9; explicit `terraform_1.5.x` isn't a thing — use `mise exec terraform@1.5 -- terraform plan` for the non-default.

### Switching to opentofu

Replace `terraform =` with `opentofu =`. Update CI. Update state files if needed (for 1.6+ divergence). See opentofu migration docs for state compatibility.

## Rollback

Reinstall tfenv:

```sh
git clone https://github.com/tfutils/tfenv.git ~/.tfenv
```

Your `.terraform-version` files are untouched.

## See also

- `mise-lang-node-overview` — similar structure for Node (if you're also migrating from nvm).
- `mise-migrate-from-asdf` — general migration shape.
- `mise-backends-overview` — aqua vs github for terraform.
- opentofu migration: `opentofu.org/docs/intro/migration/`.
