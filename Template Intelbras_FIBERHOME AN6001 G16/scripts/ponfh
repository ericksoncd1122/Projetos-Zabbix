#!/bin/bash

# Monitoramento FiberHome/Intelbras AN6001-G16 - V5.22 Fix JSON/cache para alertas estáticos de PON
# Coleta dinâmica de ONUs por PON/status via SNMP direto na OLT.
# Compatível com itens externos do Zabbix.
#
# Item Zabbix:
#   ponfh "SLOT/PON" "STATUS" "IP_DA_OLT" "COMMUNITY" "PORTA" "TIMEOUT" "RETRIES" "CACHE_TTL"
#
# Status/consultas:
#   0 = LOS
#   1 = Online
#   2 = Offline
#   3 = Sem dados
#   4 = Sem energia / Dying Gasp
#   total/all/5 = total de ONUs autorizadas na PON
#   down = total de ONUs indisponíveis na PON (LOS + Offline + Sem dados + Sem energia)
#   online_percent = percentual de ONUs online na PON
#   down_percent = percentual de ONUs indisponíveis na PON
#   los_percent = percentual de ONUs em LOS na PON
#   energy_percent = percentual de ONUs sem energia na PON
#   json = retorna todos os contadores da PON em JSON para itens dependentes

set -o pipefail

# Garante ponto decimal nos percentuais, mesmo em servidores com locale pt_BR.
export LC_ALL=C
export LANG=C

OID_SLOT=".1.3.6.1.4.1.5875.800.3.10.1.1.2"
OID_PON=".1.3.6.1.4.1.5875.800.3.10.1.1.3"
OID_STATUS=".1.3.6.1.4.1.5875.800.3.10.1.1.11"

usage() {
  cat >&2 <<'USAGE'
Erro! Use uma das opções abaixo:

  Item Zabbix:
    ponfh "SLOT/PON" "STATUS" "IP_DA_OLT" "COMMUNITY" "PORTA" "TIMEOUT" "RETRIES" "CACHE_TTL"

  Descoberta LLD:
    ponfh --lld "IP_DA_OLT" "COMMUNITY" "PORTA" "TIMEOUT" "RETRIES" "CACHE_TTL"

  Resumo:
    ponfh --summary "IP_DA_OLT" "COMMUNITY" "PORTA" "TIMEOUT" "RETRIES" "CACHE_TTL"

Exemplos:
  ponfh "1/5" "2" "192.0.2.10" "public" "161" "2" "0" "300"
  ponfh "1/5" "down_percent" "192.0.2.10" "public" "161" "2" "0" "300"
  ponfh --lld "192.0.2.10" "public" "161" "2" "0" "300"
USAGE
}

snmp_tool() {
  if command -v snmpbulkwalk >/dev/null 2>&1; then
    echo "snmpbulkwalk"
  elif command -v snmpwalk >/dev/null 2>&1; then
    echo "snmpwalk"
  else
    echo "Erro! Instale o pacote snmp no servidor/proxy Zabbix." >&2
    exit 1
  fi
}

sanitize_cache_key() {
  printf '%s' "$1" | sha1sum | awk '{print $1}'
}

cache_base_for() {
  local ip="$1" community="$2" port="$3"
  local hash
  hash="$(sanitize_cache_key "${ip}|${community}|${port}")"
  echo "/tmp/ponfh_zabbix_${hash}"
}

normalize_number() {
  local value="$1" default_value="$2"
  if [[ "$value" =~ ^[0-9]+$ ]]; then
    echo "$value"
  else
    echo "$default_value"
  fi
}

file_is_fresh() {
  local file="$1" ttl="$2"
  [[ -s "$file" ]] || return 1
  [[ "$ttl" -gt 0 ]] || return 1
  local now mtime age
  now="$(date +%s)"
  mtime="$(stat -c %Y "$file" 2>/dev/null || echo 0)"
  age=$((now - mtime))
  [[ "$age" -le "$ttl" ]]
}

