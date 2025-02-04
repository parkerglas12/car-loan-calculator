import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def amortization_calculation(p: float, r: float, n: int) -> float:
    return p * (((r * (1 + r) ** n)) / ((1 + r) ** n - 1))

def calculate_total_tax_paid(car_price: float, trade_in_amount: float, tax_rate: float) -> float:
    return (car_price - trade_in_amount) * tax_rate / 100

def main() -> None:
    st.set_page_config(page_title="Car Loan Calculator")
    st.title("Car Loan Calculator")

    # First set of columns
    col1, col2 = st.columns(2)
    auto_price: float = col1.number_input("Auto Price", min_value=1.0, value=10000.0, format="%.2f", step=100.0)
    loan_term: int = col1.number_input("Loan Term", min_value=1, value=60)
    interest_rate: float = col1.number_input("Interest Rate", min_value=0.01, value=5.0, format="%.2f")
    down_payment: float = col1.number_input("Down Payment", min_value=0.0, value=2500.0, format="%.2f", step=100.0)

    trade_in: float = col2.number_input("Trade-in Value", min_value=0.0, value=0.0, format="%.2f", step=100.0)
    sales_tax_rate: float = col2.number_input("Sales Tax", min_value=0.01, value=6.875, format="%.3f")
    fees: float = col2.number_input("Title, Registration, and Other Fees", min_value=0.0, value=0.0, format="%.2f", step=10.0)
    include_fees: bool = col2.checkbox("Include All Fees In Loan")

    # Calculate tax paid
    tax_paid: float = calculate_total_tax_paid(auto_price, trade_in, sales_tax_rate)

    # Check for including fees in loan
    if not include_fees:
        total_loan_amount: float = auto_price - down_payment - trade_in
        upfront_payment: float = down_payment + tax_paid + fees
    else:
        total_loan_amount: float = auto_price - down_payment - trade_in + tax_paid + fees
        upfront_payment: float = down_payment

    monthly_payment: float = amortization_calculation(total_loan_amount, interest_rate / 100 / 12, loan_term)
    total_loan_payments: float = monthly_payment * loan_term
    total_loan_interest: float = total_loan_payments - total_loan_amount
    total: float = auto_price + total_loan_interest + tax_paid + fees

    # Creating Dataframe for graph
    schedule: list[dict[str, float]] = []
    balance: float = total_loan_amount
    for _ in range(1, loan_term + 1):
        interest_payment: float = balance * (interest_rate / 100 / 12)
        principle_payment: float = monthly_payment - interest_payment
        balance -= principle_payment

        schedule.append({
            "Interest": interest_payment,
            "Principle": principle_payment,
        })
    df = pd.DataFrame(schedule, index=range(1, loan_term + 1))

    st.write("## Loan & Payment Details")

    # Second set of columns
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Loan Amount", value=f"${total_loan_amount:,.2f}")
    col2.metric(label=f"Total of {loan_term} Loan Payments", value=f"${total_loan_payments:,.2f}")
    col3.metric(label="Total Loan Interest", value=f"${total_loan_interest:,.2f}")

    col1.metric(label="Upfront Payment", value=f"${upfront_payment:,.2f}")
    col2.metric(label="Sales Tax", value=f"${tax_paid:,.2f}")
    col3.metric(label="Monthly Payment", value=f"${monthly_payment:,.2f}")

    col1.metric(label="Total Cost (price, interest, tax, fees)", value=f"${total:,.2f}")

    # Graph colors
    colors: list[str] = ["#14db3a", "#00a6ff"]

    st.write("## Loan Breakdown")

    # Donut chart
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"), facecolor="none")
    ax.set_facecolor("none")
    labels: list[str] = ["Interest", "Principle"]
    data: list[float] = [total_loan_interest, total_loan_amount]

    wedges, _, autotexts = ax.pie(
        data, labels=None, autopct="%1.1f%%", wedgeprops=dict(width=0.6), startangle=-40, pctdistance=0.7, colors=colors
    )

    for text in autotexts:
        text.set_color("white")
        text.set_fontsize(8)
    
    legend = ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), frameon=False)
    plt.setp(legend.get_texts(), color="#ffffff")

    st.pyplot(fig)

    # Bar chart
    st.bar_chart(df, x_label="Month", y_label="$ Amount", color=colors)

if __name__ == "__main__":
    main()