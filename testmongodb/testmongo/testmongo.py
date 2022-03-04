import os
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
#from pickle import TRUE
#from dns import _immutable_ctx

load_dotenv()
TOKEN = os.getenv('MONGOTEST')
#client = discord.Client()
cluster = MongoClient(os.getenv('MONGOCONNECT'))
db = cluster["UserData"]
collection = db["UserData"]
intents = discord.Intents().all()

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(ctx):
    # infinite loop prevention
    if ctx.author == bot.user:
        return
    if (str(ctx.content)[0] != '!'):
        buzzwords = ["python", "discord", "lego", "code"]
        words = str(ctx.content.lower()).split()
        for word in words:
            if word in buzzwords:
                await buzzwordSpotted(ctx, word)
    else:
        await bot.process_commands(ctx) # commands won't process without this, because I overrode on_message
    
                
async def buzzwordSpotted(ctx, word):
    myquery = { "discord_id": ctx.author.id, "word": word }
    if (collection.count_documents(myquery) == 0):
        post = {"discord_id": ctx.author.id, "word": word, "score": 1}
        collection.insert_one(post) 
        await ctx.channel.send(word + " added to database for " + str(ctx.author))
    else:
        query = {"discord_id": ctx.author.id, "word": word}
        user = collection.find(query)
        for result in user:
            score = result["score"]
        score = score + 1;
        collection.update_one({"discord_id":ctx.author.id, "word": word}, {"$set":{"score":score}})
        await ctx.channel.send(word + " score is " + str(score) + " for " + str(ctx.author))
            
@bot.command(name='reset', help='resets your score for a word')
async def resetscore(ctx, word):
    buzzwords = ["python", "discord", "lego", "code"]
    if word not in buzzwords:
        await ctx.channel.send(word + " is not one of the buzzwords.")
        return
    myquery = { "discord_id": ctx.author.id, "word": word}
    if (collection.count_documents(myquery) == 0):
        post = {"discord_id": ctx.author.id, "word": word, "score": 0}
        collection.insert_one(post)
        await ctx.channel.send(str(ctx.author) + " didn't have a score for " + word + " but it's zero now.")
    else:
        collection.update_one({"discord_id":ctx.author.id, "word": word}, {"$set": {"score":0}})
        await ctx.channel.send(word + " score set to zero for " + str(ctx.author))
        
@bot.command(name='get_score', help='gets the score for a user and a word')
async def getScore(ctx, username, word):
    user = ctx.guild.get_member_named(username)
    if user is None:
        await ctx.send("No user found with this name.")
        return 
    userid = user.id
    #displayname = user.name()
    myquery = {"discord_id": userid, "word": word }
    if collection.count_documents(myquery) == 0:
        await ctx.send("No entry for this this user and " + word)
        return 
    query = {"discord_id": userid, "word": word}
    user = collection.find(query)
    for result in user:
        score = result["score"]
    await ctx.send("this user has a score of " + str(score) + " for " + word) 
               
               
@bot.command(name='list_users', help='lists users test')
async def listusers(ctx):
    for m in ctx.guild.members:
        await ctx.send(m.name + m.discriminator)
               
               
@bot.command(name='get_userid', help='gets userid test')
async def getuser(ctx, username):
    member = ctx.guild.get_member_named(username)
    await ctx.send(member.id)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return 
    raise error

        
#client.run(TOKEN)
bot.run(TOKEN)
