package com.zinnia.zenius.utils;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.pdmodel.font.PDType0Font;

import java.io.*;

public class PdfGeneratorUtil {

    public static File createPdfFromText(String text, String outputDir, String fileName) throws IOException {
        File outputFile = new File(outputDir + File.separator + fileName);

        try (PDDocument document = new PDDocument()) {
            PDPage page = new PDPage(PDRectangle.A4);
            document.addPage(page);

            InputStream fontStream = PdfGeneratorUtil.class
                    .getClassLoader()
                    .getResourceAsStream("fonts/DejaVuSans.ttf");

            if (fontStream == null) {
                throw new FileNotFoundException("Font file not found in resources/fonts/DejaVuSans.ttf");
            }

            PDType0Font font = PDType0Font.load(document, fontStream);

            PDPageContentStream contentStream = new PDPageContentStream(document, page);
            try {
                contentStream.setFont(font, 12);
                contentStream.setLeading(14.5f);

                float margin = 50;
                float yStart = 750;
                float yPosition = yStart;
                float lineHeight = 14.5f;
                float width = PDRectangle.A4.getWidth() - 2 * margin;
                contentStream.beginText();
                contentStream.newLineAtOffset(margin, yPosition);

                String[] lines = text.replace("\t", "    ")
                        .replace("\u202F", " ")
                        .replace("\u00A0", " ")
                        .replace("\r", "")
                        .split("\n");

                for (String line : lines) {
                     String[] wrappedLines = wrapText(line, font, width);

                    for (String wrappedLine : wrappedLines) {
                         if (yPosition <= margin + lineHeight) {
                            contentStream.endText();
                            contentStream.close();

                             page = new PDPage(PDRectangle.A4);
                            document.addPage(page);
                            contentStream = new PDPageContentStream(document, page);
                            contentStream.setFont(font, 12);
                            contentStream.setLeading(14.5f);
                            yPosition = yStart;
                            contentStream.beginText();
                            contentStream.newLineAtOffset(margin, yPosition);
                        }

                        contentStream.showText(wrappedLine);
                        contentStream.newLine();
                        yPosition -= lineHeight;
                    }
                }

                contentStream.endText();
            } finally {
                contentStream.close();
            }

            document.save(outputFile);
        }

        return outputFile;
    }

     private static String[] wrapText(String text, PDType0Font font, float width) throws IOException {
         float maxWidth = width;

         String[] words = text.split(" ");
        StringBuilder currentLine = new StringBuilder();
        StringBuilder wrappedText = new StringBuilder();

        for (String word : words) {
             float currentWidth = font.getStringWidth(currentLine + word) / 1000 * 12;

             if (currentWidth > maxWidth) {
                wrappedText.append(currentLine).append("\n");
                currentLine = new StringBuilder(word + " ");
            } else {
                currentLine.append(word).append(" ");
            }
        }

         if (currentLine.length() > 0) {
            wrappedText.append(currentLine);
        }

        return wrappedText.toString().split("\n");
    }

    public static int getPageCount(File pdfFile) throws IOException {
        try (PDDocument document = PDDocument.load(pdfFile)) {
            return document.getNumberOfPages();
        }
    }
}
