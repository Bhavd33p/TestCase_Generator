package com.zinnia.zenius.utils;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.List;
import java.util.Map;

@Component
public class ExcelGeneratorUtil {

    public static String generateExcel(List<Map<String, Object>> testCases, String folderPath) throws IOException {
        Workbook workbook = new XSSFWorkbook();
        Sheet sheet = workbook.createSheet("Test Cases");


        if (testCases.isEmpty()) {
            throw new IllegalArgumentException("No test cases provided.");
        }


        CellStyle wrapTextStyle = workbook.createCellStyle();
        wrapTextStyle.setWrapText(true);

        Row headerRow = sheet.createRow(0);
        Map<String, Object> firstTestCase = testCases.get(0);
        int headerCellIndex = 0;


        for (String key : firstTestCase.keySet()) {
            Cell cell = headerRow.createCell(headerCellIndex++);
            cell.setCellValue(key);
            sheet.autoSizeColumn(headerCellIndex - 1);
        }

        int rowIndex = 1;
        for (Map<String, Object> testCase : testCases) {
            Row row = sheet.createRow(rowIndex++);
            int cellIndex = 0;

            for (String key : firstTestCase.keySet()) {
                Cell cell = row.createCell(cellIndex++);
                Object value = testCase.get(key);

                if (value != null) {
                    cell.setCellValue(value.toString());
                } else {
                    cell.setCellValue("");
                }

                if ("Steps".equals(key)) {
                    System.out.println("Writing multi-line Steps: " + value);
                    cell.setCellStyle(wrapTextStyle);
                }
            }
        }

        for (int i = 0; i < firstTestCase.keySet().size(); i++) {
            sheet.autoSizeColumn(i);
        }

        File folder = new File(folderPath);
        if (!folder.exists()) {
            folder.mkdirs();
        }

        String filePath = folderPath + "/TestCases_" + System.currentTimeMillis() + ".xlsx";

        try (FileOutputStream fileOut = new FileOutputStream(filePath)) {
            workbook.write(fileOut);
        }

        workbook.close();
        System.out.println("Excel file generated at: " + filePath);
        return filePath;
    }
}
