#!/bin/bash
# -----------------------------------------------------------------------------
# RUNBOOK:         Restart {{service_name}}
# GENERATED:       $(date)
# RUNBOOK ID:      {{runbook_id}}
# OPERATOR:        {{operator_name}}
# TARGET HOST:     {{hostname}}
#
# DESCRIPTION:
# This runbook performs a controlled restart of the {{service_name}} service
# on the host {{hostname}}. It includes pre-checks to verify the service's
# current state and post-checks to ensure it restarted successfully.
#
# IMPACT:
# A brief service interruption for {{service_name}} is expected during the
# restart. This could affect dependent services or user traffic.
# -----------------------------------------------------------------------------

# --- SAFETY SETTINGS ---
# -e: exit immediately if a command exits with a non-zero status.
# -u: treat unset variables as an error when substituting.
# -o pipefail: the return value of a pipeline is the status of the last
#              command to exit with a non-zero status.
set -euo pipefail

# --- HELPER FUNCTIONS ---
# A function to prompt for user confirmation before proceeding.
function confirm() {
    # call with a prompt string
    echo -e "\n" # add a newline for readability
    read -r -p "$1 [y/N]: " response
    case "$response" in
        [yY][eE][sS]|[yY])
            # User confirmed, continue.
            echo "Proceeding..."
            ;;
        *)
            # User aborted, exit the script.
            echo "Aborting operation."
            exit 1
            ;;
    esac
}

# --- SCRIPT START ---
echo "### Starting Runbook: Restart {{service_name}} on {{hostname}} ###"
echo "Runbook ID: {{runbook_id}}"
echo "Operator: {{operator_name}}"

# --- STEP 1: PRE-CHECKS ---
echo -e "\n--- [Step 1/3] Running Pre-checks ---"
echo "This step checks the current status of the service before we make any changes."

confirm "Shall we check the status of {{service_name}} via SSH on {{hostname}}?"
ssh {{user}}@{{hostname}} "systemctl status {{service_name}} --no-pager" || echo "Warning: Service might not be running or an error occurred. Continuing."


# --- STEP 2: PERFORM ACTION ---
echo -e "\n--- [Step 2/3] Restarting Service ---"
echo "This step will execute the 'systemctl restart' command for {{service_name}} using sudo."
echo "This is the primary action of this runbook and will cause a service interruption."

confirm "Are you absolutely sure you want to restart {{service_name}} on {{hostname}}?"
ssh {{user}}@{{hostname}} "sudo systemctl restart {{service_name}}"
echo "Restart command sent."


# --- STEP 3: POST-CHECKS / VERIFICATION ---
echo -e "\n--- [Step 3/3] Verifying Service Status ---"
echo "This step verifies that the service came back online successfully after the restart."

confirm "Shall we check the final status of {{service_name}} to confirm it's active?"
ssh {{user}}@{{hostname}} "systemctl is-active {{service_name}}"

echo -e "\nChecking full status and recent logs..."
ssh {{user}}@{{hostname}} "systemctl status {{service_name}} --no-pager"
ssh {{user}}@{{hostname}} "journalctl -u {{service_name}} -n 20 --no-pager"


# --- RUNBOOK END ---
echo -e "\n### Runbook Finished Successfully ###"
echo "Operation complete. Please monitor dashboards and alerts for any anomalies."