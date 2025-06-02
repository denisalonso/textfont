# PROJETO FINAL – ANÁLISE DE NOTÍCIAS G1 COM SELENIUM E WEBDRIVER_MANAGER
# ============================================
# Denis Alonso e John Yang
# prof. Maciel

# /////////////////////////////////////////////////////////////
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
from textblob import TextBlob
import re
import time
import os
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import nltk
from nltk.corpus import stopwords
import requests
import csv
# /////////////////////////////////////////////////////////////

nltk.download('stopwords')

stopwords_pt = stopwords.words('portuguese')

# configuração do Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# ctegorias de notícias
categorias = {
    'Política': 'https://g1.globo.com/politica/',
    'Economia': 'https://g1.globo.com/economia/',
    'Mundo': 'https://g1.globo.com/mundo/',
    'Tecnologia': 'https://g1.globo.com/tecnologia/',
    'Esportes': 'https://ge.globo.com/',
    'Saúde': 'https://g1.globo.com/saude/',
    'Cultura': 'https://g1.globo.com/pop-arte/'
}

# parâmetros de coleta
scrolls_por_categoria = 20
dados = []

def data_real(link):
    try: 
        response = requests.get(link, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        #print(soup)
        # tenta extrair da tag <time datetime="...">
        tag_time = soup.find('time')
        if tag_time and tag_time.has_attr('datetime'):
            return tag_time['datetime'][:10]
        # se não der, procura por span com a data escrita
        alternativa = soup.find('span', class_='content-publication-data')
        if alternativa:
            texto = alternativa.get_text(strip=True)
            padroes = [r'\d{2}/\d{2}/\d{4}', r'\d{2}-\d{2}-\d{4}']  # usa / ou - como separadores
            for padrao in padroes:
                match = re.search(padrao, texto)
                if match:
                    data_convertida = datetime.strptime(match.group(), '%d/%m/%Y')
                    return data_convertida.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"Erro ao extrair data de {link}: {e}")
    return None           

# coleta com scroll automático
for categoria, url in categorias.items():
    print(f"\nColetando: {categoria}")
    driver.get(url)
    time.sleep(2)
    for _ in range(scrolls_por_categoria):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    noticias = soup.find_all('a', class_='feed-post-link')
    for noticia in noticias:
        # print(noticia['href'])
        titulo = noticia.text.strip()
        link = noticia['href']
        data_pub = data_real(link) or datetime.now().strftime('%Y-%m-%d')
        if titulo:
            dados.append({
                'Data_Publicacao': data_pub,
                'Categoria': categoria,
                'Titulo': titulo,
                'Link': link
            })

# fecha o Chrome
driver.quit()

# criando o dataframe
df = pd.DataFrame(dados)
df.drop_duplicates(inplace=True)
df = df[df['Titulo'].str.strip() != '']
df.reset_index(drop=True, inplace=True)

# criando o CSV
arquivo_csv = 'g1_noticias.csv'
if os.path.exists(arquivo_csv):
    df_existente = pd.read_csv(arquivo_csv)
    df_final = pd.concat([df_existente, df], ignore_index=True)
    df_final.drop_duplicates(subset=['Titulo'], inplace=True)
else:
    df_final = df
df_final.to_csv(
    arquivo_csv,
    index=False,
    sep=';',                     # para não bugar o CSV
    encoding='utf-8-sig',
    quoting=csv.QUOTE_ALL        # coloca aspas
)
print(f"\nColeta finalizada. {len(df)} novas notícias adicionadas. Base total: {len(df_final)}.")

# ===============================
#      ANÁLISE EXPLORATÓRIA
# ===============================

# limpeza do texto
def limpar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto
df_final['Titulo_Limpo'] = df_final['Titulo'].apply(limpar_texto)

# frequência de palavras por categoria
for categoria in df_final['Categoria'].unique():
    palavras = ' '.join(df_final[df_final['Categoria'] == categoria]['Titulo_Limpo']).split()
    contagem = Counter(palavras)
    print(f"\nCategoria: {categoria}")
    print("Top 5 palavras mais comuns:", contagem.most_common(5))

# gráficos de nuvem de palavras
for categoria in df_final['Categoria'].unique():
    texto = ' '.join(df_final[df_final['Categoria'] == categoria]['Titulo_Limpo'])
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texto)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Nuvem de Palavras: {categoria}')
    plt.show()

# análise de sentimentos
df_final['Polaridade'] = df_final['Titulo'].apply(lambda t: TextBlob(t).sentiment.polarity)
polaridade_media = df_final.groupby('Categoria')['Polaridade'].mean().sort_values()
print("\nPolaridade média por categoria:")
print(polaridade_media)
polaridade_media.plot(kind='barh', color='orange')
plt.title('Polaridade Média dos Títulos por Categoria')
plt.xlabel('Polaridade')
plt.grid(axis='x')
plt.tight_layout()
plt.show()

# modelagem de tópicos (LDA)
def exibir_topicos(lda_model, feature_names, n_palavras=5):
    topicos = []
    for i, topic in enumerate(lda_model.components_):
        palavras = [feature_names[i] for i in topic.argsort()[:-n_palavras - 1:-1]]
        topicos.append(", ".join(palavras))
    return topicos
for categoria in df_final['Categoria'].unique():
    titulos = df_final[df_final['Categoria'] == categoria]['Titulo_Limpo']
    if len(titulos) >= 10:
        print(f"\nTópicos da categoria: {categoria}")
        vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words=stopwords_pt)
        X = vectorizer.fit_transform(titulos)
        lda = LatentDirichletAllocation(n_components=2, random_state=42)
        lda.fit(X)
        topicos = exibir_topicos(lda, vectorizer.get_feature_names_out())
        for i, topico in enumerate(topicos):
            print(f" Tópico {i+1}: {topico}")
    else:
        print(f"\nCategoria {categoria} tem poucos títulos para modelagem.")


# ///////////////////////////////////////////////////////////