walk_oid() {
  local ip="$1" community="$2" port="$3" timeout="$4" retries="$5" oid="$6" outfile="$7"
  local tool errfile rc
  tool="$(snmp_tool)"
  errfile="$(mktemp)"

  if [[ "$tool" == "snmpbulkwalk" ]]; then
    "$tool" -v2c -c "$community" -On -Oq -Cr50 -t "$timeout" -r "$retries" "${ip}:${port}" "$oid" 2>"$errfile" \
      | awk -v base="${oid}." '
          NF >= 2 {
            idx=$1
            sub("^" base, "", idx)
            val=$NF
            gsub(/\"/, "", val)
            if (idx != $1 || $1 ~ base) print idx, val
          }
        ' > "$outfile"
  else
    "$tool" -v2c -c "$community" -On -Oq -t "$timeout" -r "$retries" "${ip}:${port}" "$oid" 2>"$errfile" \
      | awk -v base="${oid}." '
          NF >= 2 {
            idx=$1
            sub("^" base, "", idx)
            val=$NF
            gsub(/\"/, "", val)
            if (idx != $1 || $1 ~ base) print idx, val
          }
        ' > "$outfile"
  fi

  rc=${PIPESTATUS[0]}
  if [[ $rc -ne 0 ]]; then
    echo "Erro SNMP ao consultar $oid em ${ip}:${port}. Verifique IP, community, porta SNMP e ACL da OLT." >&2
    [[ -s "$errfile" ]] && cat "$errfile" >&2
    rm -f "$errfile" "$outfile"
    return 1
  fi

  rm -f "$errfile"
  return 0
}

refresh_needed_columns() {
  local ip="$1" community="$2" port="$3" timeout="$4" retries="$5" ttl="$6" base="$7" need_status="$8"
  local lock tmp have_slot have_pon have_status

  have_slot=0; have_pon=0; have_status=0
  file_is_fresh "${base}.slot" "$ttl" && have_slot=1
  file_is_fresh "${base}.pon" "$ttl" && have_pon=1
  file_is_fresh "${base}.status" "$ttl" && have_status=1

  if [[ "$need_status" == "yes" ]]; then
    [[ $have_slot -eq 1 && $have_pon -eq 1 && $have_status -eq 1 ]] && return 0
  else
    [[ $have_slot -eq 1 && $have_pon -eq 1 ]] && return 0
  fi

  lock="${base}.lock"
  if ! mkdir "$lock" 2>/dev/null; then
    sleep 1
    if [[ "$need_status" == "yes" ]]; then
      [[ -s "${base}.slot" && -s "${base}.pon" && -s "${base}.status" ]] && return 0
    else
      [[ -s "${base}.slot" && -s "${base}.pon" ]] && return 0
    fi
    return 2
  fi

  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"; rmdir "$lock" 2>/dev/null || true' EXIT

  if [[ $have_slot -ne 1 ]]; then
    walk_oid "$ip" "$community" "$port" "$timeout" "$retries" "$OID_SLOT" "$tmp/slot" || return 1
    mv "$tmp/slot" "${base}.slot"
  fi
  if [[ $have_pon -ne 1 ]]; then
    walk_oid "$ip" "$community" "$port" "$timeout" "$retries" "$OID_PON" "$tmp/pon" || return 1
    mv "$tmp/pon" "${base}.pon"
  fi
  if [[ "$need_status" == "yes" && $have_status -ne 1 ]]; then
    walk_oid "$ip" "$community" "$port" "$timeout" "$retries" "$OID_STATUS" "$tmp/status" || return 1
    mv "$tmp/status" "${base}.status"
  fi

  rm -rf "$tmp"
  rmdir "$lock" 2>/dev/null || true
  trap - EXIT
  return 0
}

normalize_pon() {
  # Aceita tanto 1/5 quanto 1_5.
  # O template V5.16 usa 1_5 dentro da key para evitar erro de parsing do Zabbix nas expressões.
  echo "$1" | sed -E 's/^[Pp][Oo][Nn][[:space:]]*//; s/[[:space:]]//g; s/_/\//g'
}

print_lld() {
  local base="$1"
  awk '
    FILENAME ~ /\.slot$/ { slot[$1]=$2; next }
    FILENAME ~ /\.pon$/  { pon[$1]=$2; next }
    END {
      for (idx in pon) {
        if (slot[idx] != "" && pon[idx] != "") {
          p=slot[idx] "/" pon[idx]
          seen[p]=1
        }
      }
      for (p in seen) print p
    }
  ' "${base}.slot" "${base}.pon" \
  | sort -t/ -k1,1n -k2,2n \
  | awk 'BEGIN { first=1; printf "{\"data\":[" }
         {
           if (!first) printf ","
           printf "{\"{#PON}\":\"%s\"}", $0
           first=0
         }
         END { printf "]}\n" }'
}

pon_stats() {
  local base="$1" wanted_slot="$2" wanted_pon="$3"
  awk -v wanted_slot="$wanted_slot" -v wanted_pon="$wanted_pon" '
    FILENAME ~ /\.slot$/   { slot[$1]=$2; next }
    FILENAME ~ /\.pon$/    { pon[$1]=$2; next }
    FILENAME ~ /\.status$/ { status[$1]=$2; next }
    END {
      total=online=offline=los=nodata=energy=0
      for (idx in pon) {
        if (slot[idx] == wanted_slot && pon[idx] == wanted_pon) {
          total++
          if (status[idx] == 1) online++
          else if (status[idx] == 2) offline++
          else if (status[idx] == 0) los++
          else if (status[idx] == 3) nodata++
          else if (status[idx] == 4) energy++
        }
      }
      down=offline+los+nodata+energy
      if (total > 0) {
        online_percent=(online/total)*100
        down_percent=(down/total)*100
        los_percent=(los/total)*100
        energy_percent=(energy/total)*100
      } else {
        online_percent=down_percent=los_percent=energy_percent=0
      }
      printf "%d %d %d %d %d %d %d %.2f %.2f %.2f %.2f\n", total, online, offline, los, nodata, energy, down, online_percent, down_percent, los_percent, energy_percent
    }
  ' "${base}.slot" "${base}.pon" "${base}.status"
}

count_or_percent() {
  local base="$1" wanted_slot="$2" wanted_pon="$3" wanted_status="$4"
  local stats total online offline los nodata energy down online_percent down_percent los_percent energy_percent
  stats="$(pon_stats "$base" "$wanted_slot" "$wanted_pon")"
  read -r total online offline los nodata energy down online_percent down_percent los_percent energy_percent <<< "$stats"
  case "$wanted_status" in
    total|all|5) echo "$total" ;;
    1) echo "$online" ;;
    2) echo "$offline" ;;
    0) echo "$los" ;;
    3) echo "$nodata" ;;
    4) echo "$energy" ;;
    down|offline_total|indisponivel|indisponiveis) echo "$down" ;;
    online_percent|online_pct) echo "$online_percent" ;;
    down_percent|down_pct|queda_percent|queda_pct) echo "$down_percent" ;;
    los_percent|los_pct) echo "$los_percent" ;;
    energy_percent|energy_pct|energia_percent|energia_pct) echo "$energy_percent" ;;
    json) printf '{"total":%d,"online":%d,"offline":%d,"los":%d,"sem_dados":%d,"sem_energia":%d,"down":%d,"online_percent":%.2f,"down_percent":%.2f,"los_percent":%.2f,"energy_percent":%.2f}\n' "$total" "$online" "$offline" "$los" "$nodata" "$energy" "$down" "$online_percent" "$down_percent" "$los_percent" "$energy_percent" ;;
    *) echo 0 ;;
  esac
}

