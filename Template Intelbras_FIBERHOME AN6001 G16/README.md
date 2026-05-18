# Template Zabbix — OLT Intelbras / FiberHome AN6001-G16 via SNMP

Template para monitoramento de OLTs **Intelbras FiberHome AN6001-G16 / família AN6000** no **Zabbix 7.x**, usando SNMP e um script externo para consolidar informações de PON/ONUs diretamente da OLT.

O projeto foi pensado para uso em ambiente de provedor e para compartilhamento público. Por isso, os arquivos deste pacote **não possuem IPs reais, communities reais, nomes reais de OLTs ou dados sensíveis**.

---

## Visão geral

Este pacote contém:

```text
.
├── README.md
├── .gitignore
├── docs/
│   └── macros_exemplo.md
├── scripts/
│   ├── ponfh
│   └── ponfh.sh
└── templates/
    └── zabbix_template_intelbras_fiberhome_an6001g16_snmp_v5_24_public.yaml
```

### Arquivos principais

| Arquivo | Função |
|---|---|
| `templates/zabbix_template_intelbras_fiberhome_an6001g16_snmp_v5_24_public.yaml` | Template pronto para importação no Zabbix. |
| `scripts/ponfh` | Script externo usado pelo Zabbix. Deve ser instalado em `/usr/lib/zabbix/externalscripts/ponfh`. |
| `scripts/ponfh.sh` | Mesmo script com extensão `.sh`, útil para leitura, edição e versionamento. |
| `docs/macros_exemplo.md` | Tabela de macros para configurar cada host de OLT. |

---

## O que o template monitora

### Chassi da OLT

- Descrição do equipamento.
- Temperatura.
- Uptime.
- Status geral de ventoinhas, quando o OID existir no equipamento.

### Cards e slots

- Descoberta automática de cards/slots.
- Tipo de card.
- Status operacional.
- CPU por card.
- Memória por card.
- Versão de hardware/software, quando disponível via SNMP.

### CPU e memória da gerência

- Descoberta da gerência.
- CPU da gerência.
- Memória da gerência.

### Interfaces via IF-MIB

- Descoberta automática de interfaces.
- Tráfego RX/TX.
- Velocidade.
- Status administrativo e operacional.
- Erros e descartes.
- Gráficos de tráfego.
- Gráficos de erros e descartes.

> Por padrão, as interfaces PON são ignoradas na regra de link down por IF-MIB para evitar falsos positivos. A PON é monitorada pela lógica de status das ONUs.

### ONUs

- Descoberta de ONUs autorizadas.
- Nome.
- Serial/LOID.
- MAC.
- Status.
- Sinal RX.
- Sinal TX.

> Por padrão, a descoberta individual de ONUs considera apenas ONUs online para evitar itens não suportados em ONUs sem dados/offline, onde alguns OIDs podem não existir.

### PONs e eventos operacionais

O template usa o script `ponfh` para consolidar status de ONUs por PON diretamente via SNMP.

Itens principais por PON:

- Total de ONUs autorizadas.
- ONUs online.
- ONUs offline.
- ONUs em LOS.
- ONUs sem dados.
- ONUs sem energia.
- Clientes offline/indisponíveis.
- Clientes online (%).
- Clientes offline/indisponíveis (%).

Alertas importantes:

- **PON 1/x down, possível rompimento**: dispara quando todas as ONUs autorizadas da PON estão em LOS.
- **PON 1/x: região sem energia, clientes off por falta de energia**: dispara quando várias ONUs da mesma PON entram em estado sem energia/Dying Gasp.
- Queda parcial de clientes por PON.
- Link down de SFP/Ethernet/GF somente quando houve tráfego nas últimas 24h.

---

## Requisitos

### No Zabbix

- Zabbix Server ou Zabbix Proxy com suporte a external scripts.
- Template testado em Zabbix 7.x.
- Host da OLT com interface SNMP configurada.
- SNMP v2c habilitado na OLT.

### No Linux que executa a coleta

Instale o pacote SNMP:

```bash
sudo apt update
sudo apt install -y snmp
```

Para distribuições baseadas em RHEL/CentOS/Alma/Rocky:

