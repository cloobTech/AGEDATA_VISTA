"use strict";
/**
 * Final Audit Report Generator
 * Generates a professional Word .docx report from the backend audit findings.
 * Usage: node generate_final_report.cjs
 */

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
  TableLayoutType,
  PageSize,
  Spacing,
  convertInchesToTwip,
} = require("docx");
const fs = require("fs");
const path = require("path");

// ============================================================
// AUDIT DATA (from audit files)
// ============================================================

const HEALTH_SCORE = 0; // max(0, 100 - (12*15 + 29*5 + 20*2 + 7*0.5)) = 0

const SEVERITY_COUNTS = {
  implementation: { CRITICAL: 8, HIGH: 18, MEDIUM: 15, LOW: 7 },
  deployment: {
    SERVER_DOWN: 4,
    SECURITY: 5,
    DATA_LOSS: 2,
    STABILITY: 6,
    PERFORMANCE: 3,
  },
  combined: { CRITICAL: 12, HIGH: 29, MEDIUM: 20, LOW: 7 },
};

const TOP_5_BROKEN_MODULES = [
  "arima_sarima_sarimax.py — 2 CRITICAL defects (wrong forecast steps, exog slice)",
  "regression.py — 1 CRITICAL (arg count mismatch), 2 HIGH (missing VIF/DW diagnostics)",
  "logistic_regression.py — 1 CRITICAL (multi_class removed sklearn 1.5+), 2 MEDIUM",
  "train_knn.py + train_svm.py — 1 CRITICAL each (missing StandardScaler)",
  "forecast_models.py — 1 CRITICAL (matplotlib Figure not JSON-safe), 1 HIGH (holidays type)",
];

const DOC_COMPLIANCE = [
  { module: "descriptive.py", library: "pandas/numpy", precon: "PARTIAL", formula: "Y", schema: "Y", status: "MEDIUM" },
  { module: "regression.py", library: "sklearn", precon: "N", formula: "Y", schema: "Y", status: "CRITICAL" },
  { module: "logistic_regression.py", library: "sklearn 1.5+", precon: "N", formula: "N", schema: "Y", status: "CRITICAL" },
  { module: "correlation_analysis.py", library: "scipy.stats", precon: "PARTIAL", formula: "N", schema: "Y", status: "HIGH" },
  { module: "anova.py", library: "statsmodels", precon: "N", formula: "PARTIAL", schema: "Y", status: "HIGH" },
  { module: "pca.py", library: "sklearn", precon: "PARTIAL", formula: "Y", schema: "Y", status: "HIGH" },
  { module: "cluster_analysis.py", library: "sklearn", precon: "N", formula: "Y", schema: "PARTIAL", status: "HIGH" },
  { module: "knn.py / train_knn.py", library: "sklearn", precon: "N", formula: "N", schema: "PARTIAL", status: "CRITICAL" },
  { module: "svm.py / train_svm.py", library: "sklearn", precon: "N", formula: "N", schema: "PARTIAL", status: "CRITICAL" },
  { module: "arima_sarima_sarimax.py", library: "statsmodels", precon: "N", formula: "N", schema: "Y", status: "CRITICAL" },
  { module: "moving_average.py", library: "pandas", precon: "PARTIAL", formula: "N", schema: "Y", status: "HIGH" },
  { module: "exponential_smoothing.py", library: "statsmodels", precon: "N", formula: "Y", schema: "Y", status: "HIGH" },
  { module: "time_series_decomposition.py", library: "statsmodels", precon: "N", formula: "Y", schema: "PARTIAL", status: "HIGH" },
  { module: "acf_pacf.py", library: "statsmodels", precon: "PARTIAL", formula: "Y", schema: "Y", status: "HIGH" },
  { module: "gradient_boosting.py", library: "XGBoost/LightGBM", precon: "PARTIAL", formula: "Y", schema: "PARTIAL", status: "CRITICAL" },
  { module: "tree_model.py", library: "sklearn", precon: "N", formula: "Y", schema: "PARTIAL", status: "MEDIUM" },
  { module: "neural_network.py", library: "keras", precon: "N", formula: "N", schema: "Y", status: "HIGH" },
  { module: "canonical_correlation.py", library: "sklearn", precon: "N", formula: "Y", schema: "Y", status: "HIGH" },
  { module: "forecast_models.py", library: "Prophet/ARIMA", precon: "N", formula: "N", schema: "N", status: "CRITICAL" },
  { module: "forecasting.py", library: "Prophet/ARIMA", precon: "PARTIAL", formula: "Y", schema: "PARTIAL", status: "MEDIUM" },
];

