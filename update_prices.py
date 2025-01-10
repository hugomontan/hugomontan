import yfinance as yf

# Lista de ativos para monitorar
assets = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum"
}

# Função para buscar preços
def fetch_prices(assets):
    prices = {}
    for symbol, name in assets.items():
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")["Close"].iloc[-1]
            prices[name] = round(price, 2)
        except Exception as e:
            prices[name] = "N/A"
    return prices

# Atualizar o README.md
def update_readme(prices):
    start_marker = "<!--START_SECTION:prices-->"
    end_marker = "<!--END_SECTION:prices-->"
    new_content = f"\n{start_marker}\n"
    new_content += "| Asset       | Price (USD) |\n"
    new_content += "|-------------|-------------|\n"
    for name, price in prices.items():
        new_content += f"| {name}      | ${price}      |\n"
    new_content += f"{end_marker}\n"

    # Lê o conteúdo atual do README
    with open("README.md", "r") as file:
        readme = file.read()

    # Substitui a seção de preços
    updated_readme = readme.split(start_marker)[0] + new_content + readme.split(end_marker)[1]

    # Salva as mudanças no README
    with open("README.md", "w") as file:
        file.write(updated_readme)

# Executar o script
if __name__ == "__main__":
    prices = fetch_prices(assets)
    update_readme(prices)
