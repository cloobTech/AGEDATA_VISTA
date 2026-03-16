"use strict";

/**
 * AgeDataVista Backend Audit Report Generator
 * Reads audit_findings.json and produces audit_report.docx
 * Requires: npm install docx
 */

const fs = require("fs");
const path = require("path");

const {
  Document,
  Packer,
  Paragraph,
  Table,
  TableRow,
  TableCell,
  TextRun,
  HeadingLevel,
  AlignmentType,
  WidthType,
  ShadingType,
  BorderStyle,
  VerticalAlign,
  PageSize,
  PageOrientation,
} = require("docx");

// ─── Colours ────────────────────────────────────────────────────────────────
const DARK_BLUE   = "1F3864"; // Dark blue heading
const MID_BLUE    = "2E75B6"; // Section heading
const LIGHT_BLUE  = "D6E4F0"; // Table alternating row
const WHITE       = "FFFFFF";
const RED         = "C0392B";
const ORANGE      = "E67E22";
const GREEN       = "27AE60";
const GRAY        = "F2F2F2";
const DARK_GRAY   = "4A4A4A";

// ─── Helpers ────────────────────────────────────────────────────────────────
function heading(text, level, color = DARK_BLUE) {
  return new Paragraph({
    heading: level,
    spacing: { before: 300, after: 150 },
    children: [
      new TextRun({
        text,
        bold: true,
        color,
        size: level === HeadingLevel.HEADING_1 ? 36 : level === HeadingLevel.HEADING_2 ? 28 : 24,
        font: "Calibri",
      }),
    ],
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 100, after: 100 },
    children: [
      new TextRun({
        text,
        size: 22,
        font: "Calibri",
        color: opts.color || DARK_GRAY,
        bold: opts.bold || false,
        italics: opts.italics || false,
      }),
    ],
    alignment: opts.align || AlignmentType.LEFT,
  });
}

function bullet(text, level = 0) {
  return new Paragraph({
    bullet: { level },
    spacing: { before: 60, after: 60 },
    children: [
      new TextRun({
        text,
        size: 20,
        font: "Calibri",
        color: DARK_GRAY,
      }),
    ],
  });
}

function severityColor(sev) {
  if (!sev) return DARK_GRAY;
  const s = sev.toUpperCase();
  if (s === "CRITICAL") return RED;
  if (s === "HIGH")     return ORANGE;
  if (s === "MEDIUM")   return "8E44AD";
  return GREEN;
}

function tableCell(text, opts = {}) {
  const bgColor = opts.bg || WHITE;
  const textColor = opts.textColor || DARK_GRAY;
  const bold = opts.bold || false;
  return new TableCell({
    shading: { type: ShadingType.CLEAR, fill: bgColor },
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 60, bottom: 60, left: 80, right: 80 },
    children: [
      new Paragraph({
        children: [
          new TextRun({
            text: String(text || ""),
            size: 18,
            font: "Calibri",
            color: textColor,
            bold,
          }),
        ],
      }),
    ],
  });
}

function headerRow(columns) {
  return new TableRow({
    tableHeader: true,
    children: columns.map((col) =>
      tableCell(col, { bg: DARK_BLUE, textColor: WHITE, bold: true })
    ),
  });
}

function dataRow(cells, isAlt = false) {
  const bg = isAlt ? LIGHT_BLUE : WHITE;
  return new TableRow({
    children: cells.map((c) =>
      typeof c === "object"
        ? tableCell(c.text, { bg: c.bg || bg, textColor: c.color || DARK_GRAY, bold: c.bold })
        : tableCell(c, { bg })
    ),
  });
}

function spacer() {
  return new Paragraph({ spacing: { before: 200, after: 200 }, children: [] });
}

function divider() {
  return new Paragraph({
    spacing: { before: 100, after: 100 },
    border: { bottom: { color: MID_BLUE, size: 6, style: BorderStyle.SINGLE } },
    children: [],
  });
}

