import os

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

API_TOKEN_ALPHA = os.environ.get("API_TOKEN_ALPHA")
API_TOKEN_NEWS = os.environ.get("API_TOKEN_NEWS")


def main():
    import requests, smtplib, datetime as dt

    def get_last_weekday(date: dt.datetime) -> dt.datetime:
        diff = 1
        if date.weekday() == 0:
            diff = 3
        elif date.weekday() == 6:
            diff = 2

        return date - dt.timedelta(days=diff)

    def get_percent(value1: float, value2: float) -> float:
        return abs(value2) * 100 / value1

    def remove_html_tags(txt):
        from bs4 import BeautifulSoup

        return BeautifulSoup(txt, features="html.parser").text

    time_now = dt.datetime.now()

    last_day = get_last_weekday(time_now)
    last_last_day = get_last_weekday(last_day)

    parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey": API_TOKEN_ALPHA,
    }
    response = requests.get(url="https://www.alphavantage.co/query", params=parameters)
    response.raise_for_status()
    stocks_data = response.json()

    close_last_day = float(
        stocks_data["Time Series (Daily)"][
            f"{last_day.year}-{str(last_day.month).zfill(2)}-{str(last_day.day).zfill(2)}"
        ]["4. close"]
    )

    close_l_last_day = float(
        stocks_data["Time Series (Daily)"][
            f"{last_last_day.year}-{str(last_last_day.month).zfill(2)}-{str(last_last_day.day).zfill(2)}"
        ]["4. close"]
    )

    price_difference = close_last_day - close_l_last_day
    percent_diff_data = get_percent(close_last_day, price_difference)

    if percent_diff_data >= 5:
        if price_difference < 0:
            percent_diff_str = f"+{percent_diff_data:.2f}"
        else:
            percent_diff_str = f"-{percent_diff_data:.2f}"

        parameters = {
            "apiKey": API_TOKEN_NEWS,
            "q": COMPANY_NAME,
            "searchIn": "title,description",
            "from": f"{last_last_day.year}-{str(last_last_day.month).zfill(2)}-{str(last_last_day.day).zfill(2)}",
            "language": "en",
            "sortBy": "popularity",
        }
        response = requests.get(
            url="https://newsapi.org/v2/everything", params=parameters
        )
        response.raise_for_status()

        news_data = response.json()["articles"][0:3]

        my_email = "nicolashilbert000@gmail.com"
        my_password = os.environ.get("MY_PASSWORD")

        articles = list()
        titles = list()
        for value in news_data:
            articles.append(
                remove_html_tags(str(value["description"]).encode("ascii", "ignore"))
            )
            titles.append(
                remove_html_tags(str(value["title"]).encode("ascii", "ignore"))
            )

        msg = ""
        for i in range(len(articles)):
            msg += f"Headline: {titles[i]}\nBrief: {articles[i]}...\n\n"

        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=my_email, password=my_password)
            connection.sendmail(
                from_addr=my_email,
                to_addrs=my_email,
                msg=f"Subject: {COMPANY_NAME} Stocks: {percent_diff_str}\n\n{msg}",
            )
            connection.close()
        print("SENT")
    input()


if __name__ == "__main__":
    main()
