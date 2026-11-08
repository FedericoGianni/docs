# Hypervisor

> [Proxmox](https://www.proxmox.com/) on metal.

## PVE Setup

1. Install [Proxmox VE](https://www.proxmox.com/en/downloads/proxmox-virtual-environment)
2. Run [post-install script](https://community-scripts.github.io/ProxmoxVE/scripts?id=post-pve-install)
3. Add node to [cluster](https://pve.proxmox.com/wiki/Cluster_Manager)
4. Configure VLAN-aware bridge:

   Trunk port on switch → VLAN-aware bridge in PVE → assign VLAN ID when creating VMs.

   ```bash
   auto lo
   iface lo inet loopback

   iface nic0 inet manual
       post-up ethtool -K nic0 rx off tx off tso off # workaround for knwon problem on {{ hw.brand_server }} nics

   auto vmbr0
   iface vmbr0 inet manual
       bridge-ports nic0
       bridge-vlan-aware yes
       bridge-vlan-options tag-aware=yes
       bridge-vids 10 20 30 40 50 60
       bridge-stp off
       bridge-fd 0

   auto vmbr0.10
   iface vmbr0.10 inet static
       address {{ ip.node1 }}/24
       gateway {{ ip.mgmt }}

   source /etc/network/interfaces.d/*
   ```

   Adjust IP per node.

5. Configure local ZFS pool (`localZFS`) + replication (see [below](#replication-and-migration)) [guide](https://www.youtube.com/watch?v=RYENnzHWawI)
6. Run [ansible](https://gitlab.com/forbay/ansible-config):

   ```bash
   ansible-playbook main.yml --limit pve
   ```

   Automates: NFS mounts (`/FORBAY`, `/FORBAY_FAST`, `/FORBAY_EPHEMERAL` — see [Storage & Backup](7-storage-backup.md)), disk optimization (noatime, tmpfs, swappiness=1, journald→RAM), log2ram, [unattended upgrades](6-update.md), LXC auto-updater, `/etc` backup, [Alloy](9-observability.md) + healthchecks + Wazuh.

## Replication and Migration

`localZFS` is replicated with `pvesr` to **both** peer nodes, so any node can take over any guest without moving a disk. K8s nodes are excluded: their HA comes from Kubernetes itself, not from PVE.

| Guest | Runs on | Replicated to |
| :--- | :--- | :--- |
| PBS, PVE exporter | pve1 | pve2, pve3 |
| MinIO, Checkmk, Suricata | pve2 | pve1, pve3 |
| PostgreSQL, Wazuh | pve3 | pve1, pve2 |
| k8s masters + workers | pve1-3 | none (replication job disabled) |

Incremental `zfs send` every 2 h (`*/2:00`), linked with `__replicate_<job>_<epoch>__` snapshots. This is a migration helper, not a backup — retention is one window; [PBS](7-storage-backup.md) is the backup.

Migrating is then a plain move of the current state:

```bash
qm migrate <vmid> <node> --with-local-disks --online   # VM
pct migrate <vmid> <node> --restart                     # LXC (no live migration)
```

> **Note:** `pve4` (remote site) is standalone, not a cluster member — nothing replicates there.

## PBS Setup

1. Install [PBS](https://www.proxmox.com/en/downloads/proxmox-backup-server)
2. Run [post-install script](https://community-scripts.github.io/ProxmoxVE/scripts?id=post-pbs-install)
3. Configure VLANs:
   - **Bare metal** — same bridge pattern as PVE, just VLAN 10 for management
   - **VM/LXC in PVE** — set VLAN ID 10 in the VM config (no internal config needed)
4. Run [ansible](https://gitlab.com/forbay/ansible-config):

   ```bash
   ansible-playbook main.yml --limit pbs
   ```

   Automates: NFS mount (`{{ ip.backup }}:/FORBAY → /mnt/pve/NFS`), [Alloy](9-observability.md).
