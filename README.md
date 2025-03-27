# ZANE-Notebooks

## Análise de Dados ZANE / Mundial

## Descrição
Estes jupyter notebooks são responsáveis por realizar os procedimentos automáticos para a análise de dados da Mundial.
Eles executam os módulos disponíveis nos arquivos,
- api/alis.py
- api/auth.py
- api/send_api.py
- preprocess/cleanup.py
- preprocess/ensemble.py 
- preprocess/movement.py

## Pré-requisitos
Linguagem python 3.9 com pip ou uma distribuição Anaconda semelhante.

## Instalação
Após a instalação do python 3.9, executar, 

> pip install -r .\requirements.txt


Caso já tenha uma versão do python anaconda, basta instalar as dependências mais específicas, como geopandas. Elas estão listadas no arquivo requirements.txt.
Para executar os notebooks, recomenda-se uma versão da sua preferência de editor. Um editor para jupyter notebooks pode ser baixado pelo pip com o comando,

> pip install jupyterlab

Ao ser executado na raiz deste diretório, o comando,

> jupyter lab

Abre a pasta para que seja possível interagir com os diferentes notebooks.

## Docker
Gerar imagem docker a partir do diretório raiz do projeto (opcional `-t`: nome da tag):
> docker build . -t pipeline-mundial

Executar imagem passando os valores das variáveis de ambiente:
- datas de início ("START_DATE") e fim ("FINISH_DATE")
- executar dados de NOx ("EXECUTE_NOX") OU dados de Abastecimento ("EXECUTE_ABASTECIMENTO")
  - OBS: O pipeline deve processar apenas uma das opções de dados a cada execução 

Ex. NOx: 
> docker run -it -e START_DATE="01/01/2025" -e FINISH_DATE="31/01/2025" -e EXECUTE_NOX="True" pipeline-mundial

Ex. Abastecimento:
> docker run -it -e START_DATE="01/01/2025" -e FINISH_DATE="31/01/2025" -e EXECUTE_ABASTECIMENTO="True" pipeline-mundial

Após iniciar o container, é possível acompanhar os logs da execução.
