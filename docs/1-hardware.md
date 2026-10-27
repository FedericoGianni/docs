# Hardware

>  Metal.

## Network

| Site | Device | Model |
| :--- | :--- | :--- |
| Main | Router 1 | {{ hw.router1 }} |
| Main | Router 2 | {{ hw.router3 }} |
| Main | Switch 1 | {{ hw.switch1 }} |
| Remote | Router 3 | {{ hw.router2 }} |
| Remote | Switch 2 | {{ hw.switch1 }} |

## Smart Plug

| Site | Device | Model | Purpose |
| :--- | :--- | :--- | :--- |
| Main | {{ hw.plug1 }} | {{ hw.plug1 }} | Remote power switch + energy consumption monitoring; used to power-cycle the homelab when it doesn't respond |

## Servers

| Site | Qty | Model | CPU | RAM | Storage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Main | 3 | {{ hw.server1 }} | {{ hw.cpu1 }} | 32 GB | 1 TB NVMe SSD + 128 GB USB NVMe (PVE OS) |
| Main | 1 | {{ hw.server3 }} | {{ hw.cpu2 }} | 4 GB | microSD 128 GB |
| Remote | 1 | {{ hw.server2 }} | {{ hw.cpu3 }} | 8 GB | SSD SATA 256 GB |
| Remote | 1 | {{ hw.server4 }} | {{ hw.cpu4 }} | 1 GB | microSD 32 GB |

## Storage

| Qty | Item | Specs | Purpose |
| :--- | :--- | :--- | :--- |
| 1 | {{ hw.nas1 }} | 2 x 2 TB HDD - RAID 1 | Main NAS storage |
| 2 | EXT USB HDD | 2 TB | Local/Remote NAS backup |
| 2 | EXT USB SSD | 256 GB | Faster NFS |
| 1 | EXT USB HDD | 500 GB | Remote USB SSDs backup |
| 2 | USB | 128 GB | Ephemeral NFS |
