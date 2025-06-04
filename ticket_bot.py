import time
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from telegram import Bot

# === Bot Setup ===
BOT_TOKEN = '8024752062:AAE_5osLpnByViFzJgJntAlmGo9b20cdvB4'
CHAT_ID = '5247051269'
bot = Bot(token=BOT_TOKEN)

# === Editable Section ===
ROUTES = [
    ("Dhaka", "Rajshahi"),
    ("Biman_Bandar", "Rajshahi"),
    ("Dhaka", "Chapainawabganj")
]

DATES = ["04-Jun-2025", "05-Jun-2025", "06-Jun-2025"]
TRAVEL_CLASS = "S_CHAIR"

# === Do Not Edit Below This Line ===
last_status = {}

async def send_message(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

async def check_tickets(from_city, to_city, date):
    global last_status

    url = f"https://eticket.railway.gov.bd/booking/train/search?fromcity={from_city}&tocity={to_city}&doj={date}&class={TRAVEL_CLASS}"

    options = Options()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    chrome_service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=chrome_service, options=options)
    driver.get(url)
    time.sleep(10)

    try:
        trips = driver.find_elements(By.CLASS_NAME, 'single-trip-wrapper')
        for trip in trips:
            try:
                train_name = trip.find_element(By.TAG_NAME, 'h2').text.strip()
                seats = trip.find_elements(By.CLASS_NAME, 'single-seat-class')

                for seat in seats:
                    seat_type = seat.find_element(By.CLASS_NAME, 'seat-class-name').text.strip()
                    seat_count = seat.find_element(By.CLASS_NAME, 'all-seats').text.strip()

                    if seat_count.isdigit() and int(seat_count) > 0:
                        key = f"{train_name}-{seat_type}-{date}-{from_city}-{to_city}"
                        previous_count = last_status.get(key)

                        if previous_count != seat_count:
                            msg = (
                                f"🚆 {train_name}\n"
                                f"📅 Date: {date}\n"
                                f"➡️ Route: {from_city} → {to_city}\n"
                                f"🪑 Class: {seat_type}\n"
                                f"🎟️ Available Tickets: {seat_count}"
                            )
                            await send_message(msg)
                            last_status[key] = seat_count
            except Exception:
                continue
    except Exception as e:
        print("Error:", e)
    finally:
        driver.quit()

async def main_loop():
    while True:
        print("Checking all routes and dates...")
        for from_city, to_city in ROUTES:
            for date in DATES:
                await check_tickets(from_city, to_city, date)
        await asyncio.sleep(41)

if __name__ == "__main__":
    asyncio.run(main_loop())
