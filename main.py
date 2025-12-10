import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

import service_ibge
import service_ipea
import service_fipe

pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', '{:.4f}'.format)

CAMINHO_PADRAO_SAIDA = "indices_acumulados.json"

def gerar_json_acumulados(caminho_saida=CAMINHO_PADRAO_SAIDA):
    print("--- Gerador de Índices Acumulados (Modularizado) ---\n")

    indices_ipea_config = {
        "SELIC": "BM12_TJOVER12",    # Taxa Selic (% a.m.)
        "TR": "BM12_TJTR12",           # TR (% a.m.)
        "Poupanca": "BM12_RNDPO12",   # Poupança (% a.m.)
        "IGPM": "IGP12_IGPMG12",      # IGP-M (% a.m.)
    }

    indices_ibge_config = {
        "IPCA": {"tabela": 1737, "variavel": 2266},  # Número-índice mensal
        "INPC": {"tabela": 1736, "variavel": 2289},  # Número-índice mensal
        "IPCAE": {"tabela": 3065, "variavel": 1117}  # IPCA-15 Número-índice
    }

    hoje = datetime.now()
    mes_atual_sistema = pd.Timestamp(hoje.year, hoje.month, 1)
    
    idx_resultado = pd.date_range(start='2007-01-01', end=mes_atual_sistema, freq='MS').normalize()
    df_resultado = pd.DataFrame(index=idx_resultado)

    dfs_consolidacao = service_ipea.get_dados_ipea(indices_ipea_config, data_inicio='2007-01-01')

    print("\n2. Coletando dados do IBGE (Números-Índices)...")
    
    dfs_numeros_indices = {}

    for nome, params in indices_ibge_config.items():
        df_temp = service_ibge.get_dados_ibge(nome, params['tabela'], params['variavel'], data_inicio='200612')
        if df_temp is not None:
            dfs_numeros_indices[nome] = df_temp

    df_fipe = service_fipe.get_dados_fipe(ano_inicio=2006)
    if df_fipe is not None:
        dfs_numeros_indices['IPC_FIPE'] = df_fipe

    print("\n5. Calculando acumulados (Lógica de Divisão de Índices)...")
    
    for nome_indice, df_indice in dfs_numeros_indices.items():
        if df_indice is not None and not df_indice.empty:
            
            try:
                indice_final = df_indice.iloc[-1].iloc[0] 
            except:
                continue

            acumulados = []
            for data_ref in df_resultado.index:
                data_base_divisor = data_ref - pd.DateOffset(months=1)
                
                data_base_divisor = pd.Timestamp(data_base_divisor).normalize()
                
                try:
                    if data_base_divisor in df_indice.index:
                        val_loc = df_indice.loc[data_base_divisor]
                        indice_base = val_loc.iloc[0] if isinstance(val_loc, pd.Series) else val_loc
                        
                        if indice_base > 0:
                            fator = indice_final / indice_base
                            pct = (fator - 1) * 100
                            acumulados.append(pct)
                        else:
                            acumulados.append(0.0)
                    else:
                        acumulados.append(0.0)
                except KeyError:
                    acumulados.append(0.0)
            
            df_resultado[nome_indice] = acumulados

    print("\n6. Calculando Índices IPEADATA e SELIC...")
    
    df_ipea_cons = pd.DataFrame(index=df_resultado.index)
    for df in dfs_consolidacao:
        df_ipea_cons = df_ipea_cons.join(df, how='left')
    
    df_ipea_cons.fillna(0.0, inplace=True)

    if 'SELIC' in df_ipea_cons.columns:
        if not df_ipea_cons.empty:
             df_ipea_cons.iloc[-1, df_ipea_cons.columns.get_loc('SELIC')] = 1.0

        selic_vals = df_ipea_cons['SELIC'].values
        n = len(selic_vals)
        selic_res = np.zeros(n)
        
        for i in range(n):
            if i < n - 1:
                selic_res[i] = np.sum(selic_vals[i+1:])
            else:
                selic_res[i] = 0.0 
        
        df_resultado['SELIC'] = selic_res

    for col in ['TR', 'Poupanca', 'IGPM']:
        if col in df_ipea_cons.columns:
            taxas = df_ipea_cons[col].values
            fatores = 1 + (taxas / 100.0)
            acumulado_reverso_fator = np.cumprod(fatores[::-1])[::-1]
            acumulado_pct = (acumulado_reverso_fator - 1) * 100
            df_resultado[col] = acumulado_pct

    df_resultado = df_resultado.round(4)
    df_export = df_resultado.sort_index().reset_index()
    df_export.rename(columns={'index': 'DATE'}, inplace=True)
    
    df_export['Ano'] = df_export['DATE'].dt.year
    df_export['Mes'] = df_export['DATE'].dt.month
    df_export['Referencia'] = df_export['DATE'].dt.strftime('%m/%Y')

    prioridade = ['Ano', 'Mes', 'Referencia', 'SELIC', 'TR', 'INPC', 'IPCA', 'IPCAE', 'IGPM', 'Poupanca', 'IPC_FIPE']
    cols_finais = [c for c in prioridade if c in df_export.columns]

    df_export.replace([np.inf, -np.inf], 0, inplace=True)
    df_export.fillna(0, inplace=True)

    json_data = df_export[cols_finais].to_dict(orient='records')
    
    dir_saida = os.path.dirname(caminho_saida)
    if dir_saida and not os.path.exists(dir_saida):
        try:
            os.makedirs(dir_saida)
            print(f"\nDiretório criado: {dir_saida}")
        except Exception as e:
            print(f"\n[ERRO] Não foi possível criar o diretório {dir_saida}: {e}")
            return

    try:
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        
        print(f"\nSucesso! Arquivo gerado em: {os.path.abspath(caminho_saida)}")
        print(f"Total de registros: {len(json_data)}")
    except Exception as e:
        print(f"\n[ERRO] Falha ao salvar arquivo: {e}")

    print("\n--- Validação Final (Exemplo: Jan/2007) ---")
    print(df_export[cols_finais].head(1).to_string(index=False))
    print("\n--- Validação Final (Últimos 3 Meses - Incluindo Atual) ---")
    print(df_export[cols_finais].tail(3).to_string(index=False))

if __name__ == "__main__":
    gerar_json_acumulados(CAMINHO_PADRAO_SAIDA)