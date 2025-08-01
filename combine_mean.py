###############################################################################
# Código escrito por inteligêcia artificial!!
#
# Atualmente não faz parte da ferramenta, é apenas um utilitário
###############################################################################

import csv
import os
from pathlib import Path

def combine_mean_metrics(base_dir: str = "./csvs"):
    """
    Combina métricas médias de exercícios equivalentes entre EstruturaDeDadosI e II,
    calculando a média ponderada pelo número de arquivos (linhas) em cada turma.
    
    Gera arquivos CSV consolidados no formato:
    - consolidated/Lista01/01Temperatura_combined_mean.csv
    - consolidated/Lista02/03Juizes_combined_mean.csv
    """
    base_path = Path(base_dir)
    consolidated_path = base_path / "consolidated"
    consolidated_path.mkdir(exist_ok=True)
    
    ed1_path = base_path / "EstruturaDeDadosI"
    ed2_path = base_path / "EstruturaDeDadosII"
    lists = [d.name for d in ed1_path.iterdir() if d.is_dir()]
    
    for list_name in lists:
        list_path = consolidated_path / list_name
        list_path.mkdir(exist_ok=True)
        
        ed1_list_path = ed1_path / list_name
        exercises = [d.name for d in ed1_list_path.iterdir() if d.is_dir()]
        
        for exercise in exercises:
            try:
                # Caminhos para os arquivos
                ed1_csv = ed1_list_path / exercise / f"{exercise}.csv"
                ed2_csv = ed2_path / list_name / exercise / f"{exercise}.csv"
                ed1_mean = ed1_list_path / exercise / f"{exercise}_mean.csv"
                ed2_mean = ed2_path / list_name / exercise / f"{exercise}_mean.csv"
                
                if not all(f.exists() for f in [ed1_csv, ed2_csv, ed1_mean, ed2_mean]):
                    continue
                
                # Contar número de arquivos (linhas - 1 para excluir cabeçalho)
                with open(ed1_csv, 'r') as f:
                    ed1_count = sum(1 for _ in csv.reader(f)) - 1
                
                with open(ed2_csv, 'r') as f:
                    ed2_count = sum(1 for _ in csv.reader(f)) - 1
                
                # Ler métricas médias
                with open(ed1_mean, 'r') as f:
                    ed1_reader = csv.reader(f)
                    ed1_headers = next(ed1_reader)
                    ed1_values = next(ed1_reader)
                
                with open(ed2_mean, 'r') as f:
                    ed2_reader = csv.reader(f)
                    ed2_headers = next(ed2_reader)
                    ed2_values = next(ed2_reader)
                
                # Calcular média ponderada
                combined_data = [
                    ["Metric", "ED1 Value", "ED2 Value", "Weighted Average", "ED1 Weight", "ED2 Weight"],
                    *[
                        [
                            header,
                            ed1_val,
                            ed2_val,
                            # Fórmula: (ed1_val * peso_ed1 + ed2_val * peso_ed2) / (peso_ed1 + peso_ed2)
                            (float(ed1_val) * ed1_count + float(ed2_val) * ed2_count) / (ed1_count + ed2_count),
                            ed1_count,
                            ed2_count
                        ]
                        for header, ed1_val, ed2_val in zip(ed1_headers, ed1_values, ed2_values)
                    ]
                ]
                
                # Salvar arquivo consolidado
                output_file = list_path / f"{exercise}_combined_mean.csv"
                with open(output_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(combined_data)
                
                print(f"Created combined metrics: {output_file}")
                
            except Exception as e:
                print(f"Error processing {exercise}: {str(e)}")

if __name__ == "__main__":
    combine_mean_metrics()
