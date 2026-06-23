#!/usr/bin/env python3
import argparse
import json
import re
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
import telnetlib
import time


PROMPT_RE = re.compile(rb"(?m)(?:^|\r?\n)[A-Za-z0-9_.:/()-]+[>#]\s*$")
ONLINE_RE = re.compile(r"\b(online|up|active|working|operational)\b", re.I)
OFFLINE_RE = re.compile(r"\b(offline|down|inactive|los|loss|dying|deactivated|disabled)\b", re.I)
SERIAL_RE = re.compile(r"\b(?:[A-Z]{4}[0-9A-F]{8}|[0-9A-F]{12,16})\b", re.I)


def fail(message, code=1):
    print(message)
    raise SystemExit(code)


def resolve_password(value):
    if value.startswith("file:"):
        path = value[5:]
    elif value.startswith("@"):
        path = value[1:]
    else:
        return value

    try:
        with open(path, "r", encoding="utf-8") as secret_file:
            password = secret_file.readline().strip()
    except OSError as exc:
        fail(f"Erro: nao foi possivel ler arquivo de senha Telnet: {exc}")

    if not password:
        fail("Erro: arquivo de senha Telnet vazio")
    return password


def telnet_login(host, user, password, timeout):
    tn = telnetlib.Telnet(host, 23, timeout=timeout)
    data = tn.read_until(b"login:", timeout=timeout)
    if b"login:" not in data.lower():
        fail("Erro: prompt de login Telnet nao encontrado")
    tn.write(user.encode() + b"\n")
    data = tn.read_until(b"Password:", timeout=timeout)
    if b"password:" not in data.lower():
        fail("Erro: prompt de senha Telnet nao encontrado")
    tn.write(password.encode() + b"\n")
    time.sleep(1)
    data = tn.read_very_eager()
    if b"Login incorrect" in data or b"login:" in data.lower():
        fail("Erro: login Telnet invalido")

    for cmd in ("paginate false", "terminal length 0", "terminal width 512", "no page"):
        run_command(tn, cmd, timeout=2, ignore_timeout=True)
    return tn


def run_command(tn, command, timeout=8, ignore_timeout=False):
    tn.write(command.encode() + b"\n")
    end = time.time() + timeout
    data = b""
    while time.time() < end:
        time.sleep(0.2)
        chunk = tn.read_very_eager()
        if chunk:
            data += chunk
            if b"--More--" in data or b"More:" in data:
                tn.write(b" ")
                data = data.replace(b"--More--", b"").replace(b"More:", b"")
            if PROMPT_RE.search(data):
                break
    if not data and not ignore_timeout:
        fail(f"Erro: comando sem resposta: {command}")
    text = data.decode("utf-8", "replace")
    lines = []
    for line in text.splitlines():
        clean = line.strip()
        if not clean or clean == command:
            continue
        if re.match(r"^[A-Za-z0-9_.:/()-]+[>#]\s*$", clean):
            continue
        lines.append(clean)
    return "\n".join(lines)


def candidate_commands(pon=None):
    if pon:
        cli_pon = pon.replace("gpon-", "gpon ")
        return [
            f"show interface {cli_pon} onu",
            f"show interface {cli_pon}",
        ]
    return [
        "show onu-interface-count",
    ]


def best_onu_output(tn, pon=None):
    errors = []
    for cmd in candidate_commands(pon):
        out = run_command(tn, cmd, timeout=10, ignore_timeout=True)
        low = out.lower()
        if not out or "invalid input" in low or "unknown command" in low or "syntax error" in low:
            errors.append(cmd)
            continue
        if "onu" in low or "ont" in low or "oper state" in low or "interface" in low:
            return out
    fail("Erro: nenhum comando de ONU/ONT retornou dados validos. Tentados: " + ", ".join(errors))


def normalize_pon(value):
    value = value.strip()
    if value.startswith("gpon-"):
        return value
    if re.match(r"^\d+/\d+/\d+$", value):
        return "gpon-" + value
    return value


