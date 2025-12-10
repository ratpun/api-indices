import requests
import pandas as pd
from datetime import datetime

def get_dados_ibge(nome_indice, tabela_id, variavel_id, data_inicio='200612'):
    """
    Busca dados de NÚMERO-ÍNDICE da API SIDRA do IBGE.
    Endpoint ajustado: /agregados/{tabela}/periodos/{inicio}-{fim}/variaveis/{variavel}?localidades=N1[all]
    """
    try:
        data_fim = datetime.now().strftime('%Y%m')
        
        url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{tabela_id}/periodos/{data_inicio}-{data_fim}/variaveis/{variavel_id}?localidades=N1[all]"
        
        print(f"   -> [IBGE] GET: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data_json = response.json()
        
        if not data_json:
            print(f"      [AVISO] {nome_indice}: JSON retornado está vazio.")
            return None

        try:
            serie_dict = data_json[0]['resultados'][0]['series'][0]['serie']
        except (IndexError, KeyError, TypeError):
            print(f"      [ERRO] {nome_indice}: Estrutura do JSON inesperada ou sem dados.")
            return None
        
        df = pd.DataFrame(list(serie_dict.items()), columns=['data', 'valor'])
        
        df['data'] = pd.to_datetime(df['data'], format='%Y%m')
        df[nome_indice] = pd.to_numeric(df['valor'], errors='coerce')
        
        df = df.dropna(subset=[nome_indice])
        df.set_index('data', inplace=True)
        df = df[[nome_indice]]
        
        df.index = df.index.normalize() + pd.offsets.MonthBegin(-1) + pd.offsets.MonthBegin(1)
        
        if df.empty:
            print(f"      [AVISO] {nome_indice}: DataFrame vazio após processamento.")
            return None

        ultimo_val = df.iloc[-1][nome_indice]
        ult_data = df.index[-1].strftime('%m/%Y')
        print(f"      [OK] {nome_indice}: Dados até {ult_data} (Último Índice: {ultimo_val:.4f})")
        return df

    except Exception as e:
        print(f"      [ERRO CRÍTICO] Falha ao buscar {nome_indice}: {str(e)}")
        return None