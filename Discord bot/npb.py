import discord
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys

# コンソールの文字コードをUTF-8に設定
sys.stdout.reconfigure(encoding="utf-8")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True  # Botがサーバーに参加・退出するための権限
intents.reactions = True  # リアクションに対する権限
client = discord.Client(intents=intents)


def scrape_yahoo_baseball_schedule():
    url = "https://baseball.yahoo.co.jp/npb/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    schedule_info = []
    bb_score_sections = soup.find_all("section", class_="bb-score")
    for bb_score_section in bb_score_sections:
        league_title = bb_score_section.find(
            "h1", class_="bb-score__title"
        ).text.strip()
        game_items = bb_score_section.find_all("li", class_="bb-score__item")
        for game_item in game_items:
            date = game_item.find("span", class_="bb-score__date").text.strip()
            venue = game_item.find("span", class_="bb-score__venue").text.strip()
            home_team = game_item.find("p", class_="bb-score__homeLogo").text.strip()
            away_team = game_item.find("p", class_="bb-score__awayLogo").text.strip()
            score = game_item.find("span", class_="bb-score__score").text.strip()
            link = game_item.find("a")["href"]
            state = game_item.find("p", class_="bb-score__link").text.strip()

            schedule_info.append(
                {
                    "league": league_title,
                    "date": date,
                    "venue": venue,
                    "home_team": home_team,
                    "away_team": away_team,
                    "score": score,
                    "link": link,
                    "state": state,
                }
            )

    return schedule_info


@client.event
async def on_ready():
    print(f"{client.user.name} がログインしました")

@client.event
async def on_message(message):
    print(f"メッセージ受信: {message.content}")
    # 以下の処理を追加


@client.event
async def on_message(message):
    if message.author == client.user:  # Bot自身のメッセージは無視
        return

    if message.content == "!schedule":
        today = datetime.now().strftime("%Y-%m-%d")
        schedule_info = scrape_yahoo_baseball_schedule()

        if not schedule_info:
            await message.channel.send("本日の試合情報はありません。")
            return

        response = f"本日({today})のプロ野球の試合情報:\n"
        for game in schedule_info:
            response += f"リーグ: {game['league']}\n"
            response += f"日程: {game['date']} / 場所: {game['venue']}\n"
            response += f"{game['home_team']} vs {game['away_team']} / スコア: {game['score']} / {game['state']}\n"
            response += f"リンク: {game['link']}\n"
            response += "---\n"

        await message.channel.send(response)


# ここにボットのトークンを入力してください
client.run("MTEzNDQ1MTI1ODE2MjQxMzY2OQ.Gw-4hL.RCawWdQgVFWcENfUjFVY5LW0F4yoGagL5LHnsI")

