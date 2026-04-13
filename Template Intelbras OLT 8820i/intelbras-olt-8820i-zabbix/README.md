<img width="439" height="115" alt="zabbix" src="https://github.com/user-attachments/assets/730bf965-3b77-4d5e-89b0-ba47655a7144" />
<img width="394" height="128" alt="intelbras" src="https://github.com/user-attachments/assets/c664389f-c101-431a-a614-a59732af19d5" />

# Template Zabbix para Intelbras OLT 8820i via SNMP

Template completo para **monitoramento da OLT Intelbras 8820i no Zabbix 7.0** utilizando **SNMP v2c**, com **descoberta automática (LLD)** de ONUs, interfaces e módulos ópticos.

Este projeto foi construído com base em **coleta real via `snmpwalk` na própria OLT**, validando os OIDs que de fato respondem no equipamento, em vez de depender apenas da documentação do fabricante.

## Objetivo

Este repositório tem como objetivo disponibilizar um template pronto para uso no Zabbix, permitindo monitorar de forma padronizada múltiplas OLTs **Intelbras 8820i** com:

- Descoberta automática de ONUs
- Descoberta automática de portas/interfaces
- Descoberta automática de módulos ópticos/SFPs
- Monitoramento de CPU, memória e uptime
- Monitoramento de potência óptica das ONUs
- Monitoramento de temperatura, tensão e potência dos transceptores
- Alerta de **queda total de ONUs por porta PON**, útil para detecção de rompimento

---

## Compatibilidade

Testado com:

- **Zabbix 7.0**
- **SNMP v2c**
- **Intelbras OLT 8820i**

> O template foi desenhado para reutilização em outras OLTs do mesmo modelo. Dependendo da versão de firmware, algum OID pode variar. Nesse caso, basta validar novamente com `snmpwalk`.

---

## Estrutura sugerida do repositório

```text
intelbras-olt-8820i-zabbix/
├── README.md
├── LICENSE
├── templates/
│   └── template_intelbras_olt_8820i_snmp_zabbix_7_validado_v4.yaml
├── docs/
│   ├── oids-validados.md
│   ├── importacao-zabbix.md
│   └── troubleshooting.md
├── imagens/
│   ├── descoberta-onus.png
│   ├── descoberta-sfps.png
│   ├── itens-template.png
│   └── triggers-template.png
└── extras/
    └── exemplos-snmpwalk.txt
```

### O que colocar em cada pasta

**`templates/`**  
Arquivo YAML final para importação no Zabbix.

**`docs/oids-validados.md`**  
Lista dos OIDs testados e aprovados na OLT.

**`docs/importacao-zabbix.md`**  
Passo a passo rápido de importação, criação do host e configuração SNMP.

**`docs/troubleshooting.md`**  
Erros comuns, itens unsupported, timeout de SNMP, problemas de discovery, etc.

**`imagens/`**  
Prints do template, itens, descobertas e gráficos.

**`extras/`**  
Saídas de `snmpwalk`, exemplos de uso e material auxiliar.

---

## Recursos do template

### 1. Monitoramento geral da OLT

O template coleta os principais dados de saúde do equipamento:

- CPU
- Memória total
- Memória livre
- Uptime
- Informações básicas do sistema

### 2. Descoberta automática de ONUs

As ONUs são descobertas automaticamente via LLD, incluindo:

- Índice da ONU
- Porta PON
- ONU ID
- Status de registro
- Status de atividade
- Status OMCI
- Serial
- RX medido pela OLT
- RX medido pela ONU

Isso permite utilizar o mesmo template em várias OLTs sem precisar cadastrar ONU por ONU manualmente.

### 3. Descoberta automática de SFPs/interfaces ópticas

O template também descobre automaticamente os módulos ópticos da OLT, trazendo:

- Nome da interface
- Presença/estado do módulo
- Vendor
- Part number
- Temperatura
- Tensão
- TX Bias
- TX Power
- RX Power

### 4. Descoberta automática de interfaces via IF-MIB

Além da MIB privada da Intelbras, o template usa IF-MIB padrão para monitorar:

- Nome da interface
- Status operacional
- Velocidade
- Tráfego de entrada
- Tráfego de saída

---

## Alerta principal do projeto

O foco principal deste template é detectar **rompimento de PON**.

Foi implementado um alerta que verifica quando:

- uma porta PON possui ONUs registradas;
- e a quantidade de ONUs ativas nessa porta cai para **zero**.

### Tempo de detecção

O template está ajustado para:

- **walk de ONUs a cada 3 minutos**;
- disparo do alerta com **1 coleta**.