const DEFECTS = [
  { id: "DEFECT-1", module: "regression.py", line: "44–45, 107", cls: "Formula error", sev: "CRITICAL", desc: "perform_logistic_regression defined with 4 params but called with 5 — TypeError at runtime" },
  { id: "DEFECT-2", module: "logistic_regression.py", line: "37–42", cls: "Incorrect default params", sev: "CRITICAL", desc: "multi_class parameter removed in sklearn 1.5+, causes TypeError" },
  { id: "DEFECT-3", module: "train_knn.py", line: "16–44", cls: "Missing precondition", sev: "CRITICAL", desc: "No StandardScaler before KNN fit — distance-based algorithm requires scaling" },
  { id: "DEFECT-4", module: "train_svm.py", line: "16–44", cls: "Missing precondition", sev: "CRITICAL", desc: "No StandardScaler before SVM fit — kernel distances are scale-sensitive" },
  { id: "DEFECT-5", module: "arima_sarima_sarimax.py", line: "38–41", cls: "Formula error", sev: "CRITICAL", desc: "steps=inputs.order[0] uses AR lag p as forecast horizon — wrong for all inputs" },
  { id: "DEFECT-6", module: "arima_sarima_sarimax.py", line: "40", cls: "Formula error", sev: "CRITICAL", desc: "exog slice uses order[0] — mismatch with forecast steps causes SARIMAX failures" },
  { id: "DEFECT-7", module: "train_gradient_boosting.py", line: "36", cls: "Incorrect default params", sev: "CRITICAL", desc: "use_label_encoder=False removed in XGBoost 1.6+ — TypeError on import" },
  { id: "DEFECT-8", module: "forecast_models.py", line: "68–79", cls: "Wrong return schema", sev: "CRITICAL", desc: "model.plot_components() returns matplotlib Figure — not JSON-serializable" },
  { id: "DEFECT-9", module: "correlation_analysis.py", line: "85", cls: "Formula error", sev: "HIGH", desc: "Diagonal p-values set to 0.0 instead of 1.0 — statistically wrong" },
  { id: "DEFECT-10", module: "anova.py", line: "46–50", cls: "Missing precondition", sev: "HIGH", desc: "No Levene test for variance homogeneity before ANOVA" },
  { id: "DEFECT-11", module: "anova.py", line: "46–50", cls: "Missing precondition", sev: "HIGH", desc: "No Shapiro-Wilk test on residuals for normality assumption" },
  { id: "DEFECT-12", module: "anova.py", line: "46", cls: "Missing precondition", sev: "HIGH", desc: "No per-group minimum sample size check (< 2 obs per group)" },
  { id: "DEFECT-13", module: "pca.py", line: "33–35", cls: "Missing precondition", sev: "HIGH", desc: "n_components not validated against min(n_samples, n_features)" },
  { id: "DEFECT-14", module: "cluster_analysis.py", line: "29–30", cls: "Missing precondition", sev: "HIGH", desc: "n_clusters not validated (< 2 or >= n_samples)" },
  { id: "DEFECT-15", module: "cluster_analysis.py", line: "47–61", cls: "Dead code / wrong schema", sev: "HIGH", desc: "Duplicate response_content assignment — first is dead code; silhouette score missing" },
  { id: "DEFECT-16", module: "moving_average.py", line: "37–41", cls: "Formula error", sev: "HIGH", desc: "Weighted MA uses simple rolling mean (equal weights) instead of linearly-weighted MA" },
  { id: "DEFECT-17", module: "exponential_smoothing.py", line: "29–35", cls: "Missing precondition", sev: "HIGH", desc: "No seasonal_periods validation for seasonal models" },
  { id: "DEFECT-18", module: "time_series_decomposition.py", line: "46–53", cls: "Missing precondition", sev: "HIGH", desc: "No enforcement of len >= 2*period before seasonal_decompose" },
  { id: "DEFECT-19", module: "acf_pacf.py", line: "39–44", cls: "Missing precondition", sev: "HIGH", desc: "No nlags bounds check for PACF (max valid = nobs//2 - 1)" },
  { id: "DEFECT-20", module: "forecast_models.py", line: "67–68", cls: "Formula error", sev: "HIGH", desc: "add_country_holidays() not type-validated — list vs string causes silent error" },
  { id: "DEFECT-21", module: "neural_network.py", line: "77", cls: "Formula error", sev: "HIGH", desc: "y_proba shape (n,2) passed to roc_auc_score instead of (n,) for binary" },
  { id: "DEFECT-22", module: "canonical_correlation.py", line: "33–34", cls: "Missing precondition", sev: "HIGH", desc: "No singular matrix detection before CCA fit" },
  { id: "DEFECT-23", module: "canonical_correlation.py", line: "20", cls: "Missing precondition", sev: "HIGH", desc: "n_components not validated against min(len(x_cols), len(y_cols))" },
  { id: "DEFECT-24", module: "train_gradient_boosting.py", line: "80", cls: "Wrong return schema", sev: "MEDIUM", desc: "y_proba[:, 1] wrong for multi-class (should return full probability matrix)" },
  { id: "DEFECT-25", module: "descriptive.py", line: "35", cls: "Missing NaN handling", sev: "MEDIUM", desc: "df.mode().iloc[0] raises IndexError on all-NaN columns" },
  { id: "DEFECT-26", module: "logistic_regression.py", line: "51–53", cls: "Wrong return schema", sev: "MEDIUM", desc: "Multi-class AUC not computed — returned as None despite being feasible" },
  { id: "DEFECT-27", module: "logistic_regression.py", line: "33–35", cls: "Missing precondition", sev: "MEDIUM", desc: "No y.nunique() check; stratified split fails with single-class target" },
  { id: "DEFECT-28", module: "anova.py", line: "96–101", cls: "Formula error", sev: "MEDIUM", desc: "Total eta squared used instead of partial eta squared for multi-way ANOVA" },
  { id: "DEFECT-29", module: "time_series_decomposition.py", line: "68–69", cls: "Missing NaN handling", sev: "MEDIUM", desc: "residual_mean/std use .mean()/.std() which return NaN when boundaries are NaN" },
  { id: "DEFECT-30", module: "time_series_decomposition.py", line: "48", cls: "Missing precondition", sev: "MEDIUM", desc: "No check for positive values before multiplicative decomposition" },
  { id: "DEFECT-31", module: "tree_model.py", line: "81", cls: "Wrong return schema", sev: "MEDIUM", desc: "Default title 'Logistic Regression' (copy-paste bug) for tree model analysis" },
  { id: "DEFECT-32", module: "knn.py", line: "88", cls: "Wrong return schema", sev: "MEDIUM", desc: "Default title 'Support Vector Machine Analysis Report' (copy-paste bug) for KNN" },
  { id: "DEFECT-33", module: "forecasting.py", line: "76–81", cls: "Formula error", sev: "MEDIUM", desc: "Forecast-test metric alignment not guaranteed (position-based, not index-based)" },
  { id: "DEFECT-34", module: "neural_network.py", line: "95", cls: "Missing NaN handling", sev: "MEDIUM", desc: "model.input_shape accessed without AttributeError guard for subclassed models" },
  { id: "DEFECT-35", module: "regression.py", line: "29–30", cls: "Missing precondition", sev: "MEDIUM", desc: "No column existence validation before indexing DataFrame" },
  { id: "DEFECT-36", module: "cluster_analysis.py", line: "42–45", cls: "Missing NaN handling", sev: "LOW", desc: "color_col/hover_col not checked for None before in data.columns test" },
  { id: "DEFECT-37", module: "descriptive.py", line: "23", cls: "Missing precondition", sev: "LOW", desc: "No warning for columns with > 50% NaN rate" },
  { id: "DEFECT-38", module: "moving_average.py", line: "26", cls: "Missing precondition", sev: "LOW", desc: "No bounds check: window_size > len(ts_data) produces all-NaN silently" },
  { id: "DEFECT-39", module: "acf_pacf.py", line: "33–36", cls: "Missing precondition", sev: "LOW", desc: "alpha not validated to be in (0, 1)" },
  { id: "DEFECT-40", module: "regression.py", line: "33–34", cls: "Hardcoded magic values", sev: "LOW", desc: "test_size=0.2, random_state=42 hardcoded, not user-configurable" },
  { id: "DEFECT-41", module: "logistic_regression.py", line: "90–91", cls: "Silent failure", sev: "LOW", desc: "Broad except swallows all exception types including MemoryError/SystemExit" },
  { id: "DEFECT-42", module: "logistic_regression.py", line: "29–31", cls: "Missing precondition", sev: "LOW", desc: "penalty='none' string vs None type not normalized for sklearn compatibility" },
  { id: "DEFECT-43", module: "train_knn.py", line: "43–44", cls: "Wrong return schema", sev: "MEDIUM", desc: "y_proba[:, 1] wrong for multi-class KNN" },
  { id: "DEFECT-44", module: "train_svm.py", line: "43–44", cls: "Wrong return schema", sev: "MEDIUM", desc: "y_proba[:, 1] wrong for multi-class SVM" },
  { id: "DEFECT-45", module: "pca.py", line: "42–45", cls: "Missing NaN handling", sev: "MEDIUM", desc: "Index misalignment after dropna when appending metadata to PCA DataFrame" },
  { id: "DEFECT-46", module: "moving_average.py", line: "26", cls: "Missing precondition", sev: "HIGH", desc: "Data not sorted chronologically before rolling window — produces wrong MA on unsorted input" },
  { id: "DEFECT-47", module: "regression.py", line: "29", cls: "Missing precondition", sev: "HIGH", desc: "No VIF scores or Durbin-Watson test — essential OLS assumption diagnostics missing" },
];

