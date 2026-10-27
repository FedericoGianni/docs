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

5. Configure local ZFS pool + replication [guide](https://www.youtube.com/watch?v=RYENnzHWawI)
6. Run [ansible](https://gitlab.com/forbay/ansible-config):

   ```bash
   ansible-playbook main.yml --limit pve
   ```

   Automates: NFS mounts (`/FORBAY`, `/FORBAY_FAST`, `/FORBAY_EPHEMERAL` — see [Storage & Backup](6-storage-backup.md)), disk optimization (noatime, tmpfs, swappiness=1, journald→RAM), log2ram, [unattended upgrades](5-update.md), LXC auto-updater, `/etc` backup, [Alloy](7-observability.md) + healthchecks + Wazuh.

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

   Automates: NFS mount (`{{ ip.backup }}:/FORBAY → /mnt/pve/NFS`), [Alloy](7-observability.md).