// ─── Report Builder ──────────────────────────────────────────────────────────
function buildReport(data) {
  const meta   = data.audit_metadata;
  const sum    = data.overall_summary;
  const ph1    = data.phase1_environment;
  const ph2    = data.phase2_static_analysis;
  const ph3    = data.phase3_test_results;
  const ph4    = data.phase4_route_schema_audit;
  const ph5    = data.phase5_deployment_audit;
  const top20  = data.top20_prioritized_fixes;

  const scoreColor = sum.health_score >= 70 ? GREEN : sum.health_score >= 50 ? ORANGE : RED;

  const sections = [];

  // ── Title Page ──────────────────────────────────────────────────────────
  sections.push(
    new Paragraph({
      spacing: { before: 600, after: 200 },
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({
          text: "AgeDataVista Backend",
          bold: true,
          size: 52,
          color: DARK_BLUE,
          font: "Calibri",
        }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 100, after: 600 },
      children: [
        new TextRun({
          text: "Full Technical Audit Report",
          size: 36,
          color: MID_BLUE,
          font: "Calibri",
          italics: true,
        }),
      ],
    }),
    new Table({
      width: { size: 50, type: WidthType.PERCENTAGE },
      alignment: AlignmentType.CENTER,
      rows: [
        dataRow(["Audit Date", meta.audit_date]),
        dataRow(["Project",    meta.project], true),
        dataRow(["Python",     meta.python_version]),
        dataRow(["FastAPI",    meta.fastapi_version], true),
        dataRow(["Files Audited", meta.total_python_files]),
      ],
    }),
    spacer(),
    divider(),
  );

  // ── Section 1: Executive Summary ────────────────────────────────────────
  sections.push(
    heading("1. Executive Summary", HeadingLevel.HEADING_1),
    spacer(),

    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        headerRow(["Metric", "Value"]),
        dataRow([
          { text: "Overall Health Score", bold: true },
          { text: `${sum.health_score} / 100`, color: scoreColor, bold: true },
        ], false),
        dataRow(["Critical Findings", sum.critical_count], true),
        dataRow(["High Findings",     sum.high_count]),
        dataRow(["Medium Findings",   sum.medium_count], true),
        dataRow(["Low Findings",      sum.low_count]),
        dataRow(["Total Findings",    sum.total_findings], true),
        dataRow(["Test Pass Rate",    `${ph3.pass_rate_percent}% (${ph3.passed}/${ph3.total})`]),
        dataRow(["Tests Passed",      ph3.passed], true),
        dataRow(["Tests Failed",      ph3.failed]),
      ],
    }),

    spacer(),
    para(sum.assessment, { italics: true }),
    spacer(),

    para("Modules Broken at Runtime:", { bold: true }),
    ...sum.modules_broken_at_runtime.map((m) => bullet(`• ${m}`)),
    spacer(),
    divider(),
  );

  // ── Section 2: Environment & Deployment Issues ───────────────────────────
  sections.push(
    heading("2. Environment & Deployment Issues", HeadingLevel.HEADING_1),
    para(ph1.summary),
    spacer(),
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        headerRow(["ID", "Severity", "Category", "File", "Description"]),
        ...[...ph1.findings, ...ph5.findings].map((f, i) =>
          dataRow([
            f.id,
            { text: f.severity, color: severityColor(f.severity), bold: true },
            f.category,
            f.file || "-",
            (f.description || "").substring(0, 180) + ((f.description || "").length > 180 ? "..." : ""),
          ], i % 2 === 1)
        ),
      ],
    }),
    spacer(),
    divider(),
  );

  // ── Section 3: Analysis Module Audit ────────────────────────────────────
  sections.push(
    heading("3. Analysis Module Static Analysis", HeadingLevel.HEADING_1),
    para(ph2.summary),
    spacer(),
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        headerRow(["ID", "Severity", "Category", "File", "Description"]),
        ...ph2.findings.map((f, i) =>
          dataRow([
            f.id,
            { text: f.severity, color: severityColor(f.severity), bold: true },
            f.category,
            f.file || "-",
            (f.description || "").substring(0, 180) + ((f.description || "").length > 180 ? "..." : ""),
          ], i % 2 === 1)
        ),
      ],
    }),
    spacer(),
    divider(),
  );

  // ── Section 4: Unit Test Results ────────────────────────────────────────
  sections.push(
    heading("4. Unit Test Results", HeadingLevel.HEADING_1),
    para(`${ph3.passed} passed / ${ph3.failed} failed / ${ph3.total} total — runtime: ~280 seconds`),
    spacer(),
    heading("4a. Failures (Confirm Real Bugs)", HeadingLevel.HEADING_2, MID_BLUE),
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        headerRow(["Test Name", "Root Cause"]),
        ...ph3.failures.map((f, i) =>
          dataRow([f.test, f.reason], i % 2 === 1)
        ),
      ],
    }),
    spacer(),
    heading("4b. Notable Passing Tests", HeadingLevel.HEADING_2, MID_BLUE),
    ...ph3.notable_passes.map((p) => bullet(p)),
    spacer(),
    divider(),
  );

  // ── Section 5: Route & Schema Issues ────────────────────────────────────
  sections.push(
    heading("5. Route & Schema Audit", HeadingLevel.HEADING_1),
    para(ph4.summary),
    spacer(),
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        headerRow(["ID", "Severity", "Category", "File", "Description"]),
        ...ph4.findings.map((f, i) =>
          dataRow([
            f.id,
            { text: f.severity, color: severityColor(f.severity), bold: true },
            f.category,
            f.file || "-",
            (f.description || "").substring(0, 200) + ((f.description || "").length > 200 ? "..." : ""),
          ], i % 2 === 1)
        ),
      ],
    }),
    spacer(),
    divider(),
  );

  // ── Section 6: Top 20 Prioritized Fixes ─────────────────────────────────
  sections.push(
    heading("6. Top 20 Prioritized Fixes", HeadingLevel.HEADING_1),
    spacer(),
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        headerRow(["#", "Finding ID", "Fix Description", "Effort"]),
        ...top20.map((fix, i) =>
          dataRow([
            { text: String(fix.priority), bold: true },
            fix.id,
            fix.fix,
            fix.effort,
          ], i % 2 === 1)
        ),
      ],
    }),
    spacer(),
    divider(),
  );

  // ── Section 7: Recommended Refactoring Prompt ───────────────────────────
  sections.push(
    heading("7. Recommended Refactoring Prompt", HeadingLevel.HEADING_1),
    para("Use the following prompt with an AI coding assistant to systematically apply the top-priority fixes:", { italics: true }),
    spacer(),
    new Paragraph({
      shading: { type: ShadingType.CLEAR, fill: GRAY },
      border: {
        top:    { color: MID_BLUE, size: 4, style: BorderStyle.SINGLE },
        bottom: { color: MID_BLUE, size: 4, style: BorderStyle.SINGLE },
        left:   { color: MID_BLUE, size: 4, style: BorderStyle.SINGLE },
        right:  { color: MID_BLUE, size: 4, style: BorderStyle.SINGLE },
      },
      spacing: { before: 100, after: 100 },
      children: [
        new TextRun({
          text: data.refactoring_prompt,
          size: 18,
          font: "Courier New",
          color: DARK_GRAY,
        }),
      ],
    }),
    spacer(),
  );

  return sections;
}

// ─── Main ───────────────────────────────────────────────────────────────────
async function main() {
  const findingsPath = path.join(__dirname, "audit_findings.json");
  const outputPath   = path.join(__dirname, "audit_report.docx");

  if (!fs.existsSync(findingsPath)) {
    console.error("audit_findings.json not found at", findingsPath);
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(findingsPath, "utf8"));
  console.log("Loaded audit_findings.json — building report...");

  const children = buildReport(data);

  const doc = new Document({
    title: "AgeDataVista Backend Audit Report",
    description: "Full technical audit of the FastAPI data analytics backend",
    creator: "Claude Code Automated Audit",
    sections: [
      {
        properties: {
          page: {
            size: {
              orientation: PageOrientation.PORTRAIT,
              width: 12240,   // US Letter width in twips (8.5in * 1440)
              height: 15840,  // US Letter height in twips (11in * 1440)
            },
            margin: {
              top: 1080,
              right: 1080,
              bottom: 1080,
              left: 1080,
            },
          },
        },
        children,
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  console.log(`\n✅ Audit report written to: ${outputPath}`);
  console.log(`   Size: ${(buffer.length / 1024).toFixed(1)} KB`);
}

main().catch((err) => {
  console.error("Error generating report:", err);
  process.exit(1);
});