```bash
sudo dnf install -y net-snmp-utils
```

---

## Instalação do script externo

No servidor Zabbix ou no Zabbix Proxy responsável por coletar a OLT, copie o script para a pasta de external scripts.

### Debian/Ubuntu com Zabbix Server

```bash
sudo cp scripts/ponfh /usr/lib/zabbix/externalscripts/ponfh
sudo chown zabbix:zabbix /usr/lib/zabbix/externalscripts/ponfh
sudo chmod +x /usr/lib/zabbix/externalscripts/ponfh
```

Confirme:

```bash
ls -lh /usr/lib/zabbix/externalscripts/ponfh
```

O resultado deve mostrar permissão de execução, por exemplo:

```text
-rwxr-xr-x 1 zabbix zabbix ... /usr/lib/zabbix/externalscripts/ponfh
```

### Quando usar Zabbix Proxy

Se o host da OLT for monitorado por proxy, o script precisa estar no **proxy**, não apenas no servidor principal:

```bash
sudo cp scripts/ponfh /usr/lib/zabbix/externalscripts/ponfh
sudo chown zabbix:zabbix /usr/lib/zabbix/externalscripts/ponfh
sudo chmod +x /usr/lib/zabbix/externalscripts/ponfh
```

Depois recarregue o cache do proxy:

```bash
sudo zabbix_proxy -R config_cache_reload
```

---

## Testes manuais do script

Substitua:

```text
192.0.2.10      -> IP da sua OLT
public          -> community SNMP da sua OLT
```

### Testar resumo JSON de uma PON

```bash
sudo -u zabbix /usr/lib/zabbix/externalscripts/ponfh "1_4" "json" "192.0.2.10" "public" "161" "1" "0" "300"
```

O retorno esperado é JSON válido, por exemplo:

```json
{"total":21,"online":14,"offline":0,"los":1,"sem_dados":6,"sem_energia":0,"down":7,"online_percent":66.67,"down_percent":33.33,"los_percent":4.76,"energy_percent":0.00}
```

### Testar uma PON sem ONUs

```bash
sudo -u zabbix /usr/lib/zabbix/externalscripts/ponfh "1_15" "json" "192.0.2.10" "public" "161" "1" "0" "300"
```

Mesmo sem ONUs, o retorno precisa ser JSON válido:

```json
{"total":0,"online":0,"offline":0,"los":0,"sem_dados":0,"sem_energia":0,"down":0,"online_percent":0.00,"down_percent":0.00,"los_percent":0.00,"energy_percent":0.00}
```

### Testar LLD de PONs via script

```bash
sudo -u zabbix /usr/lib/zabbix/externalscripts/ponfh --lld-v514 "192.0.2.10" "public" "161" "1" "0" "300"
```

Exemplo de retorno:

```json
{"data":[{"{#PON}":"1/1"},{"{#PON}":"1/2"},{"{#PON}":"1/3"},{"{#PON}":"1/4"}]}
```

---

## Importação do template no Zabbix

1. Acesse o Zabbix Web.
2. Vá em **Coleta de dados > Templates**.
3. Clique em **Importar**.
4. Selecione o arquivo:

```text
templates/zabbix_template_intelbras_fiberhome_an6001g16_snmp_v5_24_public.yaml
```

5. Mantenha as opções padrão de importação:
   - Atualizar existente: habilitado.
   - Criar novo: habilitado.
   - Excluir ausentes: opcional. Use com cuidado em ambiente de produção.
6. Clique em **Importar**.

---

## Criação/configuração do host da OLT

### 1. Criar host

Acesse:

```text
Coleta de dados > Hosts > Criar host
```

Preencha:

```text
Nome do host: OLT-EXEMPLO-AN6001G16
Nome visível: OLT-EXEMPLO-AN6001G16
Grupo: OLTs, Network devices ou o grupo usado no seu ambiente
```

### 2. Interface SNMP

Adicione uma interface SNMP:

```text
Tipo: SNMP
IP: 192.0.2.10
Conectar a: IP
Porta: 161
```

### 3. Vincular template

Na aba **Templates**, vincule:

```text
Template - OLT Intelbras FiberHome AN6001-G16 SNMP Direto V5.24 Unificado
```

### 4. Configurar macros no host

Na aba **Macros**, configure as macros abaixo. Nunca publique os valores reais em repositórios públicos.

| Macro | Exemplo público | Descrição |
|---|---:|---|
| `{$OLT.SNMP.IP}` | `192.0.2.10` | IP ou DNS usado pelo script externo `ponfh`. |
| `{$SNMP_COMMUNITY}` | `public` | Community SNMP v2c da OLT. |
| `{$SNMP_PORT}` | `161` | Porta SNMP. |
| `{$SNMP_TIMEOUT}` | `1` | Timeout do script para chamadas SNMP. |
| `{$SNMP_RETRIES}` | `0` | Tentativas extras. |
| `{$PONFH.CACHE_TTL}` | `300` | Tempo de cache local do script, em segundos. |
| `{$ONU.PON.MIN.CLIENTES}` | `1` | Mínimo de ONUs autorizadas para considerar alerta de PON. |
| `{$ONU.ENERGIA.REGIAO.MIN}` | `5` | Mínimo de ONUs sem energia na PON para alertar região sem energia. |
| `{$ONU.QUEDA30.PERCENT}` | `30` | Percentual para alerta de queda parcial. |
| `{$ONU.QUEDA50.PERCENT}` | `50` | Percentual para alerta de queda mais severa. |
| `{$IF.LINKDOWN.MIN.BPS}` | `1000` | Tráfego mínimo nas últimas 24h para alertar link down em SFP/Ethernet/GF. |

Exemplo:

```text
{$OLT.SNMP.IP}              = 192.0.2.10
{$SNMP_COMMUNITY}           = public
{$SNMP_PORT}                = 161
{$SNMP_TIMEOUT}             = 1
{$SNMP_RETRIES}             = 0
{$PONFH.CACHE_TTL}          = 300
{$ONU.PON.MIN.CLIENTES}     = 1
{$ONU.ENERGIA.REGIAO.MIN}   = 5
{$ONU.QUEDA30.PERCENT}      = 30
{$ONU.QUEDA50.PERCENT}      = 50
{$IF.LINKDOWN.MIN.BPS}      = 1000
```

> A macro `{$OLT.SNMP.IP}` é importante porque, em alguns ambientes, `{HOST.CONN}` pode resolver para o nome do host em vez do IP. O script precisa receber um IP ou DNS resolvível pelo servidor/proxy Zabbix.

---

## Recarregar cache do Zabbix

Após importar template, alterar macros ou atualizar o script:

### Zabbix Server

```bash
sudo zabbix_server -R config_cache_reload
```

### Zabbix Proxy

```bash
sudo zabbix_proxy -R config_cache_reload
```

Limpar cache local do script:

```bash
sudo rm -rf /tmp/ponfh_zabbix_*
```

---

## Executar descobertas manualmente

No Zabbix Web:

```text
Coleta de dados > Hosts > OLT > Regras de descoberta
```

Execute as regras principais:

```text
Descoberta de cards/slots da OLT
Descoberta de CPU e memória da gerência
Descoberta de interfaces de tráfego via IF-MIB
Descoberta de ONUs autorizadas e sinal óptico
Descoberta de portas PON - V5.14 forçada
```

Aguarde alguns minutos e confira:

```text
Monitoramento > Dados recentes
```

Pesquise por:

```text
PON 1/4
ONU 1/4
Interface
CPU
Memória
```

---

## Regras de alerta

### PON down / possível rompimento

O alerta dispara quando:

```text
Total de ONUs autorizadas da PON >= {$ONU.PON.MIN.CLIENTES}
E
Quantidade de ONUs em LOS = Total de ONUs autorizadas da PON
```

Nome do alerta:

```text
PON 1/x down, possível rompimento
```

### Região sem energia

O alerta dispara quando:

```text
Quantidade de ONUs sem energia na PON >= {$ONU.ENERGIA.REGIAO.MIN}
```

Nome do alerta:

```text
PON 1/x: região sem energia, clientes off por falta de energia
```

### Link down de interfaces SFP/Ethernet/GF

O alerta dispara quando:

