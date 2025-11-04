Projeto Recife Resiliente: Monitor Colaborativo de Enchentes
Um projeto de análise de dados e ciência cívica para mapear e combater os impactos das enchentes na cidade do Recife de forma colaborativa.

📄 Sobre o Projeto
Recife, uma cidade marcada por sua beleza e por seus rios, enfrenta um desafio histórico e recorrente: as enchentes. Em períodos de chuvas mais intensas, diversos pontos da cidade sofrem com alagamentos que impactam diretamente a vida de milhares de cidadãos, causando transtornos no trânsito e danos ao patrimônio.

Nosso projeto propõe o desenvolvimento de uma plataforma web/mobile que funcionará como uma rede social colaborativa, focada no monitoramento de enchentes em tempo real. A principal força desta ferramenta reside na participação ativa dos cidadãos, que se tornarão a principal fonte de dados para a plataforma.

O objetivo é criar um ecossistema de informação que beneficie a todos:

Para o cidadão: Uma ferramenta prática para auxiliar na tomada de decisões e na segurança durante períodos chuvosos.

Para a cidade: Uma fonte de dados rica e atualizada, fundamental para um planejamento urbano mais inteligente e uma gestão de crises mais eficiente.

✨ Funcionalidades Principais
Mapeamento em Tempo Real: Usuários podem marcar em um mapa as vias que se encontram alagadas, congestionadas ou intransitáveis.

Classificação de Intensidade: Para cada marcação, o usuário pode atribuir uma nota (ex: 0 a 10) para classificar a gravidade do alagamento.

Relatos Detalhados: Possibilidade de adicionar comentários e fotos para enriquecer as informações.

Dashboard e Visualização de Dados: A plataforma analisará os dados recebidos e gerará visualizações dinâmicas, como gráficos e mapas de calor, mostrando os pontos com maior recorrência e intensidade de alagamentos.

Análise Histórica: Os dados coletados fornecerão insights valiosos para estudos e para o planejamento urbano por parte do poder público.

💻 Tecnologias Utilizadas
Após análise de diferentes abordagens, o stack tecnológico definido para o projeto foi:

Linguagem: Python

Framework Backend: Django

Análise de Dados: Pandas

A escolha pelo Python com Django e Pandas foi estratégica. Essa combinação nos permite construir uma aplicação robusta e, ao mesmo tempo, integrar diretamente as rotinas de análise e manipulação de dados no backend, sem a necessidade de criar uma API separada apenas para isso, otimizando o desenvolvimento. Alternativas como Java com Spring ou a linguagem R foram consideradas, mas a stack escolhida representa o caminho com menor complexidade e maior sinergia para os objetivos do projeto.

🚀 Próximos Passos
[ ] Estruturação do banco de dados.

[ ] Desenvolvimento dos endpoints da API com Django Rest Framework.

[ ] Criação da interface de usuário (frontend) para o mapa interativo.

[ ] Implementação das rotinas de análise com Pandas para a geração dos gráficos.

[ ] Testes iniciais e fase beta com usuários convidados.

🤝 Como Contribuir
Este é um projeto de código aberto e adoraríamos receber sua ajuda! Se você tem interesse em contribuir, por favor, siga os passos abaixo:

Faça um Fork deste repositório.

Crie uma nova Branch (git checkout -b feature/sua-feature).

Faça o Commit das suas alterações (git commit -m 'Adiciona nova feature').

Faça o Push para a sua Branch (git push origin feature/sua-feature).

Abra um Pull Request.

"MATRIZ DE CONFUSÃO"
Uma matriz de confusão é uma tabela que compara os resultados previstos por um modelo de classificação com os resultados reais para avaliar seu desempenho. Ela é especialmente útil para modelos com duas ou mais categorias e pode ser usada para calcular métricas como precisão, recall e acurácia. 


A matriz é composta por quatro componentes principais (para classificação binária):

Verdadeiros Positivos (VP): O modelo previu corretamente a classe positiva. 
Verdadeiros Negativos (VN): O modelo previu corretamente a classe negativa. 
Falsos Positivos (FP): O modelo previu a classe positiva, mas a realidade era negativa (erro do tipo I). 
Falsos Negativos (FN): O modelo previu a classe negativa, mas a realidade era positiva (erro do tipo II). 