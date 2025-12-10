import ipeadatapy as ipea
import pandas as pd

def get_dados_ipea(indices_dict, data_inicio='2007-01-01'):
    """
    Busca e consolida taxas mensais do IPEADATA.
    Retorna uma lista de DataFrames processados.
    """
    dfs_lista = []
    print("1. Coletando dados do IPEADATA...")
    
    for nome_json, codigo in indices_dict.items():
        try:
            print(f"   -> [IPEA] Buscando {nome_json} ({codigo})...", end=" ")
            
            df = ipea.timeseries(codigo)
            df.index = pd.to_datetime(df.index).normalize()
            
            df = df[df.index >= data_inicio]
            
            cols = [c for c in df.columns if isinstance(c, str)]
            col_alvo = next((c for c in cols if codigo.upper() in c.upper()), df.columns[-1])
            
            df_temp = pd.DataFrame(index=df.index)
            df_temp[nome_json] = pd.to_numeric(df[col_alvo], errors='coerce')
            
            df_temp = df_temp.resample('MS').first()
            
            if not df_temp.empty:
                dfs_lista.append(df_temp)
                val_ultimo = df_temp.iloc[-1][nome_json]
                print(f"OK (Último: {val_ultimo:.4f}%)")
            else:
                print("Vazio.")
        except Exception as e:
            print(f"[ERRO] {str(e)}")
            
    return dfs_lista