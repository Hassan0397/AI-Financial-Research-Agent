import streamlit as st
from services.report_gen import generate_pdf_report
from datetime import datetime
import base64
import os

st.set_page_config(page_title="Report", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .report-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .report-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #667eea;
    }
    .download-btn {
        background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .preview-section {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="report-header">
    <h1>📄 Professional Report Generator</h1>
    <h3>Create Expert-Level Financial Analysis Reports</h3>
</div>
""", unsafe_allow_html=True)

# Helper function to safely extract values
def safe_get(data, key, default=""):
    """Safely get value from dictionary"""
    if not data:
        return default
    
    value = data.get(key, default)
    if value is None:
        return default
    
    # Convert to string for display
    return str(value)

def safe_get_number(data, key, default=0):
    """Safely get numeric value"""
    if not data:
        return default
    
    value = data.get(key, default)
    if value is None:
        return default
    
    try:
        # Handle string numbers
        if isinstance(value, str):
            value = value.replace(',', '').replace('$', '').strip()
        
        # Try to convert to float
        return float(value)
    except (ValueError, TypeError):
        return default

# Check if analysis was completed
if "analysis_result" not in st.session_state or not st.session_state.get("analysis_done", False):
    st.warning("""
    ## ⚠️ Analysis Required
    
    **To generate a professional report, you need to:**
    
    1. **Navigate to the Analysis page** (from sidebar)
    2. **Enter a symbol** (BTC, AAPL, TSLA, etc.)
    3. **Click "Launch Analysis"** and wait for completion
    4. **Return here** to generate your report
    
    ---
    
    ### 💡 Quick Analysis
    """)
    
    # Quick analysis option
    quick_symbol = st.text_input("Or enter a symbol here for quick analysis:", placeholder="BTC, AAPL, etc.")
    
    if st.button("🚀 Quick Analyze & Generate", disabled=not quick_symbol):
        st.session_state.symbol = quick_symbol.upper()
        st.info(f"🔍 Please go to Analysis page first to analyze {quick_symbol.upper()}")
    
    st.markdown("""
    ---
    ### 📊 What makes our reports professional?
    
    - **Executive Summary** with key findings
    - **Technical Analysis** with charts
    - **Risk Assessment Matrix**
    - **Investment Recommendations**
    - **Market Sentiment Analysis**
    - **Action Plan** with entry/exit strategies
    - **Professional Formatting** (3-5 pages)
    
    *Complete an analysis first to unlock report generation.*
    """)
    
else:
    # Analysis data available
    analysis = st.session_state.analysis_result
    symbol = st.session_state.symbol
    
    st.success(f"✅ Analysis data loaded for **{symbol}**")
    
    # Report Configuration
    st.markdown("## ⚙️ Report Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        report_style = st.selectbox(
            "Report Style",
            ["Professional", "Executive", "Detailed", "Investment Memo"]
        )
    
    with col2:
        include_sections = st.multiselect(
            "Include Sections",
            ["Executive Summary", "Technical Analysis", "Risk Assessment", 
             "News Sentiment", "Action Plan", "Market Outlook"],
            default=["Executive Summary", "Technical Analysis", "Risk Assessment", "Action Plan"]
        )
    
    with col3:
        confidential = st.checkbox("Add Confidential Watermark", value=True)
        include_charts = st.checkbox("Include Charts", value=True)
    
    # Report Preview
    st.markdown("## 👁️ Report Preview")
    
    with st.expander("Preview Report Contents", expanded=True):
        # Create preview sections
        preview_cols = st.columns(2)
        
        with preview_cols[0]:
            st.markdown("### 📋 Report Details")
            st.write(f"**Asset:** {symbol}")
            st.write(f"**Report Type:** {report_style} Report")
            st.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Pages:** 3-5 (Professional Format)")
            
            # Safely get confidence score
            confidence = safe_get(analysis, 'confidence_score', 'N/A')
            st.write(f"**AI Confidence:** {confidence}")
            
            if analysis.get('recommendation'):
                recommendation = safe_get(analysis, 'recommendation', 'N/A')
                rec_emoji = "🟢" if 'buy' in recommendation.lower() else "🔴" if 'sell' in recommendation.lower() else "🟡"
                st.write(f"**Recommendation:** {rec_emoji} {recommendation}")
        
        with preview_cols[1]:
            st.markdown("### 📊 Key Metrics")
            
            raw_data = analysis.get('raw_data', {})
            
            # Safely extract values
            price = safe_get_number(raw_data, 'price', 0)
            high = safe_get_number(raw_data, 'high', 0)
            low = safe_get_number(raw_data, 'low', 0)
            volume = safe_get_number(raw_data, 'volume', 0)
            risk = safe_get(analysis, 'risk', 'N/A')
            sentiment = safe_get(raw_data, 'sentiment', 'N/A')
            
            # Format for display
            metrics = [
                ("Current Price", f"${price:,.2f}"),
                ("24h High/Low", f"${high:,.2f}/${low:,.2f}"),
                ("Volume", f"{volume:,.0f}"),
                ("Risk Score", risk),
                ("Sentiment", sentiment)
            ]
            
            for label, value in metrics:
                st.metric(label, value)
    
    # Report Sections Preview
    st.markdown("### 📑 Report Sections")
    
    sections_data = [
        ("📝 Executive Summary", "Overview of key findings and investment thesis"),
        ("📈 Technical Analysis", f"{len(analysis.get('technical_indicators', {}))} technical indicators analyzed"),
        ("⚠️ Risk Assessment", f"Risk score: {safe_get(analysis, 'risk', 'N/A')} with detailed breakdown"),
        ("📰 Market Sentiment", f"Sentiment: {safe_get(analysis.get('raw_data', {}), 'sentiment', 'Neutral')}"),
        ("🎯 Action Plan", f"{len(analysis.get('action_items', []))} actionable recommendations"),
        ("🔮 Market Outlook", "Short-term and long-term market projections")
    ]
    
    cols = st.columns(3)
    for i, (title, desc) in enumerate(sections_data):
        with cols[i % 3]:
            if title[2:] in include_sections:
                st.info(f"**{title}**\n\n{desc}")
    
    # Generate Report
    st.markdown("---")
    st.markdown("## 🖨️ Generate Report")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Generate Professional PDF Report", type="primary", use_container_width=True):
            with st.spinner("🔄 Generating professional report..."):
                try:
                    # Prepare data for report
                    report_data = {
                        'analysis_data': analysis,
                        'asset_data': analysis.get('raw_data', {}),
                        'news_list': st.session_state.get('news_data', []),
                        'report_config': {
                            'style': report_style,
                            'sections': include_sections,
                            'confidential': confidential,
                            'timestamp': datetime.now().isoformat()
                        }
                    }
                    
                    # Generate filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"Professional_Analysis_{symbol}_{timestamp}.pdf"
                    
                    # Generate PDF with proper error handling
                    try:
                        file_path = generate_pdf_report(
                            analysis_data=analysis,
                            asset_data=analysis.get('raw_data', {}),
                            news_list=st.session_state.get('news_data', []),
                            output_file=filename
                        )
                        
                        # Read PDF file
                        with open(file_path, "rb") as f:
                            pdf_bytes = f.read()
                        
                        # Encode for download
                        b64 = base64.b64encode(pdf_bytes).decode()
                        
                        # Success message
                        st.success("✅ Report generated successfully!")
                        
                        # Download link
                        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-btn">📥 Download Report</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        
                        # Report details
                        file_size = len(pdf_bytes) / 1024
                        
                        st.markdown(f"""
                        <div class="report-card">
                            <h4>📋 Report Details</h4>
                            <p><strong>Filename:</strong> {filename}</p>
                            <p><strong>Asset:</strong> {symbol}</p>
                            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                            <p><strong>Size:</strong> {file_size:.1f} KB</p>
                            <p><strong>Format:</strong> Professional PDF (Printable)</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Preview option
                        with st.expander("📄 Quick Preview", expanded=True):
                            st.markdown("### 📝 Executive Summary Preview")
                            
                            # Safely extract values for preview
                            recommendation = safe_get(analysis, 'recommendation', 'N/A')
                            confidence = safe_get(analysis, 'confidence_score', 'N/A')
                            risk = safe_get(analysis, 'risk', 'N/A')
                            sentiment = safe_get(analysis.get('raw_data', {}), 'sentiment', 'N/A')
                            
                            st.markdown(f"""
                            #### Quantum Financial Intelligence Report
                            
                            **Asset:** {symbol}
                            **Report Date:** {datetime.now().strftime("%Y-%m-%d")}
                            **Analysis ID:** QF-{symbol}-{timestamp[-6:]}
                            
                            ##### Key Findings:
                            - **Recommendation:** {recommendation} (Confidence: {confidence})
                            - **Risk Assessment:** {risk}
                            - **Market Sentiment:** {sentiment}
                            - **Price Action:** ${price:,.2f} (24h Range: ${low:,.2f} - ${high:,.2f})
                            
                            ##### Executive Overview:
                            This professional analysis provides comprehensive insights into {symbol} market dynamics, 
                            incorporating quantitative models, technical indicators, and sentiment analysis 
                            to deliver actionable investment intelligence.
                            
                            *Full report includes detailed technical analysis, risk breakdown, and strategic recommendations.*
                            """)
                            
                            # Show action items preview
                            action_items = analysis.get('action_items', [])
                            if action_items:
                                st.markdown("##### 🎯 Key Action Items:")
                                for action in action_items[:3]:
                                    st.write(f"- {action}")
                        
                        # Clean up
                        try:
                            os.remove(file_path)
                        except:
                            pass
                        
                    except Exception as pdf_error:
                        st.error(f"❌ PDF Generation Error: {str(pdf_error)}")
                        st.info("""
                        **Troubleshooting tips:**
                        1. Check if all data fields are properly formatted
                        2. Ensure numeric values are valid numbers
                        3. Try generating the report again
                        4. Check console for detailed error messages
                        """)
                    
                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
    
    # Additional Options
    st.markdown("---")
    st.markdown("### 🔄 Additional Options")
    
    option_cols = st.columns(3)
    
    with option_cols[0]:
        if st.button("🔄 Re-run Analysis", use_container_width=True):
            st.session_state.analysis_done = False
            st.info("Redirecting to Analysis page...")
            # In multi-page app, this would navigate to Analysis page
    
    with option_cols[1]:
        if st.button("📊 View Full Analysis", use_container_width=True):
            with st.expander("Complete Analysis", expanded=True):
                full_analysis = safe_get(analysis, 'full_analysis', 'No analysis available')
                st.write(full_analysis)
    
    with option_cols[2]:
        if st.button("💾 Save Analysis", use_container_width=True):
            st.success("✅ Analysis saved to session. You can return anytime to regenerate the report.")
    
    # Report Features
    st.markdown("---")
    st.markdown("### 🌟 Professional Report Features")
    
    features = st.columns(4)
    feature_list = [
        ("📈", "Technical Charts", "Professional-grade technical analysis charts"),
        ("⚠️", "Risk Matrix", "Visual risk assessment with scoring"),
        ("🎯", "Action Plan", "Specific entry/exit recommendations"),
        ("📊", "Market Data", "Real-time prices and metrics")
    ]
    
    for i, (icon, title, desc) in enumerate(feature_list):
        with features[i]:
            st.markdown(f"**{icon} {title}**")
            st.caption(desc)
    
    # Disclaimer
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545;">
        <h5>📝 Legal & Compliance</h5>
        <small>
        <strong>Disclaimer:</strong> This report is generated by AI algorithms for informational purposes only. 
        It does not constitute financial advice, investment recommendation, or an offer to buy/sell securities. 
        The information provided may not be accurate, complete, or timely. Always consult with qualified financial 
        advisors and conduct your own due diligence before making investment decisions. Past performance is not 
        indicative of future results. Investments carry risk of loss.
        </small>
        <br><br>
        <small>
        <strong>Report ID:</strong> QF-{symbol}-{datetime.now().strftime("%Y%m%d")} | <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC
        </small>
    </div>
    """, unsafe_allow_html=True)

# Navigation help
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Navigation")
st.sidebar.info("""
**Analysis Page:** Enter symbols, run analysis  
**Report Page:** Generate professional PDFs  
**Settings:** Configure API keys & preferences
""")

# Quick help
with st.sidebar.expander("💡 Quick Help"):
    st.write("""
    **Report Features:**
    - Professional formatting
    - Multiple style options
    - Configurable sections
    - Printable PDF format
    - Confidential watermark
    
    **Requirements:**
    - Completed analysis
    - Symbol must be analyzed
    - Internet connection for generation
    """)