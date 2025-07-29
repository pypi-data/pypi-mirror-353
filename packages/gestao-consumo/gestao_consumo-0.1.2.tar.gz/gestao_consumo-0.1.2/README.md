# Gestão de Consumo de Água, Energia e Gás.
Sistema com o objetivo de monitorar e gerenciar o consumo de água, energia e gás em residências.

Desenvolvido pelo Grupo 3:

David Duarte,
Danilson Gonçalves,
Wilker Lopes
e Rafael Fortes.

Disciplina: Metodologias Ágeis de Desenvolvimento de Software 

Curso: Tecnologias de informação, Web e Multimédia – 2º ano

### O que encontrará aqui:  
✔ **Descrições detalhadas** do projeto e objetivos.  
✔ **Registros de progresso** atualizados (sprints, tarefas concluídas).  
✔ **Decisões importantes** tomadas pela equipa.  
✔ **Dados técnicos** (arquitetura, tecnologias usadas).  
✔ **Relatórios** (testes, erros corrigidos, próximos passos). 


🔗 **[Acessar Documento Completo](https://docs.google.com/document/d/1ffJ3UgqVm5QwMyX5_xuHerhVnf9KYjAf/edit#heading=h.cklkopwvz07y)**  
# Pypi do projeto
Para usar e testar o codigo, clica no link abaixo, as instruções de como usar codigo seguem-se logo abaixo do link.

🔗 **[Acessar o Pypi do projeto](https://pypi.org/project/gestao-consumo/)**

# Como usar o codigo

Este sistema permite o **registro, validação, monitoramento e geração de relatórios** sobre o consumo de **água, energia e gás** em diferentes residências. Ideal para análises de eficiência energética e sustentabilidade doméstica.

## Funcionalidades

* Cadastro de casas com localização, morada e certificado energético;
* Registro de consumo por tipo ("agua", "energia", "gas"), com validação dos dados;
* Geração de relatórios gerais e individuais;
* Detecção de erros/inconsistências nos dados;
* Exibição em tabelas formatadas com `tabulate`;
* Informação sobre o período de maior gasto por tipo de consumo.

## Instalação de Dependências
Antes de usar o código, é necessário que o usuário instala as seguintes bibliotecas, caso não tenha:
```python
pip install pandas
pip install tabulate
```

> Requer Python 3.6 (ou superior)

## Instalação de pacotes do codigo
Atenção: Verifica sempre a versão do codigo no Pypi, estando na pagina do projeto, vai em "Histórico de lançamentos"
e seleciona a versão, lá se pode encontrar um comando em especifico como "pip install gestao-consumo==0.1.2" onde o numero
após o nome do projeto, é a versão mais recente, caso se o comando instalar uma versão diferente ou uma anterior.
```python
pip install gestao-consumo
```
## Como usar o codigo

Abrindo o terminal ou o PowerShell digite "python" para usar python, abaixo segue-se os comandos para usar o codigo...
```python
import gestaodeconsumo
```
Este codigo aqui, cria o sistema e instancia o controlador principal que gerencia todas as casas e consumos
```python
data = gestaodeconsumo.ControladorCasas()
```
## Adicionar casas
Sintaxe do coidgo: data.adicionar_casa(codigo, latitude, longitude, morada, certificado_energetico, apelido)
adiciona a casa "001" com localização, morada e certificado
```python
data.adicionar_casa("001", 41.1578, -8.6299, "Rua do Porto 123", "A+", "Casa Central")
```
## Registrar os consumos
Sintaxe: data.registrar_consumo(codigo, tipo, periodo, quantidade, custo)
Cada linha adiciona o consumo de um tipo (água, energia ou gás) para um mês específico
Exemplo:  15000 litros de água com custo de 45.75€ em jan/2025
          350 kWh de energia com custo de 120.50€ no mesmo período
```python
data.registrar_consumo("001", "agua", "01/2025", 15000, 45.75)
data.registrar_consumo("001", "energia", "01/2025", 350, 120.50)
data.registrar_consumo("001", "gas", "01/2025", 550, 70.90)
```
## Listar consumo
Exibe o histórico de consumo por tipo e casa, formatado em tabela, inserindo o codigo da casa (Exmplo:"001") e o que deseja listar, como agua, energia e gas.
```python
data.listar_consumo("001", "agua")
data.listar_consumo("001", "energia")
data.listar_consumo("001", "gas")
```
## Gerar relatórios gerais e individuais
Relatório geral: consolida o consumo de todas as casas
Relatório individual: detalha o consumo por casa
Ambos são exibidos diretamente no terminal
```python
data.gerar_relatorio_geral()
data.gerar_relatorio_individual()
```
## Verificar consistência dos dados
- Verifica se há consumos negativos, períodos repetidos ou certificados inválidos
- Útil para auditoria de dados
- Verificar consistência dos dados
- Checa se há consumos negativos, períodos repetidos ou certificados inválidos
- Útil para auditoria de dados
```python
data.verificar_integridade()
```

## Tipos de consumo válidos

* `agua`
* `energia`
* `gas`

## Formato do período

* Sempre no formato `"MM/AAAA"` (ex: `"01/2025"`)

## Certificados energéticos aceitos

```python
"A+", "A", "B", "B-", "C", "D", "E", "F", "G"
```

## Sobre as classes do trabalho

* `Casa`: representa uma residência com atributos e consumos;
* `ControladorCasas`: gerencia o conjunto de casas e relatórios;
* `Validador`: garante que os dados inseridos sejam coerentes;
* `GeradorTabelas`: imprime dados formatados com `tabulate`.

## Validações automáticas

* Certificados inválidos são rejeitados no cadastro;
* Coordenadas fora do intervalo geográfico válido são rejeitadas;
* Consumos com valores ou custos negativos são sinalizados;
* Períodos duplicados para o mesmo tipo de consumo são impedidos.

## Observações

* O sistema ainda aceita dados com erros *após aviso*, para fins de auditoria ou testes.
* Todos os relatórios são exibidos diretamente no terminal com formatação visual.

# Sobre o Segundo Projeto 📝
🔗 [Acessar o Segundo Projeto](https://github.com/WilkerJoseLopes/Projeto2G3)

Abril 2025
