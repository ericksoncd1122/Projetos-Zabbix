# Origem do template

Este template foi criado a partir do modelo oficial que ja acompanha o **Zabbix 7**:

```text
MikroTik CRS317-1G-16SRM by SNMP
```

A copia publicada neste projeto recebeu o nome:

```text
0Wnet - MikroTik CRS317-1G-16SRM por SNMP
```

## O que foi alterado

- Traducao dos nomes de itens, triggers, eventos, descricoes, dashboard e mapas de valor para PT-BR.
- Aplicacao do prefixo `0Wnet -` no nome do template.
- Ajuste das referencias internas para apontarem para o nome da copia traduzida.

## O que foi mantido

- OIDs.
- Keys dos itens.
- Regras de descoberta.
- Macros tecnicas.
- Expressoes das triggers.
- Estrutura geral do template oficial.

## Nota de seguranca

O template nao contem IP real, senha, community SNMP real ou qualquer dado sensivel. Configure esses dados diretamente no host ou por macros do Zabbix conforme a politica do ambiente.
