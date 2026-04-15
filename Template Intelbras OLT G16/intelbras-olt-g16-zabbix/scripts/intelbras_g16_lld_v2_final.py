#!/usr/bin/env python3
import json
import re
import subprocess
import sys
from typing import List, Dict


def run_snmpwalk(host: str, community: str, oid: str) -> str:
    cmd = [
        'snmpwalk', '-v2c', '-c', community, '-On', '-t', '10', '-r', '1', host, oid
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    # snmpwalk often returns rc 1 with partial output on sparse trees; use stdout if present.
    out = (proc.stdout or '').replace('\r', '')
    return out


def pon_from_ifdescr(host: str, community: str) -> Dict[str, List[Dict[str, str]]]:
    out = []
    seen = set()
    data = run_snmpwalk(host, community, '.1.3.6.1.2.1.2.2.1.2')
    for line in data.splitlines():
        m = re.match(r'^\.1\.3\.6\.1\.2\.1\.2\.2\.1\.2\.(\d+)\s+=\s+STRING:\s+"([^"]+)"$', line)
        if not m:
            continue
        ifindex, ifname = m.groups()
        pm = re.match(r'^g0\/(\d+)$', ifname.strip())
        if not pm:
            continue
        port = pm.group(1)
        if ifindex in seen:
            continue
        seen.add(ifindex)
        out.append({
            '{#IFINDEX}': ifindex,
            '{#PORT}': port,
            '{#PORTNAME}': ifname.strip(),
            '{#GROUP}': '0',
        })
    return {'data': out}


def uplink_from_ifdescr(host: str, community: str) -> Dict[str, List[Dict[str, str]]]:
    out = []
    seen = set()
    data = run_snmpwalk(host, community, '.1.3.6.1.2.1.2.2.1.2')
    for line in data.splitlines():
        m = re.match(r'^\.1\.3\.6\.1\.2\.1\.2\.2\.1\.2\.(\d+)\s+=\s+STRING:\s+"([^"]+)"$', line)
        if not m:
            continue
        ifindex, ifname = m.groups()
        pm = re.match(r'^e([12])\/(\d+)$', ifname.strip())
        if not pm:
            continue
        group, port = pm.groups()
        if ifindex in seen:
            continue
        seen.add(ifindex)
        out.append({
            '{#IFINDEX}': ifindex,
            '{#GROUP}': group,
            '{#PORT}': port,
            '{#PORTNAME}': ifname.strip(),
        })
    return {'data': out}


def sfp_from_vendor_tree(host: str, community: str) -> Dict[str, List[Dict[str, str]]]:
    out = []
    seen = set()
    # Use transceiver type column. Discover only ports whose value is not '-'.
    data = run_snmpwalk(host, community, '.1.3.6.1.4.1.13464.1.14.2.3.3.1.3')
    for line in data.splitlines():
        m = re.match(r'^\.1\.3\.6\.1\.4\.1\.13464\.1\.14\.2\.3\.3\.1\.3\.(\d+)\.(\d+)\s+=\s+STRING:\s+"([^"]*)"$', line)
        if not m:
            continue
        group, port, sfptype = m.groups()
        sfptype = sfptype.strip()
        if sfptype in ('', '-'):
            continue
        idx = f'{group}.{port}'
        if idx in seen:
            continue
        seen.add(idx)
        if group == '0':
            name = f'g0/{port}'
        elif group == '1':
            name = f'e1/{port}'
        elif group == '2':
            name = f'e2/{port}'
        else:
            name = f'{group}/{port}'
        out.append({
            '{#GROUP}': group,
            '{#PORT}': port,
            '{#PORTNAME}': name,
            '{#SFPINDEX}': idx,
        })
    return {'data': out}


def onu_from_status_tree(host: str, community: str) -> Dict[str, List[Dict[str, str]]]:
    out = []
    seen = set()
    # Use operational-status column; index format group.pon.onu
    data = run_snmpwalk(host, community, '.1.3.6.1.4.1.13464.1.14.2.4.1.1.1.6')
    for line in data.splitlines():
        m = re.match(r'^\.1\.3\.6\.1\.4\.1\.13464\.1\.14\.2\.4\.1\.1\.1\.6\.(\d+)\.(\d+)\.(\d+)\s+=\s+INTEGER:\s+\d+$', line)
        if not m:
            continue
        group, pon, onu = m.groups()
        idx = f'{group}.{pon}.{onu}'
        if idx in seen:
            continue
        seen.add(idx)
        out.append({
            '{#SNMPINDEX}': idx,
            '{#GROUP}': group,
            '{#ONU_PORT}': pon,
            '{#ONU_INDEX}': onu,
        })
    return {'data': out}


def main() -> int:
    if len(sys.argv) != 4:
        print(json.dumps({'data': []}))
        return 0

    mode, host, community = sys.argv[1], sys.argv[2], sys.argv[3]
    try:
        if mode == 'pon':
            result = pon_from_ifdescr(host, community)
        elif mode == 'uplink':
            result = uplink_from_ifdescr(host, community)
        elif mode == 'sfp':
            result = sfp_from_vendor_tree(host, community)
        elif mode == 'onu':
            result = onu_from_status_tree(host, community)
        else:
            result = {'data': []}
    except Exception:
        result = {'data': []}

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