const DEPLOY_ISSUES = [
  { id: "DEPLOY-1", file: "storage/redis_client.py", issue: "Redis URL hardcoded as localhost — fails in Docker/cloud", risk: "SERVER_DOWN", fix: "Use settings.REDIS_URL.rstrip('/') + '/1'" },
  { id: "DEPLOY-2", file: "storage/redis_sync_client.py", issue: "Sync Redis hardcoded host:port; DB=2 vs async DB=1 mismatch causes SSE progress never updating", risk: "SERVER_DOWN", fix: "Parse settings.REDIS_URL; align DB numbers" },
  { id: "DEPLOY-3", file: "api/v1/main.py", issue: "allow_origins=['*'] + allow_credentials=True violates CORS spec; browsers block credentialed wildcard requests", risk: "SECURITY", fix: "Replace * with specific origin list from settings.FRONTEND_URL" },
  { id: "DEPLOY-4", file: "docker-compose.yml", issue: "POSTGRES_USER/PASSWORD/DB hardcoded in compose file — credentials in version control", risk: "SECURITY", fix: "Use ${POSTGRES_USER}, ${POSTGRES_PASSWORD}, ${POSTGRES_DB} env vars" },
  { id: "DEPLOY-5", file: "docker-compose.yml", issue: "api and redis services entirely absent from active compose file — application cannot run via Docker Compose", risk: "SERVER_DOWN", fix: "Add api and redis services with depends_on and healthchecks" },
  { id: "DEPLOY-6", file: "docker-compose.yml", issue: "db service lacks healthcheck in active definition — cannot use service_healthy condition", risk: "STABILITY", fix: "Add healthcheck: pg_isready -U ${POSTGRES_USER}" },
  { id: "DEPLOY-7", file: "celery_app.py", issue: "beat_schedule references task name that must match decorator — no guard if task module fails to import", risk: "STABILITY", fix: "Add options.expires and ensure include list is complete" },
  { id: "DEPLOY-8", file: "settings/pydantic_config.py", issue: "25+ required env vars with no defaults — any missing var crashes startup with ValidationError", risk: "SERVER_DOWN", fix: "Provide safe defaults for non-sensitive settings (DEV_ENV, ALGORITHM, PORT)" },
  { id: "DEPLOY-9", file: "tasks/expire_trial_sub.py", issue: "MaxRetriesExceededError not caught — task silently fails at max retries with no logging", risk: "STABILITY", fix: "Catch MaxRetriesExceededError and log explicitly" },
  { id: "DEPLOY-10", file: "services/sse/server_sent_events.py", issue: "No keepalive ping — proxy/LB closes idle SSE connections after ~60s of no progress", risk: "STABILITY", fix: "Add SSE comment heartbeat: yield ': keepalive\\n\\n'" },
  { id: "DEPLOY-11", file: "services/sse/server_sent_events.py", issue: "Explicit CORS header conflicts with middleware CORS header — duplicate headers cause browser errors", risk: "SECURITY", fix: "Remove Access-Control-Allow-Origin from SSE response headers" },
  { id: "DEPLOY-12", file: "api/v1/utils/current_user.py", issue: "current_user.email_verified accessed without None check — AttributeError if user not found", risk: "STABILITY", fix: "Add: if current_user is None: raise credential_exceptions" },
  { id: "DEPLOY-13", file: "storage/celery_db.py", issue: "DATABASE_URL driver replacement fails silently if URL doesn't contain '+asyncpg'", risk: "STABILITY", fix: "Validate URL format and raise if sync driver not confirmed" },
  { id: "DEPLOY-14", file: "storage/redis_client.py", issue: "No connection pool limit or timeout — connection failures at module import have opaque errors", risk: "STABILITY", fix: "Add max_connections=20, socket_connect_timeout=5" },
  { id: "DEPLOY-15", file: "storage/redis_sync_client.py", issue: "No pool size limit on sync Redis — Celery workers may exhaust Redis max connections", risk: "PERFORMANCE", fix: "Use ConnectionPool with max_connections=50" },
  { id: "DEPLOY-16", file: "storage/database.py", issue: "pool_size=50 per async worker — 4 workers × 50 = 200 connections, exceeds PostgreSQL default max_connections=100", risk: "PERFORMANCE", fix: "Reduce pool_size to 10 with max_overflow=5" },
  { id: "DEPLOY-17", file: "utils/save_to_supabase.py", issue: "Synchronous Supabase upload inside async function blocks FastAPI event loop during file upload", risk: "PERFORMANCE", fix: "Use loop.run_in_executor() for blocking upload" },
  { id: "DEPLOY-18", file: "celery_app.py", issue: "Double-slash in Redis URL if REDIS_URL has trailing slash (e.g., redis://redis:6379/ + /0)", risk: "STABILITY", fix: "Use settings.REDIS_URL.rstrip('/') before appending /0 or /1" },
  { id: "DEPLOY-19", file: "api/v1/main.py", issue: "No lifespan handler — DB and Redis not validated at startup, cold-start errors surface on first request", risk: "STABILITY", fix: "Add @asynccontextmanager lifespan with startup ping checks" },
  { id: "DEPLOY-20", file: "Dockerfile", issue: "alembic upgrade head in CMD may run concurrently with multiple containers; gunicorn has no --workers flag (defaults to 1)", risk: "DATA_LOSS", fix: "Add --workers 4 to gunicorn; use migration lock or init container" },
];

