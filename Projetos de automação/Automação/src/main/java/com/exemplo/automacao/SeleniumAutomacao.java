package com.exemplo.automacao;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class SeleniumAutomacao {

    public static void main(String[] args) {
        // Baixa e configura automaticamente o driver do Chrome
        WebDriverManager.chromedriver().setup();

        // Inicia o navegador
        WebDriver driver = new ChromeDriver();
        try {
            // Acessa o site alvo
            driver.get("https://www.google.com");

            // Exibe título atual no console
            System.out.println("Título: " + driver.getTitle());

            // Aguarda visualização (opcional)
            Thread.sleep(3000);

        } catch (InterruptedException e) {
            e.printStackTrace();
        } finally {
            // Fecha o navegador
            driver.quit();
        }
    }
}