def extract_pon(line, default=None):
    match = re.search(r"\bgpon-(\d+/\d+/\d+)\b", line, re.I)
    if match:
        return "gpon-" + match.group(1)
    match = re.search(r"\b(\d+/\d+/\d+)(?:/|\s+|:)", line)
    if match:
        return "gpon-" + match.group(1)
    return default


def extract_onu_id(line, pon):
    plain_pon = pon.replace("gpon-", "") if pon else ""
    patterns = [
        rf"\b{re.escape(pon)}[/:\s]+(\d+)\b" if pon else None,
        rf"\b{re.escape(plain_pon)}[/:\s]+(\d+)\b" if plain_pon else None,
        r"\bonu\s*[:#-]?\s*(\d+)\b",
        r"\bont\s*[:#-]?\s*(\d+)\b",
    ]
    for pattern in [p for p in patterns if p]:
        match = re.search(pattern, line, re.I)
        if match:
            return match.group(1)
    tokens = re.split(r"\s+", line.strip())
    for token in tokens[:4]:
        if token.isdigit():
            return token
    return None


def parse_rows(output, default_pon=None):
    rows = []
    for raw in output.splitlines():
        line = raw.strip()
        if not line or set(line) <= set("-= "):
            continue
        if re.search(r"\b(Itf|ONU ID|Serial|Oper State|Software|Name)\b", line, re.I):
            continue
        table = re.match(r"^(?P<pon>\d+/\d+/\d+)\s+(?P<onu>\d+)\s+(?P<serial>\S+)\s+(?P<state>Up|Down)\b(?P<rest>.*)$", line, re.I)
        if table:
            state = table.group("state").lower()
            rows.append({
                "pon": "gpon-" + table.group("pon"),
                "onu": table.group("onu"),
                "serial": table.group("serial").upper(),
                "status": "online" if state == "up" else "offline",
                "raw": line,
            })
            continue

        pon = extract_pon(line.replace("gpon ", "gpon-"), default=default_pon)
        status = "online" if ONLINE_RE.search(line) else "offline" if OFFLINE_RE.search(line) else "unknown"
        if not pon or status == "unknown":
            continue
        onu_id = extract_onu_id(line, pon)
        serial = SERIAL_RE.search(line)
        rows.append({
            "pon": pon,
            "onu": onu_id or str(len(rows) + 1),
            "serial": serial.group(0).upper() if serial else "",
            "status": status,
            "raw": line,
        })
    return rows


def count_rows(rows, mode):
    if mode == "total":
        return len(rows)
    return sum(1 for row in rows if row["status"] == mode)


def command_count_fallback(output):
    match = re.search(r"Count:\s*(\d+)\s*lines?", output, re.I)
    return int(match.group(1)) if match else None


def parse_interface_counts(output):
    counts = {}
    for raw in output.splitlines():
        line = raw.strip()
        match = re.match(
            r"^\d+\s+(gpon-\d+/\d+/\d+)\s+(\d+)\s+\d+\s+(\d+)\s+(\d+)\s*$",
            line,
            re.I,
        )
        if match:
            counts[match.group(1)] = {
                "total": int(match.group(2)),
                "online": int(match.group(3)),
                "offline": int(match.group(4)),
            }
    return counts


def cli_pon_name(pon):
    return normalize_pon(pon).replace("gpon-", "gpon ")


def parse_pppoe_sessions(output, default_pon=None):
    sessions = {}
    for raw in output.splitlines():
        line = raw.strip()
        match = re.match(
            r"^(?P<pon>\d+/\d+/\d+)\s+(?P<onu>\d+)\s+(?P<session>\d+)\s+(?P<mac>[0-9a-f:]{17})\s*$",
            line,
            re.I,
        )
        if not match:
            continue
        pon = "gpon-" + match.group("pon")
        sessions[(pon, match.group("onu"))] = {
            "session": match.group("session"),
            "mac": match.group("mac").upper(),
        }
    return sessions


