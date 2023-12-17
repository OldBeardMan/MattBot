import discord
from discord.ext import commands, tasks
import asyncio
import os
import forPlaylist
import random
from pointSystem import pointSystem

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='>', intents=intents)

playlist = forPlaylist.create('music')

cat_images_folder = 'cat_images'

point_system = pointSystem()

def get_random_cat_image():
    cat_images = [file for file in os.listdir(cat_images_folder) if file.endswith(('.png', '.jpg', '.jpeg'))]

    if cat_images:
        random_cat_image = random.choice(cat_images)
        return os.path.join(cat_images_folder, random_cat_image)
    else:
        return None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name='Matt Krupa'))
    channel_id = 1173158666174742538
    channel = bot.get_channel(channel_id)
    await channel.connect()
    print("Bot is ready.")
    background_music.start()

async def play_music():
    while playlist:
        file_path = playlist.pop(0)
        if os.path.isfile(file_path):
            channel = bot.voice_clients[0].channel
            voice_channel = discord.utils.get(bot.voice_clients, guild=channel.guild)

            print(f"Attempting to play: {file_path}")

            # Odtwarzaj utwór
            voice_channel.play(discord.FFmpegPCMAudio(file_path), after=lambda e: print('done', e))

            # Poczekaj do zakończenia odtwarzania aktualnego utworu
            while voice_channel.is_playing():
                await asyncio.sleep(1)

            # Po zakończeniu utworu, dodaj go z powrotem do playlisty
            playlist.append(file_path)

            # Odczekaj chwilę przed sprawdzeniem następnego utworu
            await asyncio.sleep(5)
        else:
            print(f"File not found: {file_path}")
            await asyncio.sleep(1)
            playlist.append(file_path)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return
    
    keyword_responses = {
        "kuna": "kuna",
        "matt": "If you want to know more about Matt check out: https://mattkrupa.net/",
        "sprytek": "It's me!"
    }

    for keyword, response in keyword_responses.items():
        if keyword in message.content:
            await message.channel.send(response)
            break


        
@tasks.loop(seconds=5)
async def background_music():
    # Sprawdź, czy bot jest w kanałach głosowych
    if not bot.voice_clients:
        print("Bot is not in a voice channel.")
        return

    print("Checking for music...")
    # Odtwarzaj muzykę
    await play_music()

@bot.command(name='reality')
async def reality(ctx):
    await ctx.send("Can you really enjoy reality anymore?")

@bot.command(name='sprytek')
async def sprytek(ctx):
    cat_image = get_random_cat_image()
    
    if cat_image:
        with open(cat_image, 'rb') as file:
            await ctx.send(file=discord.File(file))
    else:
        await ctx.send("Nie znaleziono żadnych zdjęć kota.")

@bot.command(name='quiz')
async def quiz(ctx):

    channel = ctx.channel
    channel_id = channel.id

    if channel_id != '1186017543924744192':
        await ctx.send("Piszesz na złym kanale! Przejdź na kanał 'quiz', aby nie spamić innym!")
        return
    
    author = ctx.author
    user_id = author.id
    point_system.add_user(user_id)

    question_id = random(0,1)

    if question_id == 0:
        question = "W którym roku się urodziłem?"
        answer = "2012"
    elif question_id == 1:
        question = "W którym roku Matt wydał swój pierwszy album?"
        answer = "2020"
    elif question_id == 2:
        question = "Kto założył instagrama Matt'a?"
        answer = "wool"


    await ctx.send(question)

    def check_answer(message):
        return message.author == author and message.channel == ctx.channel

    try:
        answer_message = await bot.wait_for('message', check=check_answer, timeout=10) 

        if answer_message.content == answer: 
            point_system.add_points(user_id, 1)
            await ctx.send("Poprawna odpowiedź! Zdobywasz 1 punkt.")
            await ctx.send(f"Masz aktualnie na koncie: {point_system.get_points(user_id)}")
        else:
            await ctx.send("Niestety, to nie jest poprawna odpowiedź.")

    except asyncio.TimeoutError:
        await ctx.send("Czas na odpowiedź minął.")

# Uruchom bota
bot.run('')