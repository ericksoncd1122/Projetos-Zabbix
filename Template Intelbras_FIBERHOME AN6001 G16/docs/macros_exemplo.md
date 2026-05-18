# Macros de exemplo para o host Zabbix

Use estes valores como modelo. Substitua `192.0.2.10` e `public` pelos dados da sua OLT.

| Macro | Exemplo | Descrição |
|---|---:|---|
| `{$OLT.SNMP.IP}` | `192.0.2.10` | IP ou DNS que o script externo `ponfh` usará para consultar a OLT. |
| `{$SNMP_COMMUNITY}` | `public` | Community SNMP v2c da OLT. |
| `{$SNMP_PORT}` | `161` | Porta SNMP. |
| `{$SNMP_TIMEOUT}` | `1` | Timeout, em segundos, para cada consulta SNMP do script. |
| `{$SNMP_RETRIES}` | `0` | Tentativas extras por consulta SNMP. |
| `{$PONFH.CACHE_TTL}` | `300` | Cache local do script, em segundos. |
| `{$ONU.PON.MIN.CLIENTES}` | `1` | Mínimo de ONUs autorizadas para validar alerta de PON. |
| `{$ONU.ENERGIA.REGIAO.MIN}` | `5` | Mínimo de ONUs sem energia na mesma PON para alertar região sem energia. |
| `{$ONU.QUEDA30.PERCENT}` | `30` | Percentual para alerta de queda parcial de clientes. |
| `{$ONU.QUEDA50.PERCENT}` | `50` | Percentual para alerta de queda mais severa de clientes. |
| `{$IF.LINKDOWN.MIN.BPS}` | `1000` | Tráfego mínimo nas últimas 24h para alertar link down em SFP/Ethernet/GF. |

> Para uso público, não coloque IPs reais, nomes reais de OLTs, communities reais ou dados do seu provedor no repositório.
