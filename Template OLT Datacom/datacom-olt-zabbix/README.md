# Template Datacom DM4615 GPON para Zabbix

Template em portugues para monitoramento de OLT Datacom DM4615 GPON no Zabbix 7.

O projeto combina coletas SNMP com um script externo via Telnet para obter dados que a OLT nao entrega de forma completa por SNMP, como contadores de ONUs por PON, estado de ONUs e sessoes PPPoE vistas pelo intermediate-agent.

Todos os exemplos abaixo usam dados ficticios.

## Recursos

- Descoberta de interfaces por SNMP.
- Descoberta separada de uplinks `gigabit-ethernet-*` e `ten-gigabit-ethernet-*`.
- Descoberta de PONs `gpon-*`.
- Contadores por PON: ONUs autorizadas, online e offline.
- Descoberta de ONUs via Telnet.
- Consulta de PPPoE por ONU: sessao ativa e MAC remoto.
- Alertas de PON e uplink com severidade Desastre.
- Alertas individuais de ONU offline removidos para reduzir ruido operacional.

## Arquivos

- `templates/template_0wnet_datacom_dm4615_corrigido_zabbix7.yaml`: template para importar no Zabbix.
- `scripts/datacom_dm4615_onu.py`: script externo usado pelas descobertas e itens de ONU/PPPoE.

## Requisitos

- Zabbix 7.x.
- Host com interface SNMP configurada.
- SNMP v2c liberado entre Zabbix e OLT.
- Telnet liberado entre Zabbix e OLT.
- Usuario Telnet com permissao para executar comandos `show`.
- Python 3 no servidor/proxy Zabbix que executa external scripts.

## Passo a passo manual

### 1. Copiar o script para external scripts

No servidor ou proxy Zabbix responsavel pela coleta:

```bash
sudo install -m 0755 scripts/datacom_dm4615_onu.py /usr/lib/zabbix/externalscripts/datacom_dm4615_onu.py
sudo chown root:root /usr/lib/zabbix/externalscripts/datacom_dm4615_onu.py
```

Se o seu ambiente usa outro diretorio de external scripts, confira o parametro `ExternalScripts` no arquivo de configuracao do Zabbix Server ou Proxy.

### 2. Testar o script manualmente

Use dados ficticios abaixo como exemplo:

```bash
/usr/lib/zabbix/externalscripts/datacom_dm4615_onu.py raw 192.0.2.10 'usuario_exemplo' 'senha_exemplo' gpon-1/1/1
/usr/lib/zabbix/externalscripts/datacom_dm4615_onu.py pon-count 192.0.2.10 'usuario_exemplo' 'senha_exemplo' gpon-1/1/1 online
/usr/lib/zabbix/externalscripts/datacom_dm4615_onu.py onu-lld 192.0.2.10 'usuario_exemplo' 'senha_exemplo'
/usr/lib/zabbix/externalscripts/datacom_dm4615_onu.py onu-value 192.0.2.10 'usuario_exemplo' 'senha_exemplo' gpon-1/1/1 1 pppoe
```

Resultados esperados:

- `raw`: deve retornar a tabela de ONUs da PON.
- `pon-count`: deve retornar um numero.
- `onu-lld`: deve retornar JSON LLD.
- `pppoe`: deve retornar `Session ID` e `Remote MAC`, ou vazio quando nao houver sessao.

### 3. Importar o template

No frontend do Zabbix:

1. Acesse `Data collection` > `Templates`.
2. Clique em `Import`.
3. Selecione `templates/template_0wnet_datacom_dm4615_corrigido_zabbix7.yaml`.
4. Marque criacao/atualizacao de templates, itens, descobertas, triggers, graficos e value maps.
5. Clique em `Import`.

### 4. Vincular o template ao host

No host da OLT:

1. Configure a interface SNMP com o IP da OLT, por exemplo `192.0.2.10`.
2. Vincule o template `0Wnet - Datacom DM4615 GPON corrigido`.
3. Configure as macros do host.

Macros obrigatorias:

- `{$SNMP_COMMUNITY}`: comunidade SNMP, se nao for herdada de macro global.
- `{$DATACOM.TELNET.USER}`: usuario Telnet da OLT.
- `{$DATACOM.TELNET.PASSWORD_REF}`: referencia para arquivo local com a senha Telnet, por padrao `file:/etc/zabbix/datacom_dm4615_telnet.pass`.

Para evitar que a senha apareca na lista de processos, grave a senha em arquivo no servidor Zabbix:

```bash
sudo install -o zabbix -g zabbix -m 600 /dev/null /etc/zabbix/datacom_dm4615_telnet.pass
sudo bash -c 'read -rsp "Senha Telnet: " pass; echo; printf "%s\n" "$pass" > /etc/zabbix/datacom_dm4615_telnet.pass'
```

