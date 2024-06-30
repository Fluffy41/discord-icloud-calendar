from caldav import DAVClient
import dotenv
import os
import datetime
import discord
from discord import app_commands
from icalendar import Calendar

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
    print(f'{client.user} has connected to Discord!')


@tree.command(
    name="calendars",
    description="Get a list of calendars",
    guild=discord.Object(id=os.getenv("GUILD_ID"))
)
async def calendar_list(interaction):
    print(calendars)

    print([calendar.name for calendar in calendars])

    await interaction.response.send_message([calendar.name for calendar in calendars])

@tree.command(
    name="events",
    description="Get a list of events of a specific calendar till a certain number of days",
    guild=discord.Object(id=os.getenv("GUILD_ID"))
)
async def event_list(interaction, calendar_name: str, till_days: int):
    calendar = [calendar for calendar in calendars if calendar.name == calendar_name][0]

    start_date = datetime.datetime.now()
    end_date = start_date + datetime.timedelta(days=till_days)

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

    await interaction.response.send_message(events_list_beautiful)


client.run(os.getenv("DISCORD_TOKEN"))
