import yfinance as yf

# Lista de ativos para monitorar
assets = {
    "BTC-USD": "Bitcoin",
    "SOL-USD": "Solana",
    "^BVSP": "IBOVESPA",
    "^GSPC": "S&P 500",
    "BPAC11.SA": "BTG Pactual"
}

# Função para buscar preços e variações
def fetch_prices_and_changes(assets):
    prices_and_changes = {}
    for symbol, name in assets.items():
        try:
            # Busca dados do ativo
            ticker = yf.Ticker(symbol)
            history = ticker.history(period="5d", interval="1d")  # Ajuste no período para garantir dados
            print(f"Data for {name} ({symbol}):\n", history)  # Debug: Exibe os dados retornados

            # Calcula preço e variação
            latest_close = history["Close"].iloc[-1]
            previous_close = history["Close"].iloc[-2]
            change_percent = ((latest_close - previous_close) / previous_close) * 100

            prices_and_changes[name] = {
                "price": round(latest_close, 2),
                "change": round(change_percent, 2),
            }
        except Exception as e:
            # Debug: Exibe erros no console
            print(f"Error for {name} ({symbol}): {e}")
            prices_and_changes[name] = {"price": "N/A", "change": "N/A"}
    return prices_and_changes

# Atualizar o README.md
def update_readme(prices_and_changes):
    start_marker = "<!--START_SECTION:prices-->"
    end_marker = "<!--END_SECTION:prices-->"
    new_content = f"\n{start_marker}\n"

    # Cabeçalho da tabela
    new_content += "| Bitcoin | Solana | IBOVESPA | S&P 500 | BTG Pactual |\n"
    new_content += "|:-------:|:------:|:--------:|:-------:|:-----------:|\n"

    # Preenchendo a tabela com preços e variações
    new_content += "| "
    for name, data in prices_and_changes.items():
        prefix = "$" if name not in ["IBOVESPA", "BTG Pactual"] else "R$" if name == "BTG Pactual" else ""
        change = f"{data['change']}%" if data['change'] != "N/A" else "N/A"
        value = f"{prefix}{data['price']} ({change})"
        new_content += f"{value} | "
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
    # Busca preços e variações
    prices_and_changes = fetch_prices_and_changes(assets)
    print("\nFinal Prices and Changes Data:\n", prices_and_changes)  # Debug final: Verifica os dados processados

    # Atualiza o README
    update_readme(prices_and_changes)