Macros opcionais de ajuste:

- `{$DATACOM.PON.DOWN.MIN.ONUS}`: minimo de ONUs autorizadas para alertar queda total.
- `{$DATACOM.PON.MONITOR}`: habilita alertas de PON. Padrao `1`.
- `{$DATACOM.PON.MASS.DOWN.MIN.ONUS}`: minimo historico de ONUs online para avaliar queda massiva.
- `{$DATACOM.PON.MASS.DOWN.PCT}`: percentual restante de ONUs online para classificar queda massiva.
- `{$DATACOM.UPLINK.IFNAME.MATCHES}`: regex de nomes de interfaces consideradas uplink.
- `{$DATACOM.UPLINK.TRAFFIC.MIN.BPS}`: trafego minimo nas ultimas 24h para considerar uma porta uplink em uso.

Para manter uma PON descoberta, mas sem alerta porque ela nao esta em uso, crie uma macro contextual no host:

```text
{$DATACOM.PON.MONITOR:"gpon-1/1/16"} = 0
```

Quando essa macro contextual esta em `0`, os alertas daquela PON deixam de abrir e o alerta de PON down pode recuperar mesmo que a porta continue fisicamente down.

### 5. Executar as descobertas

No host, execute manualmente:

- `Descoberta de CPU e memoria`
- `Descoberta de interfaces`
- `Descoberta de uplinks`
- `Descoberta de PONs GPON`
- `Descoberta de ONUs via Telnet`

Depois confira se foram criados itens de PON, uplink, ONU e PPPoE.

### 6. Ajustar capacidade do Zabbix server

Este template usa checks externos via Telnet. Para evitar alertas de uso alto de `poller` e `icmp pinger`, ajuste o servidor Zabbix conforme a carga do ambiente:

```ini
StartPollers=20
StartPingers=5
StartPollersUnreachable=5
```

Depois reinicie o servidor Zabbix:

```bash
sudo systemctl restart zabbix-server
```

## Logica dos alertas de PON

O template usa o estado fisico da PON junto com contadores de ONUs para separar cenarios comuns:

- `PON down - provavel rompimento, SFP ou falha da porta GPON`: dispara quando a interface GPON fica diferente de `Up`, a PON esta habilitada por `{$DATACOM.PON.MONITOR:"{#PONNAME}"}`, existe ONU autorizada e houve ONU online nos ultimos 30 minutos.
- `PON up sem ONUs online - provavel falta de energia na localidade ou rompimento apos splitter`: dispara quando a PON continua fisicamente `Up`, mas todas as ONUs ficam sem comunicacao por 30 minutos.
- `PON com queda massiva de ONUs`: dispara quando a PON continua `Up`, possui pelo menos `{$DATACOM.PON.MASS.DOWN.MIN.ONUS}` ONUs autorizadas no momento e a quantidade online fica por 30 minutos ate `{$DATACOM.PON.MASS.DOWN.PCT}` do melhor valor das ultimas 24h.

Esses alertas usam severidade `Desastre`.

## Alertas de uplink

A descoberta de uplinks filtra interfaces por:

- `gigabit-ethernet-*`
- `ten-gigabit-ethernet-*`

O alerta `Uplink {#IFNAME} down` dispara quando a porta fica diferente de `Up` e teve trafego acima de `{$DATACOM.UPLINK.TRAFFIC.MIN.BPS}` nas ultimas 24h.

Esse alerta usa severidade `Desastre`.

## ONUs individuais

Os itens individuais de ONU sao mantidos para consulta e base de calculo, mas o alerta individual `ONU offline` nao faz parte do template para evitar ruido operacional.

O foco do monitoramento fica em:

- PON down.
- PON sem ONUs online.
- Queda massiva de ONUs por PON.
- Uplink down.

## PPPoE por ONU

A OLT Datacom DmOS expoe sessoes PPPoE pelo comando:

```text
show pppoe intermediate-agent sessions interface gpon 1/1/1
```

O template coleta, por ONU:

- `PPPoE ativo`: `1` quando existe sessao PPPoE ativa na ONU, `0` quando nao existe.
- `PPPoE sessao e MAC remoto`: retorna `Session ID` e `Remote MAC` da sessao vista pela OLT.

Observacao: no equipamento validado, esse comando nao mostrou o usuario/login PPPoE, apenas `Session ID` e `Remote MAC`.

## Boas praticas antes de publicar

- Nao publique walks reais de SNMP.
- Nao publique IPs, nomes de hosts, usuarios, senhas, seriais, MACs, descricoes de clientes ou logins PPPoE reais.
- Use sempre exemplos de documentacao, como `192.0.2.10`, `OLT-DATACOM-EXEMPLO`, `usuario_exemplo` e `senha_exemplo`.