def pppoe_sessions_for_pon(tn, pon):
    output = run_command(
        tn,
        f"show pppoe intermediate-agent sessions interface {cli_pon_name(pon)}",
        timeout=10,
        ignore_timeout=True,
    )
    low = output.lower()
    if "syntax error" in low or "invalid input" in low or "unknown argument" in low:
        fail("Erro: comando PPPoE nao suportado nesta OLT")
    return parse_pppoe_sessions(output, default_pon=pon)


def main():
    parser = argparse.ArgumentParser(description="Datacom DM4615 ONU helper for Zabbix external checks")
    parser.add_argument("action", choices=["pon-count", "onu-lld", "onu-value", "raw"])
    parser.add_argument("host")
    parser.add_argument("user")
    parser.add_argument("password")
    parser.add_argument("extra", nargs="*")
    parser.add_argument("--timeout", type=int, default=8)
    args = parser.parse_args()

    password = resolve_password(args.password)
    tn = telnet_login(args.host, args.user, password, args.timeout)
    try:
        if args.action == "pon-count":
            if len(args.extra) != 2:
                fail("Uso: pon-count <host> <user> <password> <pon> <online|offline|total>")
            pon = normalize_pon(args.extra[0])
            mode = args.extra[1].lower()
            output = best_onu_output(tn, pon=pon)
            fallback = command_count_fallback(output)
            rows = parse_rows(output, default_pon=pon)
            if rows:
                print(count_rows(rows, mode))
            elif fallback is not None and mode == "total":
                print(fallback)
            else:
                counts = parse_interface_counts(run_command(tn, "show onu-interface-count", timeout=8))
                print(counts.get(pon, {}).get(mode, 0))
        elif args.action == "onu-lld":
            counts = parse_interface_counts(run_command(tn, "show onu-interface-count", timeout=8))
            pons = [pon for pon in sorted(counts) if counts[pon].get("total", 0) > 0]
            output = "\n".join(best_onu_output(tn, pon=pon) for pon in pons)
            rows = parse_rows(output)
            data = []
            seen = set()
            for row in rows:
                key = (row["pon"], row["onu"])
                if key in seen:
                    continue
                seen.add(key)
                data.append({
                    "{#PONNAME}": row["pon"],
                    "{#ONUID}": row["onu"],
                    "{#ONUSERIAL}": row["serial"] or f"{row['pon']}/{row['onu']}",
                })
            print(json.dumps({"data": data}, separators=(",", ":")))
        elif args.action == "onu-value":
            if len(args.extra) != 3:
                fail("Uso: onu-value <host> <user> <password> <pon> <onu> <status|serial|raw|pppoe|pppoe-active>")
            pon = normalize_pon(args.extra[0])
            onu_id = args.extra[1]
            field = args.extra[2].lower()
            if field in ("pppoe", "pppoe-active"):
                session = pppoe_sessions_for_pon(tn, pon).get((pon, onu_id))
                if field == "pppoe-active":
                    print(1 if session else 0)
                else:
                    print(f"{session['session']} {session['mac']}" if session else "")
            else:
                rows = parse_rows(best_onu_output(tn, pon=pon), default_pon=pon)
                row = next((r for r in rows if r["onu"] == onu_id), None)
                if not row:
                    fail("Erro: ONU nao encontrada")
                if field == "status":
                    print(1 if row["status"] == "online" else 0)
                elif field == "serial":
                    print(row["serial"])
                elif field == "raw":
                    print(row["raw"])
                else:
                    fail("Erro: campo invalido")
        elif args.action == "raw":
            pon = normalize_pon(args.extra[0]) if args.extra else None
            print(best_onu_output(tn, pon=pon))
    finally:
        try:
            tn.write(b"exit\n")
            tn.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
