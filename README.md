# CitizenTech - Contribuição de SERS (Soluções em Energias Renováveis e Sustentáveis)

**Global Solution 2026.2 | Ciência da Computação**

## Integrantes
- Enzo Lozano – RM 574944 
- João Florencio – RM 576950
- Ryan Alves – RM 576880

## Problema
Praça comunitária no bairro Ipiranga (SP) com iluminação convencional ligada
~12 h por noite em potência máxima, sem monitoramento.

## Solução
Comparação entre (A) troca por LED e (B) LED com dimerização por sensor de
presença + energia solar fotovoltaica, com indicadores no Neighborhood Action Dashboard.

## Cálculo base
E (kWh) = P (W) x t (h) / 1000

## Diagrama
```mermaid
flowchart LR
    SOL[Paineis solares 2,75 kWp] --> INV[Inversor]
    INV --> QD[Quadro de distribuicao]
    REDE[Rede eletrica - Enel SP] <--> QD
    QD --> LED[20 luminarias LED]
    SEN[Sensores de presenca e luminosidade] --> CTRL[Controlador de dimerizacao]
    CTRL --> LED
    MED[Medidor de energia consumida e gerada] --> GW[Gateway IoT]
    SEN --> GW
    GW --> PROC[Processamento: calculo de indicadores]
    PROC --> DASH[Neighborhood Action Dashboard]
```

## Como rodar

Requisitos: Python 3. A biblioteca matplotlib é opcional e só serve para gerar o gráfico.

```bash
pip install matplotlib
cd sers
python calculo_indicadores.py
```

O script imprime os resultados e gera `indicadores.json` (usado pelo dashboard) e `grafico_consumo.png`.

## Referências

- BRASIL. Ministério da Ciência, Tecnologia e Inovação (MCTI). SIRENE: fatores de emissão de CO₂ da geração de energia elétrica. Disponível em: https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao. 
- EIXOS. Brasil tem menor taxa de emissão de carbono na geração elétrica em onze anos. https://eixos.com.br/brasil-tem-menor-taxa-de-emissao-de-carbono-na-geracao-eletrica-em-onze-anos/. 
- AGÊNCIA INFRA. ANEEL aprova reajuste de 10,18% nas tarifas da Enel SP. 30 jun. https://agenciainfra.com/blog/?p=43652. 

## Limitações

- Os resultados são projeções condicionadas às premissas adotadas, e não resultados garantidos.
- Número de luminárias, potências, tarifa, custos e horas de sol pleno são estimativas.
- Na alternativa B, o balanço de 100% de energia renovável depende da compensação de créditos na rede, porque a geração é diurna e a iluminação é noturna. Baterias não foram consideradas.
- Não foram considerados taxas e encargos da compensação, manutenção nem as emissões do ciclo de vida dos painéis.
- Como a matriz elétrica brasileira já é pouco emissora, as emissões evitadas são pequenas em termos absolutos.
- O dashboard usa dados estimados ou simulados, sem medição real.
