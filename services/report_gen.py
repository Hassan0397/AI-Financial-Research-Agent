from fpdf import FPDF
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import base64
import re

# -----------------------------------------------------------
#  PROFESSIONAL PDF REPORT GENERATOR - ENHANCED
# -----------------------------------------------------------

def _clean_text_for_pdf(text):
    """Clean text for PDF encoding (Latin-1 compatible)"""
    if text is None:
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Replace common problematic Unicode characters
    replacements = {
        '\u2014': '--',     # em dash
        '\u2013': '-',      # en dash
        '\u2018': "'",      # left single quote
        '\u2019': "'",      # right single quote
        '\u201c': '"',      # left double quote
        '\u201d': '"',      # right double quote
        '\u2026': '...',    # ellipsis
        '\u00a0': ' ',      # non-breaking space
        '\u00ae': '(R)',    # registered trademark
        '\u00a9': '(C)',    # copyright
        '\u2122': '(TM)',    # trademark
        '\u00b0': ' deg',   # degree symbol
        '\u00b1': '+/-',    # plus-minus
        '\u00bc': '1/4',    # fraction 1/4
        '\u00bd': '1/2',    # fraction 1/2
        '\u00be': '3/4',    # fraction 3/4
        '\u00f7': '/',      # division
        '\u00d7': 'x',      # multiplication
        '\u2012': '-',      # figure dash
        '\u2010': '-',      # hyphen
        '\u2011': '-',      # non-breaking hyphen
        '\u2212': '-',      # minus sign
        '\u00b2': '^2',     # superscript 2
        '\u00b3': '^3',     # superscript 3
        '\u00b9': '^1',     # superscript 1
        '\u20ac': 'EUR',    # euro
        '\u00a3': 'GBP',    # pound
        '\u00a5': 'JPY',    # yen
        '\u00a2': 'cents',  # cent
        '\u00a7': 'SS',     # section
        '\u00b6': 'PP',     # paragraph
        '\u2022': '*',      # bullet
        '\u25cf': '*',      # black circle
        '\u25cb': 'o',      # white circle
        '\u25a0': '■',      # black square
        '\u25aa': '▪',      # black small square
        '\u25b2': '^',      # black up-pointing triangle
        '\u25bc': 'v',      # black down-pointing triangle
    }
    
    # Apply replacements
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    
    # Remove any remaining non-Latin-1 characters using regex
    # This preserves ASCII and common Latin-1 characters
    text = re.sub(r'[^\x00-\xFF]', ' ', text)
    
    # Clean up multiple spaces
    text = ' '.join(text.split())
    
    return text

def _safe_format_number(value, default=0):
    """Safely format numbers, handling strings and None"""
    if value is None:
        return default
    
    try:
        if isinstance(value, str):
            # Remove commas, currency symbols, and other non-numeric characters
            value = value.replace(',', '').replace('$', '').replace('€', '').replace('£', '').strip()
        
        # Try to convert to float
        num = float(value)
        return num
    except (ValueError, TypeError):
        return default

def _safe_format_price(price):
    """Safely format price values"""
    price_num = _safe_format_number(price, 0)
    return f"${price_num:,.2f}"

def _safe_format_volume(volume):
    """Safely format volume values"""
    volume_num = _safe_format_number(volume, 0)
    if volume_num >= 1_000_000_000:
        return f"${volume_num/1_000_000_000:.2f}B"
    elif volume_num >= 1_000_000:
        return f"${volume_num/1_000_000:.2f}M"
    elif volume_num >= 1_000:
        return f"${volume_num/1_000:.2f}K"
    else:
        return f"${volume_num:,.0f}"

