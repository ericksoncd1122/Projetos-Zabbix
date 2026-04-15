# Intelbras G16 by SNMP para Zabbix 7

Template avançado para monitoramento da **OLT Intelbras G16** no **Zabbix 7**, com descoberta automática, itens dinâmicos, alertas operacionais e dashboards.

## Visão geral

Este projeto foi construído para monitorar a OLT Intelbras G16 utilizando **SNMP** e **scripts externos** do Zabbix, permitindo descoberta automática dos principais objetos do equipamento.

A solução foi ajustada em ambiente real a partir de `snmpwalk` da própria OLT, o que permitiu mapear corretamente a árvore privada da Intelbras (`1.3.6.1.4.1.13464`).

## O que o template monitora

### Sistema da OLT
- CPU
- Memória
- Temperatura do chipset switch
- Temperatura do chipset GPON
- Uptime
- Nome do sistema
- ICMP

### PONs
- Descoberta automática das portas `g0/1` a `g0/16`
- Status operacional
- RX Mbps
- TX Mbps
- RX pps
- TX pps
- RX utilização
- TX utilização
- Quantidade de ONUs total / online / offline por PON
- Alerta de PON down
- Alerta de “todas as ONUs offline” para indicar possível falta de energia/localidade ou rompimento quando a PON permanece operacional

### Uplinks Ethernet
- Descoberta automática das portas `e1/x` e `e2/x`
- Status operacional
- In bps
- Out bps
- Speed
- Alerta de link down apenas para interfaces relevantes

### SFPs / Transceivers
- Descoberta automática dos módulos
- Tipo do transceiver
- Classe
- Tipo de conector
- Número de série
- Fabricante
- Data de fabricação
- Temperatura
- Tensão
- Bias current
- RX power
- TX power

### ONUs
- Descoberta automática das ONUs por índice SNMP
- Status operacional
- Serial
- Vendor ID
- Device ID
- Tipo
- Distância
- Active/deactive time
- Main version
- Secondary version
- RX optical
- TX optical

### Dashboard
- Saúde do sistema
- Contadores de ONUs
- RX médio das ONUs online por PON
- Quantidade de ONUs online por PON
- Gráficos de PON
- Gráficos de uplink
- Gráficos de SFP
- Gráficos por ONU

## Arquivos finais do projeto

### Template final
- `template_intelbras_g16_zabbix7_final.yaml`

### Scripts finais
- `intelbras_g16_lld_v2.py` → discovery dinâmica de PON, uplink, SFP e ONU
- `intelbras_g16_panel_v1.py` → itens agregados usados no dashboard

## Pré-requisitos

- Zabbix Server 7.x
- Pacote `snmpwalk` instalado no servidor Zabbix
- Permissão para usar scripts externos
- Comunidade SNMP configurada na OLT
- Acesso do servidor Zabbix ao IP da OLT

No Debian/Ubuntu:

```bash
apt update
apt install -y snmp
```

### Instalação dos scripts no servidor Zabbix

Copie os dois scripts para o diretório de `externalscripts` do Zabbix.

Caminho mais comum:

```bash
/usr/lib/zabbix/externalscripts/
```

### Copiar os scripts

```bash
cp intelbras_g16_lld_v2.py /usr/lib/zabbix/externalscripts/
cp intelbras_g16_panel_v1.py /usr/lib/zabbix/externalscripts/
```

### Dar permissão de execução

```bash
chmod +x /usr/lib/zabbix/externalscripts/intelbras_g16_lld_v2.py
chmod +x /usr/lib/zabbix/externalscripts/intelbras_g16_panel_v1.py
```

### Ajustar proprietário, se necessário

```bash
chown root:root /usr/lib/zabbix/externalscripts/intelbras_g16_lld_v2.py
chown root:root /usr/lib/zabbix/externalscripts/intelbras_g16_panel_v1.py
```

## Testes manuais dos scripts

Substitua o IP e a community conforme o seu ambiente.

### Discovery

```bash
/usr/lib/zabbix/externalscripts/intelbras_g16_lld_v2.py pon <OLT_IP> <SNMP_COMMUNITY>
/usr/lib/zabbix/externalscripts/intelbras_g16_lld_v2.py uplink <OLT_IP> <SNMP_COMMUNITY>
/usr/lib/zabbix/externalscripts/intelbras_g16_lld_v2.py sfp <OLT_IP> <SNMP_COMMUNITY>
/usr/lib/zabbix/externalscripts/intelbras_g16_lld_v2.py onu <OLT_IP> <SNMP_COMMUNITY>
```

Os comandos acima devem retornar JSON com `data`.

### Painéis agregados

```bash
/usr/lib/zabbix/externalscripts/intelbras_g16_panel_v1.py pon_online <OLT_IP> <SNMP_COMMUNITY> 1
/usr/lib/zabbix/externalscripts/intelbras_g16_panel_v1.py pon_rx_avg <OLT_IP> <SNMP_COMMUNITY> 1
```

Exemplo esperado:

```text
15
-20.68
```

### Testar como usuário zabbix

É importante validar também com o usuário do serviço:

