# teste-operacoes

Este pacote `teste_operacoes_lib` oferece funções essenciais para operações matemáticas básicas e serve como um exemplo prático de empacotamento em Python.

O pacote `teste_operacoes_lib` é usado para:
	- Realizar operações de adição, subtração, multiplicação e divisão de números.
	- Demonstrar a estrutura e o processo de criação de um pacote Python distribuível.
	- Fornecer um esqueleto funcional para o desenvolvimento de novos pacotes.

## Instalação

Você pode instalar este pacote usando o gerenciador de pacotes [pip](https://pip.pypa.io/en/stable/) diretamente do PyPI (após o upload):

```bash
pip install teste-operacoes
Uso
Aqui estão alguns exemplos de como importar e utilizar as funções deste pacote:

Python

# Importa a função de saudação do módulo principal do pacote
from teste_operacoes_lib import saudar

# Importa as funções de operações matemáticas de um submódulo
from teste_operacoes_lib.operacoes import somar, subtrair, multiplicar, dividir

# Exemplo de chamada da função de saudação
print(saudar())
# Saída esperada: Olá do meu pacote de operações de teste!

# Exemplos de uso das funções matemáticas
resultado_soma = somar(10, 5)
print(f"10 + 5 = {resultado_soma}")
# Saída esperada: 10 + 5 = 15

resultado_subtracao = subtrair(20, 8)
print(f"20 - 8 = {resultado_subtracao}")
# Saída esperada: 20 - 8 = 12

resultado_multiplicacao = multiplicar(4, 6)
print(f"4 * 6 = {resultado_multiplicacao}")
# Saída esperada: 4 * 6 = 24

try:
    resultado_divisao = dividir(25, 5)
    print(f"25 / 5 = {resultado_divisao}")
    # Saída esperada: 25 / 5 = 5.0

    # Teste de divisão por zero para demonstrar o tratamento de erro
    dividir(10, 0)
except ValueError as e:
    print(f"Erro ao tentar dividir por zero: {e}")
    # Saída esperada: Erro ao tentar dividir por zero: Não é possível dividir por zero.
Autor
Rommano Moreira Mismetti

Licença
Este projeto está licenciado sob a Licença MIT.

MIT