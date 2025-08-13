import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.BANK_LLM import run_analysis,load_llm
from plotly.subplots import make_subplots
from app.GENPDF import generate_docx
import tempfile
import os
from datetime import datetime
from app.DPROCESS import (
    process_csv_file,
    analyze_bank_transactions,
    format_analysis_for_prompt,
    count_tokens
)

# ========== Streamlit App Configuration ========== #
st.set_page_config(
    page_title="Bank Statement Dashboard",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with modern glassmorphism and animations

file_path = os.path.join(os.path.dirname(__file__), "app", "style.css")
with open(file_path) as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ========== Enhanced Sidebar ========== #
with st.sidebar:
    st.markdown('<div class="animate-fadeInUp">', unsafe_allow_html=True)
    st.title("🏦 Bank Analyzer")
    st.markdown("**Transform your financial data into insights**")
    st.markdown("---")
    
    # Enhanced File uploader
    uploaded_file = st.file_uploader(
        "📁 Upload your bank statement CSV", 
        type=["csv"],
        help="Drag and drop your CSV file here or click to browse"
    )
    
    st.markdown("---")
    
    # Analysis Options with better styling
    st.markdown("### ⚙️ Analysis Options")
    
    col1, col2 = st.columns(2)
    with col1:
        show_raw_data = st.checkbox("📊 Raw Data", value=True)
        show_llm_prompt = st.checkbox("🤖 LLM Prompt", value=True)
    with col2:
        show_token_count = st.checkbox("🔢 Token Count", value=True)
        show_animations = st.checkbox("✨ Animations", value=True)
    
    st.markdown("---")
    
    # Enhanced About section
    st.markdown("### 💡 About")
    st.markdown("""
    **Features:**
    - 📈 Interactive visualizations
    - 🔍 Smart transaction analysis
    - 🤖 AI-ready prompt generation
    - 📊 Real-time filtering
    - 🎨 Modern glass UI
    """)
    
    st.markdown("---")
    st.markdown("*Built with ❤️ by- RISHABH😎*")
    st.markdown('</div>', unsafe_allow_html=True)

# ========== Enhanced Main Content ========== #
st.markdown('<div class="animate-fadeInUp">', unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="glass-card">
    <h1 style="text-align: center; margin-bottom: 0;">🏦 Bank Statement Analyzer</h1>
    <p style="text-align: center; color: rgba(255,255,255,0.8); font-size: 1.2rem; margin-top: 0;">
        Unlock the power of your financial data with AI-driven insights
    </p>
</div>
""", unsafe_allow_html=True)

if not uploaded_file:
    # Enhanced empty state
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 48px;">
        <h2>🚀 Get Started</h2>
        <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem;">
            Upload your bank statement CSV file to begin your financial journey
        </p>
        <div style="margin: 32px 0;">
            <div style="font-size: 4rem; margin-bottom: 16px;">📈</div>
            <p style="color: rgba(255,255,255,0.6);">
                Visualize • Analyze • Understand
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 16px;">📊</div>
            <h3>Smart Analytics</h3>
            <p style="color: rgba(255,255,255,0.7);">Advanced transaction analysis with AI insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 16px;">📈</div>
            <h3>Visual Insights</h3>
            <p style="color: rgba(255,255,255,0.7);">Interactive charts and trend analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 16px;">🤖</div>
            <h3>AI Ready</h3>
            <p style="color: rgba(255,255,255,0.7);">Generate prompts for AI analysis</p>
        </div>
        """, unsafe_allow_html=True)

else:
    try:
        # Enhanced file processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name

        # Processing with enhanced feedback
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("🔄 Processing your file..."):
            status_text.text("Reading CSV file...")
            progress_bar.progress(25)
            df = process_csv_file(temp_path)
            os.remove(temp_path)
            
            status_text.text("Analyzing transactions...")
            progress_bar.progress(75)
            analysis = analyze_bank_transactions(df)
            progress_bar.progress(100)
            
        status_text.empty()
        progress_bar.empty()
        
        st.success("✅ Analysis complete! Your financial insights are ready.")

        # Enhanced Dashboard Layout with better tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends", "🔍 Explorer", "🤖 AI Analysis"])

        with tab1:
            st.markdown('<div class="animate-fadeInUp">', unsafe_allow_html=True)
            
            # Enhanced Summary Metrics
            st.markdown("""
            <div class="glass-card">
                <h2>💰 Financial Summary</h2>
                <p style="color: rgba(255,255,255,0.7);">Your transaction overview at a glance</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Three rows of metrics for better layout
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("📊 Total Transactions", f"{analysis['total_transactions']:,}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("📉 Debits", f"{analysis['debit_transactions']:,}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("📈 Credits", f"{analysis['credit_transactions']:,}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                avg_debit = analysis['amounts']['avg_debit']
                st.metric("💸 Avg Debit", f"₹{avg_debit:,.2f}")
                st.markdown('</div>', unsafe_allow_html=True)

            # Second row - amounts
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                total_debit = analysis['amounts']['total_debit']
                st.metric("💰 Total Debited", f"₹{total_debit:,.2f}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                total_credit = analysis['amounts']['total_credit']
                st.metric("💵 Total Credited", f"₹{total_credit:,.2f}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                if 'opening_balance' in analysis:
                    net_change = analysis['net_savings']
                    delta_color = "normal" if net_change >= 0 else "inverse"
                    st.metric("📊 Net Change", f"₹{net_change:,.2f}", delta=f"₹{net_change:,.2f}", delta_color=delta_color)
                st.markdown('</div>', unsafe_allow_html=True)

            # Balance Information with enhanced design
            if 'opening_balance' in analysis:
                st.markdown("""
                <div class="glass-card">
                    <h3>🏦 Account Balance Journey</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Create a balance visualization
                balance_fig = go.Figure()
                balance_fig.add_trace(go.Scatter(
                    x=['Opening Balance', 'Closing Balance'],
                    y=[analysis['opening_balance'], analysis['closing_balance']],
                    mode='lines+markers',
                    line=dict(color='#4facfe', width=4),
                    marker=dict(size=12, color=['#667eea', '#4facfe']),
                    fill='tonexty'
                ))
                
                balance_fig.update_layout(
                    title="Balance Trend",
                    xaxis_title="",
                    yaxis_title="Amount (₹)",
                    template="plotly_dark",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=300
                )
                
                st.plotly_chart(balance_fig, use_container_width=True)

            # Enhanced sample data
            if show_raw_data:
                st.markdown("""
                <div class="glass-card">
                    <h3>📋 Recent Transactions</h3>
                    <p style="color: rgba(255,255,255,0.7);">Latest 10 transactions from your statement</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Style the dataframe
                styled_df = df.head(10).style.format({
                    'dr': '₹{:,.2f}',
                    'cr': '₹{:,.2f}',
                    'balance': '₹{:,.2f}'
                })
                
                st.dataframe(styled_df, use_container_width=True, height=400)
            
            st.markdown('</div>', unsafe_allow_html=True)

        
        with tab2:
                st.markdown('<div class="animate-fadeInUp">', unsafe_allow_html=True)

                # 🌄 Daily Trends
                st.markdown("""
                <div class="glass-card">
                    <h2>📈 Transaction Trends</h2>
                    <p style="color: rgba(255,255,255,0.7);">Visualize your spending and earning patterns</p>
                </div>
                """, unsafe_allow_html=True)

                daily_df = pd.DataFrame(analysis.get("raw_data", {}).get("daily", []))
                monthly_df = pd.DataFrame(analysis.get("raw_data", {}).get("monthly", []))

                if not daily_df.empty and "date" in daily_df.columns:
                    daily_df["date"] = pd.to_datetime(daily_df["date"], errors="coerce")
                    daily_df = daily_df.sort_values("date")

                    fig = make_subplots(
                        rows=2, cols=1,
                        subplot_titles=("Daily Transactions Overview", "Debit vs Credit Comparison"),
                        vertical_spacing=0.1
                    )

                    # Daily Bar Chart
                    fig.add_trace(go.Bar(
                        x=daily_df['date'],
                        y=daily_df['dr'],
                        name='Debits',
                        marker_color='#ff6b6b',
                        opacity=0.8
                    ), row=1, col=1)

                    fig.add_trace(go.Bar(
                        x=daily_df['date'],
                        y=daily_df['cr'],
                        name='Credits',
                        marker_color='#4ecdc4',
                        opacity=0.8
                    ), row=1, col=1)

                    # Debit vs Credit Trends
                    fig.add_trace(go.Scatter(
                        x=daily_df['date'],
                        y=daily_df['dr'],
                        mode='lines+markers',
                        name='Debit Trend',
                        line=dict(color='#ff6b6b', width=3),
                        marker=dict(size=8)
                    ), row=2, col=1)

                    fig.add_trace(go.Scatter(
                        x=daily_df['date'],
                        y=daily_df['cr'],
                        mode='lines+markers',
                        name='Credit Trend',
                        line=dict(color='#4ecdc4', width=3),
                        marker=dict(size=8)
                    ), row=2, col=1)

                    fig.update_layout(
                        height=800,
                        template="plotly_dark",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        showlegend=True
                    )

                    st.plotly_chart(fig, use_container_width=True)

                # 📅 Monthly Trends
                if not monthly_df.empty and "date" in monthly_df.columns:
                    st.markdown("""
                    <div class="glass-card">
                        <h3>📅 Monthly Financial Flow</h3>
                    </div>
                    """, unsafe_allow_html=True)

                    monthly_df["date"] = pd.to_datetime(monthly_df["date"], errors="coerce")
                    monthly_df["month"] = monthly_df["date"].dt.to_period("M").dt.to_timestamp()
                    monthly_grouped = monthly_df.groupby("month").agg({"cr": "sum", "dr": "sum"}).reset_index()

                    fig_monthly = go.Figure()

                    fig_monthly.add_trace(go.Scatter(
                        x=monthly_grouped['month'],
                        y=monthly_grouped['cr'],
                        fill='tozeroy',
                        mode='lines+markers',
                        name='Credits',
                        line=dict(color='#4ecdc4', width=3),
                        marker=dict(size=10)
                    ))

                    fig_monthly.add_trace(go.Scatter(
                        x=monthly_grouped['month'],
                        y=monthly_grouped['dr'],
                        fill='tozeroy',
                        mode='lines+markers',
                        name='Debits',
                        line=dict(color='#ff6b6b', width=3),
                        marker=dict(size=10)
                    ))

                    fig_monthly.update_layout(
                        title="Monthly Transaction Flow",
                        xaxis_title="Month",
                        yaxis_title="Amount (₹)",
                        template="plotly_dark",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        height=500
                    )

                    st.plotly_chart(fig_monthly, use_container_width=True)

                # 🛍️ Merchant Insights
                if "merchant_analysis" in analysis and analysis["merchant_analysis"]:
                    st.markdown("""
                    <div class="glass-card">
                        <h3>🛍️ Merchant Insights</h3>
                        <p style="color: rgba(255,255,255,0.7);">Your most frequent transaction partners</p>
                    </div>
                    """, unsafe_allow_html=True)

                    merchant_data = [(k, v) for k, v in analysis["merchant_analysis"].items() if isinstance(v, (int, float))]
                    merchant_df = pd.DataFrame(merchant_data, columns=["Merchant", "Mentions"]).sort_values("Mentions", ascending=False)

                    if not merchant_df.empty:
                        fig_merchant = go.Figure(go.Bar(
                            x=merchant_df["Mentions"],
                            y=merchant_df["Merchant"],
                            orientation='h',
                            marker=dict(
                                color=merchant_df["Mentions"],
                                colorscale='Viridis',
                                colorbar=dict(title="Frequency")
                            )
                        ))

                        fig_merchant.update_layout(
                            title="Most Frequent Merchants",
                            xaxis_title="Number of Mentions",
                            yaxis_title="",
                            template="plotly_dark",
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white'),
                            height=max(400, len(merchant_df) * 30)
                        )

                        st.plotly_chart(fig_merchant, use_container_width=True)

                st.markdown('</div>', unsafe_allow_html=True)



        with tab3:
            st.markdown('<div class="animate-fadeInUp">', unsafe_allow_html=True)
            
            # Enhanced Transaction Explorer
            st.markdown("""
            <div class="glass-card">
                <h2>🔍 Transaction Explorer</h2>
                <p style="color: rgba(255,255,255,0.7);">Search and filter your transactions with precision</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced search and filter section
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                search_term = st.text_input("🔍 Search transactions", placeholder="Enter keywords, merchant names, or descriptions...")
            
            with col2:
                min_amount = st.number_input("💰 Min amount (₹)", min_value=0, value=0, step=100)
            
            with col3:
                max_amount = st.number_input("💰 Max amount (₹)", min_value=0, value=int(df[['dr', 'cr']].max().max()) if not df.empty else 1000000, step=100)
            
            # Additional filters
            col1, col2 = st.columns(2)
            
            with col1:
                transaction_type = st.selectbox("📊 Transaction Type", ["All", "Debits Only", "Credits Only"])
            
            with col2:
                date_range = st.date_input("📅 Date Range", value=[], help="Select start and end dates")
            
            # Apply filters
            filtered_df = df.copy()
            
            if search_term:
                filtered_df = filtered_df[filtered_df['desc'].str.contains(search_term, case=False, na=False)]
            
            if transaction_type == "Debits Only":
                filtered_df = filtered_df[filtered_df['dr'] > 0]
            elif transaction_type == "Credits Only":
                filtered_df = filtered_df[filtered_df['cr'] > 0]
            
            # Amount filtering
            if min_amount > 0:
                filtered_df = filtered_df[(filtered_df['dr'] >= min_amount) | (filtered_df['cr'] >= min_amount)]
            
            if max_amount > 0:
                filtered_df = filtered_df[(filtered_df['dr'] <= max_amount) | (filtered_df['cr'] <= max_amount)]
            
            # Date filtering
            if len(date_range) == 2:
                filtered_df['date'] = pd.to_datetime(filtered_df['date'], errors='coerce')
                filtered_df = filtered_df[(filtered_df['date'] >= pd.to_datetime(date_range[0])) & 
                                        (filtered_df['date'] <= pd.to_datetime(date_range[1]))]
            
            # Display filtered results
            st.markdown(f"""
            <div class="glass-card">
                <h3>📋 Filtered Results</h3>
                <p style="color: rgba(255,255,255,0.7);">
                    Showing {len(filtered_df):,} transactions out of {len(df):,} total
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if not filtered_df.empty:
                # Enhanced dataframe display
                display_df = filtered_df.sort_values('date', ascending=False)
                
                # Add some styling to highlight large transactions
                def highlight_large_transactions(row):
                    if row['dr'] > filtered_df['dr'].quantile(0.9) or row['cr'] > filtered_df['cr'].quantile(0.9):
                        return ['background-color: rgba(255, 107, 107, 0.2)'] * len(row)
                    return [''] * len(row)
                
                styled_df = display_df.style.apply(highlight_large_transactions, axis=1)
                
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    height=600
                )
                
                # Quick stats for filtered data
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("📊 Filtered Count", f"{len(filtered_df):,}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    filtered_debits = filtered_df['dr'].sum()
                    st.metric("💸 Total Debits", f"₹{filtered_debits:,.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    filtered_credits = filtered_df['cr'].sum()
                    st.metric("💰 Total Credits", f"₹{filtered_credits:,.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    net_filtered = filtered_credits - filtered_debits
                    st.metric("📈 Net Amount", f"₹{net_filtered:,.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("🔍 No transactions match your filter criteria. Try adjusting your search parameters.")
            
            st.markdown('</div>', unsafe_allow_html=True)

            with tab4:
                st.markdown('<div class="animate-fadeInUp">', unsafe_allow_html=True)

                # Sample Queries
                st.markdown("""
                <div class="glass-card">
                    <h3>💡 Sample AI Queries</h3>
                    <p style="color: rgba(255,255,255,0.7); margin-bottom: 16px;">
                        Try these prompts with your financial data:
                    </p>
                </div>
                """, unsafe_allow_html=True)

                sample_queries = [
                    "Analyze my spending patterns and identify areas where I can save money",
                    "Create a budget plan based on my transaction history",
                    "Identify any unusual or suspicious transactions",
                    "Predict my future expenses based on current trends",
                    "Suggest investment opportunities based on my cash flow",
                    "Help me set realistic financial goals"
                ]

                cols = st.columns(2)
                for i, query in enumerate(sample_queries):
                    with cols[i % 2]:
                        if st.button(f"💡 {query}", key=f"query_{i}",
                                    use_container_width=True,
                                    help=f"Click to analyze: {query}"):
                            st.session_state.llm_question = query
                            st.session_state.llm_style = "default"
                            st.rerun()

                st.markdown("""
                <div class="glass-card">
                    <h2>🤖 AI Analysis Hub</h2>
                    <p style="color: rgba(255,255,255,0.7);">
                        Chat with your financial data and generate smart insights
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Analysis style selector
                style_label = {
                    "default": "🗣️ Ask a question",
                    "summary": "📋 Summary",
                    "fraud_check": "🚨 Fraud Check",
                    "income_vs_expense": "📊 Income vs Expense",
                    "budget_advice": "💡 Budget Advice"
                }

                if 'llm_style' not in st.session_state:
                    st.session_state.llm_style = "summary"

                style = st.selectbox("Choose AI analysis type", 
                                    options=list(style_label.keys()),
                                    format_func=lambda x: style_label[x],
                                    index=list(style_label.keys()).index(st.session_state.llm_style))

                # Chat-like input
                if 'llm_question' not in st.session_state:
                    st.session_state.llm_question = ""

                question = st.text_input("❓ Enter your question", 
                                        value=st.session_state.llm_question,
                                        placeholder="e.g., What are my top spending categories?",
                                        key="question_input")

                # Run Analysis
                if st.button("🚀 Run AI Analysis"):
                    with st.spinner("🧠 Thinking..."):
                        llm = load_llm()
                        prompt_text = format_analysis_for_prompt(analysis, df)
                        result = run_analysis(llm, prompt_text, question, style)

                    st.session_state.llm_result = result
                    st.session_state.llm_prompt_text = prompt_text

                # Show Result
                if 'llm_result' in st.session_state:
                    st.markdown("""
                    <div class="glass-card">
                        <h3>📨 AI Response</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    st.success(st.session_state.llm_result)

                    # Prompt & Token Stats
                    with st.expander("📦 View Generated Prompt & Token Info"):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.text_area("📜 Prompt Text", 
                                        value=st.session_state.llm_prompt_text, 
                                        height=400,
                                        label_visibility="collapsed")
                        with col2:
                            st.markdown('<div class="metric-card" style="text-align: center; padding: 30px;">', unsafe_allow_html=True)
                            if show_token_count:
                                tokens, chars = count_tokens(st.session_state.llm_prompt_text)
                                st.metric("🔢 Tokens", f"{tokens:,}")
                                st.metric("📝 Characters", f"{chars:,}")
                                st.progress(min(tokens / 4096, 1.0))
                                st.caption(f"Context usage: {tokens / 4096:.1%}")
                            st.markdown('</div>', unsafe_allow_html=True)


                    # 📥 DOCX Download
                    doc_buffer = generate_docx(question, st.session_state.llm_result)
                    st.download_button("📥 Download DOCX", data=doc_buffer,
                                    file_name="financial_ai_report.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

                    st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"""
        ❌ **Error Processing File**
        
        {str(e)}
        
        **Troubleshooting Tips:**
        - Ensure your CSV file has the correct format
        - Check that date columns are properly formatted
        - Verify that amount columns contain numeric values
        - Make sure the file isn't corrupted
        """)
        
        # Enhanced error display
        with st.expander("🔧 Technical Details"):
            st.code(str(e), language="python")

# Enhanced footer
st.markdown("""
<div style="margin-top: 48px; text-align: center; color: rgba(255,255,255,0.5);">
    <hr style="border: 1px solid rgba(255,255,255,0.1); margin: 32px 0;">
    <p>
        Built with ❤️ using Streamlit • Enhanced UI with Glassmorphism Design
    </p>
    <p style="font-size: 0.8rem;">
        Your data is processed locally and never stored on our servers
    </p>
</div>
""", unsafe_allow_html=True)

# Floating stats (if data is loaded)
if uploaded_file and 'analysis' in locals():
  st.markdown("""
<style>
#emoji-buddy {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 100px;
    height: 100px;
    background-color: #fffad1;
    border-radius: 50%;
    font-size: 60px;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    cursor: pointer;
    z-index: 9999;
    transition: transform 0.2s ease-in-out;
}

/* Jump animation */
@keyframes jump {
    0%   { transform: translateY(0); }
    30%  { transform: translateY(-30px); }
    60%  { transform: translateY(0); }
    80%  { transform: translateY(-10px); }
    100% { transform: translateY(0); }
}
</style>

<div id="emoji-buddy">😃</div>

<script>
const emojis = ["😃", "🥲", "😘", "🤔", "😴", "🤩"];
let index = 0;

function jumpAndChange() {
    const buddy = document.getElementById("emoji-buddy");

    // Add jump animation
    buddy.style.animation = "jump 0.8s ease";

    // Change emoji
    index = (index + 1) % emojis.length;
    buddy.innerText = emojis[index];

    // Reset animation after jump
    setTimeout(() => {
        buddy.style.animation = "";
    }, 800);
}

// Loop every 5 seconds
setInterval(jumpAndChange, 5000);
</script>
""", unsafe_allow_html=True)
