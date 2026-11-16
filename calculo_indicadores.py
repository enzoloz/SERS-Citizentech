"""
SERS - Global Solution 2026.2 | CitizenTech - Neighborhood Action Dashboard
Contribuição de SERS: análise energética da iluminação de uma praça (bairro Ipiranga, SP)

Fórmula base (enunciado, item 4.2):  E (kWh) = P (W) x t (h) / 1000

ATENÇÃO: todos os valores em PREMISSAS são estimativas/hipóteses.
"""
import json
import math

# ----------------------------- PREMISSAS -----------------------------
P = {
    "n_luminarias": 20,            # nº de postes da praça 
    "pot_convencional_w": 150,     # lâmpada convencional 
    "pot_led_w": 50,               # luminária LED equivalente 
    "fator_dimerizacao": 0.5,      # potência a 50% no horário de baixo movimento
    "horas_noite_h": 12,           # horas ligadas por noite
    "horas_dimerizadas_h": 6,      # horas/noite com dimerização (alternativa B)
    "dias_mes": 30,                # meses de 30 dias nos valores mensais
    "dias_ano": 365,               # valores anuais usam 365 dias
    "tarifa_rs_kwh": 0.90,         # R$/kWh 
    "fator_emissao_kg_kwh": 0.0385,  # kg CO2/kWh (média SIN 2023, MCTI)
    "hsp_kwh_m2_dia": 4.5,         # horas de sol pleno 
    "pr": 0.80,                    # performance ratio do sistema FV 
    "pot_painel_wp": 550,          # potência de cada painel
    "custo_luminaria_led_rs": 600,   # R$ por luminária instalada 
    "custo_controle_total_rs": 4500,  # sensores + controle + gateway 
    "custo_fv_rs_wp": 4.00,        # R$/Wp instalado 
}


def energia_kwh(potencia_w, horas, qtd):
    """E = P x t / 1000, multiplicado pela quantidade de equipamentos."""
    return potencia_w * horas * qtd / 1000


def cenario(nome, kwh_dia, investimento, geracao_fv_mes=0.0):
    kwh_mes = kwh_dia * P["dias_mes"]
    kwh_ano = kwh_dia * P["dias_ano"]
    rede_mes = max(0.0, kwh_mes - geracao_fv_mes)         
    renovavel_pct = 0.0 if kwh_mes == 0 else min(100.0, geracao_fv_mes / kwh_mes * 100)
    return {
        "cenario": nome,
        "consumo_kwh_dia": round(kwh_dia, 2),
        "consumo_kwh_mes": round(kwh_mes, 1),
        "consumo_kwh_ano": round(kwh_ano, 1),
        "energia_da_rede_kwh_mes": round(rede_mes, 1),
        "custo_rs_mes": round(rede_mes * P["tarifa_rs_kwh"], 2),
        "renovavel_pct": round(renovavel_pct, 1),
        "investimento_rs": round(investimento, 2),
    }


def main():
    n = P["n_luminarias"]
    h = P["horas_noite_h"]
    hd = P["horas_dimerizadas_h"]

    # --- Cenário 0: base (convencional) ---
    e0 = energia_kwh(P["pot_convencional_w"], h, n)
    base = cenario("Base - convencional", e0, 0)

    # --- Alternativa A: LED ---
    ea = energia_kwh(P["pot_led_w"], h, n)
    alt_a = cenario("A - LED", ea, n * P["custo_luminaria_led_rs"])

    # --- Alternativa B: LED + dimerização + fotovoltaico ---
    eb = (energia_kwh(P["pot_led_w"], h - hd, n)
          + energia_kwh(P["pot_led_w"] * P["fator_dimerizacao"], hd, n))
    kwp_necessario = eb / (P["hsp_kwh_m2_dia"] * P["pr"])
    n_paineis = math.ceil(kwp_necessario * 1000 / P["pot_painel_wp"])
    kwp_instalado = n_paineis * P["pot_painel_wp"] / 1000
    geracao_mes = kwp_instalado * P["hsp_kwh_m2_dia"] * P["pr"] * P["dias_mes"]
    inv_b = (n * P["custo_luminaria_led_rs"] + P["custo_controle_total_rs"]
             + kwp_instalado * 1000 * P["custo_fv_rs_wp"])
    alt_b = cenario("B - LED + dimerização + FV", eb, inv_b, geracao_mes)
    alt_b.update({"kwp_necessario": round(kwp_necessario, 2),
                  "n_paineis": n_paineis,
                  "kwp_instalado": round(kwp_instalado, 2),
                  "geracao_fv_kwh_mes": round(geracao_mes, 1)})

    # --- Indicadores comparados com a base ---
    for c in (alt_a, alt_b):
        c["economia_kwh_mes"] = round(base["consumo_kwh_mes"] - c["energia_da_rede_kwh_mes"], 1)
        c["economia_pct"] = round(c["economia_kwh_mes"] / base["consumo_kwh_mes"] * 100, 1)
        c["economia_rs_mes"] = round(base["custo_rs_mes"] - c["custo_rs_mes"], 2)
        
        kwh_rede_ano = c["energia_da_rede_kwh_mes"] / P["dias_mes"] * P["dias_ano"]
        evitado_ano = base["consumo_kwh_ano"] - kwh_rede_ano
        c["co2_evitado_kg_ano"] = round(evitado_ano * P["fator_emissao_kg_kwh"], 1)
        c["payback_meses"] = round(c["investimento_rs"] / c["economia_rs_mes"], 1)
    base["co2_emitido_kg_ano"] = round(base["consumo_kwh_ano"] * P["fator_emissao_kg_kwh"], 1)

    resultado = {"premissas": P, "cenarios": [base, alt_a, alt_b]}

    
    with open("indicadores.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    for c in resultado["cenarios"]:
        print("\n==", c["cenario"])
        for k, v in c.items():
            if k != "cenario":
                print(f"  {k}: {v}")

    try:
        import matplotlib.pyplot as plt
        nomes = ["Base", "A (LED)", "B (LED+FV)"]
        consumo = [c["consumo_kwh_mes"] for c in resultado["cenarios"]]
        rede = [c["energia_da_rede_kwh_mes"] for c in resultado["cenarios"]]
        x = range(3)
        plt.bar([i - 0.2 for i in x], consumo, width=0.4, label="Consumo (kWh/mês)")
        plt.bar([i + 0.2 for i in x], rede, width=0.4, label="Energia da rede (kWh/mês)")
        plt.xticks(list(x), nomes)
        plt.ylabel("kWh/mês")
        plt.title("Praça - comparação de alternativas")
        plt.legend()
        plt.savefig("grafico_consumo.png", dpi=150, bbox_inches="tight")
        print("\nGráfico salvo em grafico_consumo.png")
    except ImportError:
        print("\n(matplotlib não instalado - gráfico não gerado)")


if __name__ == "__main__":
    main()
