package com.zinnia.zenius.config;
import com.zinnia.zenius.repository.TestTemplateRepository;
import com.zinnia.zenius.service.JiraConfluenceLinkProcessingService;
import com.zinnia.zenius.service.TemplateService;
import com.zinnia.zenius.service.WordTxtFilesProcessingService;
import com.zinnia.zenius.utils.ExcelGeneratorUtil;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
 import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.web.client.RestTemplate;

import java.util.concurrent.Executor;

@Configuration
public class AppConfig {
    @Bean
    public RestTemplate restTemplate() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(10000);
        factory.setReadTimeout(600000);
        return new RestTemplate(factory);
    }
}









