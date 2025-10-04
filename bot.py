import stoat # stoat.py
import os, asyncio, json
import random, time
from io import BytesIO

TOKEN = None
prefix = "cat!"

os.makedirs("data", exist_ok=True)

cattypes = json.load(open("cats.json", 'r'))

# Load existing data from db.json
def load_db(guildId):
    try:
        with open(f"data/{guildId}.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save data to db.json
def save_db(guildId, data):
    with open(f"data/{guildId}.json", 'w') as f:
        json.dump(data, f, indent=4)

client = stoat.Client()  # Initialize the client.

@client.on(stoat.ReadyEvent)  # Listen to an event.
async def on_ready(event, /):
    print(f"Logged in as {client.user}")
    asyncio.create_task(spawncats())

@client.on(stoat.MessageCreateEvent)
async def on_message(event, /):
    message = event.message

    if message.content == f"{prefix}ping":
        await message.channel.send("pong!")  # Send a message.

    if message.content == f"{prefix}inv":
        db = load_db(message.server.id)
        db["inventories"].setdefault(message.author.id, {})
        data = ""
        if message.author.id in db["inventories"] and db["inventories"][message.author.id]:
            for cattype in cattypes:
                if cattype in db["inventories"][message.author.id]:
                    if db["inventories"][message.author.id][cattype] > 0:
                        if len(cattypes[cattype]) > 1:
                            emojicat = cattypes[cattype][1]
                        else:
                            emojicat = "🔳"
                        data += f"{emojicat}**{cattype}** {db['inventories'][message.author.id][cattype]}\n"
            await message.channel.send(embeds=[stoat.SendableEmbed(title=f"{message.author}#{message.author.discriminator}'s cats:", description=data, color="#6e593c")])
        else:
            await message.channel.send("u hav no cats :01K6PMEC5D8TAABQG6X5REH6GH:")  # Send a message.

    if message.content.startswith(f"{prefix}setup"):
        db = load_db(message.server.id)
        db.setdefault("channels", {})
        db["channels"].setdefault(message.channel.id, {})
        db["channels"][message.channel.id].setdefault("lastspawntime", 0)
        db["channels"][message.channel.id].setdefault("lastcatchtime", 0)
        db["channels"][message.channel.id].setdefault("nextspawntime", 0)
        db["channels"][message.channel.id].setdefault("currenttype", None)
        save_db(message.server.id, db)
        await message.channel.send("channel set up")

    if message.content.lower() == "cat":
        db = load_db(message.server.id)
        db.setdefault("channels", {})
        if message.channel.id in db["channels"]:
            if not db["channels"][message.channel.id]["currenttype"] is None:
                db.setdefault("inventories", {})
                cattype = db["channels"][message.channel.id]["currenttype"]
                if len(cattypes[cattype]) > 1:
                    emojicat = cattypes[cattype][1]
                else:
                    emojicat = "🔳"
                db["inventories"].setdefault(message.author.id, {})
                db["inventories"][message.author.id].setdefault(cattype, 0)
                db["inventories"][message.author.id][cattype] += 1
                db["channels"][message.channel.id]["currenttype"] = None
                db["channels"][message.channel.id]["lastcatchtime"] = int(time.time())
                db["channels"][message.channel.id]["nextspawntime"] = int(time.time()) + random.randint(120,1200)
                await message.channel.send(f"{message.author}#{message.author.discriminator} cought {emojicat} {cattype} cat!!!!1!\nYou now have {db['inventories'][message.author.id][cattype]} cats of dat type!!!\nthis fella was cought in {timestamp(db['channels'][message.channel.id]['lastspawntime'])}seconds!!!!")
                save_db(message.server.id, db)

async def spawncats():
    while True:  # loop forever
        for file in os.listdir('data/'):
            data = json.load(open(f"data/{file}", 'r'))
            if "channels" in data:
                for channel in data["channels"]:
                    data["channels"][channel].setdefault("currenttype", None)
                    data["channels"][channel].setdefault("nextspawntime", None)
                    if data["channels"][channel]["currenttype"] is None and int(time.time()) >= data["channels"][channel]["nextspawntime"]:
                        chnl = client.get_channel(channel)
                        weights = []
                        cats = []
                        for cat in cattypes:
                            weights.append(cattypes[cat][0])
                            cats.append(cat)
                        cattype = random.choices(cats, weights=weights, k=1)[0]

                        if len(cattypes[cattype]) > 1:
                            emojicat = cattypes[cattype][1]
                        else:
                            emojicat = "🔳"

                        #with open("cat.png", "rb") as f:
                        #    img_data = f.read()
                        #buffer = BytesIO(img_data)
                        #buffer.name = "cat.png"
                        #await chnl.send(f"{emojicat} {cattype} cat has appeared! Type \"cat\" to catch it!\n", attachments=[buffer])
                        await chnl.send(f"{emojicat} {cattype} cat has appeared! Type [\"cat\"](https://cdn.stoatusercontent.com/attachments/x42n-UZ5Nvjmder2_BwvuKGIbsedXPBX1BrEKV8pJY/image.png) to catch it!\n")
                        data["channels"][channel]["nextspawntime"] = None
                        data["channels"][channel]["lastspawntime"] = time.time()
                        data["channels"][channel]["currenttype"] = cattype
                        save_db(chnl.server.id, data)

        await asyncio.sleep(1)

def timestamp(then):
    try:
        # some math to make time look cool
        time_caught = round(abs(time.time() - then), 3)  # cry about it
        if time_caught >= 1:
            time_caught = round(time_caught, 2)

        days, time_left = divmod(time_caught, 86400)
        hours, time_left = divmod(time_left, 3600)
        minutes, seconds = divmod(time_left, 60)

        caught_time = ""
        if days:
            caught_time = caught_time + str(int(days)) + " days "
        if hours:
            caught_time = caught_time + str(int(hours)) + " hours "
        if minutes:
            caught_time = caught_time + str(int(minutes)) + " minutes "
        if seconds:
            pre_time = round(seconds, 3)
            if pre_time % 1 == 0:
                # replace .0 with .00 basically
                pre_time = str(int(pre_time)) + ".00"
            caught_time = caught_time + str(pre_time) + " seconds "
        if not caught_time:
            caught_time = "0.000 seconds (woah) "
        return caught_time
    except Exception:
        # if some of the above explodes just give up
        return "undefined amounts of time "

# Run the client which is an abstraction of calling the start coroutine.
client.run(TOKEN) 
