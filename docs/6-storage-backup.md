# Storage & Backup

> Wait, you guys are getting backups?!

This document summarizes the storage layout and backup strategy across my infrastructure. It follows the 3-2-1 backup rule, with an off-site copy to another location.

---

## Storage

| Storage | Type  | Purpose  | Backed Up |
| :--- | :--- | :--- | :--- |
| **gdrive** | Cloud Storage | Multi-device sync layer and extra copy for important documents | Synced to `/FORBAY` (covered by `/FORBAY` backup) |
| **`/FORBAY`** | NFS Share ({{ hw.brand_nas }} NAS) | 2 HDDs (RAID 1) — General storage, PBS backups | Via restic |
| **`/FORBAY_FAST`** | NFS Share (`{{ hw.host6 }}`) | LVM of 2 USB SSDs (`ext4`): Faster I/O storage - MinIO S3 data | Via restic |
| **`/FORBAY_EPHEMERAL`** | NFS Share (`{{ hw.host6 }}`) | LVM of 2 USB drives (`ext4`) — Expendable / temporary data | - |
| **MinIO S3** | S3 Object Storage | Mounted from `/FORBAY` | Covered by `/FORBAY` backup |

### Benchmarks

`fio` ([`nfs-bench.fio`](assets/snippets/nfs-bench.fio)): 1 MiB seq + 4 KiB rand, 512 MiB, 20 s.
To reproduce: run `fio nfs-bench.fio` from inside each share (on host) or its NFS mountpoint (over NFS).


| Storage | Where | Seq Read (MiB/s) | Seq Write (MiB/s) | 4K Rand Read (MiB/s) | 4K Rand Write (MiB/s) |
| :--- | :--- | ---: | ---: | ---: | ---: |
| `/FORBAY` | on host | 66 | 70 | 0.4 | 1.2 |
| `/FORBAY` | over NFS | 32.3 | 6.2 | 0.34 | 0.05 |
| `/FORBAY_FAST` | on host | 210 | 317 | 19.5 | 29.1 |
| `/FORBAY_FAST` | over NFS | 28.5 | 22.8 | 6.4 | 0.6 |
| `/FORBAY_EPHEMERAL` | on host | 75 | 30 | 8.1 | 3.4 |
| `/FORBAY_EPHEMERAL` | over NFS | 28.5 | 15.7 | 6.2 | 0.7 |
| `localZFS` (ref comparison, not NFS) | on `{{ hw.host1 }}` | 1540 | 346 | 14.4 | 484 |


## Backup

### Data Backup
#### /FORBAY

| Task                 | Tool        | Type      | Schedule   | Retention     | Source → Destination              |
| -------------------- | ----------- | --------- | --------------------- | ------------- | --------------------------------- |
| gdrive to `/FORBAY`        | rclone      | Automatic | Daily 12:00 & 20:00  | Mirror (sync) | gdrive → NAS local                |
| `/FORBAY` to ext HDD      | restic      | Automatic | Daily 09:00  | 6 months     | NAS → External USB HDD            |
| ext HDD to remote DR | restic copy | Automatic | Daily 12:00 | Mirror (sync) | External USB HDD → {{ hw.host7 }} (remote) |

#### /FORBAY_FAST

| Task                   | Tool          | Type                        | Schedule | Retention | Source → Destination  |
| ---------------------- | ------------- | --------------------------- | --------------------- | --------- | --------------------- |
| `/FORBAY_FAST` offsite | restic + SFTP | Automatic | Daily 08:15 | 6 months  | {{ hw.host6 }} → {{ hw.host7 }} (remote) |


> **Note:** *`/FORBAY_FAST` does not strictly follow 3-2-1 backup yet because an extra local HDD hasn't been purchased; only offsite backup to {{ hw.host7 }} is used for now.*

### Network Devices Backup

| Device Type       | Tool | Type   | Schedule  | Destination |
| ----------------- | ------------- | ------ | --------- | ----------- |
| {{ hw.brand_router }} Router | Manual Export | Manual | As needed | gdrive      |
| Other Devices     | Manual Export | Manual | As needed | gdrive      |

---

### Proxmox Host Backup

| Task                                | Tool / Method | Type      | Schedule   | Destination |
| ----------------------------------- | ------------- | --------- | ---------- | ----------- |
| Proxmox config backup (e.g. `/etc`) | Custom Script | Automatic | cron.daily | `/FORBAY`     |

---

### Virtual Machine Backup

| Task      | Tool                  | Type      | Schedule                    | Destination |
| --------- | --------------------- | --------- | --------------------------- | ----------- |
| VM backup | Proxmox Backup Server | Automatic | Every day at 21:00 (per VM) | `/FORBAY`     |

### K8S Resources Backup

| Task              | Tool                         | Type      | Schedule           | Destination     |
| :---------------- | :--------------------------- | :-------- | :----------------- | :-------------- |
| Cluster resources | Velero + Node Agent (Restic) | Automatic | Every day at 10:00 | MinIO S3 Bucket |
| etcd snapshots    | RKE2 CronJob                 | Automatic | Every 30 min       | MinIO S3 Bucket |
