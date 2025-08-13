import os
import pandas as pd
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from app.DPROCESS import process_csv_file,analyze_bank_transactions,format_analysis_for_prompt

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Step 2: Set up Groq LLM
def load_llm():
    return ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="Llama3-8b-8192"
    )

# Step 3: Define prompt templates
def prompting(style="default"):
    """Returns a tailored prompt template for bank statement analysis.
    
    Args:
        style: Analysis type - "summary", "spending_patterns", "fraud_check",
               "income_vs_expense", "budget_advice", or "default"
               
    Returns:
        PromptTemplate configured for the requested analysis style
    """
    if style == "summary":
        return PromptTemplate(
            input_variables=["data"],
            template="""
You are a senior bank analyst with expertise in statistical data interpretation. 

Given the following CSV transaction data:

{data}

Generate a comprehensive statistical summary including:

1. Account Overview:
- Total transactions: [count]
- Analysis period: [start date] to [end date] ([duration])
- Opening balance: [amount]
- Closing balance: [amount]
- Net change: [amount] ([% change if applicable])

2. Financial Statistics:
- Total credits: [amount] ([count] transactions)
- Total debits: [amount] ([count] transactions)
- Average transaction amount: [amount]
- Largest credit: [amount] on [date] (description)
- Largest debit: [amount] on [date] (description)

3. Monthly Trends:
- Average monthly income: [amount]
- Average monthly expenses: [amount]
- Monthly surplus/deficit: [amount]
- Busiest transaction days: [day names]

4. Key Observations:
[3-5 bullet points highlighting most significant patterns, anomalies, or notable transactions]

Format your response with clear headings and use precise figures. Provide context for any unusual patterns.
"""
        )
    elif style == "fraud_check":
        return PromptTemplate(
            input_variables=["data"],
            template="""
You are a forensic accounting specialist.

Analyze these transactions for potential fraud:

{data}

Conduct the following statistical checks:

1. Anomaly Detection:
- Transactions >3 standard deviations from mean
- After-hours transactions (outside 9am-5pm)
- Geographic anomalies (unusual locations)

2. Pattern Analysis:
- Duplicate transaction amounts
- Rapid sequence transactions (<5 min apart)
- Round-number transactions (e.g., $500.00)

3. Risk Assessment:
For each suspicious transaction:
- Date/time
- Amount
- Merchant/vendor
- Anomaly type
- Risk score (1-5)

Format findings as a risk matrix with supporting statistics.
"""
        )
    elif style == "income_vs_expense":
        return PromptTemplate(
            input_variables=["data"],
            template="""
You are a wealth management advisor.

Analyze this financial data:

{data}

Provide a statistical comparison:

1. Income Analysis:
- Total income: [amount]
- Primary income sources
- Income frequency/distribution
- Income stability (coefficient of variation)

2. Expense Analysis:
- Fixed vs variable expenses
- Essential vs discretionary
- Expense volatility

3. Savings Capacity:
- Monthly savings rate: [amount] ([%])
- Projected annual savings
- Break-even analysis

Include quarterly trends and statistical significance of changes.
"""
        )
    elif style == "budget_advice":
        return PromptTemplate(
            input_variables=["data"],
            template="""
You are a personal finance optimization algorithm.

Based on:

{data}

Generate data-driven recommendations:

1. Current State Analysis:
- Spending efficiency score (1-100)
- Worst performing categories
- Best performing categories

2. Optimization Opportunities:
- Top 3 potential savings areas
- Estimated monthly savings potential
- Recommended budget caps per category

3. Action Plan:
- Immediate actions (quick wins)
- Medium-term adjustments
- Long-term strategy

Support all recommendations with statistical evidence.
"""
        )
    else:  # default
        return PromptTemplate(
            input_variables=["data", "question"],
            template="""
You are an AI financial analyst with statistical modeling capabilities.

Given this data:

{data}

Regarding the question: "{question}"

Provide a response that includes:
1. Direct answer
2. Supporting statistics
3. Data visualization suggestions
4. Confidence level in the analysis
5. Relevant trends/patterns
6. Any data limitations

Structure your response professionally with clear section headings.
"""
)

# Step 4: Run LLM analysis
def run_analysis(llm, data_text, question, style="default"):
    prompt_template = prompting(style)
     # Wrap in LLMChain
    chain = LLMChain(llm=llm, prompt=prompt_template)
    if style == "default":
        inputs = {"data": data_text, "question": question}
    else:
        inputs = {"data": data_text}
    return chain.run(inputs)

# Step 5: Prompt user for style
def choose_style():
    print("\nChoose analysis style:")
    print("1. Default (ask your own question)")
    print("2. Summary")
    print("3. Fraud Check")
    print("4. Income vs Expense")
    print("5. Budget Advice")
    style_map = {
        "1": "default",
        "2": "summary",
        "3": "fraud_check",
        "4": "income_vs_expense",
        "5": "budget_advice"
    }
    choice = input("Enter number (default: 1): ").strip()
    return style_map.get(choice, "default")

def main_bank_llm():
    file_path = input("📂 Enter file path (.csv or .pdf): ").strip()
    while not file_path or not os.path.isfile(file_path):
        print("❌ Invalid file path. Please try again.")
        file_path = input("📂 Enter file path (.csv or .pdf): ").strip()

    if file_path.lower().endswith('.csv'):
        print("📊 Processing CSV file...")
        try:
            # process_csv_file should return (DataFrame, text_for_llm)
            df = process_csv_file(file_path)
            analysis=analyze_bank_transactions(df)
            all_data_text=format_analysis_for_prompt(analysis,df)
            print("\nLLM Prompt Text (truncated to 8000 chars):")

            style = choose_style()
            if style == "default":
                question = input("❓ Ask your question about the CSV data: ").strip()
                if not question:
                    print("⚠️ No question provided. Exiting.")
                    return
            else:
                question = None

            llm = load_llm()
            print("\n🔍 Running analysis...\n")
            result = run_analysis(llm, all_data_text, question, style)
            print("\n🧠 Analysis Result:\n")
            print(result)
        except Exception as e:
            print(f"❌ Error while processing CSV: {e}")
    else:
        print("❌ Unsupported file format. Please provide a CSV or PDF file.")

if __name__ == "__main__":
    main_bank_llm()
