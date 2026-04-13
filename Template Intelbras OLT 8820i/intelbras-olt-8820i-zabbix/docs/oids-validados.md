# OIDs validados - Intelbras OLT 8820i

Este documento reúne os **OIDs validados em coleta real** na **Intelbras OLT 8820i**, usados como base para o template Zabbix deste projeto.

> Importante: os OIDs abaixo foram confirmados em ambiente real por meio de `snmpget`, `snmpgetnext` e `snmpwalk`. Em versões diferentes de firmware, algum comportamento pode variar.

## Ambiente usado na validação

- Modelo: **Intelbras OLT 8820i**
- Protocolo: **SNMP v2c**
- Zabbix alvo: **7.0**
- Método de validação: `snmpget`, `snmpgetnext`, `snmpwalk`

---

## 1. OIDs gerais do sistema

### CPU
```text
.1.3.6.1.4.1.2021.11.9.0
```
Uso de CPU em percentual.

### Memória total
```text
.1.3.6.1.4.1.2021.4.5.0
```
Memória total reportada pelo agente SNMP.

### Memória livre
```text
.1.3.6.1.4.1.2021.4.6.0
```
Memória livre reportada pelo agente SNMP.

### Uptime
```text
.1.3.6.1.2.1.1.3.0
```
Tempo desde o último boot.

### System description
```text
.1.3.6.1.2.1.1.1.0
```
Descrição do equipamento.

### System name
```text
.1.3.6.1.2.1.1.5.0
```
Nome do equipamento.

### System location
```text
.1.3.6.1.2.1.1.6.0
```
Localização cadastrada no dispositivo.

---

## 2. Raiz privada Intelbras

### Enterprise Intelbras
```text
.1.3.6.1.4.1.26138
```
Raiz privada do fabricante.

### Tabela privada de interfaces ópticas / SFPs
```text
.1.3.6.1.4.1.26138.1.1.1.1.1
```
Usada para descoberta e leitura dos módulos ópticos.

### Tabela privada de ONUs
```text
.1.3.6.1.4.1.26138.1.2.1.1.1
```
Usada para descoberta e leitura das ONUs.

---

## 3. OIDs da tabela de ONUs

Base:
```text
.1.3.6.1.4.1.26138.1.2.1.1.1
```

### Índice da ONU
```text
.1.3.6.1.4.1.26138.1.2.1.1.1.1
```
Índice interno usado na tabela.

### Porta PON
```text
.1.3.6.1.4.1.26138.1.2.1.1.1.2
```
Número da porta PON à qual a ONU pertence.

### ONU ID
```text
.1.3.6.1.4.1.26138.1.2.1.1.1.3
```
Identificador da ONU dentro da porta.

### ONU registrada
```text
.1.3.6.1.4.1.26138.1.2.1.1.1.4
```
Status de registro da ONU.

### ONU ativa
```text
.1.3.6.1.4.1.26138.1.2.1.1.1.5
```
Status operacional/ativo da ONU.

### Serial da ONU
```text
.1.3.6.1.4.1.26138.1.2.1.1.1.6
```
Serial reportado pela OLT.

### Estado OMCI
```text
.1.3.6.1.4.1.26138.1.2.1.1.1.7
```
Estado relacionado ao gerenciamento OMCI.

### RX da ONU visto pela OLT
```text
.1.3.6.1.4.1.26138.1.2.1.1.1.8
```
Potência óptica recebida pela OLT referente à ONU.

### RX da OLT visto pela ONU
```text
.1.3.6.1.4.1.26138.1.2.1.1.1.9
```
Potência óptica recebida pela ONU.

### Observações sobre os OIDs de potência das ONUs
- Os valores foram retornados como **STRING**, por exemplo: `-27.70`.
- Em alguns casos a OLT retorna `--` quando não há leitura válida.
- No template, esses campos são tratados com item mestre + item dependente + pré-processamento para evitar `unsupported`.

