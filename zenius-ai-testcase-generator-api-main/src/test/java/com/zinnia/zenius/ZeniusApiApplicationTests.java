package com.zinnia.zenius;

import io.qameta.allure.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
@Epic("Zenius AI Test Case Generator")
@Feature("Application Context")
class ZeniusApiApplicationTests {

	private static final Logger LOGGER = LoggerFactory.getLogger(ZeniusApiApplicationTests.class);

	@Test
	@DisplayName("Application Context Loads Successfully")
	@Description("Verify that the Spring Boot application context loads without any errors")
	@Severity(SeverityLevel.BLOCKER)
	@Tag("smoke")
	@Story("Application Startup")
	void contextLoads() {
		LOGGER.info("Context loaded successfully");
		Allure.step("Application context loading", () -> {
			LOGGER.info("Spring Boot application context is loading...");
		});
		
		Allure.step("Verify context is loaded", () -> {
			LOGGER.info("Context loaded successfully - All beans are initialized");
		});
	}

}
