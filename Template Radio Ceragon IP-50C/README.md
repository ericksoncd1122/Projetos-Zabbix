<img width="1280" height="720" alt="1693380828340" src="https://github.com/user-attachments/assets/abcb64c0-290b-4680-bc90-271d42fa05f5" />
# zabbix-ceragon-ip50c
Template de monitoramento SNMP para rádios Ceragon IP-50C no Zabbix 7.0.18
# Zabbix Template - Ceragon IP-50C

Template para monitoramento de rádios **Ceragon IP-50C** via **SNMP** no **Zabbix 7.0.18**.

## Visão geral

Este projeto foi criado para facilitar o monitoramento de rádios Ceragon IP-50C no Zabbix, com foco em disponibilidade, desempenho de interfaces e geração de alertas úteis para operação.

## Recursos incluídos

- Itens estáticos de sistema
- Item mestre de SNMP walk para interfaces
- Descoberta automática de interfaces via LLD
- Protótipos de itens para status, velocidade, tráfego, erros e descartes
- Protótipos de triggers para link down, alta utilização e alta taxa de erros
- Protótipo de gráfico de tráfego por interface

## Compatibilidade

- Equipamento: Ceragon IP-50C
- Protocolo: SNMP
- Plataforma alvo: Zabbix 7.0.18

## Como importar no Zabbix

1. Baixe o arquivo YAML deste repositório
2. No Zabbix, acesse Data collection > Templates
3. Clique em Import
4. Selecione o arquivo do template
5. Revise as regras de importação e confirme

## Estrutura do repositório
<img width="3808" height="1681" alt="image" src="https://github.com/user-attachments/assets/a8cbac8f-a325-45c0-a3f9-b00b20572460" />
<img width="2619" height="957" alt="image" src="https://github.com/user-attachments/assets/d4985ffe-9e9e-4cd5-a3df-85dbe1fbd5b9" />
<img width="2091" height="1411" alt="image" src="https://github.com/user-attachments/assets/62ced473-3259-4457-8f77-bcbc6ce6192e" />



