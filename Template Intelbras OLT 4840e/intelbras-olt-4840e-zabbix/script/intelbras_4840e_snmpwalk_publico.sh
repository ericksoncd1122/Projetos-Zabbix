#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Uso: $0 <IP_DA_OLT> <COMMUNITY_SNMP>"
  echo
  echo "Exemplo:"
  echo "  $0 192.0.2.10 public"
  exit 1
fi

IP="$1"
COMMUNITY="$2"
BASE_OUT="${3:-/tmp/intelbras_4840e_walks}"
OUTDIR="${BASE_OUT}/snmpwalk_olt_4840e_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$OUTDIR"

echo "[1/8] Testando conectividade SNMP..."
snmpget -v2c -c "$COMMUNITY" -On "$IP" 1.3.6.1.2.1.1.5.0 | tee "$OUTDIR/test_sysname.txt"

echo "[2/8] Coletando system..."
snmpwalk -v2c -c "$COMMUNITY" -On "$IP" 1.3.6.1.2.1.1 | tee "$OUTDIR/system.walk"

echo "[3/8] Coletando interfaces IF-MIB..."
snmpwalk -v2c -c "$COMMUNITY" -On "$IP" 1.3.6.1.2.1.2 | tee "$OUTDIR/interfaces_ifmib.walk"
snmpwalk -v2c -c "$COMMUNITY" -On "$IP" 1.3.6.1.2.1.31.1.1 | tee "$OUTDIR/interfaces_ifx.walk"

echo "[4/8] Coletando vendor general..."
snmpwalk -v2c -c "$COMMUNITY" -On "$IP" 1.3.6.1.4.1.13464.1.2.1.1.2 | tee "$OUTDIR/vendor_general.walk"

echo "[5/8] Coletando ONU status/info..."
snmpwalk -v2c -c "$COMMUNITY" -On "$IP" 1.3.6.1.4.1.13464.1.13.3.1.1 | tee "$OUTDIR/onu_status.walk"

echo "[6/8] Coletando ONU OPM..."
snmpwalk -v2c -c "$COMMUNITY" -On "$IP" 1.3.6.1.4.1.13464.1.13.3.3.1 | tee "$OUTDIR/onu_opm.walk"

echo "[7/8] Coletando PON status/módulos..."
snmpwalk -v2c -c "$COMMUNITY" -On "$IP" 1.3.6.1.4.1.13464.1.13.2.1.1 | tee "$OUTDIR/pon_status.walk"
snmpwalk -v2c -c "$COMMUNITY" -On "$IP" 1.3.6.1.4.1.13464.1.13.2.2.1 | tee "$OUTDIR/pon_module.walk"

echo "[8/8] Coletando árvore enterprise completa..."
snmpwalk -v2c -c "$COMMUNITY" -On "$IP" 1.3.6.1.4.1.13464 | tee "$OUTDIR/full_enterprise.walk"

echo
echo "Coleta concluída em: $OUTDIR"
echo
ls -lh "$OUTDIR"
