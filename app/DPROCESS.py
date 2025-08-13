import pandas as pd
import re
from datetime import datetime
import numpy as np
from transformers import AutoTokenizer

def count_tokens(text, tokenizer_name="t5-base"):
    """Count tokens using open-source tokenizers
    
    Args:
        text (str): Text to count tokens for
        tokenizer_name (str): Name of tokenizer to use (default: "t5-base")
        
    Returns:
        tuple: (num_tokens, num_chars)
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        tokens = tokenizer.encode(text)
        return len(tokens), len(text)
    except Exception as e:
        print(f"Error counting tokens with {tokenizer_name}: {str(e)}")
        return 0, 0

def preprocess_compact_csv(file_path):
    """Preprocesses compact CSV bank statements to clean and standardize the data.
    d
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Cleaned dataframe with standardized columns
    """
    try:
        # Load the full CSV file to find the start of transaction section
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Locate the transaction table header
        start_idx = None
        for i, line in enumerate(lines):
            if "Txn Date" in line and "Description" in line:
                start_idx = i
                break

        if start_idx is None:
            raise ValueError("Transaction table header not found in the CSV file.")

        # Read from transaction table onward
        df = pd.read_csv(file_path, skiprows=start_idx)

        # Clean dates and remove ='...'
        df['Txn Date'] = pd.to_datetime(
            df['Txn Date'].astype(str).str.replace('="', '').str.replace('"', ''),
            dayfirst=True,
            errors='coerce'
        )
        df['Value Date'] = pd.to_datetime(
            df['Value Date'].astype(str).str.replace('="', '').str.replace('"', ''),
            dayfirst=True,
            errors='coerce'
        )
        
        # Remove extra formatting from cheque numbers
        if 'Cheque No.' in df.columns:
            df['Cheque No.'] = df['Cheque No.'].astype(str).str.replace('="', '').str.replace('"', '')

        # Remove unwanted columns if exists
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Clean monetary columns
        def clean_money(val):
            if pd.isna(val) or str(val).strip() in ['', 'NaN', 'nan', 'None']:
                return 0.0
            return float(re.sub(r'[^\d.-]', '', str(val)))
        
        monetary_cols = ['Debit', 'Credit', 'Balance']
        for col in monetary_cols:
            if col in df.columns:
                df[col] = df[col].apply(clean_money)

        # Keep only relevant columns and rename for compactness
        required_cols = ['Txn Date', 'Description', 'Debit', 'Credit', 'Balance']
        available_cols = [col for col in required_cols if col in df.columns]
        
        df = df[available_cols]
        df.rename(columns={
            'Txn Date': 'date',
            'Description': 'desc',
            'Debit': 'dr',
            'Credit': 'cr',
            'Balance': 'bal'
        }, inplace=True)

        # Drop rows with null dates
        df = df.dropna(subset=['date'])
        
        return df

    except Exception as e:
        raise ValueError(f"Error processing CSV file: {str(e)}")


def process_csv_file(file_path):
    """Process CSV file and return cleaned transaction data
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Processed transaction data
    """
    try:
        transactions_df = preprocess_compact_csv(file_path)
        return transactions_df
    except Exception as e:
        raise ValueError(f"Failed to process CSV file: {str(e)}")


def analyze_bank_transactions(df):
    """Analyzes bank transaction data and computes key metrics
    
    Args:
        df (pd.DataFrame): Processed transaction data
        
    Returns:
        dict: Dictionary containing analysis results
    """
    try:
        # Validate input dataframe
        required_cols = {'date', 'dr', 'cr'}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            raise ValueError(f"Missing required columns: {missing}")

        # Convert date to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])

        # Basic Metrics
        total_txns = len(df)
        start_date = df['date'].min()
        end_date = df['date'].max()
        period_days = (end_date - start_date).days + 1
        
        total_debit = df['dr'].sum()
        total_credit = df['cr'].sum()
        
        # Balance calculations if balance column exists
        balance_info = {}
        if 'bal' in df.columns:
            opening_balance = df.iloc[0]['bal']
            closing_balance = df.iloc[-1]['bal']
            net_savings = closing_balance - opening_balance
            balance_info = {
                "opening_balance": round(opening_balance, 2),
                "closing_balance": round(closing_balance, 2),
                "net_savings": round(net_savings, 2)
            }
        
        # Daily aggregates
        daily = df.groupby(df['date'].dt.date).agg({'dr': 'sum', 'cr': 'sum'}).reset_index()
        top_debit_days = daily.nlargest(3, 'dr')
        top_credit_days = daily.nlargest(3, 'cr')

        # Low-spending days (bottom 10% of spending days)
        low_spend_days = daily[daily['dr'] < daily['dr'].quantile(0.1)].nsmallest(2, 'dr')

        # Monthly aggregates
        monthly = df.groupby(df['date'].dt.to_period('M')).agg({'dr': 'sum', 'cr': 'sum'}).reset_index()
        monthly['date'] = monthly['date'].dt.to_timestamp()
        
        # Frequent keywords (merchant analysis)
        common_keywords = ['amazon', 'zomato', 'blinkit', 'dmrc', 'razorpay', 'swiggy', 
                          'uber', 'ola', 'paytm', 'google', 'lic', 'airtel', 'jio']
        freq_dict = {}
        desc_text = ' '.join(df['desc'].astype(str).str.lower())
        
        for keyword in common_keywords:
            freq_dict[keyword] = desc_text.count(keyword)
        
        frequent_merchants = {k: v for k, v in sorted(freq_dict.items(), key=lambda item: item[1], reverse=True) if v > 0}

        # Transaction frequency analysis
        debit_txns = len(df[df['dr'] > 0])
        credit_txns = len(df[df['cr'] > 0])
        
        # Average transaction amounts
        avg_debit = df['dr'].mean() if debit_txns > 0 else 0
        avg_credit = df['cr'].mean() if credit_txns > 0 else 0

        return {
            "total_transactions": total_txns,
            "debit_transactions": debit_txns,
            "credit_transactions": credit_txns,
            "time_period": {
                "start_date": start_date.strftime('%d-%b-%Y'),
                "end_date": end_date.strftime('%d-%b-%Y'),
                "days": period_days
            },
            "amounts": {
                "total_debit": round(total_debit, 2),
                "total_credit": round(total_credit, 2),
                "avg_debit": round(avg_debit, 2),
                "avg_credit": round(avg_credit, 2)
            },
            **balance_info,
            "daily_analysis": {
                "top_debit_days": top_debit_days.to_dict(orient='records'),
                "top_credit_days": top_credit_days.to_dict(orient='records'),
                "low_spend_days": low_spend_days.to_dict(orient='records')
            },
            "monthly_trends": monthly.to_dict(orient='records'),
            "merchant_analysis": frequent_merchants,
            "analysis_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            
            # ✅ NEW: Full raw data for plotting full graphs
            "raw_data": {
                "daily": daily.to_dict(orient='records'),
                "monthly": monthly.to_dict(orient='records')
            }
        }

        
    except Exception as e:
        raise ValueError(f"Error analyzing transactions: {str(e)}")


def format_analysis_for_prompt(analysis_dict,df):
    """Formats the analysis dictionary into a readable prompt string
    
    Args:
        analysis_dict (dict): Analysis results from analyze_bank_transactions()
        
    Returns:
        str: Formatted string ready for LLM prompt
    """
    try:
        lines = []
        lines.append("📊 Comprehensive Bank Statement Analysis\n")
        lines.append("="*50)
        
        # Basic Info
        lines.append("\n📅 Time Period:")
        lines.append(f"• From: {analysis_dict['time_period']['start_date']}")
        lines.append(f"• To: {analysis_dict['time_period']['end_date']}")
        lines.append(f"• Duration: {analysis_dict['time_period']['days']} days")
        
        lines.append("\n🧮 Transaction Summary:")
        lines.append(f"• Total Transactions: {analysis_dict['total_transactions']}")
        lines.append(f"  → Debits: {analysis_dict['debit_transactions']}")
        lines.append(f"  → Credits: {analysis_dict['credit_transactions']}")
        
        # Amounts
        lines.append("\n💰 Amounts Analysis:")
        lines.append(f"• Total Debited: ₹{analysis_dict['amounts']['total_debit']}")
        lines.append(f"• Total Credited: ₹{analysis_dict['amounts']['total_credit']}")
        lines.append(f"• Average Debit: ₹{analysis_dict['amounts']['avg_debit']}")
        lines.append(f"• Average Credit: ₹{analysis_dict['amounts']['avg_credit']}")
        
        # Balance info if available
        if 'opening_balance' in analysis_dict:
            lines.append("\n🏦 Balance Information:")
            lines.append(f"• Opening Balance: ₹{analysis_dict['opening_balance']}")
            lines.append(f"• Closing Balance: ₹{analysis_dict['closing_balance']}")
            lines.append(f"• Net Change: ₹{analysis_dict['net_savings']} " + 
                       ("(Increase)" if analysis_dict['net_savings'] >=0 else "(Decrease)"))
        
        # Daily Analysis
        lines.append("\n📈 Top Spending Days:")
        for day in analysis_dict['daily_analysis']['top_debit_days']:
            lines.append(f"  → {day['date']}: ₹{day['dr']}")
            
        lines.append("\n📉 Top Income Days:")
        for day in analysis_dict['daily_analysis']['top_credit_days']:
            lines.append(f"  → {day['date']}: ₹{day['cr']}")
            
        lines.append("\n🌱 Most Frugal Days:")
        for day in analysis_dict['daily_analysis']['low_spend_days']:
            lines.append(f"  → {day['date']}: Spent ₹{day['dr']}, Received ₹{day['cr']}")
        
        # Merchant Analysis
        if analysis_dict['merchant_analysis']:
            lines.append("\n🛍️ Frequent Merchants/Keywords:")
            for merchant, count in analysis_dict['merchant_analysis'].items():
                lines.append(f"  • {merchant.title()}: {count} mentions")
        
        # Monthly Trends
        if 'monthly_trends' in analysis_dict and analysis_dict['monthly_trends']:
            lines.append("\n📅 Monthly Trends:")
            for month in analysis_dict['monthly_trends']:
                month_date = pd.to_datetime(month['date']).strftime('%b %Y')
                lines.append(f"  • {month_date}: Spent ₹{month['dr']}, Received ₹{month['cr']}")
        lines.append("\n" + "="*50)
        lines.append(f"\nAnalysis performed on: {analysis_dict['analysis_date']}")
        for _, row in df.iterrows():
            line = f"{row['date'].strftime('%d-%m-%Y')} | {row['desc'][:40]}... | -{row['dr'] if row['dr'] > 0 else ''} +{row['cr'] if row['cr'] > 0 else ''} = {row['bal']}"
            lines.append(line)
        return "\n".join(lines)
    
    except Exception as e:
        raise ValueError(f"Error formatting analysis: {str(e)}")



def main_dprocess():
    """Main function to execute the bank statement analysis"""
    print("Bank Statement Analysis Tool")
    print("=" * 50)
    
    try:
        file_path = input("Enter the path to your bank statement (CSV): ").strip()
        
        if not file_path.lower().endswith('.csv'):
            print("Error: Please provide a CSV file.")
            return
        
        print("\nProcessing file...")
        df = process_csv_file(file_path)
        
        print("\nSample of processed data:")
        print(df.head(3).to_string(index=False))
        
        print("\nAnalyzing transactions...")
        analysis = analyze_bank_transactions(df)
        
        print("\nAnalysis Results:")
        new=format_analysis_for_prompt(analysis,df)
        print(new)
        
        print("Tokens-:")
        print(count_tokens(new))
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        print("\nAnalysis complete.")


if __name__ == "__main__":
    main_dprocess()