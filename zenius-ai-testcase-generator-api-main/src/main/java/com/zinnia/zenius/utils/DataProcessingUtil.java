package com.zinnia.zenius.utils;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;
import org.apache.poi.xwpf.usermodel.*;
import java.io.InputStream;
import java.util.List;
import java.util.StringJoiner;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;

public class DataProcessingUtil {
    private static final Logger logger = LoggerFactory.getLogger(DataProcessingUtil.class);

    public static List<String> extractColumnsFromFile(MultipartFile file) throws IOException {
        List<String> columns = new ArrayList<>();
        InputStream inputStream = file.getInputStream();

        try (Workbook workbook = WorkbookFactory.create(inputStream)) {
            Sheet sheet = workbook.getSheetAt(0);
            Row headerRow = sheet.getRow(0);

            if (headerRow != null) {
                for (Cell cell : headerRow) {
                    cell.setCellType(CellType.STRING);
                    columns.add(cell.getStringCellValue().trim());
                }
            }
        } catch (Exception e) {
            logger.error("Error extracting columns: {}", e.getMessage(), e);
        }

        return columns;
    }

    public static String extractIdFromLink(String source, String link) {
        if (source.equalsIgnoreCase("jira")) {
            return link.replaceAll(".*/browse/([A-Z]+-\\d+).*", "$1");
        } else if (source.equalsIgnoreCase("confluence")) {
            return link.replaceAll(".*/pages/(\\d+).*", "$1");
        }
        return null;
    }

    public static String generateHash(String content) throws NoSuchAlgorithmException {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hashBytes = digest.digest(content.getBytes());
        StringBuilder hexString = new StringBuilder();
        for (byte b : hashBytes) {
            hexString.append(String.format("%02x", b));
        }
        return hexString.toString();
    }

public static String extractTextFromDocx(InputStream inputStream) throws IOException {
    StringBuilder extractedText = new StringBuilder();

    try (XWPFDocument document = new XWPFDocument(inputStream)) {
        boolean isRequestedFunctionalityTable = document.getParagraphs()
                .stream()
                .anyMatch(p -> p.getText().trim().equalsIgnoreCase("Requested Functionality"));

        if (isRequestedFunctionalityTable) {
            List<XWPFTable> tables = document.getTables();
            boolean tableFound = false;

            for (XWPFTable table : tables) {
                for (XWPFTableRow row : table.getRows()) {
                    List<XWPFTableCell> cells = row.getTableCells();

                    if (!cells.isEmpty()) {
                        String firstColumnText = cells.get(0).getText().trim().toLowerCase();

                        if (isRelevantColumn(firstColumnText)) {
                            tableFound = true;
                            extractedText.append("\n[").append(firstColumnText).append("]\n");

                            StringJoiner columnData = new StringJoiner("\n");
                            for (int i = 1; i < cells.size(); i++) {
                                columnData.add("Column " + (i + 1) + ": " + cells.get(i).getText().trim());
                            }
                            extractedText.append(columnData);
                        }
                    }
                }
            }

            return tableFound
                    ? extractedText.toString()
                    : "No relevant data found in the 'Requested Functionality' table.";
        } else {
             StringBuilder fullText = new StringBuilder();
            for (IBodyElement element : document.getBodyElements()) {
                if (element instanceof XWPFParagraph) {
                    XWPFParagraph paragraph = (XWPFParagraph) element;
                    String text = paragraph.getText().trim();
                    if (!text.isEmpty()) {
                        fullText.append(text).append("\n");
                    }
                } else if (element instanceof XWPFTable) {
                    XWPFTable table = (XWPFTable) element;
                    for (XWPFTableRow row : table.getRows()) {
                        for (XWPFTableCell cell : row.getTableCells()) {
                            fullText.append(cell.getText().trim()).append(" ");
                        }
                        fullText.append("\n");
                    }
                }
            }
            return fullText.toString().trim();
        }
    }
}


    private static boolean isRelevantColumn(String text) {
        return text.contains("current state") ||
                text.contains("including existing assets") ||
                text.contains("documentation if available") ||
                text.contains("client request") ||
                text.contains("business need");
    }


    public static String extractTextFromPdf(InputStream inputStream) throws IOException {
        try (PDDocument document = PDDocument.load(inputStream)) {
            PDFTextStripper pdfStripper = new PDFTextStripper();
            return pdfStripper.getText(document);
        }
    }
    public static String extractTextFromExcel(InputStream inputStream) throws IOException {
        StringBuilder extractedText = new StringBuilder();
        try (Workbook workbook = new XSSFWorkbook(inputStream)) {
            for (Sheet sheet : workbook) {
                for (Row row : sheet) {
                    for (Cell cell : row) {
                        extractedText.append(getCellValue(cell)).append(" ");
                    }
                    extractedText.append("\n");
                }
            }
        }
        return extractedText.toString();
    }
    public static String getCellValue(Cell cell) {
        return switch (cell.getCellType()) {
            case STRING -> cell.getStringCellValue();
            case NUMERIC -> String.valueOf(cell.getNumericCellValue());
            case BOOLEAN -> String.valueOf(cell.getBooleanCellValue());
            case FORMULA -> cell.getCellFormula();
            default -> "";
        };
    }
}



