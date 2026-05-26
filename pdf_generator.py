import io
import time
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_pdf_report(pitch, market_data, finance_data, mvp_data, synthesis_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("CONFIDENTIAL VC DUE DILIGENCE REPORT", styles['Title']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"<b>Startup Pitch:</b> {pitch}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Executive Summary (from Synthesis)
    if synthesis_data:
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Paragraph(f"<b>Strongest Signal:</b> {synthesis_data.get('strongest_signal', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Biggest Contradiction:</b> {synthesis_data.get('biggest_contradiction', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Critical Path:</b>", styles['Normal']))
        for p in synthesis_data.get('critical_path', []):
            story.append(Paragraph(f"- {p}", styles['Normal']))
        story.append(Spacer(1, 12))

    # Market Analysis
    if market_data:
        story.append(Paragraph("Market Analysis", styles['Heading2']))
        metrics = market_data.get("Market_Metrics", {})
        if metrics:
            tam = metrics.get("TAM", {}).get("value", "-")
            sam = metrics.get("SAM", {}).get("value", "-")
            som = metrics.get("SOM", {}).get("value", "-")
            cagr = metrics.get("CAGR", {}).get("value", "-")
            data = [["Metric", "Value"],
                    ["TAM", tam],
                    ["SAM", sam],
                    ["SOM", som],
                    ["CAGR", cagr]]
            t = Table(data, colWidths=[100, 200])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            story.append(t)
        story.append(Spacer(1, 12))

    # Financial Analysis
    if finance_data:
        story.append(Paragraph("Financial Analysis", styles['Heading2']))
        story.append(Paragraph(f"<b>Investment Score:</b> {finance_data.get('Investment_Score', '-')}/100", styles['Normal']))
        story.append(Paragraph(f"<b>LTV/CAC Estimate:</b> {finance_data.get('LTV_CAC_Estimate', '-')}", styles['Normal']))
        story.append(Paragraph(f"<b>Capital Intensity:</b> {finance_data.get('Capital_Intensity', '-')}", styles['Normal']))
        story.append(Paragraph(f"<b>Payback Period:</b> {finance_data.get('Payback_Period_Months', '-')}", styles['Normal']))
        story.append(Spacer(1, 12))

    # MVP Roadmap Summary
    if mvp_data:
        story.append(Paragraph("MVP Roadmap Summary", styles['Heading2']))
        story.append(Paragraph(f"<b>Complexity Score:</b> {mvp_data.get('Complexity_Score', '-')}", styles['Normal']))
        story.append(Paragraph(f"<b>Time to Market:</b> {mvp_data.get('Time_to_Market', '-')}", styles['Normal']))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Focus Features:</b>", styles['Normal']))
        for feat in mvp_data.get("MVP_Focus_Features", []):
            story.append(Paragraph(f"- {feat}", styles['Normal']))
        story.append(Spacer(1, 12))

    # Risk Register
    story.append(Paragraph("Risk Register", styles['Heading2']))
    risk_data = [["Risk Type", "Description"]]
    if finance_data and "Red_Flags" in finance_data:
        for flag in finance_data["Red_Flags"]:
            risk_data.append(["Financial", flag])
    if finance_data and "Death_Scenario" in finance_data:
        risk_data.append(["Death Scenario", finance_data["Death_Scenario"]])
    if market_data and "Regulatory_Risks" in market_data:
        for reg in market_data["Regulatory_Risks"]:
            risk_data.append(["Regulatory", reg.get("regulation", "") + ": " + reg.get("impact", "")])
    if market_data and "Choke_Points" in market_data:
        for cp in market_data["Choke_Points"]:
            risk_data.append(["Choke Point", cp.get("lethal_scenario", "")])

    if len(risk_data) > 1:
        rt = Table(risk_data, colWidths=[100, 350])
        rt.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkred),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), True)
        ]))
        story.append(rt)
    else:
        story.append(Paragraph("No major risks recorded.", styles['Normal']))
        
    story.append(Spacer(1, 24))
    story.append(Paragraph(f"Generated by AI Startup Analyst v3.0 - {time.strftime('%Y-%m-%d %H:%M:%S')}", styles['Italic']))

    doc.build(story)
    buffer.seek(0)
    return buffer
