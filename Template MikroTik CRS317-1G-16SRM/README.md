# Template Zabbix - MikroTik CRS317-1G-16S+RM via SNMP

Template para monitoramento do **MikroTik CRS317-1G-16S+RM** via **SNMP** no **Zabbix 7.0**.

Este modelo **ja vem com o Zabbix 7** como template oficial:

```text
MikroTik CRS317-1G-16SRM by SNMP
```

Neste projeto, foi feita uma copia desse template oficial e aplicada apenas a traducao para **PT-BR**, com nome personalizado:

```text
0Wnet - MikroTik CRS317-1G-16SRM por SNMP
```

---

## Origem

- Template base: `MikroTik CRS317-1G-16SRM by SNMP`
- Origem: template oficial incluido no Zabbix 7
- Alteracao feita: traducao dos textos para PT-BR e aplicacao do prefixo `0Wnet -`
- Estrutura de monitoramento: mantida a partir do template oficial

O objetivo e facilitar o uso em ambientes em portugues, mantendo a compatibilidade e a estrutura original do template do Zabbix.

---

## Recursos incluidos

O template mantem os recursos do modelo oficial do Zabbix 7, incluindo:

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
- Equipamento: MikroTik CRS317-1G-16S+RM
- Protocolo: SNMP
- Base do template: oficial do Zabbix 7

---

## Estrutura

```text
.
├── README.md
├── docs/
│   └── origem.md
└── templates/
    └── template_0wnet_mikrotik_crs317_1g_16srm_by_snmp.yaml
```

---

## Como importar no Zabbix

1. Acesse **Coleta de dados > Templates**.
2. Clique em **Importar**.
3. Selecione o arquivo:

```text
templates/template_0wnet_mikrotik_crs317_1g_16srm_by_snmp.yaml
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

Este projeto nao substitui o template oficial original do Zabbix. Ele e uma copia traduzida e personalizada para facilitar a operacao em PT-BR.
