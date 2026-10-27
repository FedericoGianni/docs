#!/usr/bin/env python3
"""Generate public scrambled values from secrets.local.yml.

The mapping is keyed by secrets.key (HMAC-SHA256), so the scrambled values
cannot be mapped back to the real ones without the key. Subnet relationships
are preserved: a host stays inside its scrambled subnet.
"""

import hashlib
import hmac
import ipaddress
import sys
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent.parent
SECRETS = BASE / "secrets.local.yml"
KEY = BASE / "secrets.key"
OUT = BASE / "secrets.scrambled.yml"


def derive(key_bytes, label, modulo):
    digest = hmac.new(key_bytes, label.encode(), hashlib.sha256).digest()
    return int.from_bytes(digest[:8], "big") % modulo


def main():
    if not SECRETS.exists():
        print(f"missing {SECRETS.name}")
        return 1
    if not KEY.exists():
        print(f"missing {KEY.name}; needed to scramble values")
        return 1

    real = yaml.safe_load(SECRETS.read_text(encoding="utf-8")) or {}
    key = KEY.read_bytes()
    nets = {
        name: ipaddress.ip_network(str(cidr))
        for name, cidr in (real.get("net") or {}).items()
    }

    scrambled = {}
    used = []
    # Parents before children, so /28s stay inside their /24.
    for name in sorted(nets, key=lambda n: nets[n].prefixlen):
        net = nets[name]
        parents = [n for n in nets.values() if n != net and net.subnet_of(n)]
        if parents:
            parent = min(parents, key=lambda n: n.prefixlen)
            parent_name = next(k for k, v in nets.items() if v == parent)
            offset = int(net.network_address) - int(parent.network_address)
            base = int(scrambled[parent_name].network_address) + offset
            scrambled[name] = ipaddress.ip_network((base, net.prefixlen), strict=False)
            continue

        for _ in range(1000):
            second = 1 + derive(key, f"net:{name}:2", 254)
            third = derive(key, f"net:{name}:3", 256)
            candidate = ipaddress.ip_network(
                f"10.{second}.{third}.0/{net.prefixlen}", strict=False
            )
            if not any(candidate.overlaps(existing) for existing in used):
                used.append(candidate)
                scrambled[name] = candidate
                break
        else:
            print(f"could not allocate a subnet for {name}")
            return 1

    out = {
        "domain": "example.com",
        "ip": {},
        "net": {name: str(net) for name, net in scrambled.items()},
    }

    for name, value in (real.get("ip") or {}).items():
        addr = ipaddress.ip_address(str(value))
        containers = [n for n in nets.values() if addr in n]
        if not containers:
            print(f"{name} ({addr}) is not inside any net; add a subnet")
            return 1
        parent = min(containers, key=lambda n: n.prefixlen)
        parent_name = next(k for k, v in nets.items() if v == parent)
        hosts = max(parent.num_addresses - 2, 1)
        host = 1 + derive(key, f"ip:{name}:host", hosts)
        out["ip"][name] = str(
            ipaddress.ip_address(int(scrambled[parent_name].network_address) + host)
        )

    hw_out = {}
    used = set()
    words = [
        "Aster", "Borealis", "Cobalt", "Delta", "Ember", "Fjord", "Granite",
        "Harbor", "Iris", "Juniper", "Kestrel", "Lumen", "Marlin", "Nimbus",
        "Onyx", "Pioneer", "Quartz", "Raven", "Summit", "Tundra", "Umber",
        "Vertex", "Willow", "Xenon", "Yarrow", "Zephyr",
    ]
    for name in (real.get("hw") or {}):
        base = words[derive(key, f"hw:{name}", len(words))]
        number = 1 + derive(key, f"hw:{name}:n", 99)
        fake = f"{base}-{number:02d}"
        while fake in used:
            number = number % 99 + 1
            fake = f"{base}-{number:02d}"
        used.add(fake)
        hw_out[name] = fake
    out["hw"] = hw_out

    links_out = {}
    for name in (real.get("links") or {}):
        word = words[derive(key, f"link:{name}", len(words))].lower()
        links_out[name] = f"https://example.com/{word}"
    out["links"] = links_out

    OUT.write_text(yaml.safe_dump(out, sort_keys=False), encoding="utf-8")
    print(f"wrote {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
