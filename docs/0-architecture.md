# Architecture

## Infrastructure architecture

```mermaid
flowchart TB
    subgraph MAIN["MAIN SITE"]
        direction TB

        MAIN_WAN["{{ hw.brand_gateway }}<br/>Internet Gateway<br/>{{ ip.gateway }}"]
        MAIN_ROUTER["{{ hw.brand_router }}<br/>Main Router<br/>{{ ip.router }}"]
        SWITCH["{{ hw.switch1 }}<br/>Switch"]
        MAIN_WAN ---|"WAN"| MAIN_ROUTER
        MAIN_ROUTER --- SWITCH

        NAS["{{ hw.nas1 }}<br/>NAS<br/>{{ ip.nas }}"]
        SBC_MAIN["{{ hw.server3 }}<br/>{{ ip.sbc_main }}"]

        subgraph MAIN_PVE["Proxmox VE Cluster"]
            direction LR

            subgraph PVE1["{{ hw.host1 }} · {{ hw.server1 }}<br/>{{ ip.node1 }}"]
                direction TB
                PBS["PBS<br/>{{ ip.pbs }}"]
                PVE_EXP["PVE Exporter<br/>{{ ip.pve_exp }}"]
                M1["k8s-master-1<br/>{{ ip.m1 }}"]
                W1["k8s-worker-1<br/>{{ ip.w1 }}"]
                PBS ~~~ PVE_EXP ~~~ M1 ~~~ W1
            end

            subgraph PVE3["{{ hw.host3 }} · {{ hw.server1 }}<br/>{{ ip.node3 }}"]
                direction TB
                M3["k8s-master-3<br/>{{ ip.m3 }}"]
                W3["k8s-worker-3<br/>{{ ip.w3 }}"]
                POSTGRES["PostgreSQL<br/>{{ ip.postgres }}"]
                WAZUH["Wazuh<br/>{{ ip.wazuh }}"]
                M3 ~~~ W3 ~~~ POSTGRES ~~~ WAZUH
            end

            subgraph PVE2["{{ hw.host2 }} · {{ hw.server1 }}<br/>{{ ip.node2 }}"]
                direction TB
                M2["k8s-master-2<br/>{{ ip.m2 }}"]
                W2["k8s-worker-2<br/>{{ ip.w2 }}"]
                SURICATA["Suricata<br/>{{ ip.suricata }}"]
                MINIO["MinIO<br/>{{ ip.minio }}"]
                M2 ~~~ W2 ~~~ SURICATA ~~~ MINIO
            end

        end

        %% Keep network devices above the cluster and storage nodes.
        SWITCH ~~~ MAIN_PVE
        MAIN_ROUTER --- PVE1
        MAIN_ROUTER --- PVE2
        MAIN_ROUTER --- PVE3
        SWITCH --- NAS
        SWITCH --- SBC_MAIN

    end

    INTERNET(("Internet"))

    subgraph REMOTE["REMOTE SITE"]
        direction TB

        REMOTE_ROUTER["{{ hw.router2 }}<br/>Remote Router"]
        REMOTE_SWITCH["{{ hw.switch1 }}<br/>Switch"]

        subgraph REMOTE_LAN["{{ net.lan_remote }}"]
            direction TB

            subgraph PVE4["{{ hw.host4 }} · {{ hw.server2 }}<br/>{{ ip.node4 }}"]
                direction TB
                OPENCLAW["OpenClaw<br/>{{ ip.openclaw }}"]
                CHECKMK_SO["Checkmk<br/>{{ ip.checkmk_so }}"]
                PVE_EXP_SO["PVE Exporter<br/>{{ ip.pve_exp_so }}"]
                K3S_SO["k8s-single-node<br/>{{ ip.k3s_so }}"]
                OPENCLAW ~~~ CHECKMK_SO ~~~ PVE_EXP_SO ~~~ K3S_SO
            end

            SBC_REMOTE["{{ hw.server4 }}<br/>{{ ip.sbc_remote }}"]
        end

        REMOTE_ROUTER --- REMOTE_SWITCH
        REMOTE_SWITCH --- PVE4
        REMOTE_SWITCH --- SBC_REMOTE
    end

    subgraph CLOUD["CLOUD"]
        direction TB
        OCI1["OCI 1<br/>{{ ip.oci1 }}"]
        OCI2["OCI 2<br/>{{ ip.oci2 }}"]
    end

    MAIN_WAN --- INTERNET
    INTERNET --- REMOTE_ROUTER
    
    SBC_REMOTE -.->|"VPN"| MAIN_ROUTER
    OCI1 -.->|"VPN"| MAIN_ROUTER
    OCI2 -.->|"VPN"| MAIN_ROUTER

    classDef baremetal stroke-width:2px
    classDef vm stroke-width:1px
    classDef lxc stroke-width:1px
    classDef network stroke-width:2px

    class NAS,SBC_MAIN,SBC_REMOTE baremetal
    class M1,M2,M3,W1,W2,W3,SURICATA,WAZUH,OCI1,OCI2 vm
    class PBS,PVE_EXP,MINIO,POSTGRES,OPENCLAW,CHECKMK_SO,PVE_EXP_SO,K3S_SO lxc
    class MAIN_WAN,MAIN_ROUTER,REMOTE_ROUTER,REMOTE_SWITCH,INTERNET,SWITCH network
```

**Legend**

<ul class="forbay-legend">
  <li><span class="swatch baremetal"></span> Bare metal</li>
  <li><span class="swatch vm"></span> Virtual machine</li>
  <li><span class="swatch lxc"></span> Container</li>
  <li><span class="swatch network"></span> Network device</li>
</ul>

See [Network](3-network.md) for the full network topology.
