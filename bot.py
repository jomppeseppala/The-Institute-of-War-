import discord
import random
import asyncio
from datetime import datetime, time, timedelta
import os
from flask import Flask
import threading

TOKEN = os.environ['TOKEN']
ANNOUNCEMENT_FILE = 'announcements.txt'
CHANNEL_NAME = 'summoner-lounge-arjen-sankarit'
ANNOUNCEMENT_TIME = time(hour=14, minute=0)  # Adjust to your preferred time

# Flask app for web server
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>The Institute of War Discord Bot</h1>
    <p>Bot Status: Online and Running</p>
    <p>Daily announcements at 14:00</p>
    <p>Available commands:</p>
    <ul>
        <li>!institute - Get a random announcement</li>
        <li>!report @user - Report a summoner</li>
        <li>!late - Send late warning</li>
        <li>!absence - Send absence notice</li>
        <li>!flex - Call for match staffing</li>
    </ul>
    '''

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Intents setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Load announcements from file with separator
with open(ANNOUNCEMENT_FILE, 'r', encoding='utf-8') as f:
    file_content = f.read()
    announcements = [announcement.strip() for announcement in file_content.split('---') if announcement.strip()]

async def wait_until(target_time):
    now = datetime.now()
    future = datetime.combine(now.date(), target_time)
    if future < now:
        future += timedelta(days=1)
    await asyncio.sleep((future - now).total_seconds())

async def send_daily_announcement():
    await client.wait_until_ready()
    channel = discord.utils.get(client.get_all_channels(), name=CHANNEL_NAME)
    while True:
        await wait_until(ANNOUNCEMENT_TIME)
        announcement = random.choice(announcements)
        await channel.send(announcement)
        await asyncio.sleep(86400)  # Wait 24 hours

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    replit_url = os.environ.get('REPLIT_DEV_DOMAIN', 'your-repl-url.repl.co')
    print(f'Web server running at: https://{replit_url}')
    client.loop.create_task(send_daily_announcement())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # !institute - Random announcement
    if message.content.lower() == '!institute':
        announcement = random.choice(announcements)
        await message.channel.send(announcement)

    # !report - Formal Tribunal message
    elif message.content.startswith('!report'):
        if message.mentions:
            reported_user = message.mentions[0]
            tribunal_message = (
                f"This is an automated response from the Tribunal.\n\n"
                f"Thank you for your report regarding the conduct of Summoner {reported_user.mention}.\n"
                f"Your submission has been logged and a preliminary review has been initiated.\n\n"
                f"While the specifics of this investigation are confidential, please be assured that all reports are handled with the utmost seriousness and strict adherence to the Summoner's Code.\n\n"
                f"Misuse of the reporting system—including the submission of baseless, frivolous, or malicious reports—constitutes a violation of Tribunal policies and may result in sanctions against the reporting party.\n\n"
                f"Further disruptive actions by the reported Summoner, or any continued misuse of this system, may lead to disciplinary measures including, but not limited to, summoning suspension, mandatory Tribunal hearings, or permanent revocation of Summoner credentials.\n\n"
                f"Thank you for your cooperation.\n\n"
                f"The Tribunal"
            )
            await message.channel.send(tribunal_message)
        else:
            await message.channel.send("Please specify a Summoner to report. Usage: `!report @username`.")

    # !late - Casual boss-style warning
    elif message.content.startswith('!late'):
        if message.mentions:
            target_user = message.mentions[0]
            late_messages = [
                f"Summoner {target_user.mention},\nYour extended “break” has been noted. The match schedule is on hold, and everyone is waiting on you to return to the lobby.\n\nThis is not a suggestion. Please report back to the lobby immediately to resume operations.\n\nThe Institute of War",
                f"Summoner {target_user.mention},\nThis is an official reminder: your unexplained delay is holding up the match. Colleagues are waiting, and further delays are unacceptable.\n\nPlease return to the lobby immediately to avoid escalation.\n\nThe Institute of War"
            ]
            await message.channel.send(random.choice(late_messages))
        else:
            await message.channel.send("Please specify a Summoner for the late warning. Usage: `!late @username`.")

    # !absence - Serious absence notices
    elif message.content.startswith('!absence'):
        if message.mentions:
            target_user = message.mentions[0]
            absence_messages = [
                f"Summoner {target_user.mention},\nYour prolonged absence has been documented. Champions under your care have been left unsupervised, resulting in chaos and a complete breakdown of order.\n\nYou are hereby accused of dereliction of duty and champion neglect. Immediate return is expected. Failure to comply will result in mandatory Tribunal review and potential revocation of Summoner credentials.\n\nThis is your formal warning.\n\nThe Tribunal",
                f"Attention Summoner {target_user.mention},\nThis is a formal notice regarding your recent extended absence. Assigned champions have been left without guidance, resulting in operational delays and disruptions.\n\nContinued non-compliance with established protocols may result in disciplinary action, including but not limited to summoning suspension and formal Tribunal hearings.\n\nThis matter has been logged and is currently under review. No further details will be provided at this time.\n\nThe Tribunal"
            ]
            await message.channel.send(random.choice(absence_messages))
        else:
            await message.channel.send("Please specify a Summoner for the absence notice. Usage: `!absence @username`.")

    # !flex - Casual work call for match staffing
    elif message.content.startswith('!flex'):
        flex_messages = [
            "Summoners,\nA scheduled match is about to begin, and 3 to 5 Summoners are needed to fill available spots and keep things running smoothly.\n\nPlease report to the lobby when available.\n\nThe Institute of War",
            "Summoners,\n3 to 5 Summoners are needed for the upcoming match to ensure it can proceed without delay.\n\nYour timely response is appreciated.\n\nThe Institute of War"
        ]
        await message.channel.send(random.choice(flex_messages))

# Start Flask server in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

client.run(TOKEN)