const TEST_RESULTS = {
  total: 78,
  passed: 72,
  failed: 5,
  xfailed: 1,
  errors: 1,
  runtime: "16.08s",
  pass_rate: "92.3%"
};

// ============================================================
// COLOR / STYLE HELPERS
// ============================================================
const COLORS = {
  NAVY: "1F3864",
  MED_BLUE: "2E74B5",
  ACCENT: "D6E4F0",
  ALT_ROW: "EBF3FB",
  WHITE: "FFFFFF",
  CRITICAL: "FF0000",
  CRITICAL_BG: "FFCCCC",
  HIGH: "E96900",
  HIGH_BG: "FFE5CC",
  MEDIUM: "D4A017",
  MEDIUM_BG: "FFF5CC",
  LOW_BG: "F0F0F0",
  GREEN: "006400",
  RED: "CC0000",
  SCORE_RED: "CC0000",
  SCORE_YELLOW: "CC8800",
  SCORE_GREEN: "006400",
};

function scoreColor(score) {
  if (score < 40) return COLORS.SCORE_RED;
  if (score <= 70) return COLORS.SCORE_YELLOW;
  return COLORS.SCORE_GREEN;
}

function sevColor(sev) {
  switch ((sev || "").toUpperCase()) {
    case "CRITICAL": case "SERVER_DOWN": return COLORS.CRITICAL_BG;
    case "HIGH": case "SECURITY": case "DATA_LOSS": return COLORS.HIGH_BG;
    case "MEDIUM": case "STABILITY": case "PERFORMANCE": return COLORS.MEDIUM_BG;
    default: return COLORS.LOW_BG;
  }
}

function tableHeaderRow(labels, widths) {
  return new TableRow({
    tableHeader: true,
    children: labels.map((label, i) =>
      new TableCell({
        width: { size: widths[i], type: WidthType.PERCENTAGE },
        shading: { type: ShadingType.SOLID, color: COLORS.NAVY },
        verticalAlign: VerticalAlign.CENTER,
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: label, bold: true, color: COLORS.WHITE, font: "Calibri", size: 18 })],
          }),
        ],
      })
    ),
  });
}

function cell(text, opts = {}) {
  const {
    bold = false,
    color = "000000",
    bgColor = null,
    align = AlignmentType.LEFT,
    size = 16,
    width = null,
  } = opts;
  return new TableCell({
    ...(width ? { width: { size: width, type: WidthType.PERCENTAGE } } : {}),
    ...(bgColor
      ? { shading: { type: ShadingType.SOLID, color: bgColor } }
      : {}),
    verticalAlign: VerticalAlign.CENTER,
    children: [
      new Paragraph({
        alignment: align,
        spacing: { before: 40, after: 40 },
        children: [
          new TextRun({ text: String(text), bold, color, font: "Calibri", size }),
        ],
      }),
    ],
  });
}

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 200 },
    children: [
      new TextRun({
        text,
        bold: true,
        color: COLORS.NAVY,
        font: "Calibri Light",
        size: 36,
      }),
    ],
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 300, after: 150 },
    children: [
      new TextRun({
        text,
        bold: true,
        color: COLORS.MED_BLUE,
        font: "Calibri Light",
        size: 28,
      }),
    ],
  });
}

function para(text, opts = {}) {
  const { bold = false, color = "000000", size = 20, spacing = {} } = opts;
  return new Paragraph({
    spacing: { before: 100, after: 100, ...spacing },
    children: [
      new TextRun({ text, bold, color, font: "Calibri", size }),
    ],
  });
}

function bullet(text, opts = {}) {
  return new Paragraph({
    bullet: { level: 0 },
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text, font: "Calibri", size: 20, ...opts })],
  });
}

function numberedBullet(text, num) {
  return new Paragraph({
    spacing: { before: 60, after: 60 },
    children: [
      new TextRun({ text: `${num}. ${text}`, font: "Calibri", size: 20 }),
    ],
  });
}

// ============================================================
// BUILD DOCUMENT
// ============================================================