print_summary() {
  local base="$1"
  awk '
    FILENAME ~ /\.slot$/   { slot[$1]=$2; next }
    FILENAME ~ /\.pon$/    { pon[$1]=$2; next }
    FILENAME ~ /\.status$/ { status[$1]=$2; next }
    END {
      for (idx in pon) {
        p=slot[idx] "/" pon[idx]
        s=status[idx]
        c[p,s]++
        total[p]++
      }
      for (p in total) {
        down=(c[p,2]+0)+(c[p,0]+0)+(c[p,3]+0)+(c[p,4]+0)
        pct=(total[p]>0)?(down/total[p]*100):0
        printf "%s|%d|%d|%d|%d|%d|%d|%.2f\n", p, c[p,1]+0, c[p,2]+0, c[p,0]+0, c[p,3]+0, c[p,4]+0, total[p]+0, pct
      }
    }
  ' "${base}.slot" "${base}.pon" "${base}.status" \
  | sort -t/ -k1,1n -k2,2n \
  | awk -F'|' 'BEGIN { printf "%-8s %8s %8s %8s %10s %12s %8s %10s\n", "PON", "ONLINE", "OFFLINE", "LOS", "SEM_DADOS", "SEM_ENERGIA", "TOTAL", "OFF_%" }
              { printf "%-8s %8s %8s %8s %10s %12s %8s %9s%%\n", $1, $2, $3, $4, $5, $6, $7, $8 }'
}

MODE="normal"
if [[ "$1" == "--summary" || "$1" == "summary" ]]; then
  MODE="summary"; shift
elif [[ "$1" == "--lld" || "$1" == "lld" || "$1" == "--lld-v514" || "$1" == "lld-v514" ]]; then
  MODE="lld"; shift
fi

if [[ "$MODE" == "summary" || "$MODE" == "lld" ]]; then
  IP="$1"
  COMMUNITY="${2:-public}"
  PORT="${3:-161}"
  TIMEOUT="$(normalize_number "${4:-2}" 2)"
  RETRIES="$(normalize_number "${5:-0}" 0)"
  CACHE_TTL="$(normalize_number "${6:-300}" 300)"
  [[ -z "$IP" ]] && usage && exit 1
  BASE="$(cache_base_for "$IP" "$COMMUNITY" "$PORT")"
  NEED_STATUS="no"
  [[ "$MODE" == "summary" ]] && NEED_STATUS="yes"
  refresh_needed_columns "$IP" "$COMMUNITY" "$PORT" "$TIMEOUT" "$RETRIES" "$CACHE_TTL" "$BASE" "$NEED_STATUS"
  rc=$?
  if [[ $rc -ne 0 ]]; then
    if [[ "$MODE" == "lld" ]]; then
      echo '{"data":[]}'
      exit 0
    fi
    if [[ -s "${BASE}.slot" && -s "${BASE}.pon" && -s "${BASE}.status" ]]; then
      print_summary "$BASE"
      exit 0
    fi
    echo "SEM_DADOS: erro ao atualizar cache SNMP da OLT. Teste no terminal: ponfh --summary IP COMMUNITY 161 2 0 300"
    exit 0
  fi
  if [[ "$MODE" == "summary" ]]; then
    print_summary "$BASE"
  else
    print_lld "$BASE"
  fi
  exit 0