Na prática, isso permite identificar queda total de uma PON em cerca de **3 minutos**, mantendo um equilíbrio entre velocidade e estabilidade do SNMP.

---

## Alertas incluídos

### Alertas ativos no template

- Host indisponível por ICMP
- CPU alta
- Memória baixa
- SFP ausente/inativo
- Temperatura alta de módulo óptico
- **Todas as ONUs caíram em uma porta PON**

### Alertas removidos propositalmente

Essas informações continuam sendo coletadas no template, mas **sem gerar evento**:

- ONU inativa
- OMCI inativo
- RX da ONU abaixo de -28 dBm
- RX da OLT abaixo de -28 dBm

Esses itens foram mantidos apenas para consulta, histórico e construção de gráficos, evitando excesso de alarmes desnecessários.

---

## Requisitos

Antes de usar o template, garanta que:

- o SNMP da OLT esteja habilitado;
- o servidor Zabbix consiga alcançar a OLT via rede;
- a community SNMP esteja configurada corretamente;
- a interface SNMP do host no Zabbix esteja cadastrada com IP correto.

Exemplo de configuração utilizada nos testes:

```text
IP da OLT: 10.20.20.6
Versão SNMP: v2c
Community: WNET-TELECOM
```

---

## Como importar no Zabbix

1. Acesse **Data collection > Templates**.
2. Clique em **Import**.
3. Selecione o arquivo YAML em `templates/`.
4. Importe o template.
5. Crie ou edite o host da OLT.
6. Configure a interface SNMP com:
   - IP da OLT
   - Porta 161
   - SNMPv2
   - Community correta
7. Vincule o template ao host.
8. Aguarde as primeiras coletas e discoveries.

---

## Comportamento importante dos itens RAW

O template utiliza itens mestres do tipo `walk[]` para reduzir a quantidade de consultas individuais SNMP e melhorar a eficiência do monitoramento.

Esses itens RAW podem aparecer sem histórico visível, mesmo funcionando corretamente. Isso acontece porque eles servem como base para:

- discovery das ONUs;
- discovery dos módulos ópticos;
- discovery das interfaces;
- criação dos itens dependentes.

Ou seja: mesmo que o item mestre não mostre valor visível no frontend, ele pode estar alimentando corretamente todo o restante do template.

---

## Por que este projeto é útil

Quem trabalha com OLT sabe que um dos maiores desafios não é apenas monitorar o equipamento, mas sim detectar rapidamente eventos que realmente indicam falha operacional.

Neste projeto, o foco foi construir um template com utilidade prática para operação, especialmente para cenários como:

- rompimento de fibra em uma PON;
- perda total de clientes de uma porta GPON;
- acompanhamento de potência óptica;
- validação do estado dos módulos da OLT;
- padronização de monitoramento em múltiplas OLTs.

---

## Próximos passos sugeridos

Melhorias que podem ser adicionadas futuramente ao projeto:

- gráficos prontos por PON
- dashboards no Grafana
- alertas por degradação parcial da PON
- correlação entre quantidade de ONUs ativas e registradas
- agrupamento de eventos por porta
- documentação complementar dos estados OMCI e ativo

---

## Como contribuir

Contribuições são bem-vindas.

Você pode colaborar com:

- validação em outras versões de firmware da 8820i;
- novos OIDs da Intelbras;
- melhorias nas triggers;
- dashboards;
- documentação;
- correções no template.

Se encontrar algum comportamento diferente em outra OLT, abra uma issue com:

- modelo do equipamento;
- versão de firmware;
- saída dos OIDs testados;
- print do erro no Zabbix, se houver.

---

## Boas práticas para publicar no GitHub

Antes de subir o projeto, recomenda-se:

1. Renomear os arquivos com nomes curtos e consistentes.
2. Remover IPs internos, communities e dados sensíveis dos exemplos.
3. Adicionar prints reais do funcionamento.
4. Incluir licença.
5. Criar uma seção de versão/changelog.

Exemplo:

```text
v1.0.0 - Primeira versão pública
- Template validado em OLT Intelbras 8820i
- Discovery de ONUs, SFPs e interfaces
- Alerta de queda total por porta PON
```

---

## Licença

Escolha uma licença para o projeto antes de publicar. Para projetos técnicos de compartilhamento aberto, uma opção comum é a **MIT License**.

---

## Autor

Projeto desenvolvido para monitoramento de OLT Intelbras 8820i no Zabbix, com foco operacional em ambientes ISP.

Se você utilizar este template e ele te ajudar no dia a dia, considere registrar melhorias e compartilhar sua experiência.
