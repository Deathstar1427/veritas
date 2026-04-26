"""
PDF Report Generator for Veritas
Generates professional bias audit reports with charts and metrics
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import io
import tempfile
import matplotlib.pyplot as plt
import matplotlib
import os

matplotlib.use("Agg")  # Non-interactive backend


def _safe_str(value, fallback="N/A"):
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback

# Register UTF-8 compatible fonts to handle special characters
try:
    # Try to use DejaVuSans which supports most Unicode characters
    if os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        pdfmetrics.registerFont(
            TTFont("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        )
    elif os.path.exists("C:/Windows/Fonts/DejaVuSans.ttf"):
        pdfmetrics.registerFont(TTFont("DejaVuSans", "C:/Windows/Fonts/DejaVuSans.ttf"))
except:
    pass  # Fall back to built-in fonts


def generate_bar_chart(data_dict, title, filename):
    """Generate a bar chart as PNG image"""
    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    fig.patch.set_facecolor("#0f0f13")
    ax.set_facecolor("#18181f")

    groups = list(data_dict.keys())
    values = list(data_dict.values())

    # Color bars: highlight lowest in red
    colors_list = ["#6366f1"] * len(values)
    if values:
        min_idx = values.index(min(values))
        colors_list[min_idx] = "#ef4444"

    bars = ax.bar(groups, values, color=colors_list, edgecolor="#27272f", linewidth=1.5)

    # Styling
    ax.set_ylabel("Approval Rate (%)", color="#71717a", fontsize=11)
    ax.set_title(title, color="white", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylim(0, 100)
    ax.tick_params(colors="#71717a")
    ax.grid(axis="y", alpha=0.2, color="#27272f")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#27272f")
    ax.spines["bottom"].set_color("#27272f")

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.1f}%",
            ha="center",
            va="bottom",
            color="white",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(filename, facecolor="#0f0f13", edgecolor="none", bbox_inches="tight")
    plt.close()


def generate_disparate_impact_chart(dir_value, filename):
    """Generate donut chart for disparate impact ratio"""
    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    fig.patch.set_facecolor("#0f0f13")
    ax.set_facecolor("#0f0f13")

    if dir_value is None or dir_value > 1:
        dir_value = 1.0

    # Color based on threshold (0.8)
    if dir_value < 0.8:
        color = "#ef4444"  # Red - bias detected
        text_status = "BIAS DETECTED"
    else:
        color = "#10b981"  # Green - fair
        text_status = "FAIR"

    sizes = [dir_value * 100, (1 - dir_value) * 100]
    colors_pie = [color, "#27272f"]

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=["Fair", "Biased"],
        colors=colors_pie,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"color": "white", "fontsize": 10},
    )

    # Create donut hole
    centre_circle = plt.Circle((0, 0), 0.70, fc="#0f0f13")
    ax.add_artist(centre_circle)

    # Add center text
    ax.text(
        0,
        0,
        text_status,
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color=color,
    )
    ax.text(
        0,
        -0.15,
        f"Ratio: {dir_value:.2f}",
        ha="center",
        va="center",
        fontsize=10,
        color="#71717a",
    )

    plt.tight_layout()
    plt.savefig(filename, facecolor="#0f0f13", edgecolor="none", bbox_inches="tight")
    plt.close()


def generate_pdf_report(bias_results, gemini_explanation):
    """
    Generate complete PDF report with charts, metrics, and explanation
    Returns bytes suitable for response download
    """

    # Use a temporary directory for all chart images
    tmp_dir = tempfile.mkdtemp(prefix="veritas_charts_")
    chart_files = []

    try:
        # Create BytesIO buffer
        pdf_buffer = io.BytesIO()

        # Create PDF
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )

        styles = getSampleStyleSheet()
        story = []

        # Custom styles for dark theme
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#ffffff"),
            spaceAfter=12,
            fontName="Helvetica-Bold",
        )

        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#6366f1"),
            spaceAfter=10,
            fontName="Helvetica-Bold",
        )

        body_style = ParagraphStyle(
            "CustomBody",
            parent=styles["BodyText"],
            fontSize=10,
            textColor=colors.HexColor("#ffffff"),
            spaceAfter=8,
            leading=14,
        )

        # ===== HEADER =====
        story.append(Paragraph("Veritas", title_style))
        story.append(Paragraph("Bias Audit Report", styles["Heading2"]))

        # Domain and timestamp - explicitly resolved as strings so header fields
        # are deterministic and never depend on external rendering timing.
        domain = _safe_str(bias_results.get("domain"), "Unknown").title()
        records_analyzed = _safe_str(bias_results.get("total_records"), "0")
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        info_data = [
            ["Domain:", domain],
            ["Records Analyzed:", records_analyzed],
            ["Generated:", generated_at],
        ]

        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#18181f")),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#ffffff")),
                    ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#ffffff")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#27272f")),
                ]
            )
        )
        story.append(info_table)
        story.append(Spacer(1, 0.3 * inch))

        # ===== METRICS PER ATTRIBUTE =====
        bias_metrics = bias_results.get("bias_metrics", {})

        for attr_name, attr_data in bias_metrics.items():
            # Attribute heading
            story.append(
                Paragraph(f"Protected Attribute: {attr_name.title()}", heading_style)
            )

            # Severity badge
            severity = attr_data.get("bias_severity", "Unknown").upper()
            if severity == "HIGH":
                severity_color = colors.HexColor("#ef4444")
            elif severity == "MEDIUM":
                severity_color = colors.HexColor("#f59e0b")
            else:
                severity_color = colors.HexColor("#10b981")

            badge_data = [["BIAS SEVERITY: " + severity]]
            badge_table = Table(badge_data, colWidths=[6 * inch])
            badge_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, 0), severity_color),
                        ("TEXTCOLOR", (0, 0), (0, 0), colors.HexColor("#ffffff")),
                        ("ALIGN", (0, 0), (0, 0), "CENTER"),
                        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (0, 0), 12),
                        ("PADDING", (0, 0), (0, 0), 10),
                    ]
                )
            )
            story.append(badge_table)
            story.append(Spacer(1, 0.15 * inch))

            # Metrics table
            group_rates = attr_data.get("group_selection_rates", {})
            dpd = attr_data.get("demographic_parity_difference")
            eod = attr_data.get("equalized_odds_difference")
            dir_val = attr_data.get("disparate_impact_ratio")

            metrics_data = [
                ["Metric", "Value"],
                [
                    "Demographic Parity Difference",
                    f"{dpd:.4f}" if dpd is not None else "N/A",
                ],
                ["Equalized Odds Difference", f"{eod:.4f}" if eod is not None else "N/A"],
                [
                    "Disparate Impact Ratio",
                    f"{dir_val:.4f}" if dir_val is not None else "N/A",
                ],
            ]

            metrics_table = Table(metrics_data, colWidths=[3.5 * inch, 2.5 * inch])
            metrics_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366f1")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#ffffff")),
                        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#ffffff")),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#18181f")),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("PADDING", (0, 0), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#27272f")),
                    ]
                )
            )
            story.append(metrics_table)
            story.append(Spacer(1, 0.2 * inch))

            # Group outcome rates chart
            if group_rates:
                chart_filename = os.path.join(tmp_dir, f"chart_{attr_name}.png")
                chart_files.append(chart_filename)
                generate_bar_chart(
                    group_rates, f"{attr_name.title()} - Outcome Rates (%)", chart_filename
                )

                try:
                    img = Image(chart_filename, width=5.5 * inch, height=2.75 * inch)
                    story.append(img)
                    story.append(Spacer(1, 0.2 * inch))
                except Exception as e:
                    story.append(
                        Paragraph(f"[Chart generation failed: {str(e)}]", body_style)
                    )
                    story.append(Spacer(1, 0.2 * inch))

            # Disparate Impact Ratio chart
            if dir_val is not None:
                dir_chart_filename = os.path.join(tmp_dir, f"dir_chart_{attr_name}.png")
                chart_files.append(dir_chart_filename)
                generate_disparate_impact_chart(dir_val, dir_chart_filename)

                try:
                    img = Image(dir_chart_filename, width=3 * inch, height=3 * inch)
                    story.append(img)
                except Exception as e:
                    story.append(Paragraph(f"[DIR chart failed: {str(e)}]", body_style))

            story.append(Spacer(1, 0.3 * inch))

        # ===== GEMINI EXPLANATION =====
        story.append(PageBreak())
        story.append(Paragraph("Fairness Audit Explanation", heading_style))
        story.append(Paragraph(gemini_explanation, body_style))

        # ===== FOOTER =====
        story.append(Spacer(1, 0.3 * inch))
        footer_text = f"Report generated by Veritas on {generated_at}"
        story.append(
            Paragraph(
                footer_text,
                ParagraphStyle(
                    "Footer",
                    parent=styles["BodyText"],
                    fontSize=8,
                    textColor=colors.HexColor("#71717a"),
                    alignment=TA_CENTER,
                ),
            )
        )

        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)

        return pdf_buffer.getvalue()

    finally:
        # Clean up temporary chart files
        import shutil
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass

