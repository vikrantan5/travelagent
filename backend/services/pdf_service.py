"""
PDF Generation Service for Travel Plans
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import json
from datetime import datetime
import os
from pathlib import Path

def clean_markdown_for_pdf(text: str) -> str:
    """Clean markdown formatting for PDF"""
    # Remove markdown formatting
    text = text.replace('**', '')
    text = text.replace('##', '')
    text = text.replace('#', '')
    text = text.replace('*', '')
    text = text.replace('- ', '• ')
    return text

def generate_trip_pdf(trip_data: dict, output_path: str) -> str:
    """
    Generate a PDF from trip plan data
    
    Args:
        trip_data: Dictionary containing trip plan details
        output_path: Path where PDF should be saved
        
    Returns:
        Path to generated PDF file
    """
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for PDF elements
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#3b82f6'),
        spaceAfter=6,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        leading=14
    )
    
    # Title
    story.append(Paragraph("🌍 Your Travel Plan", title_style))
    story.append(Spacer(1, 0.2 * inch))
    
    # Generated date
    date_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    story.append(Paragraph(date_text, body_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Extract and format data
    try:
        # Destination Overview
        if 'destination_agent_response' in trip_data:
            story.append(Paragraph("📍 Destination Overview", heading_style))
            dest_text = clean_markdown_for_pdf(trip_data['destination_agent_response'][:1500])
            story.append(Paragraph(dest_text, body_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Flight Recommendations
        if 'flight_agent_response' in trip_data:
            story.append(Paragraph("✈️ Flight Recommendations", heading_style))
            flight_text = clean_markdown_for_pdf(trip_data['flight_agent_response'][:1500])
            story.append(Paragraph(flight_text, body_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Hotel Recommendations
        if 'hotel_agent_response' in trip_data:
            story.append(Paragraph("🏨 Hotel Recommendations", heading_style))
            hotel_text = clean_markdown_for_pdf(trip_data['hotel_agent_response'][:1500])
            story.append(Paragraph(hotel_text, body_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Page break before itinerary
        story.append(PageBreak())
        
        # Restaurant Recommendations
        if 'restaurant_agent_response' in trip_data:
            story.append(Paragraph("🍽️ Restaurant Recommendations", heading_style))
            restaurant_text = clean_markdown_for_pdf(trip_data['restaurant_agent_response'][:1500])
            story.append(Paragraph(restaurant_text, body_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Itinerary
        if 'itinerary_agent_response' in trip_data:
            story.append(Paragraph("📅 Day-by-Day Itinerary", heading_style))
            itinerary_text = clean_markdown_for_pdf(trip_data['itinerary_agent_response'][:2000])
            story.append(Paragraph(itinerary_text, body_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Budget Breakdown
        if 'budget_agent_response' in trip_data:
            story.append(PageBreak())
            story.append(Paragraph("💰 Budget Breakdown", heading_style))
            budget_text = clean_markdown_for_pdf(trip_data['budget_agent_response'][:1500])
            story.append(Paragraph(budget_text, body_style))
            story.append(Spacer(1, 0.2 * inch))
        
        # Product Recommendations
        if 'product_recommendations' in trip_data and trip_data['product_recommendations']:
            story.append(Paragraph("🎒 Recommended Travel Essentials", heading_style))
            products = trip_data['product_recommendations']
            for product in products[:8]:
                product_text = f"• <b>{product.get('name', 'Product')}</b> ({product.get('category', 'General')})"
                story.append(Paragraph(product_text, body_style))
                reason_text = f"  {product.get('reason', '')}"
                story.append(Paragraph(reason_text, body_style))
                price_text = f"  Price: {product.get('price_range', 'N/A')}"
                story.append(Paragraph(price_text, body_style))
                story.append(Spacer(1, 0.1 * inch))
        
        # Footer
        story.append(Spacer(1, 0.5 * inch))
        footer_text = "Powered by TripCraft AI - Your Intelligent Travel Companion"
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        story.append(Paragraph(footer_text, footer_style))
        
    except Exception as e:
        error_text = f"Error generating some sections: {str(e)}"
        story.append(Paragraph(error_text, body_style))
    
    # Build PDF
    doc.build(story)
    
    return output_path


def generate_trip_pdf_from_json(trip_json: str, destination_name: str = "trip") -> str:
    """
    Generate PDF from JSON string
    
    Args:
        trip_json: JSON string containing trip data
        destination_name: Name for the PDF file
        
    Returns:
        Path to generated PDF
    """
    # Parse JSON
    trip_data = json.loads(trip_json) if isinstance(trip_json, str) else trip_json
    
    # Create output directory if it doesn't exist
    output_dir = Path("/tmp/trip_pdfs")
    output_dir.mkdir(exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in destination_name if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{safe_name}_{timestamp}.pdf"
    output_path = str(output_dir / filename)
    
    # Generate PDF
    return generate_trip_pdf(trip_data, output_path)
