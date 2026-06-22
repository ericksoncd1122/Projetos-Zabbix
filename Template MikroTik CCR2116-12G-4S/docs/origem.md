# Origem do template

Este template foi criado a partir da estrutura do template MikroTik CRS317 ja publicado neste repositorio:

```text
0Wnet - MikroTik CRS317-1G-16SRM por SNMP
```

A copia publicada para o CCR2116 recebeu o nome:

```text
0Wnet - MikroTik CCR2116-12G-4S por SNMP
```

## O que foi alterado

- Adaptacao do nome, descricao e identidade visual para o modelo MikroTik CCR2116-12G-4S+.
- Regeneracao dos UUIDs em formato UUIDv4 para importacao no Zabbix 7.0.
- Ajuste das referencias internas para apontarem para o nome da copia CCR2116.

## O que foi mantido

- OIDs.
- Keys dos itens.
- Regras de descoberta.
- Macros tecnicas.
- Expressoes das triggers.
- Estrutura geral de monitoramento MikroTik/RouterOS por SNMP.

## Validacao

- YAML validado localmente.
- Importacao testada via API no Zabbix 7.0.25.
- Template localizado apos importacao pelo nome `CCR2116`.
- Dry-run de vinculo executado no host de teste antes de qualquer vinculo real.

## Nota de seguranca

O template nao contem IP real, senha, community SNMP real ou qualquer dado sensivel. Configure esses dados diretamente no host ou por macros do Zabbix conforme a politica do ambiente.
