# Automação com Selenium

Este projeto contém uma bateria de testes de automação web usando Selenium WebDriver e JUnit 5.

## Estrutura do Projeto

- `src/main/java`: Código principal (exemplo de uso do Selenium).
- `src/test/java`: Testes automatizados.
  - `SeleniumAutomacaoTest.java`: Testes funcionais para Google e YouTube.
  - `TestSuite.java`: Suíte para executar todos os testes.

## Dependências

- Selenium WebDriver 4.14.0
- WebDriverManager 5.4.0
- JUnit 5.11.0

## Como Executar

1. Instale JDK 17 e Maven.
2. Execute `mvn test` para rodar todos os testes.
3. Para executar apenas a suíte: `mvn test -Dtest=TestSuite`.

Os testes rodam em modo headless por padrão para facilitar integração com CI/CD.