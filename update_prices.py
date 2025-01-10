import yfinance as yf

assets = {
    "BTC-USD": "Bitcoin",
    "SOL-USD": "Solana",
    "^BVSP": "IBOVESPA",
    "^GSPC": "S&P 500",
    "BPAC11.SA": "BTG Pactual"
}

def fetch_prices(assets):
    prices = {}
    for symbol, name in assets.items():
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="5d")["Close"].dropna().iloc[-1]  # Último preço disponível
            prices[name] = round(price, 2)
        except Exception as e:
            prices[name] = "N/A"
    return prices

def update_readme(prices):
    start_marker = "<!--START_SECTION:prices-->"
    end_marker = "<!--END_SECTION:prices-->"
    new_content = f"\n{start_marker}\n"
    new_content += "| Bitcoin | Solana | IBOVESPA | S&P 500 | BTG Pactual |\n"
    new_content += "|:-------:|:------:|:--------:|:-------:|:-----------:|\n"
    new_content += "| " + " | ".join([f"${price}" for price in prices.values()]) + " |\n"
    new_content += f"{end_marker}\n"

    with open("README.md", "r") as file:
        readme = file.read()

    updated_readme = readme.split(start_marker)[0] + new_content + readme.split(end_marker)[1]

    with open("README.md", "w") as file:
        file.write(updated_readme)

if __name__ == "__main__":
    prices = fetch_prices(assets)
    update_readme(prices)