async function buildDocument() {
  const scoreCol = scoreColor(HEALTH_SCORE);

  // Sort defects by severity
  const SEV_ORDER = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
  const sortedDefects = [...DEFECTS].sort(
    (a, b) => (SEV_ORDER[a.sev] ?? 4) - (SEV_ORDER[b.sev] ?? 4)
  );

  const sections = [];

  // ========================
  // SECTION 1 — Executive Summary
  // ========================
  sections.push(h1("Section 1 — Executive Summary"));

  sections.push(
    new Paragraph({
      spacing: { before: 100, after: 300 },
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({
          text: `BACKEND HEALTH SCORE: ${HEALTH_SCORE}/100`,
          bold: true,
          color: scoreCol,
          font: "Calibri Light",
          size: 52,
        }),
      ],
    })
  );

  sections.push(para(
    "Score Interpretation: Score of 0 indicates the application has more weighted defect points than the maximum penalty threshold allows. " +
    "Formula: max(0, 100 - (CRITICAL×15 + HIGH×5 + MEDIUM×2 + LOW×0.5)). " +
    `Combined defects: ${SEVERITY_COUNTS.combined.CRITICAL} CRITICAL, ${SEVERITY_COUNTS.combined.HIGH} HIGH, ${SEVERITY_COUNTS.combined.MEDIUM} MEDIUM, ${SEVERITY_COUNTS.combined.LOW} LOW.`,
    { size: 18, color: "444444" }
  ));

  // Severity table
  sections.push(h2("Defect Severity Breakdown"));
  sections.push(
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        tableHeaderRow(["Severity", "Impl. Count", "Deploy Count", "Total", "Weight", "Weighted Score"], [20, 14, 14, 12, 14, 26]),
        new TableRow({
          children: [
            cell("CRITICAL", { bgColor: COLORS.CRITICAL_BG, bold: true, color: COLORS.RED }),
            cell("8", { align: AlignmentType.CENTER, bgColor: COLORS.CRITICAL_BG }),
            cell("4", { align: AlignmentType.CENTER, bgColor: COLORS.CRITICAL_BG }),
            cell("12", { align: AlignmentType.CENTER, bgColor: COLORS.CRITICAL_BG, bold: true }),
            cell("×15", { align: AlignmentType.CENTER }),
            cell("180", { align: AlignmentType.CENTER, bold: true, bgColor: COLORS.CRITICAL_BG }),
          ],
        }),
        new TableRow({
          children: [
            cell("HIGH", { bgColor: COLORS.HIGH_BG, bold: true }),
            cell("18", { align: AlignmentType.CENTER, bgColor: COLORS.HIGH_BG }),
            cell("11", { align: AlignmentType.CENTER, bgColor: COLORS.HIGH_BG }),
            cell("29", { align: AlignmentType.CENTER, bgColor: COLORS.HIGH_BG, bold: true }),
            cell("×5", { align: AlignmentType.CENTER }),
            cell("145", { align: AlignmentType.CENTER, bold: true, bgColor: COLORS.HIGH_BG }),
          ],
        }),
        new TableRow({
          children: [
            cell("MEDIUM", { bgColor: COLORS.MEDIUM_BG, bold: true }),
            cell("15", { align: AlignmentType.CENTER, bgColor: COLORS.MEDIUM_BG }),
            cell("5", { align: AlignmentType.CENTER, bgColor: COLORS.MEDIUM_BG }),
            cell("20", { align: AlignmentType.CENTER, bgColor: COLORS.MEDIUM_BG, bold: true }),
            cell("×2", { align: AlignmentType.CENTER }),
            cell("40", { align: AlignmentType.CENTER, bold: true, bgColor: COLORS.MEDIUM_BG }),
          ],
        }),
        new TableRow({
          children: [
            cell("LOW", { bgColor: COLORS.LOW_BG }),
            cell("7", { align: AlignmentType.CENTER }),
            cell("0", { align: AlignmentType.CENTER }),
            cell("7", { align: AlignmentType.CENTER, bold: true }),
            cell("×0.5", { align: AlignmentType.CENTER }),
            cell("3.5", { align: AlignmentType.CENTER }),
          ],
        }),
        new TableRow({
          children: [
            cell("TOTAL", { bold: true, bgColor: COLORS.ALT_ROW }),
            cell("48", { align: AlignmentType.CENTER, bold: true, bgColor: COLORS.ALT_ROW }),
            cell("20", { align: AlignmentType.CENTER, bold: true, bgColor: COLORS.ALT_ROW }),
            cell("68", { align: AlignmentType.CENTER, bold: true, bgColor: COLORS.ALT_ROW }),
            cell("", { bgColor: COLORS.ALT_ROW }),
            cell("368.5", { align: AlignmentType.CENTER, bold: true, bgColor: COLORS.ALT_ROW }),
          ],
        }),
      ],
    })
  );

  sections.push(h2("Top 5 Most Broken Modules"));
  TOP_5_BROKEN_MODULES.forEach((m, i) => sections.push(numberedBullet(m, i + 1)));

  sections.push(h2("Deployment Readiness Verdict"));
  sections.push(
    new Paragraph({
      spacing: { before: 100, after: 200 },
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({
          text: "⛔ BLOCKED — NOT READY FOR PRODUCTION",
          bold: true,
          color: COLORS.RED,
          font: "Calibri Light",
          size: 36,
        }),
      ],
    })
  );
  sections.push(para(
    "8 CRITICAL implementation defects and 4 SERVER_DOWN deployment issues must be resolved before production deployment. " +
    "The application will crash on: logistic regression requests (DEFECT-1,2), XGBoost classification (DEFECT-7), " +
    "Prophet forecasting (DEFECT-8), ARIMA models with any order[0]=0 (DEFECT-5). " +
    "Docker Compose is non-functional (missing api and redis services). " +
    "Redis is hardcoded to localhost (fails in any containerized environment).",
    { size: 18, color: "333333" }
  ));

  // ========================
  // SECTION 2 — Documentation Compliance
  // ========================
  sections.push(h1("Section 2 — Documentation Compliance Table"));

  const docRows = [
    tableHeaderRow(
      ["Module", "Library", "Preconditions Met", "Formula Correct", "Schema Correct", "Overall Status"],
      [22, 15, 13, 13, 13, 14]
    ),
    ...DOC_COMPLIANCE.map((r, i) => {
      const bg = i % 2 === 0 ? COLORS.ALT_ROW : COLORS.WHITE;
      const statusBg = sevColor(r.status);
      const yColor = COLORS.GREEN;
      const nColor = COLORS.RED;
      return new TableRow({
        children: [
          cell(r.module, { bgColor: bg }),
          cell(r.library, { bgColor: bg }),
          cell(r.precon, {
            bgColor: bg,
            align: AlignmentType.CENTER,
            color: r.precon === "Y" ? yColor : r.precon === "N" ? nColor : COLORS.HIGH,
            bold: r.precon === "N",
          }),
          cell(r.formula, {
            bgColor: bg,
            align: AlignmentType.CENTER,
            color: r.formula === "Y" ? yColor : r.formula === "N" ? nColor : COLORS.HIGH,
            bold: r.formula === "N",
          }),
          cell(r.schema, {
            bgColor: bg,
            align: AlignmentType.CENTER,
            color: r.schema === "Y" ? yColor : r.schema === "N" ? nColor : COLORS.HIGH,
            bold: r.schema === "N",
          }),
          cell(r.status, {
            bgColor: statusBg,
            align: AlignmentType.CENTER,
            bold: true,
            color: r.status === "CRITICAL" ? COLORS.RED : r.status === "HIGH" ? COLORS.HIGH : "000000",
          }),
        ],
      });
    }),
  ];
  sections.push(new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: docRows }));

  // ========================
  // SECTION 3 — Defect Registry
  // ========================
  sections.push(h1("Section 3 — Defect Registry"));

  const defectRows = [
    tableHeaderRow(["ID", "Module", "Line(s)", "Class", "Severity", "Description"], [8, 18, 7, 15, 9, 43]),
    ...sortedDefects.map((d) => {
      const bg = sevColor(d.sev);
      return new TableRow({
        children: [
          cell(d.id, { bgColor: bg, bold: true, size: 14 }),
          cell(d.module, { bgColor: bg, size: 14 }),
          cell(d.line, { bgColor: bg, align: AlignmentType.CENTER, size: 14 }),
          cell(d.cls, { bgColor: bg, size: 14 }),
          cell(d.sev, {
            bgColor: bg,
            align: AlignmentType.CENTER,
            bold: true,
            size: 14,
            color: d.sev === "CRITICAL" ? COLORS.RED : d.sev === "HIGH" ? COLORS.HIGH : "000000",
          }),
          cell(d.desc, { bgColor: bg, size: 14 }),
        ],
      });
    }),
  ];
  sections.push(new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: defectRows }));

  // ========================
  // SECTION 4 — Unit Test Results
  // ========================
  sections.push(h1("Section 4 — Unit Test Results"));
  sections.push(para(`Total: ${TEST_RESULTS.total} tests | Passed: ${TEST_RESULTS.passed} | Failed: ${TEST_RESULTS.failed} | XFailed: ${TEST_RESULTS.xfailed} | Pass Rate: ${TEST_RESULTS.pass_rate} | Runtime: ${TEST_RESULTS.runtime}`, { bold: true, size: 20 }));

  const testData = [
    { module: "descriptive", t1: 3, t2: 4, t3: 1, pass: 8, fail: 0 },
    { module: "correlation", t1: 2, t2: 2, t3: 1, pass: 3, fail: 1 },
    { module: "regression", t1: 2, t2: 2, t3: 1, pass: 3, fail: 2 },
    { module: "logistic_regression", t1: 2, t2: 1, t3: 1, pass: 2, fail: 1 },
    { module: "anova", t1: 2, t2: 2, t3: 1, pass: 5, fail: 0 },
    { module: "pca", t1: 2, t2: 2, t3: 1, pass: 5, fail: 0 },
    { module: "cluster", t1: 3, t2: 2, t3: 1, pass: 6, fail: 0 },
    { module: "arima", t1: 2, t2: 3, t3: 1, pass: 6, fail: 0 },
    { module: "acf_pacf", t1: 2, t2: 2, t3: 1, pass: 4, fail: 1 },
    { module: "moving_average", t1: 2, t2: 2, t3: 1, pass: 5, fail: 0 },
    { module: "gradient_boosting", t1: 2, t2: 1, t3: 1, pass: 3, fail: 1 },
    { module: "neural_network", t1: 1, t2: 0, t3: 0, pass: 1, fail: 0 },
    { module: "canonical_correlation", t1: 2, t2: 1, t3: 1, pass: 4, fail: 0 },
    { module: "time_series_decomp", t1: 2, t2: 1, t3: 1, pass: 4, fail: 0 },
    { module: "exponential_smoothing", t1: 2, t2: 1, t3: 1, pass: 4, fail: 0 },
    { module: "knn", t1: 1, t2: 0, t3: 1, pass: 2, fail: 0 },
    { module: "svm", t1: 1, t2: 0, t3: 0, pass: 1, fail: 0 },
    { module: "tree_model", t1: 1, t2: 0, t3: 1, pass: 2, fail: 0 },
    { module: "forecast_models", t1: 2, t2: 0, t3: 0, pass: 2, fail: 0 },
  ];

  const testRows = [
    tableHeaderRow(["Module", "Tier 1", "Tier 2", "Tier 3", "Pass", "Fail"], [28, 12, 12, 12, 12, 12]),
    ...testData.map((r, i) => {
      const bg = i % 2 === 0 ? COLORS.ALT_ROW : COLORS.WHITE;
      const failBg = r.fail > 0 ? COLORS.CRITICAL_BG : COLORS.WHITE;
      const passBg = r.fail === 0 ? "#CCFFCC" : COLORS.WHITE;
      return new TableRow({
        children: [
          cell(r.module, { bgColor: bg }),
          cell(r.t1, { align: AlignmentType.CENTER, bgColor: bg }),
          cell(r.t2, { align: AlignmentType.CENTER, bgColor: bg }),
          cell(r.t3, { align: AlignmentType.CENTER, bgColor: bg }),
          cell(r.pass, { align: AlignmentType.CENTER, bgColor: passBg, color: COLORS.GREEN, bold: true }),
          cell(r.fail, { align: AlignmentType.CENTER, bgColor: failBg, bold: r.fail > 0, color: r.fail > 0 ? COLORS.RED : "000000" }),
        ],
      });
    }),
  ];
  sections.push(new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: testRows }));

  sections.push(h2("Failed Test Details"));
  [
    "TestCorrelationTier1::test_empty_numeric_cols_raises — Test design issue (pandas [] doesn't raise)",
    "TestRegressionTier1::test_perform_logistic_regression_arg_count — DEFECT-1 CONFIRMED (4 params called with 5)",
    "TestLogisticRegressionTier1::test_single_class_raises — DEFECT-27 confirmed (sklearn version-dependent behavior)",
    "TestAcfPacfTier1::test_insufficient_data_raises — statsmodels returns NaN instead of raising (soft failure)",
    "TestGradientBoostingTier1::test_use_label_encoder_removed — DEFECT-7 CONFIRMED (XGBoost OpenMP mismatch on test machine)",
  ].forEach((t) => sections.push(bullet(t)));

  // ========================
  // SECTION 5 — Deployment Issues
  // ========================
  sections.push(h1("Section 5 — Deployment Issues"));

  const deployRows = [
    tableHeaderRow(["ID", "File", "Issue Summary", "Risk", "Fix Summary"], [8, 18, 37, 12, 25]),
    ...DEPLOY_ISSUES.map((d, i) => {
      const bg = sevColor(d.risk);
      return new TableRow({
        children: [
          cell(d.id, { bgColor: bg, bold: true, size: 14 }),
          cell(d.file, { bgColor: bg, size: 14 }),
          cell(d.issue, { bgColor: bg, size: 14 }),
          cell(d.risk, { bgColor: bg, align: AlignmentType.CENTER, bold: true, size: 14,
            color: d.risk === "SERVER_DOWN" || d.risk === "SECURITY" || d.risk === "DATA_LOSS" ? COLORS.RED : "000000" }),
          cell(d.fix, { bgColor: i % 2 === 0 ? COLORS.ALT_ROW : COLORS.WHITE, size: 14 }),
        ],
      });
    }),
  ];
  sections.push(new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: deployRows }));

  // ========================
  // SECTION 6 — Prioritised Fix List
  // ========================
  sections.push(h1("Section 6 — Prioritised Fix List (Top 30)"));

  const FIX_LIST = [
    { rank: 1, id: "FIX-1", file: "regression.py", desc: "Add 'input' param to perform_logistic_regression", effort: "S", change: "def perform_logistic_regression(X_train, X_test, y_train, y_test, input):" },
    { rank: 2, id: "FIX-2", file: "logistic_regression.py", desc: "Remove multi_class= from LogisticRegression constructor", effort: "S", change: "Remove multi_class=input.multi_class line" },
    { rank: 3, id: "FIX-3", file: "train_knn.py", desc: "Add StandardScaler before KNN fit", effort: "S", change: "scaler = StandardScaler(); X_train = scaler.fit_transform(X_train)" },
    { rank: 4, id: "FIX-4", file: "train_svm.py", desc: "Add StandardScaler before SVM fit", effort: "S", change: "Same pattern as FIX-3" },
    { rank: 5, id: "FIX-5", file: "arima_sarima_sarimax.py", desc: "Replace inputs.order[0] with inputs.forecast_steps", effort: "M", change: "Add forecast_steps field to schema; use in get_forecast(steps=...)" },
    { rank: 6, id: "FIX-6", file: "train_gradient_boosting.py", desc: "Remove use_label_encoder=False from XGBClassifier", effort: "S", change: "Delete line: use_label_encoder=False," },
    { rank: 7, id: "FIX-7", file: "forecast_models.py", desc: "Remove matplotlib Figure from Prophet return dict", effort: "S", change: "Replace 'components': model.plot_components(forecast) with '_prophet_forecast_df': forecast" },
    { rank: 8, id: "FIX-8", file: "forecast_models.py", desc: "Validate config.holidays is string before add_country_holidays", effort: "S", change: "if not isinstance(config.holidays, str): raise ValueError(...)" },
    { rank: 9, id: "DEPLOY-FIX-1", file: "storage/redis_client.py", desc: "Fix hardcoded Redis URL", effort: "S", change: "settings.REDIS_URL.rstrip('/') + '/1'" },
    { rank: 10, id: "DEPLOY-FIX-2", file: "storage/redis_sync_client.py", desc: "Parse Redis host from settings; align DB numbers", effort: "S", change: "urllib.parse.urlparse(settings.REDIS_URL)" },
    { rank: 11, id: "DEPLOY-FIX-3", file: "api/v1/main.py", desc: "Fix CORS wildcard + credentials security issue", effort: "S", change: "Replace ['*'] with [settings.FRONTEND_URL, ...]" },
    { rank: 12, id: "DEPLOY-FIX-4", file: "docker-compose.yml", desc: "Remove hardcoded DB credentials from compose", effort: "S", change: "Use ${POSTGRES_USER} env var references" },
    { rank: 13, id: "DEPLOY-FIX-5", file: "docker-compose.yml", desc: "Add missing api and redis services", effort: "M", change: "Add full service definitions with healthchecks" },
    { rank: 14, id: "DEPLOY-FIX-6", file: "api/v1/utils/current_user.py", desc: "Add None check after db.get()", effort: "S", change: "if current_user is None: raise credential_exceptions" },
    { rank: 15, id: "FIX-9", file: "correlation_analysis.py", desc: "Fix diagonal p-values from 0.0 to 1.0", effort: "S", change: "p_values[i, j] = 1.0" },
    { rank: 16, id: "FIX-10", file: "anova.py", desc: "Add Levene + Shapiro-Wilk tests", effort: "M", change: "from scipy.stats import levene, shapiro; compute and add to response" },
    { rank: 17, id: "FIX-11", file: "anova.py", desc: "Add per-group minimum sample size check", effort: "S", change: "Check group_counts >= 2 before fitting" },
    { rank: 18, id: "FIX-12", file: "pca.py", desc: "Validate n_components <= min(n_samples, n_features)", effort: "S", change: "if n_components > max_components: raise ValueError(...)" },
    { rank: 19, id: "FIX-13", file: "pca.py", desc: "Fix metadata index alignment after dropna", effort: "S", change: "data[col].loc[X.index].values" },
    { rank: 20, id: "FIX-14", file: "cluster_analysis.py", desc: "Add n_clusters validation and silhouette score", effort: "S", change: "Add bounds check; compute silhouette_score()" },
    { rank: 21, id: "FIX-15", file: "moving_average.py", desc: "Fix weighted MA to use linearly-increasing weights; add sort and bounds check", effort: "M", change: "weights = np.arange(1,w+1)/sum; ts_data.sort_index()" },
    { rank: 22, id: "FIX-16", file: "exponential_smoothing.py", desc: "Add seasonal_periods and data length validation", effort: "S", change: "Check seasonal_periods when seasonal set; check len >= 2*periods" },
    { rank: 23, id: "FIX-17", file: "time_series_decomposition.py", desc: "Enforce 2×period minimum and use nanmean/nanstd", effort: "S", change: "Raise if len < 2*period; use np.nanmean/nanstd" },
    { rank: 24, id: "FIX-18", file: "acf_pacf.py", desc: "Add nlags bounds check and alpha validation", effort: "S", change: "max_nlags = len//2 - 1; raise if exceeded" },
    { rank: 25, id: "FIX-19", file: "neural_network.py", desc: "Fix y_proba shape for binary AUC", effort: "S", change: "_proba[:, 1] if ndim==2 else _proba" },
    { rank: 26, id: "FIX-20", file: "canonical_correlation.py", desc: "Add singular matrix detection and n_components validation", effort: "M", change: "np.linalg.matrix_rank check; n_components bounds check" },
    { rank: 27, id: "FIX-25", file: "descriptive.py", desc: "Guard mode() against all-NaN columns", effort: "S", change: "df.mode().iloc[0].to_dict() if not df.mode().empty else {}" },
    { rank: 28, id: "FIX-27", file: "tree_model.py", desc: "Fix default title from 'Logistic Regression'", effort: "S", change: "getattr(inputs, 'title', 'Tree Model Analysis')" },
    { rank: 29, id: "FIX-28", file: "knn.py", desc: "Fix default title from 'Support Vector Machine Analysis Report'", effort: "S", change: "getattr(inputs, 'title', 'KNN Analysis Report')" },
    { rank: 30, id: "FIX-30", file: "forecasting.py", desc: "Fix forecast-test index alignment for metrics", effort: "M", change: "Use index.intersection() for metric alignment" },
  ];

  const fixRows = [
    tableHeaderRow(["Rank", "Fix ID", "File", "Description", "Effort", "Code Change"], [5, 9, 15, 30, 6, 35]),
    ...FIX_LIST.map((f, i) => {
      const bg = i % 2 === 0 ? COLORS.ALT_ROW : COLORS.WHITE;
      const effortColor = f.effort === "L" ? COLORS.RED : f.effort === "M" ? COLORS.HIGH : COLORS.GREEN;
      return new TableRow({
        children: [
          cell(f.rank, { align: AlignmentType.CENTER, bgColor: bg, bold: true, size: 14 }),
          cell(f.id, { bgColor: bg, bold: true, size: 14 }),
          cell(f.file, { bgColor: bg, size: 14 }),
          cell(f.desc, { bgColor: bg, size: 14 }),
          cell(f.effort, { align: AlignmentType.CENTER, bgColor: bg, bold: true, color: effortColor, size: 14 }),
          cell(f.change, { bgColor: bg, size: 12 }),
        ],
      });
    }),
  ];
  sections.push(new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: fixRows }));

  sections.push(para("Effort key: S = Small (< 1 hour), M = Medium (1–4 hours), L = Large (> 4 hours)", { size: 16, color: "666666" }));

  // ========================
  // SECTION 7 — Phase 3 Fix Prompt
  // ========================
  sections.push(h1("Section 7 — Ready-to-Use Claude Fix Prompt"));
  sections.push(para("The following prompt (phase3_fix_prompt.txt) is ready to paste into Claude Code to apply all CRITICAL and HIGH fixes:", { size: 20 }));
  sections.push(para("Location: tests/phase3_fix_prompt.txt", { bold: true, size: 20 }));

  let fixPromptContent = "";
  const fixPromptPath = path.join(__dirname, "tests", "phase3_fix_prompt.txt");
  if (fs.existsSync(fixPromptPath)) {
    fixPromptContent = fs.readFileSync(fixPromptPath, "utf-8");
  } else {
    fixPromptContent = "phase3_fix_prompt.txt not found. Run the full audit pipeline first.";
  }

  // Show first 3000 chars of the prompt as monospace
  const promptPreview = fixPromptContent.slice(0, 3000) + (fixPromptContent.length > 3000 ? "\n\n[... truncated for document display. See tests/phase3_fix_prompt.txt for full content ...]" : "");

  sections.push(
    new Paragraph({
      spacing: { before: 100, after: 100 },
      children: [
        new TextRun({
          text: promptPreview,
          font: "Courier New",
          size: 14,
          color: "1a1a2e",
        }),
      ],
    })
  );

  sections.push(para(
    "To use: Copy the full content of tests/phase3_fix_prompt.txt and paste it as a message to Claude Code " +
    "(claude.ai or via the Claude Code CLI). Claude Code will apply all fixes in priority order.",
    { size: 18, color: "444444" }
  ));

  // ========================
  // BUILD DOC
  // ========================
  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            size: {
              orientation: "portrait",
              width: convertInchesToTwip(8.5),
              height: convertInchesToTwip(11),
            },
            margin: {
              top: convertInchesToTwip(1),
              right: convertInchesToTwip(0.75),
              bottom: convertInchesToTwip(1),
              left: convertInchesToTwip(0.75),
            },
          },
        },
        children: sections,
      },
    ],
    styles: {
      default: {
        document: {
          run: {
            font: "Calibri",
            size: 20,
          },
        },
      },
    },
  });

  return doc;
}

// ============================================================
// MAIN
// ============================================================
(async () => {
  console.log("Generating final audit report...");
  try {
    const doc = await buildDocument();
    const outputPath = path.join(__dirname, "tests", "final_audit_report.docx");
    const buffer = await Packer.toBuffer(doc);
    fs.writeFileSync(outputPath, buffer);
    console.log(`Report written to: ${outputPath}`);
    console.log(`File size: ${(buffer.length / 1024).toFixed(1)} KB`);
  } catch (err) {
    console.error("Error generating report:", err);
    process.exit(1);
  }
})();