---

## 4. OIDs da tabela de interfaces ópticas / SFPs

Base:
```text
.1.3.6.1.4.1.26138.1.1.1.1.1
```

### Índice
```text
.1.3.6.1.4.1.26138.1.1.1.1.1.1
```
Índice interno da interface/módulo.

### Nome da interface
```text
.1.3.6.1.4.1.26138.1.1.1.1.1.2
```
Exemplos observados: `eth1`, `gpon1`, `xeth1`.

### Presença / estado do módulo
```text
.1.3.6.1.4.1.26138.1.1.1.1.1.3
```
Indica o estado do módulo óptico associado à interface.

### Vendor / descrição
```text
.1.3.6.1.4.1.26138.1.1.1.1.1.4
```
Informação textual do fabricante/modelo do transceptor.

### Part number
```text
.1.3.6.1.4.1.26138.1.1.1.1.1.5
```
Part number reportado pelo módulo.

### Temperatura
```text
.1.3.6.1.4.1.26138.1.1.1.1.1.6
```
Temperatura do módulo. Em muitas interfaces sem módulo, pode retornar `--`.

### Tensão
```text
.1.3.6.1.4.1.26138.1.1.1.1.1.7
```
Tensão do módulo óptico.

### TX Bias
```text
.1.3.6.1.4.1.26138.1.1.1.1.1.8
```
Corrente de bias do transmissor.

### TX Power
```text
.1.3.6.1.4.1.26138.1.1.1.1.1.9
```
Potência óptica de transmissão.

### RX Power
```text
.1.3.6.1.4.1.26138.1.1.1.1.1.10
```
Potência óptica de recepção.

### Observações sobre os OIDs ópticos dos SFPs
- Também retornam frequentemente como **STRING**.
- Interfaces sem módulo ou sem leitura podem retornar `--`.
- O template trata esses campos com pré-processamento para manter estabilidade.

---

## 5. IF-MIB padrão validada

Além da MIB privada, a IF-MIB padrão também respondeu corretamente e foi usada no template.

### ifDescr
```text
.1.3.6.1.2.1.2.2.1.2
```
Descrição da interface.

### ifOperStatus
```text
.1.3.6.1.2.1.2.2.1.8
```
Status operacional da interface.

### ifName
```text
.1.3.6.1.2.1.31.1.1.1.1
```
Nome lógico da interface.

### ifHCInOctets
```text
.1.3.6.1.2.1.31.1.1.1.6
```
Tráfego de entrada em octetos (64 bits).

### ifHCOutOctets
```text
.1.3.6.1.2.1.31.1.1.1.10
```
Tráfego de saída em octetos (64 bits).

---

## 6. O que entrou no template a partir desses OIDs

Com base na validação, o template passou a incluir:

- Itens de sistema para CPU, memória e uptime.
- Descoberta automática de ONUs.
- Descoberta automática de SFPs/interfaces ópticas.
- Descoberta automática de interfaces padrão via IF-MIB.
- Itens dependentes para valores ópticos.
- Trigger agregada de **queda total de ONUs por porta PON**.

---

## 7. Recomendações para novas validações

Se você for validar outra 8820i ou outra versão de firmware, siga esta ordem:

1. Teste conectividade com `ping`.
2. Teste `sysDescr.0` e `sysUpTime.0` com `snmpget`.
3. Valide a raiz `.1.3.6.1.4.1.26138` com `snmpgetnext`.
4. Faça `snmpwalk` por coluna, não na árvore inteira de uma vez.
5. Verifique se os campos ópticos retornam número ou `--`.
6. Só depois ajuste o template.

---

## 8. Observação final

Este documento serve como referência técnica para o template publicado neste repositório. Ele pode ser expandido futuramente com:

- mapeamento dos estados inteiros de OMCI;
- interpretação exata dos valores de status da ONU;
- exemplos por firmware;
- novos OIDs descobertos em laboratório ou produção.
