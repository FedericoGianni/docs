# Update

> It was just a patch update, what could possibly go wrong?

This document summarizes the update approach for devices and services across the infrastructure.

---

## Network Devices Updates

| Device | Update Method | Type | Schedule | Notes |
| :--- | :--- | :--- | :--- | :--- |
| {{ hw.brand_router }} Router | Built-in System | Automatic | Regular automatic | Via router firmware updates |
| {{ hw.brand_gateway }} | Built-in System | Automatic | Regular automatic | Official firmware updates |


## NAS Updates

| Device | Update Method | Type | Schedule | Notes |
| :--- | :--- | :--- | :--- | :--- |
| {{ hw.brand_nas }} | Built-in System | Automatic | Weekly | Official {{ hw.brand_nas }} firmware channel |


## Proxmox Hosts Updates

| Device | Update Method | Type | Schedule | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Proxmox Nodes Security Upgrades | Unattended Upgrades | Automatic | Daily | |
| Proxmox Nodes Core Upgrades | Manual | Manual | On-demand | |

## LXC Containers Updates

| Service | Update Method | Type | Schedule | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Proxmox LXC | Cron | Automatic | Daily | Via [script](https://community-scripts.org/scripts/update-lxcs) set up on every pve host |

## Virtual Machines Updates

| Service | Update Method | Type | Schedule | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Proxmox VMs | Unattended Upgrades | Automatic | Daily | Via OS package managers |

## Kubernetes Updates
| Service | Update Method | Type | Schedule | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Kubernetes | [Automated upgrades](https://docs.k3s.io/upgrades/automated) | Automatic | Rolling updates | Configured in [ArgoCD](4-iac.md) |
| Applications | [Renovate](https://docs.renovatebot.com/) | Semi-automatic (opens MR) | Rolling updates | Configured as K8S job |

