import logging
from caldav import DAVClient
import dotenv
import os
import datetime
import discord
from discord import app_commands
from discord.ext import tasks
from icalendar import Calendar

# Configure logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

dotenv.load_dotenv()

# Discord bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# iCloud calDAV URL
url = "https://caldav.icloud.com"

# iCloud username and password
username = os.getenv("ICLOUD_USERNAME")
password = os.getenv("ICLOUD_PASSWORD")

# Create a DAV client
davClient = DAVClient(url, username=username, password=password)

# Access your calendars
principal = davClient.principal()
calendars = principal.calendars()


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=os.getenv("GUILD_ID")))
    logging.info(f'{client.user} has connected to Discord!')
    print(f'{client.user} has connected to Discord!')


@tree.command(
    name="calendars",
    description="Get a list of calendars",
    guild=discord.Object(id=os.getenv("GUILD_ID"))
)
async def calendar_list(interaction):
    calendarList = [calendar.name for calendar in calendars]
    logging.info('Executing calendar_list command')
    print('Executing calendar_list command')
    for calendar in calendarList:
        if calendar in os.getenv("calendarDenylist").split(", "):
            print("on Denylist")
            calendarList.remove(calendar)

    await interaction.response.send_message(calendarList)


@tree.command(
    name="events",
    description="Get a list of events of a specific calendar till a certain number of days",
    guild=discord.Object(id=os.getenv("GUILD_ID"))
)
async def event_request(interaction, calendar_name: str, till_days: int):
    logging.info(f'Executing event_request command for calendar: {calendar_name} and days: {till_days}')
    event = event_list(calendar_name, till_days)
    await interaction.response.send_message(event)


def event_list(calendar_name: str, till_days: int):
    logging.info(f'Executing event_list command for calendar: {calendar_name} and days: {till_days}')
    print(f'Executing event_list command for calendar: {calendar_name} and days: {till_days}')
    calendar = [calendar for calendar in calendars if calendar.name == calendar_name][0]

    start_date = datetime.datetime.now()
    end_date = start_date + datetime.timedelta(days=till_days)

    print(calendar)

    events = calendar.date_search(start_date, end_date)

    events_list = []
    for event in events:

        event = Calendar.from_ical(event.data)

        for component in event.walk():
            if component.name == "VEVENT":
                event_name = component.get('summary')
                event_start = component.get('dtstart').dt
                event_end = component.get('dtend').dt
                events_list.append((event_name, event_start, event_end))

        unix_timestamp_start = int(event_start.timestamp())
        unix_timestamp_end = int(event_end.timestamp())

    events_list_beautiful = f"Upcoming events in {calendar_name}:\n {event_name} \n begins in <t:{unix_timestamp_start}:R> \n <t:{unix_timestamp_start}:f> - <t:{unix_timestamp_end}:f> \n\n"

    print(events_list_beautiful)

    return events_list_beautiful

live_calendar_status = False

@tree.command(
    name="livecalendar",
    description="Will edit the Message every 5 Minutes to show the upcoming events",
    guild=discord.Object(id=os.getenv("GUILD_ID"))
)
async def live_calendar(interaction, calendar_name: str):
    global live_calendar_status
    message_id = None
    print(f"Executing live_calendar command for {calendar_name}")
    if not live_calendar_status:
        live_calendar_status = True
        await interaction.response.send_message(content="Live calendar started", delete_after=5)
        channel_id = interaction.channel_id
        channel = client.get_channel(channel_id)
        message = await channel.send(content="None")
        message_id = message.id
        calendar_refresher.start(calendar_name, message_id)
    else:
        live_calendar_status = False
        calendar_refresher.stop()
        message = await channel.fetch_message(message_id)
        await message.delete()
        await interaction.response.send("Live calendar stopped", delete_after=5)


@tasks.loop(seconds=5)
async def calendar_refresher(calendar_name, message_id):
    channel = client.get_channel(1256742751106633759)
    message = await channel.fetch_message(message_id)
    """await channel.send(calendar_name)
    await channel.send(counter)"""
    events = event_list(calendar_name, 1)
    print(events)
    await message.edit(content=events)

client.run(os.getenv("DISCORD_TOKEN"))
