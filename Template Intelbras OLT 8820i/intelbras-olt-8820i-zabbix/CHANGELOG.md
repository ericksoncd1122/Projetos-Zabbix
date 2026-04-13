# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

Este projeto segue a ideia de versionamento semântico, adaptada à evolução do template e da documentação.

## [1.0.0] - 2026-04-13

### Adicionado
- Primeira versão pública do projeto para monitoramento da **Intelbras OLT 8820i** no **Zabbix 7.0**.
- Coleta SNMP validada em equipamento real, com levantamento de OIDs por `snmpget`, `snmpgetnext` e `snmpwalk`.
- Itens de sistema para CPU, memória total, memória livre, uptime, nome e descrição do equipamento.
- Descoberta automática de **ONUs** via LLD.
- Descoberta automática de **interfaces ópticas/SFPs** via LLD.
- Descoberta automática de **interfaces IF-MIB** via LLD.
- Itens dependentes para tratamento de valores ópticos retornados como `--`.
- Trigger de indisponibilidade por ICMP.
- Trigger de CPU alta.
- Trigger de memória livre baixa.
- Trigger de temperatura alta de módulo óptico.
- Trigger agregada para **queda total de ONUs por porta PON**, útil para detecção de possível rompimento.

### Alterado
- Ajustada a lógica do monitoramento para priorizar alertas operacionais realmente úteis em ambiente ISP.
- Intervalo de coleta do `walk` de ONUs definido em **3 minutos**.
- Trigger de queda total por PON configurada para **1 coleta**, reduzindo o tempo de detecção para cerca de **3 minutos**.

### Removido
- Alertas individuais de **ONU inativa**.
- Alertas individuais de **OMCI inativo**.
- Alertas individuais de **RX da ONU abaixo de -28 dBm**.
- Alertas individuais de **RX da OLT abaixo de -28 dBm**.

### Observações
- Os itens removidos como alerta continuam presentes no template para consulta, histórico, troubleshooting e uso em gráficos.
- O template foi desenhado para reutilização em outras OLTs do mesmo modelo, desde que os OIDs respondam de forma compatível.

## [Unreleased]

### Ideias para próximas versões
- Gráficos prontos por porta PON.
- Itens agregados por porta para acompanhamento de degradação parcial.
- Dashboards prontos para Zabbix ou Grafana.
- Mapeamento mais detalhado dos estados OMCI e ativo.
- Ajustes de severidade e event tags para correlação mais refinada.
