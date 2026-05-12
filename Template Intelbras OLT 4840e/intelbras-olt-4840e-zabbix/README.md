# Template Intelbras EPON 4840E para Zabbix

Template em português para monitoramento da **OLT Intelbras EPON 4840E** via **SNMP** no **Zabbix**.

Este projeto foi construído a partir de coleta real via `snmpwalk`, validação prática em ambiente de produção e diversos ajustes para tornar o template mais confiável, limpo e reutilizável em outras OLTs do mesmo modelo.

## Objetivo

Entregar um template pronto para uso, com descoberta automática, gráficos, alertas e dashboard, permitindo monitorar a OLT Intelbras EPON 4840E de forma organizada e sem depender de configuração manual porta por porta.

## Compatibilidade

- Zabbix 7.x
- OLT Intelbras EPON 4840E
- SNMP v2c

## Principais recursos

### Visão geral da OLT
- Nome do equipamento
- Descrição do equipamento
- Uptime
- CPU ociosa
- CPU em uso
- Memória total
- Memória livre
- Memória em uso (%)

### Descoberta automática de interfaces
- Descoberta via IF-MIB
- Estado operacional
- Tráfego de entrada
- Tráfego de saída
- Gráficos automáticos por interface

### Descoberta automática de PONs
- Estado operacional da PON
- Total de ONUs por PON
- ONUs online por PON
- Gráfico por PON com ONUs registradas e ativas

### Descoberta automática de ONUs
- Estado da ONU
- Sinal RX da ONU
- Gráfico individual de sinal RX por ONU

## Lógica dos alertas

### Alerta de interface down
O alerta de interface foi ajustado para evitar ruído.

Ele só dispara quando:
1. a interface fica down
2. a interface teve tráfego relevante nas últimas 24 horas

Com isso, interfaces sem uso não geram alerta indevido.

### Alerta de PON down
O alerta de PON foi ajustado para refletir um cenário operacional mais útil.

Ele só dispara quando:
1. a PON está down
2. existe pelo menos uma ONU cadastrada nessa PON
3. houve ONU online nessa PON nas últimas 24 horas
4. no momento atual todas as ONUs dessa PON estão offline

Esse comportamento ajuda a identificar situações compatíveis com:
- possível falta de energia
- possível rompimento
- falha total no segmento daquela PON

## Dashboard incluído

O template possui um painel único com:
- resumo de CPU e memória
- memória total e livre
- grade das PONs com ONUs registradas e ativas
- gráficos de tráfego das interfaces
- gráficos de sinal RX das ONUs

## Itens removidos para reduzir ruído

Durante os testes, alguns itens foram removidos por não agregarem valor prático ou gerarem confusão no uso diário:

- velocidade de interface
- extra state 20
- extra state 23
- último registro da ONU

## Arquivos principais

### Template
Arquivo YAML pronto para importação no Zabbix.

Exemplo de nome:
```text
template_intelbras_4840e_final_ptbr_v26_painel_unico.yaml
```

### Script de coleta SNMP
Script auxiliar para extrair informações da OLT e validar OIDs em ambiente Linux.

Exemplo de nome:
```text
intelbras_4840e_snmpwalk_publico.sh
```

## Como usar o script de coleta

### 1. Dar permissão de execução
```bash
chmod +x intelbras_4840e_snmpwalk_publico.sh
```

### 2. Executar informando IP e community
```bash
./intelbras_4840e_snmpwalk_publico.sh 192.0.2.10 COMMUNITY_SNMP
```

### 3. Resultado
O script cria uma pasta com vários arquivos `.walk`, incluindo:
- system.walk
- interfaces_ifmib.walk
- interfaces_ifx.walk
- vendor_general.walk
- onu_status.walk
- onu_opm.walk
- pon_status.walk
- pon_module.walk
- full_enterprise.walk

## Como importar o template no Zabbix

1. Acesse **Coleção de dados > Templates**
2. Clique em **Importar**
3. Selecione o arquivo YAML do template
4. Marque as opções:
   - Atualizar existente
   - Criar novo
   - Excluir ausentes
5. Importe o template
6. Vincule o template ao host da OLT

## Configuração do host no Zabbix

Ao criar o host da OLT no Zabbix:
- adicione interface SNMP
- configure SNMP v2c
- informe a community correspondente ao seu ambiente
- vincule o template

## Observações importantes

- Este projeto **não inclui dados sensíveis**, como IPs reais, communities reais ou informações internas de ambiente.
- O script público usa parâmetros informados em linha de comando para facilitar reutilização e publicação.
- O comportamento do template foi ajustado com foco em operação real, reduzindo alertas desnecessários.

## Possíveis melhorias futuras

- identificação mais amigável das ONUs com nome comercial ou serial, caso o equipamento exponha essa informação de forma consistente via SNMP
- widgets adicionais para contadores resumidos no dashboard
- expansão para outros modelos Intelbras EPON da mesma família

## Créditos

Projeto desenvolvido e ajustado em laboratório e ambiente real por iniciativa própria para apoiar o monitoramento de equipamentos no Zabbix.

**Créditos:** Erickson Correa - Gestor em TI

## Aviso

Este material é distribuído como base técnica para estudo, testes e uso operacional. Recomenda-se validar o comportamento do template no seu ambiente antes de aplicar em produção em larga escala.