fi

PON_RAW="$1"
STATUS="$2"
IP="$3"
COMMUNITY="${4:-public}"
PORT="${5:-161}"
TIMEOUT="$(normalize_number "${6:-2}" 2)"
RETRIES="$(normalize_number "${7:-0}" 0)"
CACHE_TTL="$(normalize_number "${8:-300}" 300)"

if [[ -z "$PON_RAW" || -z "$STATUS" || -z "$IP" ]]; then
  usage
  exit 1
fi

PON_CLEAN="$(normalize_pon "$PON_RAW")"
SLOT="${PON_CLEAN%%/*}"
PON_REST="${PON_CLEAN#*/}"
PON_PORT="${PON_REST%%/*}"

if [[ -z "$SLOT" || -z "$PON_PORT" || "$SLOT" == "$PON_CLEAN" ]]; then
  echo "Erro! PON inválida: '$PON_RAW'. Use o formato SLOT/PON, exemplo: 1/5." >&2
  exit 1
fi

if ! [[ "$STATUS" =~ ^[0-4]$ || "$STATUS" == "5" || "$STATUS" == "total" || "$STATUS" == "all" || "$STATUS" == "down" || "$STATUS" == "offline_total" || "$STATUS" == "indisponivel" || "$STATUS" == "indisponiveis" || "$STATUS" == "online_percent" || "$STATUS" == "online_pct" || "$STATUS" == "down_percent" || "$STATUS" == "down_pct" || "$STATUS" == "queda_percent" || "$STATUS" == "queda_pct" || "$STATUS" == "los_percent" || "$STATUS" == "los_pct" || "$STATUS" == "energy_percent" || "$STATUS" == "energy_pct" || "$STATUS" == "energia_percent" || "$STATUS" == "energia_pct" || "$STATUS" == "json" ]]; then
  echo "Erro! Status inválido: '$STATUS'. Use 0/1/2/3/4, total, down, online_percent, down_percent ou json." >&2
  exit 1
fi

BASE="$(cache_base_for "$IP" "$COMMUNITY" "$PORT")"
NEED_STATUS="yes"
[[ "$STATUS" == "total" || "$STATUS" == "all" || "$STATUS" == "5" ]] && NEED_STATUS="no"

refresh_needed_columns "$IP" "$COMMUNITY" "$PORT" "$TIMEOUT" "$RETRIES" "$CACHE_TTL" "$BASE" "$NEED_STATUS"
rc=$?
if [[ $rc -ne 0 ]]; then
  # Importante para itens dependentes do Zabbix:
  # quando o item mestre usa STATUS=json, nunca podemos retornar somente "0",
  # pois o pré-processamento JSONPath dos itens dependentes fica não suportado.
  # Se existir cache antigo válido, usamos o cache. Se não existir, retornamos JSON zerado.
  if [[ "$STATUS" == "json" ]]; then
    if [[ -s "${BASE}.slot" && -s "${BASE}.pon" && -s "${BASE}.status" ]]; then
      count_or_percent "$BASE" "$SLOT" "$PON_PORT" "$STATUS"
    else
      printf '{"total":0,"online":0,"offline":0,"los":0,"sem_dados":0,"sem_energia":0,"down":0,"online_percent":0.00,"down_percent":0.00,"los_percent":0.00,"energy_percent":0.00}
'
    fi
  else
    echo 0
  fi
  exit 0
fi

if [[ "$NEED_STATUS" == "no" ]]; then
  # total só precisa de slot/pon, mas a função completa também funciona se status existir.
  # Mantemos a versão antiga para garantir total mesmo sem status.
  awk -v wanted_slot="$SLOT" -v wanted_pon="$PON_PORT" '
    FILENAME ~ /\.slot$/ { slot[$1]=$2; next }
    FILENAME ~ /\.pon$/  { pon[$1]=$2; next }
    END { count=0; for (idx in pon) if (slot[idx] == wanted_slot && pon[idx] == wanted_pon) count++; print count }
  ' "${BASE}.slot" "${BASE}.pon"
else
  count_or_percent "$BASE" "$SLOT" "$PON_PORT" "$STATUS"
fi
