# =================================================================================
# PROJETO: ANÁLISE PREDITIVA DE PREÇOS DE IMÓVEIS EM BRASÍLIA-DF
# ETAPA 4.3: MODELO FINAL - RANDOM FOREST OTIMIZADO
#
# OBJETIVO:
# Este script representa a solução final e mais robusta do projeto. Após
# diagnosticar o overfitting no modelo anterior, aplicamos técnicas de
# regularização (limitando a profundidade e o crescimento das árvores) para
# criar um modelo que não apenas tem alta precisão, mas também é generalizável
# e confiável.
# =================================================================================

# --- Preparando as Ferramentas de Modelagem ---
import matplotlib
matplotlib.use('Agg')

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# --- Definindo a Estética e o Ambiente ---
NOME_ARQUIVO_LIMPO = 'imoveis_df_cleaned.csv'
PASTA_GRAFICOS = 'graficos_modelo'

if not os.path.exists(PASTA_GRAFICOS):
    os.makedirs(PASTA_GRAFICOS)

BACKGROUND_COLOR = '#1E1E1E'
TEXT_COLOR = '#E0E0E0'
GRID_COLOR = '#444444'

plt.rcParams.update({
    'figure.facecolor': BACKGROUND_COLOR, 'axes.facecolor': BACKGROUND_COLOR,
    'axes.edgecolor': GRID_COLOR, 'axes.labelcolor': TEXT_COLOR,
    'xtick.color': TEXT_COLOR, 'ytick.color': TEXT_COLOR,
    'text.color': TEXT_COLOR, 'grid.color': GRID_COLOR,
})

# --- Carregamento e Preparação dos Dados ---
print("Carregando o dataset limpo para a modelagem...")
try:
    df = pd.read_csv(NOME_ARQUIVO_LIMPO)
    preco_min, preco_max = df['preco'].quantile(0.01), df['preco'].quantile(0.99)
    area_min, area_max = df['area_m2'].quantile(0.01), df['area_m2'].quantile(0.99)
    df = df[(df['preco'].between(preco_min, preco_max)) & (df['area_m2'].between(area_min, area_max))]
    print(f"Dataset carregado com {len(df)} registos.")
except FileNotFoundError:
    print(f"ERRO: Ficheiro '{NOME_ARQUIVO_LIMPO}' não encontrado.")
    exit()

# --- Definição de Features, Alvo e Divisão dos Dados ---
features = ['area_m2', 'quartos', 'vagas', 'suites', 'tem_suite', 'bairro']
target = 'preco'

X = df[features]
y = df[target]

numerical_features = ['area_m2', 'quartos', 'vagas', 'suites', 'tem_suite']
categorical_features = ['bairro']

preprocessor = ColumnTransformer(
    transformers=[('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)],
    remainder='passthrough'
)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Função Auxiliar para Plotar Resultados ---
def plotar_resultados(y_verdadeiro, y_previsto, titulo, nome_arquivo):
    plt.figure(figsize=(10, 10))
    plt.scatter(y_verdadeiro, y_previsto, alpha=0.5, color="#17BECF")
    plt.plot([y_verdadeiro.min(), y_verdadeiro.max()], [y_verdadeiro.min(), y_verdadeiro.max()], '--', lw=2, color="#FF7F0E")
    plt.title(titulo, fontsize=16, weight='bold', color=TEXT_COLOR)
    plt.xlabel('Preços Reais (R$)', fontsize=12)
    plt.ylabel('Preços Previstos (R$)', fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    caminho_grafico = os.path.join(PASTA_GRAFICOS, nome_arquivo)
    plt.savefig(caminho_grafico, dpi=300)
    plt.close()
    print(f"Gráfico de avaliação salvo em: '{caminho_grafico}'")

# --- Treinamento e Avaliação do Modelo ---
print("\n--- Treinando Modelo 3: Random Forest Otimizado (com regularização) ---")
y_log_train = np.log1p(y_train)
y_log_test = np.log1p(y_test)

pipeline_rf_opt = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(
        n_estimators=100, random_state=42, n_jobs=-1,
        max_depth=15, min_samples_leaf=5
    ))
])

pipeline_rf_opt.fit(X_train, y_log_train)
y_pred_log_rf_opt = pipeline_rf_opt.predict(X_test)

y_test_real_opt = np.expm1(y_log_test)
y_pred_real_rf_opt = np.expm1(y_pred_log_rf_opt)

r2_rf_opt = r2_score(y_test_real_opt, y_pred_real_rf_opt)
rmse_rf_opt = np.sqrt(mean_squared_error(y_test_real_opt, y_pred_real_rf_opt))

print("\n--- Métricas de Performance (Modelo Otimizado) ---")
print(f"R² (R-quadrado): {r2_rf_opt:.4f}")
print(f"RMSE: R$ {rmse_rf_opt:,.2f}")
print("-------------------------------------------------")
print("Diagnóstico: O R² é alto mas mais realista. A regularização produziu um modelo mais generalizável.")
plotar_resultados(y_test_real_opt, y_pred_real_rf_opt, 'Preços Reais vs. Previstos (Random Forest Otimizado)', '3_resultado_rf_otimizado.png')

# --- Análise de Importância das Features do Modelo Final ---
print("\nGerando gráfico de importância das features (agregada) do modelo final...")
ohe_feature_names = pipeline_rf_opt.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(categorical_features)
all_feature_names = np.concatenate([ohe_feature_names, numerical_features])
importances = pipeline_rf_opt.named_steps['regressor'].feature_importances_
feature_importance_df = pd.DataFrame({'Feature': all_feature_names, 'Importance': importances})

bairro_importance = feature_importance_df[feature_importance_df['Feature'].str.startswith('bairro_')]['Importance'].sum()
numeric_importances = feature_importance_df[~feature_importance_df['Feature'].str.startswith('bairro_')]
aggregated_importances = pd.concat([
    pd.DataFrame([{'Feature': 'Localização (Bairro)', 'Importance': bairro_importance}]),
    numeric_importances
]).sort_values(by='Importance', ascending=False)

aggregated_importances['Feature'] = aggregated_importances['Feature'].replace({
    'area_m2': 'Área (m²)', 'quartos': 'Quartos', 'vagas': 'Vagas',
    'suites': 'Suítes', 'tem_suite': 'Tem Suíte'
})

plt.figure(figsize=(12, 8))
sns.barplot(x='Importance', y='Feature', data=aggregated_importances, palette='viridis')
plt.title('Importância Agregada das Features para o Modelo Final', fontsize=16, weight='bold', color=TEXT_COLOR)
plt.xlabel('Importância Relativa', fontsize=12)
plt.ylabel('Conceito da Feature', fontsize=12)
plt.tight_layout()
caminho_grafico_features = os.path.join(PASTA_GRAFICOS, '4_feature_importances_aggregated.png')
plt.savefig(caminho_grafico_features, dpi=300)
print(f"Gráfico de importância agregada salvo em: '{caminho_grafico_features}'")
plt.close()

print("\nProcesso do Modelo 3 concluído.")