```bash
sudo -u zabbix /usr/lib/zabbix/externalscripts/intelbras_g16_lld_v2.py pon <OLT_IP> <SNMP_COMMUNITY>
sudo -u zabbix /usr/lib/zabbix/externalscripts/intelbras_g16_lld_v2.py uplink <OLT_IP> <SNMP_COMMUNITY>
sudo -u zabbix /usr/lib/zabbix/externalscripts/intelbras_g16_lld_v2.py sfp <OLT_IP> <SNMP_COMMUNITY>
sudo -u zabbix /usr/lib/zabbix/externalscripts/intelbras_g16_lld_v2.py onu <OLT_IP> <SNMP_COMMUNITY>

sudo -u zabbix /usr/lib/zabbix/externalscripts/intelbras_g16_panel_v1.py pon_online <OLT_IP> <SNMP_COMMUNITY> 1
sudo -u zabbix /usr/lib/zabbix/externalscripts/intelbras_g16_panel_v1.py pon_rx_avg <OLT_IP> <SNMP_COMMUNITY> 1
```

## Importação do template no Zabbix

1. Acesse **Coleta de dados → Templates → Importar**.
2. Selecione o arquivo `template_intelbras_g16_dynamic_zabbix7_fix17_dashboard_panels_fix_importl.yaml`.
3. Marque:
   - **Atualizar existente**
   - **Criar novo**
   - **Excluir ausentes**
4. Clique em **Importar**.

## Vincular o template ao host da OLT

1. Acesse **Coleta de dados → Hosts**.
2. Abra o host da OLT Intelbras G16.
3. Configure a interface SNMP com o IP correto da OLT.
4. Defina a comunidade SNMP.
5. Vincule o template importado.

### Macro importante

O template utiliza a macro:

```text
{$SNMP_COMMUNITY}
```

Defina essa macro no template ou diretamente no host.

Exemplo:

```text
{$SNMP_COMMUNITY} = <SNMP_COMMUNITY>
```

## Após a vinculação

Depois de vincular o template ao host:

1. Abra o host.
2. Vá em **Regras de descoberta**.
3. Execute manualmente:
   - `PON discovery`
   - `Ethernet uplink discovery`
   - `SFP discovery`
   - `ONU discovery`
4. Aguarde de 1 a 3 minutos.
5. Verifique se os itens descobertos começaram a ser criados.

## Itens esperados após a discovery

### PON
- `PON g0/1: RX Mbps`
- `PON g0/1: TX Mbps`
- `PON g0/1: Operational status`
- `PON g0/1: ONU total`
- `PON g0/1: ONU online`
- `PON g0/1: ONU offline`

### Uplink
- `Uplink e1/1: In bps`
- `Uplink e1/1: Out bps`
- `Uplink e1/1: Speed`
- `Uplink e1/1: Operational status`

### SFP
- `SFP g0/1: Temperature`
- `SFP g0/1: RX power`
- `SFP g0/1: TX power`
- `SFP g0/1: Vendor`
- `SFP g0/1: Serial`

### ONU
- `ONU PON 1 ID 1: Operational status`
- `ONU PON 1 ID 1: Serial`
- `ONU PON 1 ID 1: RX optical`
- `ONU PON 1 ID 1: TX optical`
- `ONU PON 1 ID 1: Device ID`
- `ONU PON 1 ID 1: Main version`

## Alertas implementados

- PON down
- Todas as ONUs offline em uma PON ativa
- Uplink down
- Alertas ambientais e de sistema relevantes

> Observação: alguns alertas de consulta, como utilização alta e memória alta, foram mantidos apenas como item/consulta conforme ajuste operacional realizado durante a validação.

## Troubleshooting

### 1. Os scripts funcionam no shell, mas não no Zabbix
- Teste como usuário `zabbix`
- Verifique permissões em `/usr/lib/zabbix/externalscripts/`
- Confirme o caminho configurado em `zabbix_server.conf`

### 2. A discovery não cria itens
- Execute manualmente as regras de descoberta
- Confira se os scripts retornam JSON válido com `data`
- Verifique se a macro `{$SNMP_COMMUNITY}` está correta

### 3. Itens ópticos aparecem vazios ou não suportados
- Valide os OIDs no equipamento com `snmpwalk`
- Algumas ONUs podem não retornar todos os campos ópticos
- Revise o firmware/modelo da ONU, se necessário

### 4. Dashboard não mostra dados
- Aguarde os primeiros ciclos de coleta
- Verifique os itens externos do painel
- Teste manualmente `intelbras_g16_panel_v1.py`

## Observações finais

Este projeto foi ajustado com base em validação prática em ambiente real, com foco em estabilidade da discovery, consistência dos itens e utilidade operacional no Zabbix.

Projetos futuros podem ampliar:
- dashboards mais detalhados
- painéis por localidade
- gatilhos ópticos avançados
- refinamentos por firmware/modelo de ONU

## Créditos

Iniciativa privada com foco em ajudar a comunidade a monitorar equipamentos Intelbras no Zabbix.

**Erickson Correa – Gestor em TI**
