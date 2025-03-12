# API de Pedidos com Integração Climática

## 1. Introdução

O restaurante "Tomato" é um restaurante que atende a cidade de São Paulo por delivery. A API de pedidos desenvolvida, integra dados climáticos em tempo real para calcular taxas de entrega em dias chuvosos.

### 1.1 Regra de Negócio
A taxa de entrega varia conforme a condição climática:

**Se estiver chovendo:** A taxa de entrega será 5.0.
**Se não estiver chovendo:** A taxa de entrega será 0.0.

Esta regra é aplicada automaticamente durante o processo de criação do pedido, quando o sistema determina a condição climática usando a API externa de clima, ajustando o valor final com base nessa taxa de entrega. 

Se não for possível acessar a API de clima, a taxa de entrega será considerada 0.0, visando não prejudicar o cliente.

## 2. Estrutura de Integração

A integração ocorre com o cliente enviando um pedido via HTTP POST para a API de pedidos. A API valida o pedido e consulta a condição climática e, caso esteja chovendo, uma taxa de entrega é aplicada. Por fim, a API retorna a resposta com o valor total do pedido ao cliente.

### 2.1 Camadas

| Camada | Componentes | Descrição |
| --- | --- | --- |
| Cliente | Postman | Interface que envia pedidos para a API |
| API de pedidos | FastAPI | Gerencia rotas, middlewares e integra serviços |
Lógica de Negócio | fazer_pedido, Pedido (modelo Pydantic) | Processa pedidos, calcula taxas e total |
| Serviço Externo | Open-Meteo API (clima.py) | Fornece dados climáticos em tempo real |
| Monitoramento | Logging | Registra eventos, tempos de processamento e erros |

## 3. Qualidade de integração
O controle de qualidade do fluxo de integração garante que as interações entre os sistemas (API, componentes internos, serviços externos) ocorram corretamente. 

### 3.1 Versionamento e protocolo
A comunicação entre cliente e API é feita via HTTP, com o cliente enviando um pedido via POST e a API respondendo com um JSON. O controle de versões da API é feito por meio do cabeçalho X-API-Version.

**Objetivo:** Garantir que o cliente esteja utilizando uma versão compatível da API, prevenindo que quebras ou mudanças incompatíveis ocorram durante a interação.

**Implementação:** Ao iniciar a requisição, a versão da API fornecida pelo cliente é comparada com a versão atual da aplicação. Se houver incompatibilidade, o sistema retorna um erro 400 com uma mensagem.

```json
{
    "detail": "Versão da API incompatível. Use a versão 2.1.0"
}
```

### 3.2 Tempo de processamento

A API inclui um middleware que mede o tempo de processamento de cada requisição, em milissegundos.

**Objetivo:** Monitorar o tempo que o sistema leva para processar cada pedido e retornar uma resposta, ajudando a identificar gargalos de desempenho.

**Implementação:** O middleware calcula o tempo entre o início e o fim da requisição e adiciona esse valor no cabeçalho da resposta com a chave X-Process-Time.

Exemplo do registro no log:

```log
2025-03-11 09:26:14,823 - app.main - INFO - Tempo de processamento: 0.0231s
```

### 3.3 Logs e tratamento de exceções

**Objetivos:** 
1. Garantir que erros durante o processamento de dados ou interações com o serviço de clima não afetem a estabilidade da aplicação e sejam registrados para análise posterior. 
2. Garantir que todos os eventos importantes sejam registrados para monitoramento e auditoria.

**Implementação:** A API inclui um tratamento de exceções para garantir que qualquer erro seja registrado e uma mensagem apropriada seja retornada ao cliente. A função verificar_chuva lida com possíveis falhas de conexão com o serviço externo (API de clima) e a API principal garante que o erro não quebre o fluxo de atendimento.

Alguns erros conhecidos que são registrados com sucesso no log são:

- Versão da API incompatível
- Pedido inválido / Formato inválido
- Erro ao consultar/conectar a API externa

Exemplo de log de erro ao acessar a API externa:
```log
2025-03-11 15:30:00 - app.main - ERROR - Falha ao acessar Open-Meteo: ConnectionError  
```
## 4. Testes de Integração

### 4.1 test_version_header

**Objetivo:** Verificar se o cabeçalho X-API-Version da resposta está presente e corresponde à versão atual da API. Também garantir que o campo version no corpo da resposta também esteja correto.

**Pré-condições**
- A API está em execução na versão "2.1.0".
- A rota /pedido está acessível para requisições POST.

**Fluxo do Teste**
1. Enviar uma requisição POST para a rota /pedido, fornecendo um JSON de pedido de exemplo

2. A API processa o pedido e retorna uma resposta que inclui o cabeçalho X-API-Version e o campo version no corpo da resposta.

**Resultado Esperado**
- O cabeçalho da resposta X-API-Version deve ser igual a "2.1.0".
- O campo version no corpo da resposta deve ser igual a "2.1.0".

### 4.2 test_fazer_pedido_sem_chuva

**Objetivo:** Verificar se a taxa de entrega não é contabilizada quando não há chuva, garantindo que o valor total do pedido seja calculado corretamente.

**Pré-condições**
- A API está configurada para retornar False para a verificação de chuva (não está chovendo).
- A rota /pedido está acessível para requisições POST.

**Fluxo do Teste**
1. Substituir a função verificar_chuva pela versão mockada que retorna False (indicando que não está chovendo)

2. Enviar uma requisição POST para a rota /pedido com um JSON de pedido

3. A API processa o pedido, e a taxa de entrega é ajustada para 0.0

4. O valor total final do pedido será igual ao valor original do pedido

**Resultado Esperado**
- O campo taxa_entrega deve ser igual a 0.0
- O campo total no corpo da resposta deve ser igual ao valor original do pedido

### 4.3 test_fazer_pedido_com_chuva

**Objetivo:** Verificar se a taxa de entrega é contabilizada como ``5.0`` quando há chuva, garantindo que o valor total do pedido seja calculado corretamente.

**Pré-condições**
- A API está configurada para retornar True para a verificação de chuva
- A rota /pedido está acessível para requisições POST

**Fluxo do Teste**
1. Substituir a função verificar_chuva pela versão mockada que retorna True

2. Enviar uma requisição POST para a rota /pedido com um JSON de pedido

3. A API processa o pedido, e a taxa de entrega é ajustada para 5.0

4. O valor total final do pedido será o valor original do pedido (30.0) mais a taxa de entrega (5.0), resultando em um total de 35.0

**Resultado Esperado**
- O campo taxa_entrega deve ser igual a 5.0
- O campo total no corpo da resposta deve ser igual a 35.0









