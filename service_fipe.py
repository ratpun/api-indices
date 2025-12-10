import requests
import pandas as pd
from datetime import datetime

def get_dados_fipe(ano_inicio=2006):
    """
    Busca dados do IPC-FIPE (Número-Índice) diretamente do site da FIPE.
    Endpoint: https://www.fipe.org.br/IndicesConsulta-IPCPesquisa
    Itera por anos para construir a série histórica completa.
    """
    print("\n4. Coletando dados da FIPE (IPC - Número Índice)...")
    
    url_base = "https://www.fipe.org.br/IndicesConsulta-IPCPesquisa"
    ano_atual = datetime.now().year
    
    dados_completos = []
    
    for ano in range(ano_inicio, ano_atual + 1):
        try:
            params = {
                "anos": ano,
                "meses": "1,2,3,4,5,6,7,8,9,10,11,12",
                "categorias": "2,3,4,5,6,7,8,9", 
                "tipo": "3" 
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = requests.get(url_base, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            json_resp = response.json()
            if json_resp:
                dados_completos.extend(json_resp)
            
        except Exception as e:
            print(f"   -> [ERRO FIPE] Falha ao buscar ano {ano}: {str(e)}")
            
    if not dados_completos:
        print("   -> [AVISO] Nenhum dado retornado da FIPE.")
        return None
        
    try:
        df = pd.DataFrame(dados_completos)
        
        if 'Geral' not in df.columns or 'Ano' not in df.columns or 'Mes' not in df.columns:
            print("   -> [ERRO] Colunas esperadas ('Geral', 'Ano', 'Mes') não encontradas no JSON.")
            return None
            
        df['data'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['Mes'].astype(str) + '-01')
        
        df.set_index('data', inplace=True)
        df.sort_index(inplace=True)
        
        df.rename(columns={'Geral': 'IPC_FIPE'}, inplace=True)
        df = df[['IPC_FIPE']]
        
        df['IPC_FIPE'] = pd.to_numeric(df['IPC_FIPE'], errors='coerce')
        
        ultimo_val = df.iloc[-1]['IPC_FIPE']
        ult_data = df.index[-1].strftime('%m/%Y')
        print(f"   -> [OK] Dados FIPE até {ult_data} (Último Índice: {ultimo_val:.4f})")
        
        return df
        
    except Exception as e:
        print(f"   -> [ERRO PROCESSAMENTO FIPE] {str(e)}")
        return None