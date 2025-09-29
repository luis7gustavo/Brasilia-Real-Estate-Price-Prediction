# =============================================================================
# PROJETO: ANÁLISE PREDITIVA DE PREÇOS DE IMÓVEIS EM BRASÍLIA-DF
# ETAPA 1: COLETA DE DADOS (WEB SCRAPING)
#
# OBJETIVO:
# Este script é responsável por navegar no portal DF Imoveis, coletar
# dados brutos de anúncios de aluguel e salvá-los em um arquivo CSV.
# Ele foi projetado para ser resiliente a bloqueios e extrair o máximo
# de informações úteis para as fases seguintes de limpeza e modelagem.
# =============================================================================

# --- Parte 1: Preparando as Ferramentas ---
# Aqui, importamos todas as bibliotecas que nosso robô precisará para trabalhar.

import pandas as pd  # Essencial para organizar os dados em tabelas (DataFrames) e salvá-los.
import time          # Nosso "cronômetro", para criar pausas e simular um comportamento humano.
import random        # Para tornar nossas pausas imprevisíveis, dificultando a detecção por sistemas anti-bot.
import os            # Usado para interagir com o sistema operacional, como criar pastas.

# As estrelas do show de scraping:
from bs4 import BeautifulSoup               # O "analista" que lê o HTML e nos ajuda a encontrar as informações.
from selenium import webdriver              # O "piloto" que controla o navegador Chrome.
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager # O "mecânico" que baixa e gerencia o driver do Chrome para nós.


# --- Parte 2: Configurando a Missão ---
# Definimos os parâmetros da nossa coleta de dados.

# O ponto de partida da nossa busca. Escolhemos uma URL genérica de aluguel no DF
# pois se mostrou mais estável contra os bloqueios do site.
URL_BASE = 'https://www.dfimoveis.com.br/aluguel/df/todos/imoveis'
HOME_PAGE = 'https://www.dfimoveis.com.br/' # A página inicial, para "aquecer" nossa sessão.

# O nome do arquivo onde salvaremos nosso "minério bruto".
NOME_ARQUIVO_BRUTO = 'imoveis_aluguel_df_dataset_completo.csv'

# Limite de segurança para o número de páginas a serem raspadas.
# Isso evita que o scraper entre em um loop infinito caso algo dê errado.
MAX_PAGINAS = 350


# --- Parte 3: Montando o Robô (WebDriver) ---

print("Iniciando a configuração do nosso navegador automatizado...")

# Configurações para fazer o Chrome se comportar como queremos.
chrome_options = Options()
chrome_options.add_argument("--headless")  # Roda o Chrome em "modo fantasma", sem abrir uma janela visual. Essencial para servidores.
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# Nosso "disfarce": enviamos um User-Agent para nos parecermos com um navegador comum.
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

# Inicializamos o WebDriver, que é a ponte de comando entre nosso script e o navegador.
# O ChromeDriverManager cuida de baixar a versão correta do "motor" do Chrome, o que é uma grande ajuda.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

print("Navegador pronto para a missão!")


# --- Parte 4: A Execução da Coleta ---

# Uma lista vazia para guardar os dados de cada imóvel que encontrarmos.
dados_gerais_imoveis = []
pagina_atual = 1

