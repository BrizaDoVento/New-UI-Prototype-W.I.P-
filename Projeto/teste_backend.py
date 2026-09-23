import os
from bs4 import BeautifulSoup

NOME_ARQUIVO_HTML = "HTML comparação de BOM.txt"

def extrair_tabela_dinamica(soup, grid_id):
    grid = soup.find("table", {"id": grid_id})
    if not grid:
        return {}
    
    rows = grid.find_all("tr")
    if not rows:
        return {}

    # Mapeia dinamicamente os nomes dos cabeçalhos das colunas
    header_cols = [th.get_text(strip=True).lower() for th in rows[0].find_all(["th", "td"])]
    
    dados = {}
    for row in rows[1:]:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if not cols or len(cols) != len(header_cols):
            continue
        
        # Cria um dicionário associando cada cabeçalho ao seu respectivo valor
        linha_map = dict(zip(header_cols, cols))
        
        # Tenta identificar o código do item (Protheus Code ou similar)
        codigo = linha_map.get("protheus code") or linha_map.get("code") or cols[1]
        
        dados[codigo] = {
            "versao": linha_map.get("version", ""),
            "descricao": linha_map.get("description", ""),
            "comentario": linha_map.get("comments", ""),
            "quantidade": linha_map.get("quantity", ""),
            # Captura a coluna de posições/designadores se ela existir na tabela
            "designadores": linha_map.get("positions") or linha_map.get("posições") or linha_map.get("designators") or "N/A",
            "todos_campos": linha_map  # Guarda a linha completa mapeada
        }
        
    return dados

def executar_teste_completo():
    if not os.path.exists(NOME_ARQUIVO_HTML):
        print(f"[ERRO] O arquivo '{NOME_ARQUIVO_HTML}' não foi encontrado.")
        return

    print(f"[1] Lendo arquivo '{NOME_ARQUIVO_HTML}'...")
    with open(NOME_ARQUIVO_HTML, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    v55_data = extrair_tabela_dinamica(soup, "GridView1")
    v54_data = extrair_tabela_dinamica(soup, "GridView2")

    if not v55_data or not v54_data:
        print("[ERRO] Tabelas 'GridView1' ou 'GridView2' não encontradas no HTML.")
        return

    print(f"[2] Mapeamento concluído: Versão 55 ({len(v55_data)} itens) | Versão 54 ({len(v54_data)} itens)")
    print("[3] Analisando divergências de Quantidade e Designadores (Posições)...\n")

    divergencias = []
    todos_codigos = set(v55_data.keys()).union(set(v54_data.keys()))

    for codigo in todos_codigos:
        item_v55 = v55_data.get(codigo)
        item_v54 = v54_data.get(codigo)

        if item_v55 and item_v54:
            qtd_diff = item_v55["quantidade"] != item_v54["quantidade"]
            desig_diff = (item_v55["designadores"] != "N/A" and 
                          item_v55["designadores"] != item_v54["designadores"])

            if qtd_diff or desig_diff:
                divergencias.append({
                    "codigo": codigo,
                    "descricao": item_v55["descricao"],
                    "v55_qtd": item_v55["quantidade"],
                    "v54_qtd": item_v54["quantidade"],
                    "v55_posicoes": item_v55["designadores"],
                    "v54_posicoes": item_v54["designadores"],
                    "qtd_divergente": qtd_diff,
                    "posicao_divergente": desig_diff
                })

    if divergencias:
        print("==================================================")
        print("    [RESULTADO BACKEND]: DIVERGÊNCIAS DETECTADAS")
        print("==================================================")
        for d in divergencias:
            print(f"Código Protheus  : {d['codigo']}")
            print(f"Descrição        : {d['descricao']}")
            print(f"Qtd (v55 vs v54) : {d['v55_qtd']}  |  {d['v54_qtd']}")
            print(f"Posição / PCI    : {d['v55_posicoes']}  |  {d['v54_posicoes']}")
            print("-" * 50)
    else:
        print("==================================================")
        print("    [RESULTADO BACKEND]: NENHUMA DIVERGÊNCIA")
        print("==================================================")

if __name__ == "__main__":
    executar_teste_completo()