# Template Zabbix - MikroTik CCR2116-12G-4S+ via SNMP

Template para monitoramento do **MikroTik CCR2116-12G-4S+** via **SNMP** no **Zabbix 7.0**.

Este modelo foi criado seguindo a mesma base do template MikroTik CRS317 publicado neste repositorio, mantendo a estrutura de descobertas e os OIDs genericos do RouterOS/MikroTik.

Neste projeto, o template recebeu o nome personalizado:

```text
0Wnet - MikroTik CCR2116-12G-4S por SNMP
```

---

## Origem

- Template base: `0Wnet - MikroTik CRS317-1G-16SRM por SNMP`
- Origem da estrutura: template oficial MikroTik do Zabbix 7 adaptado em PT-BR
- Alteracao feita: adaptacao de identidade, descricao e referencias internas para o modelo CCR2116-12G-4S+
- Estrutura de monitoramento: mantida com descobertas dinamicas por SNMP

O objetivo e facilitar o uso em ambientes em portugues, mantendo compatibilidade com RouterOS e Zabbix 7.0 LTS.

---

## Recursos incluidos

O template inclui:

- monitoramento por ICMP;
- disponibilidade SNMP;
- informacoes de sistema;
- firmware, modelo e numero de serie;
- CPU;
- memoria;
- temperatura;
- interfaces de rede via descoberta automatica;
- modem LTE, quando aplicavel;
- interfaces wireless/AP, quando aplicavel;
- armazenamento;
- triggers de disponibilidade, desempenho e capacidade;
- graficos e dashboard de interfaces.

---

## Compatibilidade

- Zabbix: 7.0 LTS
- Equipamento: MikroTik CCR2116-12G-4S+
- Protocolo: SNMP
- Base do template: MikroTik/RouterOS por SNMP

---

## Estrutura

```text
.
├── README.md
├── docs/
│   └── origem.md
└── templates/
    └── template_0wnet_mikrotik_ccr2116_12g_4s_by_snmp.yaml
```

---

## Como importar no Zabbix

1. Acesse **Coleta de dados > Templates**.
2. Clique em **Importar**.
3. Selecione o arquivo:

```text
templates/template_0wnet_mikrotik_ccr2116_12g_4s_by_snmp.yaml
```

4. Mantenha as regras padrao de importacao:
   - criar ausentes;
   - atualizar existentes;
   - nao usar exclusao de itens ausentes sem revisao.
5. Confirme a importacao.

---

## Configuracao no host

No host MikroTik, configure a interface SNMP no Zabbix e defina a community SNMP conforme o seu ambiente.

Use macros do Zabbix para valores sensiveis e parametros ajustaveis. Nao grave community real diretamente no template.

---

## Observacao

Este template nao contem IP real, senha, community SNMP real ou qualquer dado sensivel. Configure esses dados diretamente no host ou por macros do Zabbix conforme a politica do ambiente.
