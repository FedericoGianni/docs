# Kubernetes

> Kubernetes shannenigans.

## Clusters

| Site | Distribution | Role |
| :--- | :--- | :--- |
| Main | RKE2 | Primary cluster |
| Remote | K3s | Secondary cluster |

## Core components

| Component | Role | Detail |
| :--- | :--- | :--- |
| Cilium | CNI | Native routing and kube-proxy replacement. |
| Traefik | Ingress | External and internal controllers; TLS termination. |
| MetalLB | Load balancer | L2 advertisement; VIPs for LoadBalancer services. |
| ArgoCD | GitOps | App-of-apps; bootstrap then self-managed. |
| kube-vip | Control plane | ARP-based VIP for the API server. |
| CoreDNS | DNS | Cluster DNS; custom internal zones via external-services. |
| cert-manager | Certificates | Let's Encrypt DNS-01 via Cloudflare; wildcard certificates. |
| Kyverno | Policy | Requests/limits, namespace quotas, secret protection. |
| Bitwarden SM Operator | Secrets | BitwardenSecret CRs materialised as Kubernetes Secrets. |
| Reflector | Secrets | Mirrors Secrets across namespaces. |
| Harbor | Registry | Private OCI registry. |
| NFS provisioner | Storage | Default and fast NFS StorageClasses. |
| Velero | Backup | Cluster backup and restore to S3. |
| RKE2 upgrade controller | Upgrades | Automated rolling cluster upgrades. |

## Related

| Section | Kubernetes content |
| :--- | :--- |
| [Network](3-network.md) | Kubernetes VLAN and remote-site subnet |
| [IaC, Automation & GitOps](4-iac.md) | OpenTofu provisioning, Ansible day-2, GitOps |
| [Update](5-update.md) | Cluster and application upgrades |
| [Storage & Backup](6-storage-backup.md) | NFS StorageClasses, Velero |
| [Observability](7-observability.md) | Metrics, logs, traces |
| [Security](8-security.md) | Cilium policies/WireGuard/mTLS, Kyverno, Trivy, secrets |
| [Disaster Recovery](9-disaster-recovery.md) | Cluster recovery |