def create_technical_indicators_chart(prices, volumes):
    """Create professional technical indicators chart"""
    # Convert to numeric lists
    prices_numeric = []
    volumes_numeric = []
    
    for price in prices:
        prices_numeric.append(_safe_format_number(price, 0))
    
    for volume in volumes:
        volumes_numeric.append(_safe_format_number(volume, 0))
    
    fig, axes = plt.subplots(3, 1, figsize=(10, 8))
    
    # Price chart
    if prices_numeric:
        axes[0].plot(prices_numeric, color='blue', linewidth=2)
        axes[0].set_title('Price Movement', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
    
    # Volume chart
    if volumes_numeric:
        axes[1].bar(range(len(volumes_numeric)), volumes_numeric, color='green', alpha=0.6)
        axes[1].set_title('Trading Volume', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
    
    # RSI simulation
    if len(prices_numeric) > 14:
        delta = pd.Series(prices_numeric).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        axes[2].plot(rsi, color='purple', linewidth=2)
        axes[2].axhline(y=70, color='r', linestyle='--', alpha=0.5)
        axes[2].axhline(y=30, color='g', linestyle='--', alpha=0.5)
        axes[2].set_title('RSI Indicator', fontsize=12, fontweight='bold')
        axes[2].set_ylim(0, 100)
    
    plt.tight_layout()
    
    # Save to bytes
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
    img_bytes.seek(0)
    plt.close()
    
    return img_bytes

def generate_pdf_report(analysis_data, asset_data=None, news_list=None, output_file="professional_analysis_report.pdf"):
    """
    Creates a professional financial analysis PDF with advanced features.
    """
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Add first page
    pdf.add_page()
    
    # Professional Header with logo
    pdf.set_fill_color(41, 128, 185)  # Blue background
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 25, "QUANTUM FINANCIAL INTELLIGENCE", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)
    
    # Report Title
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 10, "AI-POWERED MARKET ANALYSIS REPORT", ln=True, align='C')
    pdf.set_font("Arial", "I", 12)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC", ln=True, align='C')
    
    pdf.ln(15)
    
    # Executive Summary Section
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "EXECUTIVE SUMMARY", ln=True, fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", size=12)
    if analysis_data.get('recommendation'):
        rec = _clean_text_for_pdf(analysis_data['recommendation'])
        risk = _clean_text_for_pdf(analysis_data.get('risk', 'N/A'))
        confidence = _clean_text_for_pdf(analysis_data.get('confidence_score', '85%'))
        
        summary_text = f"""
        Based on advanced AI analysis and quantitative modeling, this report provides a comprehensive 
        assessment of the market position. Primary recommendation: {rec}. 
        Risk assessment: {risk}. Confidence level: {confidence}.
        """
        pdf.multi_cell(0, 8, _clean_text_for_pdf(summary_text))
    
    pdf.ln(10)
    
    # Key Metrics Table
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "KEY PERFORMANCE INDICATORS", ln=True, fill=True)
    pdf.ln(5)
    
    if analysis_data.get('raw_data'):
        raw = analysis_data['raw_data']
        
        # Safely extract and format values
        symbol = _clean_text_for_pdf(raw.get('symbol', 'N/A'))
        asset_type = _clean_text_for_pdf(raw.get('asset_type', 'N/A'))
        price = _safe_format_price(raw.get('price', 0))
        high = _safe_format_price(raw.get('high', 0))
        low = _safe_format_price(raw.get('low', 0))
        
        # Safely format volume
        volume_raw = raw.get('volume', 0)
        volume_formatted = _safe_format_volume(volume_raw)
        
        sentiment = _clean_text_for_pdf(raw.get('sentiment', 'N/A'))
        volatility = _clean_text_for_pdf(analysis_data.get('volatility', 'N/A'))
        market_cap_rank = _clean_text_for_pdf(analysis_data.get('market_cap_rank', 'N/A'))
        
        metrics = [
            ("Asset", f"{symbol.upper()} ({asset_type})"),
            ("Current Price", price),
            ("24h High", high),
            ("24h Low", low),
            ("Volume", volume_formatted),
            ("Market Sentiment", sentiment),
            ("Volatility Score", str(volatility)),
            ("Market Cap Rank", str(market_cap_rank))
        ]
        
        pdf.set_font("Arial", size=11)
        col_width = 90
        row_height = 10
        
        for i, (label, value) in enumerate(metrics):
            pdf.set_fill_color(245, 245, 245 if i % 2 == 0 else 255)
            pdf.cell(col_width, row_height, f"  {_clean_text_for_pdf(label)}:", border=0, fill=True)
            pdf.set_font("Arial", "B", 11)
            pdf.cell(col_width, row_height, f"  {_clean_text_for_pdf(value)}", border=0, fill=True, ln=True)
            pdf.set_font("Arial", size=11)
    
    pdf.ln(10)
    
    # Technical Analysis Section
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "TECHNICAL ANALYSIS", ln=True, fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", size=12)
    if analysis_data.get('technical_analysis'):
        tech_analysis = _clean_text_for_pdf(analysis_data['technical_analysis'])
        pdf.multi_cell(0, 8, tech_analysis)
    else:
        pdf.multi_cell(0, 8, "Comprehensive technical analysis including moving averages, RSI, MACD, and Bollinger Bands indicates...")
    
    pdf.ln(10)
    
    # Fundamental Analysis Section
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "FUNDAMENTAL ANALYSIS", ln=True, fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", size=12)
    if analysis_data.get('fundamental_analysis'):
        fund_analysis = _clean_text_for_pdf(analysis_data['fundamental_analysis'])
        pdf.multi_cell(0, 8, fund_analysis)
    else:
        pdf.multi_cell(0, 8, "Fundamental analysis based on market capitalization, trading volume, liquidity metrics, and comparative sector analysis...")
    
    pdf.ln(10)
    
    # Risk Assessment Matrix
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "RISK ASSESSMENT MATRIX", ln=True, fill=True)
    pdf.ln(5)
    
    risk_data = analysis_data.get('risk_breakdown', {})
    if risk_data:
        pdf.set_font("Arial", size=11)
        for risk_factor, score in risk_data.items():
            try:
                # Clean risk factor name
                risk_factor_clean = _clean_text_for_pdf(risk_factor)
                
                # Extract numeric part from score
                if isinstance(score, str):
                    if '/' in score:
                        score_num = int(score.split('/')[0])
                    else:
                        # Try to extract any number
                        import re
                        numbers = re.findall(r'\d+', str(score))
                        score_num = int(numbers[0]) if numbers else 5
                else:
                    score_num = int(score)
                
                # Ensure score is between 1-10
                score_num = max(1, min(10, score_num))
                
                # Create visual risk bar
                bar_width = int(score_num * 5)
                pdf.cell(40, 8, f"{risk_factor_clean}:")
                pdf.set_fill_color(255, 100, 100)  # Red for high risk
                if score_num <= 3:
                    pdf.set_fill_color(100, 255, 100)  # Green for low risk
                elif score_num <= 6:
                    pdf.set_fill_color(255, 200, 100)  # Yellow for medium risk
                pdf.cell(bar_width, 8, "", fill=True)
                pdf.cell(10, 8, f" {score_num}/10")
                pdf.ln(8)
            except (ValueError, TypeError):
                # If we can't parse the score, just show it as text
                pdf.cell(40, 8, f"{risk_factor_clean}:")
                pdf.cell(50, 8, f" {_clean_text_for_pdf(score)}")
                pdf.ln(8)
    else:
        pdf.multi_cell(0, 8, "Market Risk: Moderate\nLiquidity Risk: Low\nVolatility Risk: High\nRegulatory Risk: Medium")
    
    pdf.ln(10)
    
    # Investment Recommendation
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INVESTMENT RECOMMENDATION", ln=True, fill=True)
    pdf.ln(5)
    
    recommendation = _clean_text_for_pdf(analysis_data.get('recommendation', 'Hold'))
    confidence = _clean_text_for_pdf(analysis_data.get('confidence_score', '85%'))
    
    # Color code based on recommendation
    if 'buy' in recommendation.lower():
        pdf.set_text_color(0, 128, 0)  # Green
    elif 'sell' in recommendation.lower():
        pdf.set_text_color(255, 0, 0)  # Red
    else:
        pdf.set_text_color(255, 165, 0)  # Orange
    
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, f"  {recommendation.upper()}  ", ln=True, align='C', border=1)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Confidence Level: {confidence}", ln=True, align='C')
    
    pdf.ln(10)
    
    # Action Plan
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "ACTION PLAN", ln=True, fill=True)
    pdf.ln(5)
    
    action_items = analysis_data.get('action_items', [
        "1. Entry Point: Wait for pullback to support level",
        "2. Position Sizing: 5-10% of portfolio",
        "3. Stop Loss: Set at 8% below entry",
        "4. Take Profit: Target 15-20% gain",
        "5. Time Horizon: 3-6 months"
    ])
    
    pdf.set_font("Arial", size=11)
    for item in action_items:
        pdf.multi_cell(0, 8, _clean_text_for_pdf(item))
    
    pdf.ln(10)
    
    # Market News & Sentiment
    if news_list:
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "MARKET NEWS & SENTIMENT ANALYSIS", ln=True, fill=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", size=11)
        for i, news in enumerate(news_list[:5]):  # Top 5 news
            title = _clean_text_for_pdf(news.get('title', 'No title'))
            source = _clean_text_for_pdf(news.get('source', 'Unknown'))
            date = _clean_text_for_pdf(news.get('date', 'N/A'))
            description = _clean_text_for_pdf(news.get('description', ''))
            
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 8, f"{i+1}. {title}")
            pdf.set_font("Arial", "I", 10)
            pdf.multi_cell(0, 7, f"   Source: {source} | Date: {date}")
            pdf.set_font("Arial", size=11)
            # Truncate description to avoid very long lines
            truncated_desc = description[:200] + "..." if len(description) > 200 else description
            pdf.multi_cell(0, 8, f"   {truncated_desc}")
            pdf.ln(5)
    
    # Disclaimer
    pdf.add_page()
    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(100, 100, 100)
    
    disclaimer = """
    DISCLAIMER: This report is generated by AI algorithms and should not be considered as financial advice. 
    Past performance is not indicative of future results. Always conduct your own research and consult with 
    a qualified financial advisor before making investment decisions. The creators of this tool are not 
    responsible for any financial losses incurred.
    
    Report ID: {report_id}
    Model Version: Quantum AI v2.1
    Data Sources: Multiple financial APIs and real-time feeds
    """.format(report_id=datetime.now().strftime("%Y%m%d%H%M%S"))
    
    pdf.multi_cell(0, 8, _clean_text_for_pdf(disclaimer))
    
    # Save PDF
    try:
        pdf.output(output_file)
        return output_file
    except Exception as e:
        # Try alternative encoding if first attempt fails
        print(f"PDF generation error: {e}")
        # Create a simplified version if the full one fails
        return _generate_simple_pdf(analysis_data, output_file)

