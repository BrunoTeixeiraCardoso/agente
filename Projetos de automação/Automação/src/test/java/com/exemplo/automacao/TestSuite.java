package com.exemplo.automacao;

import org.junit.platform.suite.api.SelectPackages;
import org.junit.platform.suite.api.Suite;
import org.junit.platform.suite.api.SuiteDisplayName;

@Suite
@SuiteDisplayName("Bateria de Testes de Automação com Selenium")
@SelectPackages("com.exemplo.automacao")
public class TestSuite {
    // Esta classe serve como ponto de entrada para executar todos os testes no pacote
}