# O 'try...finally' é uma estrutura de segurança. O código dentro de 'finally'
# (neste caso, `driver.quit()`) será executado SEMPRE, mesmo que ocorra um erro.
# Isso garante que não deixaremos um processo do Chrome "zumbi" rodando no sistema.
try:
    # ESTRATÉGIA ANTI-BLOQUEIO: Aquecimento da Sessão
    # Primeiro, visitamos a página inicial para pegar cookies e parecer um usuário legítimo.
    print(f"Aquecendo a sessão visitando: {HOME_PAGE}")
    driver.get(HOME_PAGE)
    time.sleep(random.uniform(3, 7)) # Pausa para simular um tempo de leitura.

    # O loop principal. Ele continuará a rodar enquanto houver páginas para raspar.
    while pagina_atual <= MAX_PAGINAS:
        # Montamos a URL da página específica que queremos visitar.
        url_da_pagina = f"{URL_BASE}?pagina={pagina_atual}" if pagina_atual > 1 else URL_BASE

        print(f"\nNavegando para a Página {pagina_atual}...")
        driver.get(url_da_pagina)

        # PAUSA ESTRATÉGICA: Esperamos um tempo aleatório para não sobrecarregar
        # o servidor e evitar sermos identificados como um robô.
        pausa_aleatoria = random.uniform(4, 8)
        print(f"Pausa de {pausa_aleatoria:.2f} segundos para simular comportamento humano.")
        time.sleep(pausa_aleatoria)

        # Entregamos o código-fonte da página (HTML) para o BeautifulSoup analisar.
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Procuramos por todos os "contêineres" de anúncios na página.
        # A classe 'property-list__item' foi identificada como o padrão para cada anúncio.
        lista_anuncios = soup.find_all('div', class_='property-list__item')

        # CONDIÇÃO DE PARADA: Se a lista de anúncios estiver vazia, chegamos ao fim.
        if not lista_anuncios:
            print("Não foram encontrados mais anúncios. Missão de coleta concluída.")
            break

        print(f"Encontrados {len(lista_anuncios)} anúncios. Iniciando extração de dados...")

        # Agora, iteramos sobre cada anúncio encontrado para extrair as informações.
        for anuncio in lista_anuncios:
            try:
                # Usamos o 'find' para localizar as informações dentro de cada anúncio.
                preco = anuncio.find('p', class_='property-list__price').text.strip()
                endereco = anuncio.find('p', class_='property-list__address').text.strip()
                link = anuncio.find('a', href=True)['href']
                url_completa = f"{HOME_PAGE.strip('/')}{link}" if link.startswith('/') else link
                
                features_list = anuncio.find('ul', class_='property-list__features')

                # Uma função auxiliar para extrair características de forma segura.
                def get_feature(feature_name):
                    tag = features_list.find('li', attrs={'title': feature_name})
                    # Se a tag for encontrada, retorna o texto; senão, retorna 'N/A'.
                    return tag.text.strip() if tag else 'N/A'

                area = get_feature('Área útil')
                quartos = get_feature('Quartos')
                suites = get_feature('Suítes') # Adicionamos a extração de suítes.
                vagas = get_feature('Vagas')

                # Montamos um dicionário com os dados do imóvel.
                imovel = {
                    'preco_anuncio': preco, 'endereco': endereco, 'area_util_m2': area,
                    'quartos': quartos, 'suites': suites, 'vagas': vagas, 'url': url_completa
                }
                # Adicionamos o dicionário à nossa lista geral.
                dados_gerais_imoveis.append(imovel)
            except AttributeError:
                # Se um anúncio tiver uma estrutura HTML diferente e quebrada,
                # pulamos para o próximo para não travar o script.
                print("  -> Aviso: Um anúncio com estrutura inválida foi pulado.")
                continue

        # Incrementamos o contador para ir para a próxima página no próximo loop.
        pagina_atual += 1

finally:
    # A limpeza final: fechamos o navegador.
    print("\nFinalizando a sessão e fechando o navegador.")
    driver.quit()

# --- Parte 5: Organizando e Salvando a Colheita ---

if dados_gerais_imoveis:
    print(f"\nCriando o DataFrame com {len(dados_gerais_imoveis)} imóveis coletados.")
    # Transformamos nossa lista de dicionários em uma tabela do Pandas.
    df = pd.DataFrame(dados_gerais_imoveis)

    # Salvamos a tabela em um arquivo CSV.
    # 'index=False' evita que o índice do DataFrame seja salvo no arquivo.
    # 'encoding='utf-8-sig'' garante compatibilidade com acentos e caracteres especiais.
    df.to_csv(NOME_ARQUIVO_BRUTO, index=False, encoding='utf-8-sig')

    print(f"SUCESSO! Os dados brutos foram salvos em '{NOME_ARQUIVO_BRUTO}'")
    print("\nAmostra dos dados coletados:")
    print(df.head()) # Mostra as 5 primeiras linhas para verificação.
else:
    print("\nAVISO: Nenhum dado foi coletado. O arquivo CSV não foi gerado.")