def _generate_simple_pdf(analysis_data, output_file="simple_analysis_report.pdf"):
    """Generate a simplified PDF if the full version fails"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Simple header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Financial Analysis Report", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    
    # Basic information
    if analysis_data.get('raw_data'):
        raw = analysis_data['raw_data']
        
        # Clean all text
        symbol = _clean_text_for_pdf(raw.get('symbol', 'N/A'))
        asset_type = _clean_text_for_pdf(raw.get('asset_type', 'N/A'))
        price = _safe_format_price(raw.get('price', 0))
        recommendation = _clean_text_for_pdf(analysis_data.get('recommendation', 'Hold'))
        
        pdf.cell(0, 10, f"Asset: {symbol.upper()} ({asset_type})", ln=True)
        pdf.cell(0, 10, f"Price: {price}", ln=True)
        pdf.cell(0, 10, f"Recommendation: {recommendation}", ln=True)
        
        if analysis_data.get('risk'):
            risk = _clean_text_for_pdf(analysis_data.get('risk', 'N/A'))
            pdf.cell(0, 10, f"Risk: {risk}", ln=True)
        
        if analysis_data.get('confidence_score'):
            confidence = _clean_text_for_pdf(analysis_data.get('confidence_score', 'N/A'))
            pdf.cell(0, 10, f"Confidence: {confidence}", ln=True)
        
        pdf.ln(10)
        
        # Analysis text (truncated if too long)
        if analysis_data.get('full_analysis'):
            analysis_text = _clean_text_for_pdf(analysis_data['full_analysis'])
            # Limit to reasonable length
            if len(analysis_text) > 2000:
                analysis_text = analysis_text[:2000] + "... [truncated]"
            pdf.multi_cell(0, 8, analysis_text)
    
    # Footer
    pdf.ln(20)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    
    try:
        pdf.output(output_file)
        return output_file
    except Exception as e:
        print(f"Even simple PDF failed: {e}")
        # Create a minimal text file as last resort
        with open(output_file.replace('.pdf', '.txt'), 'w') as f:
            f.write(f"Analysis Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if analysis_data.get('raw_data'):
                raw = analysis_data['raw_data']
                f.write(f"Symbol: {raw.get('symbol', 'N/A')}\n")
                f.write(f"Price: ${raw.get('price', 0)}\n")
        return output_file.replace('.pdf', '.txt')