//






//code to get proper names of files
//package com.zinnia.zenius.utils;
//import org.apache.poi.ss.usermodel.*;
//import org.apache.poi.xssf.usermodel.XSSFWorkbook;
//import org.slf4j.Logger;
//import org.slf4j.LoggerFactory;
//import org.springframework.web.multipart.MultipartFile;
//import org.apache.poi.xwpf.usermodel.*;
//
//import java.io.*;
//import java.util.*;
//import java.util.zip.ZipEntry;
//import java.util.zip.ZipInputStream;
//
//import java.io.File;
//import java.io.FileOutputStream;
//import java.io.IOException;
//import org.apache.poi.xwpf.usermodel.*;
//import java.io.InputStream;
//import java.util.List;
//import java.util.StringJoiner;
//import java.security.MessageDigest;
//import java.security.NoSuchAlgorithmException;
//import java.util.ArrayList;
//
//import org.apache.pdfbox.pdmodel.PDDocument;
//import org.apache.pdfbox.text.PDFTextStripper;
//
//public class DataProcessingUtil {
//    private static final Logger logger = LoggerFactory.getLogger(DataProcessingUtil.class);
//
//    public static List<String> extractColumnsFromFile(MultipartFile file) throws IOException {
//        List<String> columns = new ArrayList<>();
//        InputStream inputStream = file.getInputStream();
//
//        try (Workbook workbook = WorkbookFactory.create(inputStream)) {
//            Sheet sheet = workbook.getSheetAt(0);
//            Row headerRow = sheet.getRow(0);
//
//            if (headerRow != null) {
//                for (Cell cell : headerRow) {
//                    cell.setCellType(CellType.STRING);
//                    columns.add(cell.getStringCellValue().trim());
//                }
//            }
//        } catch (Exception e) {
//            logger.error("Error extracting columns: {}", e.getMessage(), e);
//        }
//
//        return columns;
//    }
//
//    public static String extractIdFromLink(String source, String link) {
//        if (source.equalsIgnoreCase("jira")) {
//            return link.replaceAll(".*/browse/([A-Z0-9]+-\\d+).*", "$1");
//        } else if (source.equalsIgnoreCase("confluence")) {
//            return link.replaceAll(".*/pages/(\\d+).*", "$1");
//        }
//        return null;
//    }
//
//    public static String generateHash(String content) throws NoSuchAlgorithmException {
//        MessageDigest digest = MessageDigest.getInstance("SHA-256");
//        byte[] hashBytes = digest.digest(content.getBytes());
//        StringBuilder hexString = new StringBuilder();
//        for (byte b : hashBytes) {
//            hexString.append(String.format("%02x", b));
//        }
//        return hexString.toString();
//    }
//
//    public static String extractTextFromDocx(InputStream inputStream) throws IOException {
//        StringBuilder extractedText = new StringBuilder();
//
//        try (XWPFDocument document = new XWPFDocument(inputStream)) {
//            boolean isRequestedFunctionalityTable = document.getParagraphs()
//                    .stream()
//                    .anyMatch(p -> p.getText().trim().equalsIgnoreCase("Requested Functionality"));
//
//            if (isRequestedFunctionalityTable) {
//                List<XWPFTable> tables = document.getTables();
//                boolean tableFound = false;
//
//                for (XWPFTable table : tables) {
//                    for (XWPFTableRow row : table.getRows()) {
//                        List<XWPFTableCell> cells = row.getTableCells();
//
//                        if (!cells.isEmpty()) {
//                            String firstColumnText = cells.get(0).getText().trim().toLowerCase();
//
//                            if (isRelevantColumn(firstColumnText)) {
//                                tableFound = true;
//                                extractedText.append("\n[").append(firstColumnText).append("]\n");
//
//                                StringJoiner columnData = new StringJoiner("\n");
//                                for (int i = 1; i < cells.size(); i++) {
//                                    columnData.add("Column " + (i + 1) + ": " + cells.get(i).getText().trim());
//                                }
//                                extractedText.append(columnData);
//                            }
//                        }
//                    }
//                }
//
//                return tableFound
//                        ? extractedText.toString()
//                        : "No relevant data found in the 'Requested Functionality' table.";
//            } else {
//                StringBuilder fullText = new StringBuilder();
//                for (IBodyElement element : document.getBodyElements()) {
//                    if (element instanceof XWPFParagraph) {
//                        XWPFParagraph paragraph = (XWPFParagraph) element;
//                        String text = paragraph.getText().trim();
//                        if (!text.isEmpty()) {
//                            fullText.append(text).append("\n");
//                        }
//                    } else if (element instanceof XWPFTable) {
//                        XWPFTable table = (XWPFTable) element;
//                        for (XWPFTableRow row : table.getRows()) {
//                            for (XWPFTableCell cell : row.getTableCells()) {
//                                fullText.append(cell.getText().trim()).append(" ");
//                            }
//                            fullText.append("\n");
//                        }
//                    }
//                }
//                return fullText.toString().trim();
//            }
//        }
//    }
//
//
//    private static boolean isRelevantColumn(String text) {
//        return text.contains("current state") ||
//                text.contains("including existing assets") ||
//                text.contains("documentation if available") ||
//                text.contains("client request") ||
//                text.contains("business need");
//    }
//
//
//    public static String extractTextFromPdf(InputStream inputStream) throws IOException {
//        try (PDDocument document = PDDocument.load(inputStream)) {
//            PDFTextStripper pdfStripper = new PDFTextStripper();
//            return pdfStripper.getText(document);
//        }
//    }
//    public static String extractTextFromExcel(InputStream inputStream) throws IOException {
//        StringBuilder extractedText = new StringBuilder();
//        try (Workbook workbook = new XSSFWorkbook(inputStream)) {
//            for (Sheet sheet : workbook) {
//                for (Row row : sheet) {
//                    for (Cell cell : row) {
//                        extractedText.append(getCellValue(cell)).append(" ");
//                    }
//                    extractedText.append("\n");
//                }
//            }
//        }
//        return extractedText.toString();
//    }
//    public static String getCellValue(Cell cell) {
//        return switch (cell.getCellType()) {
//            case STRING -> cell.getStringCellValue();
//            case NUMERIC -> String.valueOf(cell.getNumericCellValue());
//            case BOOLEAN -> String.valueOf(cell.getBooleanCellValue());
//            case FORMULA -> cell.getCellFormula();
//            default -> "";
//        };
//    }
//    public static class DocxProcessingResult {
//        public String extractedText;
//        public List<String> hyperlinks;
//        public List<String> embeddedFileNames;
//
//        public DocxProcessingResult(String extractedText, List<String> hyperlinks, List<String> embeddedFileNames) {
//            this.extractedText = extractedText;
//            this.hyperlinks = hyperlinks;
//            this.embeddedFileNames = embeddedFileNames;
//        }
//    }
//
//    public static DocxProcessingResult extractDocxContentAndMetadata(MultipartFile file) throws Exception {
//        StringBuilder extractedText = new StringBuilder();
//        List<String> hyperlinks = new ArrayList<>();
//        List<String> embeddedFileNames = new ArrayList<>();
//
//        // Load DOCX file
//        XWPFDocument document = new XWPFDocument(file.getInputStream());
//
//        // Extract text (from table or entire document)
//        boolean foundTable = false;
//        for (XWPFTable table : document.getTables()) {
//            if (table.getText().toLowerCase().contains("requested functionality")) {
//                for (XWPFTableRow row : table.getRows()) {
//                    for (XWPFTableCell cell : row.getTableCells()) {
//                        extractedText.append(cell.getText()).append("\n");
//                    }
//                }
//                foundTable = true;
//                break;
//            }
//        }
//        if (!foundTable) {
//            // Extract text from paragraphs
//            for (XWPFParagraph paragraph : document.getParagraphs()) {
//                extractedText.append(paragraph.getText()).append("\n");
//
//                // Extract hyperlinks
//                for (XWPFRun run : paragraph.getRuns()) {
//                    if (run instanceof XWPFHyperlinkRun) {
//                        String url = ((XWPFHyperlinkRun) run).getHyperlink(document).getURL();
//                        if (url != null) {
//                            hyperlinks.add(url);
//                        }
//                    }
//                }
//            }
//        }
//
//        // Extract embedded files from DOCX
//        try (ZipInputStream zipIn = new ZipInputStream(file.getInputStream())) {
//            ZipEntry entry;
//            while ((entry = zipIn.getNextEntry()) != null) {
//                if (entry.getName().startsWith("word/embeddings/")) {
//                    String embeddedFileName = entry.getName().substring(entry.getName().lastIndexOf("/") + 1);
//                    embeddedFileNames.add(embeddedFileName);
//
//                    // Save embedded files to temporary files
//                    File tempFile = File.createTempFile("embedded_", "_" + embeddedFileName);
//                    try (FileOutputStream fos = new FileOutputStream(tempFile)) {
//                        byte[] buffer = new byte[1024];
//                        int len;
//                        while ((len = zipIn.read(buffer)) > 0) {
//                            fos.write(buffer, 0, len);
//                        }
//                    }
//                }
//            }
//        }
//
//        return new DocxProcessingResult(extractedText.toString(), hyperlinks, embeddedFileNames);
//    }
//
//
//}
//
//
//
//
