#!/usr/bin/env python3
import sys
import re
import subprocess

def snmpwalk(host: str, community: str, oid: str) -> str:
    cmd = ["snmpwalk", "-v2c", "-c", community, "-On", "-t", "8", "-r", "1", host, oid]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    if p.returncode != 0:
        return ""
    return (p.stdout or "").replace("\r", "")

def pon_online(host: str, community: str, port: str) -> int:
    txt = snmpwalk(host, community, f".1.3.6.1.4.1.13464.1.14.2.4.1.1.1.6.0.{port}")
    count = 0
    for line in txt.splitlines():
        m = re.match(r'^\.1\.3\.6\.1\.4\.1\.13464\.1\.14\.2\.4\.1\.1\.1\.6\.0\.(\d+)\.(\d+)\s+=\s+INTEGER:\s+(\d+)$', line)
        if not m:
            continue
        if m.group(1) != port:
            continue
        if m.group(3) == "1":
            count += 1
    return count

def pon_rx_avg(host: str, community: str, port: str) -> float:
    status_txt = snmpwalk(host, community, f".1.3.6.1.4.1.13464.1.14.2.4.1.1.1.6.0.{port}")
    online = set()
    for line in status_txt.splitlines():
        m = re.match(r'^\.1\.3\.6\.1\.4\.1\.13464\.1\.14\.2\.4\.1\.1\.1\.6\.0\.(\d+)\.(\d+)\s+=\s+INTEGER:\s+(\d+)$', line)
        if not m:
            continue
        p, onu, status = m.groups()
        if p == port and status == "1":
            online.add(onu)

    if not online:
        return 0.0

    rx_txt = snmpwalk(host, community, f".1.3.6.1.4.1.13464.1.14.2.4.1.9.1.5.0.{port}")
    vals = []
    for line in rx_txt.splitlines():
        m = re.match(r'^\.1\.3\.6\.1\.4\.1\.13464\.1\.14\.2\.4\.1\.9\.1\.5\.0\.(\d+)\.(\d+)\s+=\s+(?:STRING|INTEGER):\s+("?[^"]+"?|[-]?\d+(?:\.\d+)?)$', line)
        if not m:
            continue
        p, onu, raw = m.groups()
        if p != port or onu not in online:
            continue
        raw = raw.strip().strip('"')
        if raw in ("", "-"):
            continue
        try:
            vals.append(float(raw))
        except ValueError:
            continue

    if not vals:
        return 0.0

    return round(sum(vals) / len(vals), 2)

def main() -> int:
    if len(sys.argv) != 5:
        print("0")
        return 0

    mode, host, community, port = sys.argv[1:5]
    try:
        if mode == "pon_online":
            print(pon_online(host, community, port))
        elif mode == "pon_rx_avg":
            print(pon_rx_avg(host, community, port))
        else:
            print("0")
    except Exception:
        print("0")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
