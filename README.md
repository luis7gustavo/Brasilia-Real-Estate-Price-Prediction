# 🏡 Análise Preditiva de Preços de Imóveis em Brasília-DF

## 🎯 Objetivo do Projeto
Este projeto foi desenvolvido como parte de uma atividade acadêmica em **Ciência de Dados**, com o objetivo de construir um pipeline completo de **Machine Learning**, desde a **coleta de dados brutos na web** até a **construção e avaliação de um modelo preditivo** para o mercado de imóveis no Distrito Federal (DF), Brasil.

O objetivo final é criar um **modelo robusto** capaz de prever o preço de aluguel de um imóvel com base em suas características, como:
- Área (m²)
- Localização (bairro)
- Número de quartos

---

## 🚀 Jornada do Projeto

### 1. Web Scraping
- **Ferramentas**: `Selenium` e `BeautifulSoup`  
- **Alvo**: Portal **DF Imóveis**  
- **Desafios**: O site bloqueava as requisições com erro *403 Forbidden*.  
  - ✅ **Solução**: Estratégia de "aquecimento de sessão", simulando comportamento humano (visitar a homepage antes) + pausas aleatórias.

### 2. Limpeza e Pré-processamento
- Correção de desalinhamento (preço e endereço capturados trocados).  
- Remoção de dados corrompidos (estruturas HTML diferentes em anúncios específicos).  
- **Engenharia de Features**: extração do bairro a partir da URL dos anúncios, garantindo maior padronização.

### 3. Análise Exploratória de Dados (EDA)
- **Descoberta chave**: imóveis com 3 ou 4 quartos pareciam mais baratos que os de 2 quartos → **Paradoxo de Simpson**.  
- Tratamento de **outliers extremos** (preço e área).  
- Visualizações de alta qualidade em tema escuro:
  - Histogramas, boxplots, scatter plots
  - Heatmap de correlação confirmando forte relação entre **área, localização e preço**.

### 4. Modelagem Preditiva
- **Regressão Linear (modelo base)**: obteve R² negativo → inadequado.  
- **Random Forest Regressor (modelo avançado)**:
  - Aplicada transformação logarítmica no preço.
  - Inicialmente apresentou overfitting (R² ≈ 0.99).  
  - Após ajuste de hiperparâmetros (`max_depth`, `min_samples_leaf`), alcançou:
    - R² ≈ **0.96**
    - RMSE ≈ **R$ 3.329,40**

---

## 🛠 Tecnologias Utilizadas
- **Coleta de Dados**: Python, Selenium, BeautifulSoup4, Webdriver-Manager  
- **Manipulação e Análise**: Pandas, NumPy  
- **Machine Learning**: Scikit-learn (Pipeline, ColumnTransformer, RandomForestRegressor)  
- **Visualização**: Matplotlib, Seaborn  

---

## ⚙ Como Executar o Projeto

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/Brasilia-Real-Estate-Price-Prediction.git
cd Brasilia-Real-Estate-Price-Prediction

# 2. Crie e ative o ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
source .venv/bin/activate      # Linux/Mac

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute os scripts na ordem
python scraper_dfimoveis_funcional.py
python data_cleaning_final.py
python comprehensive_eda.py
python regression_model.py
