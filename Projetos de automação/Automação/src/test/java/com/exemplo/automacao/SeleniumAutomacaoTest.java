package com.exemplo.automacao;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

public class SeleniumAutomacaoTest {

    private WebDriver driver;

    @BeforeEach
    public void setup() {
        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless"); // Executa em modo headless para CI/CD
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");
        driver = new ChromeDriver(options);
    }

    @AfterEach
    public void teardown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void deveExibirTituloCorretoNaPaginaGoogle() {
        driver.get("https://www.google.com");

        String tituloAtual = driver.getTitle();

        Assertions.assertTrue(tituloAtual.toLowerCase().contains("google"),
                "O título deve conter 'Google', mas foi: " + tituloAtual);
    }

    @Test
    public void devePesquisarVideoYouTubeEBuryrMeWithMyScreams() {
        driver.get("https://www.youtube.com");

        // Aceitar cookies depending on region; tentamos clicar se aparecer
        try {
            var botaoAceitar = driver.findElement(org.openqa.selenium.By.xpath("//button[contains(., 'Aceitar tudo') or contains(., 'I agree')]") );
            if (botaoAceitar.isDisplayed()) {
                botaoAceitar.click();
            }
        } catch (Exception ignored) {
        }

        var inputBusca = driver.findElement(org.openqa.selenium.By.name("search_query"));
        inputBusca.sendKeys("bury me with my screams");
        inputBusca.submit();

        new org.openqa.selenium.support.ui.WebDriverWait(driver, java.time.Duration.ofSeconds(10))
                .until(org.openqa.selenium.support.ui.ExpectedConditions.visibilityOfElementLocated(org.openqa.selenium.By.id("video-title")));

        var primeiroResultado = driver.findElement(org.openqa.selenium.By.id("video-title"));
        Assertions.assertTrue(primeiroResultado.isDisplayed(), "O primeiro resultado deve estar visível");
        primeiroResultado.click();

        new org.openqa.selenium.support.ui.WebDriverWait(driver, java.time.Duration.ofSeconds(10))
                .until(org.openqa.selenium.support.ui.ExpectedConditions.visibilityOfElementLocated(org.openqa.selenium.By.cssSelector("h1.title")));

        String tituloVideo = driver.getTitle();
        Assertions.assertTrue(tituloVideo.toLowerCase().contains("bury me with my screams"),
                "O vídeo deve conter o título esperado, mas foi: " + tituloVideo);
    }
}
