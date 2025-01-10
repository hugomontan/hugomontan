import yfinance as yf

# Lista de ativos para monitorar
assets = {
    "BTC-USD": "Bitcoin",
    "SOL-USD": "Solana",
    "^BVSP": "IBOVESPA",
    "^GSPC": "S&P 500",
    "BPAC11.SA": "BTG Pactual"
}

# Função para buscar preços
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

# Atualizar o README.md
def update_readme(prices):
    start_marker = "<!--START_SECTION:prices-->"
    end_marker = "<!--END_SECTION:prices-->"
    new_content = f"\n{start_marker}\n"

    # Criação da tabela horizontal com prefixos personalizados
    new_content += "| Bitcoin | Solana | IBOVESPA | S&P 500 | BTG Pactual |\n"
    new_content += "|:-------:|:------:|:--------:|:-------:|:-----------:|\n"
    new_content += "| "
    for name, price in prices.items():
        if name == "BTG Pactual":
            new_content += f"R${price} | "
        elif name == "IBOVESPA":
            new_content += f"{price} | "
        else:
            new_content += f"${price} | "
    new_content = new_content.strip(" |") + " |\n"
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
