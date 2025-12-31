import streamlit as st
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools
from phi.tools.duckduckgo import DuckDuckGo
import yfinance as yf
from fpdf import FPDF
import os
from dotenv import load_dotenv

# --- 1. Environment Setup ---
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="AI Financial Analyst", page_icon="📈", layout="wide")

# --- 2. PDF Generation Function (Fixed for Deprecation Warnings) ---
# --- 2. PDF Generation Function (FIXED) ---
def create_pdf(report_text, ticker):
    pdf = FPDF()
    pdf.add_page()
    
    # Font setup
    pdf.set_font("Helvetica", size=12)
    
    # Title
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(w=0, h=10, text=f"Financial Report: {ticker}", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    
    # Body
    pdf.set_font("Helvetica", size=12)
    
    # Encoding fix for symbols
    clean_text = report_text.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(w=0, h=10, text=clean_text)
    
    # --- MAIN FIX HERE ---
    # pdf.output() returns 'bytearray', we convert it to 'bytes'
    return bytes(pdf.output())

# --- 3. UI Setup ---
st.title("📈 AI Stock Analyst Agent")
st.markdown("### Professional Financial Analysis Dashboard")

if not groq_api_key:
    st.error("⚠️ Error: GROQ_API_KEY nahi mili! Please check your .env file.")
    st.stop()

# Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Search Parameters")
    ticker = st.text_input("Stock Ticker", value="NVDA", help="Example: AAPL, TSLA, RELIANCE.NS")
    analyze_btn = st.button("view analysis", type="primary")

# --- 4. Agent Setup ---
# --- 4. Agent Setup (FIXED FOR CLOUD) ---
agent = Agent(
    name="Stock Analyst",
    model=Groq(id="llama-3.1-70b-versatile", api_key=groq_api_key),
    tools=[
        DuckDuckGo(), 
        YFinanceTools(stock_price=True, analyst_recommendations=True, stock_fundamentals=True)
    ],
    instructions=[
        "You are a Senior Financial Analyst.",
        "Your goal is to generate a comprehensive stock report.",
        "1. First, search for the latest news and sentiment.",
        "2. Then, get stock fundamentals and price data.",
        "3. Finally, combine everything into a structured report.",
        "Important: Use tables for data.",
        "Important: Give a clear Buy/Sell/Hold recommendation.",
        # --- CRITICAL FIXES FOR TOOL CALLING ERROR ---
        "CRITICAL: Do not use XML tags like <function>. Use standard JSON for tool calls.",
        "CRITICAL: If you need to call a tool, just output the JSON. Do not write text before the tool call."
    ],
    show_tool_calls=True,
    markdown=True,
)

if analyze_btn:
    # --- Feature 1: Stock Chart (Fixed yfinance method) ---
    with col2:
        st.subheader(f"{ticker} - Market Performance")
        try:
            # FIX: Using Ticker object instead of download() for better stability
            stock_obj = yf.Ticker(ticker)
            stock_data = stock_obj.history(period="1y")
            
            if not stock_data.empty:
                st.line_chart(stock_data['Close'])
            else:
                st.warning(f"No chart data found for {ticker}. Check the ticker symbol.")
        except Exception as e:
            st.warning(f"Could not load chart: {e}")

    # --- Feature 2: AI Analysis ---
    st.divider()
    st.subheader("📑 Investment Memorandum")
    
    with st.spinner(f"Analyzing {ticker} across the web & market data..."):
        try:
            # Running the agent
            response = agent.run(f"Analyze {ticker} stock and provide a detailed investment recommendation.")
            report_text = response.content
            
            # Display Report on Screen
            st.markdown(report_text)
            
            # --- Feature 3: PDF Download ---
            pdf_bytes = create_pdf(report_text, ticker)
            
            st.download_button(
                label="📥 Download Report as PDF",
                data=pdf_bytes,
                file_name=f"{ticker}_Financial_Report.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"Analysis Failed: {e}")