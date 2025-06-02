# Entrega parcial para Fontes e textos desestruturados

#### Primeira entrega: 12/05/2025
#### Entrega final: 02/06/2025

## Alunos:
 - Denis Alonso
 - John Yang

### Aviso - selenium
    Este trabalho não tinha o intuito de usar outras técnicas além do web scraping. No entanto, devido à estrutura do site do g1 (rolagem), para que pudéssemos coletar um maior número de dados, o uso da biblioteca selenium se tornou necessário.

### Aviso - execução do código
    O código demora em média de 4 a 5 minutos para terminar a análise. Colocamos prints intermediários para mostrar ao usuário que ele ainda está rodando.

### Conclusão
    Com uma mais aprofundada análise exploratória de tópicos, foi possível fazer gráficos de nuvem (das palavras mais frequentes em cada categoria de matéria) e um estudo de polaridade. Neste trabalho, o objetivo foi coletar e analisar notícias do site G1 usando Python e ferramentas como Selenium e BeautifulSoup. A ideia era entender melhor os temas mais falados em diferentes categorias (como Política, Economia, Saúde, etc.) e fazer algumas análises de sentimento e de tópicos com base nos títulos das notícias com a aplicação de técnicas de análise de sentimentos (via TextBlob) e modelagem de tópicos LDA.
    Durante o projeto, conseguimos montar uma base de dados com as notícias mais recentes, separadas por categoria e com a data real em que foram publicadas. Depois disso, usamos algumas bibliotecas para ver se os títulos tinham um tom mais positivo ou negativo (análise de polaridade) e também para descobrir quais eram os principais assuntos comentados em cada área.
    Os resultados mostraram que, por exemplo, temas como política e saúde tendem a ter títulos mais negativos, enquanto áreas como cultura ou esportes apresentam um tom mais leve (tendo em mente as notícias do período que executamos e enviamos o código pela última vez). Também conseguimos identificar palavras e assuntos que estavam se repetindo bastante nas notícias de cada categoria.
    Mesmo com os avanços, tivemos algumas dificuldades, principalmente porque o site do G1 muda bastante, o que pode atrapalhar a coleta. Além disso, como os títulos são curtos, a análise de sentimento nem sempre é tão precisa.