```text
Interface operacional down
E
Interface administrativa up
E
Houve tráfego RX ou TX nas últimas 24h acima de {$IF.LINKDOWN.MIN.BPS}
```

Interfaces PON são ignoradas por padrão nessa regra, porque a PON é monitorada pela lógica de ONUs.

### Queda parcial de clientes por PON

O template possui itens e triggers para queda parcial por percentual:

```text
{$ONU.QUEDA30.PERCENT} = 30
{$ONU.QUEDA50.PERCENT} = 50
```

---

## Como validar se o Zabbix bate com a OLT

### 1. Validar pelo script

```bash
sudo -u zabbix /usr/lib/zabbix/externalscripts/ponfh "1_4" "json" "192.0.2.10" "public" "161" "1" "0" "300"
```

### 2. Validar por SNMP direto

```bash
snmpwalk -v2c -c public 192.0.2.10 .1.3.6.1.4.1.5875.800.3.10.1.1.2
snmpwalk -v2c -c public 192.0.2.10 .1.3.6.1.4.1.5875.800.3.10.1.1.3
snmpwalk -v2c -c public 192.0.2.10 .1.3.6.1.4.1.5875.800.3.10.1.1.11
```

Status usado pelo script:

```text
0 = LOS
1 = Online
2 = Offline
3 = Sem dados
4 = Sem energia / Dying Gasp
```

---

## Troubleshooting

### Item externo retornando tudo zero

Verifique:

1. `{$OLT.SNMP.IP}` está configurado no host.
2. `{$SNMP_COMMUNITY}` está correto.
3. O servidor/proxy Zabbix resolve e alcança o IP da OLT.
4. A OLT permite SNMP a partir do servidor/proxy.
5. O script `ponfh` está executável.

Teste:

```bash
sudo -u zabbix /usr/lib/zabbix/externalscripts/ponfh "1_4" "json" "192.0.2.10" "public" "161" "1" "0" "300"
```

### `No Such Instance currently exists at this OID`

Isso pode ocorrer em ONUs offline, sem dados ou sem sinal. Por padrão, a descoberta individual de ONUs está filtrada para ONUs online:

```text
{$ONU.DISCOVERY.STATUS.MATCHES} = 1
```

Para descobrir todos os estados, altere para:

```text
{$ONU.DISCOVERY.STATUS.MATCHES} = (0|1|2|3|4)
```

### Alerta falso de interface PON down

A macro abaixo ignora PON na descoberta de interfaces IF-MIB:

```text
{$IF.DISCOVERY.NOT_MATCHES} = (^lo$|^LoopBack|^NULL|^InLoopBack|^PON)
```

A PON deve ser monitorada pelos status de ONU, não pelo IF-MIB.

### Timeout em external script

O `Timeout` do Zabbix Server/Proxy não deve ultrapassar o limite suportado pelo Zabbix. Use cache do script para reduzir carga:

```text
{$PONFH.CACHE_TTL} = 300
```

### Debug dos argumentos enviados pelo Zabbix

Adicione temporariamente no início do script, logo após `#!/bin/bash`:

```bash
echo "$(date '+%F %T') ARGS: [$1] [$2] [$3] [$4] [$5] [$6] [$7] [$8]" >> /tmp/ponfh_debug.log
```

Depois execute o item no Zabbix e confira:

```bash
cat /tmp/ponfh_debug.log
```

O esperado:

```text
ARGS: [1_4] [json] [192.0.2.10] [public] [161] [1] [0] [300]
```

Remova o debug depois do teste.

---

## Observações

- O script consulta diretamente a OLT via SNMP; não depende de banco externo.
- Para várias OLTs do mesmo modelo, o script é o mesmo. Configure apenas as macros do host.
- Se a OLT usar slot diferente de `1/x`, adapte os itens estáticos de alertas de PON ou use a parte dinâmica conforme sua topologia.
- Teste em laboratório antes de aplicar em produção.

---

## Créditos

Projeto criado para ajudar a comunidade técnica a monitorar OLTs Intelbras/FiberHome AN6001-G16 no Zabbix.

Contribuições, melhorias e correções são bem-vindas.
