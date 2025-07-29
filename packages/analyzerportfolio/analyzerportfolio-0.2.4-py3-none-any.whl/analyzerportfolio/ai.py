from datetime import datetime, timedelta
from openai import OpenAI
import yfinance as yf
from typing import Union, List, Dict
import threading
import time

def monitor_news(
    portfolio: Union[Dict, List[Dict]],
    openai_key: str = None,
    delay: int = 3600,
    loop_forever: bool = True,
    max_iterations: int = None  # unused, for compatibility
) -> None:
    def fetch_and_analyze_news():
        last_checked = datetime.now() - timedelta(seconds=delay)

        portfolios = [portfolio] if isinstance(portfolio, dict) else portfolio
        filtered_tickers = set()
        for p in portfolios:
            tickers = p.get("tickers", [])
            if not isinstance(tickers, list):
                raise ValueError(f"'tickers' must be a list in each portfolio. Found: {type(tickers)}")
            filtered_tickers.update(tickers)

        while True:
            print("[INFO] Checking news...")
            for ticker in filtered_tickers:
                print(f"[DEBUG] Fetching news for {ticker}")
                try:
                    news = yf.Ticker(ticker).news
                except Exception as e:
                    print(f"[ERROR] Failed to fetch news for {ticker}: {e}")
                    continue
                
                if news:
                    for article in news:
                        try:
                            pub_date = datetime.fromisoformat(article['content']['pubDate'].rstrip('Z'))
                        except Exception as e:
                            print(f"[WARNING] Skipping article due to pubDate error: {e}")
                            continue
                                            
                        title = article.get('title', 'No title')
                        link = article.get('link', 'No link available')
                        summary = article.get('summary', '')

                        print(f"\n[NEW] {pub_date} — {ticker}: {title}")
                        print(f"Link: {link}\nSummary: {summary}")

                        if openai_key:
                            try:
                                prompt = f"""You are a financial analyst. Given this article, analyze its potential market impact and tone:

                                        Title: {title}
                                        Summary: {summary}

                                        Respond with a concise summary of the sentiment (positive, negative, neutral), and whether this is likely to move the stock price significantly."""
                                
                                print("[INFO] Sending prompt to GPT...")
                                client = OpenAI(api_key=openai_key)

                                response = client.chat.completions.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": "You are a helpful financial analyst."},
                                        {"role": "user", "content": prompt}
                                    ],
                                    temperature=0.7,
                                )

                                answer = response.choices[0].message.content
                                print(f"\n[GPT RESPONSE] {answer}\n")
                            except Exception as e:
                                print(f"[ERROR] OpenAI request failed: {e}")
                    
                    else:
                        continue

            last_checked = datetime.now()
            if not loop_forever:
                break

            print(f"[INFO] Sleeping for {delay} seconds...\n")
            time.sleep(delay)

    # Run directly (or you can use threading.Thread if you want async)
    fetch_and_analyze_news()

def old_monitor_news(
    portfolio: Union[Dict, List[Dict]],
    openai_key: str = None,
    delay: int = 3600,
    loop_forever: bool = True,
    max_iterations: int = None
) -> None:
    """
    Monitor news for the given portfolios, optionally analyze it using OpenAI GPT, and run the process in a separate thread.
    News is retrieved from Yahoo Finance and analyzed using OpenAI GPT-4 if an API key is provided.

    Parameters:
    - portfolio (Union[Dict, List[Dict]]): The portfolio(s) to monitor.
    - openai_key (str, optional): The OpenAI API key. Default is None.
    - delay (int): Delay between checks in seconds. Default is 3600 (1 hour).
    - loop_forever (bool): If True, runs continuously. Default is True.
    - max_iterations (int, optional): If set, limits the number of iterations.
    """

    def fetch_and_analyze_news():
        last_checked = datetime.now() - timedelta(seconds=delay)

        portfolios = [portfolio] if isinstance(portfolio, dict) else portfolio
        filtered_tickers = set()
        for p in portfolios:
            tickers = p.get("tickers", [])
            if not isinstance(tickers, list):
                raise ValueError(f"'tickers' must be a list in each portfolio. Found: {type(tickers)}")
            filtered_tickers.update(tickers)

        iterations = 0

        while loop_forever or (max_iterations is None or iterations < max_iterations):
            print(f"[{datetime.now().isoformat()}] Iteration {iterations + 1}")
            for ticker in filtered_tickers:
                try:
                    news_items = yf.Ticker(ticker).news
                    for article in news_items:
                        pub_date_str = article['content'].get('pubDate')
                        if not pub_date_str:
                            continue

                        pub_date = datetime.fromisoformat(pub_date_str.rstrip('Z'))

                        if pub_date > last_checked:
                            title = article.get('title', 'No Title')
                            link = article.get('link', 'No Link')
                            summary = article.get('summary', '')

                            print(f"\n📰 {title}\n🔗 {link}\n📝 {summary}")

                            if openai_key:
                                openai.api_key = openai_key
                                prompt = f"Analyze the importance and sentiment of this financial news article:\n\nTitle: {title}\nSummary: {summary}"
                                try:
                                    response = openai.ChatCompletion.create(
                                        model="gpt-4",
                                        messages=[{"role": "user", "content": prompt}],
                                        max_tokens=150
                                    )
                                    analysis = response.choices[0].message['content'].strip()
                                    print(f"\n🤖 GPT-4 Analysis:\n{analysis}")
                                except Exception as e:
                                    print(f"Error from OpenAI: {e}")
                        else:
                            print("No recent news available")

                except Exception as e:
                    print(f"Error fetching news for {ticker}: {e}")

            last_checked = datetime.now()
            iterations += 1
            time.sleep(delay)

    # Run the task in a separate thread if looping forever
    if loop_forever:
        threading.Thread(target=fetch_and_analyze_news, daemon=True).start()
    else:
        fetch_and_analyze_news()