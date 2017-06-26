# Estudo sobre interesses de visitantes de Website

O objetivo principal deste trabalho é criar um método de registrar e possibilitar agrupar usuários com base nas urls acessadas por eles.

## Descrição do conteudo deste git
### Diretórios
* presentations - contém apresentações feitas à turma, consistingo na inicial, mid (final) e no app de filtros de visitantes interativo;
* papers - alguns artigos e white papers utilziados para realizar o trabalho;
* third-part-projects-used - outros projetos open-source utilizados no trabalho;
* data-gathering - scripts de scrap e simulacao de dados para análise;
* imgs - imagens dos resultados
### Scripts
* url_classifier.py - script para classificação das urls e registro de departamentos, categorias, etc assim como captura dos conteúdos das páginas de produtos;
* visitor_analysis.py - script para agrupamento de categorias e análise dos textos dos produtos;

## Resultados


### Dados sem filtros

Os dados sem filtros seriam os seguintes:

![no filter](imgs/geral-sem-filtro.png?raw=true "no filter")

O gráfico superior mostra os departamentos, categorias e subcategorias, enquanto o inferior mostra as palavras-chaves dos produtos visitados pelas pessoas contidas nas opções do gráfico de cima.

Abaixo mostrarei 3 caminhos de filtros, observe como as palavras-chave ficam mais específicas.

### Fogões

* Primeiramente filtrando-se por eletrodomésticos teríamos:

![eletrodom](imgs/filtro-eletrodomesticos.png?raw=true "eletrodom")

* Adicionalmente aos eletrodomésticos, filtrando-se por fogão:

![eletrodom-fogao](imgs/filtro-eletrodom-fogao.png?raw=true "eletrodom-fogao")

* Dentro do filtro de eletrodomésticos e fogão, filtrando-se por fogão 4 bocas:

![eletrodom-fogao-4bocas](imgs/filtro-eletrodom-fogao-4bocas.png?raw=true "eletrodom-fogao-4bocas")

### GuardaRoupas

* Próximo exemplo, filtrando-se primeiramente por móveis:

![moveis](imgs/filtro-moveis.png?raw=true "moveis")

* A partir do filtro móveis, filtrando-se por guardaroupas

![moveis-guardaroupa](imgs/filtro-moveis-quarto-guardaroup.png?raw=true "moveis-guardaroupa")

### Panelas

* Filtrando-se inicialmente por utilidades domésticas:

![utildom](imgs/filtro-utildomes.png?raw=true "utildom")

* Filtrando-se em seguida por panelas:

![utildom-pan](imgs/filtro-utildomes-panelas.png?raw=true "utildom-pan")

### Observado

Pode-se observar que há possiblidades de se especificar mais os interesses do visitante a mais do que o departamento, categoria e sub-categoria dos acessos.
