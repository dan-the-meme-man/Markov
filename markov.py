"""
markov.py
A Discord Bot by Dan DeGenaro
"""

import json
import random
import warnings

from discord import Activity
from discord.ext import commands

# make python hush
warnings.simplefilter("ignore")

# Discord stuff
with open('token.txt') as f:
    TOKEN = f.read() # token to connect to Discord API
link = "https://discord.com/api/oauth2/authorize?client_id=951690562694676500&permissions=67584&scope=bot" # share me
read_me = '**Commands**\n' # header for help message
command_prefix = "m!" # self-explanatory?
bot = commands.Bot(command_prefix=command_prefix) # everything is political
bot.remove_command('help') # needed for override

# Markov Model stuff
start_counts = dict() # bigram dictionary, counts of start words
counts = dict() # trigram dictionary, counts of trigrams
message_send_prob = 0 # probability of randomly sending a message
max_message_length = 0 # self-explanatory?

def write():
    # access dictionaries
    global start_counts
    global counts

    # save contents to file so Markov doesn't get amnesia
    with open('start_counts.json', 'w') as f:
        json.dump(start_counts, f)
    with open('counts.json', 'w') as f:
        json.dump(counts, f)

def gen_message(): # randomly generate a message

    message = ''

    length = random.randrange(1,max_message_length+1) # choose a random message length

    # kind of intensive, but necessary? flatten start dict
    bigrams = []
    bigram_counts = []
    for x in start_counts:
        for y in start_counts[x]:
            bigrams.append([x, y])
            bigram_counts.append(start_counts[x][y])
    
    # choose a random start sequence
    start = random.choices(bigrams, weights=bigram_counts)[0]
    message += start[0] + ' ' + start[1] + ' '
    for i in range(length): # then choose a bunch more until we hit the cap or something breaks
        try:
            next = random.choices(list(counts[start[0]][start[1]].keys()), weights=list(counts[start[0]][start[1]].values()))[0]
            message += next + ' '
            start = [start[1], next]
        except:
            break

    return message

def process_message(message):

    # access dictionaries
    global start_counts
    global counts

    words = str(message.content).split() # split message

    # include unigrams as start bigrams too!
    if len(words) == 1: words.append('')

    # count new start bigram - python should have a better way to do this :/
    if words[0] not in start_counts:
        start_counts[words[0]] = dict()
        start_counts[words[0]][words[1]] = 1
    elif words[1] not in start_counts[words[0]]:
        start_counts[words[0]][words[1]] = 1
    else:
        start_counts[words[0]][words[1]] += 1

    # count new trigrams and update counts - ugh
    for i in range(2, len(words)): # for each possible trigram
        trigram = words[i-2:i+1] # build trigram
        if trigram[0] not in counts:
            counts[trigram[0]] = dict()
            counts[trigram[0]][trigram[1]] = dict()
            counts[trigram[0]][trigram[1]][trigram[2]] = 1
        elif trigram[1] not in counts[trigram[0]]:
            counts[trigram[0]][trigram[1]] = dict()
            counts[trigram[0]][trigram[1]][trigram[2]] = 1
        elif trigram[2] not in counts[trigram[0]][trigram[1]]:
            counts[trigram[0]][trigram[1]][trigram[2]] = 1
        else:
            counts[trigram[0]][trigram[1]][trigram[2]] += 1

@bot.event
async def on_ready():

    # access dictionaries
    global start_counts
    global counts

    # load in dictionaries if they already exist to prevent explosive amnesia
    try:
        f = open('start_counts.json', 'r')
        start_counts = json.load(f)
        print('Loaded start_counts.json.')
    except: print('Coult not find start_counts.json. Starting fresh!')
    try:
        f = open('counts.json', 'r')
        counts = json.load(f)
        print('Loaded counts.json.')
    except: print('Coult not find counts.json. Starting fresh!')

    # cool political status
    await bot.change_presence(activity=Activity(name='Слава Україні!', type=2))

    # generate help file
    global read_me
    with open('README.md', 'r') as f:
        lines = f.readlines()[12:]
        for line in lines: read_me += line
    print('Generated help message.')

    # load in saved params
    global message_send_prob
    global max_message_length
    with open('params.txt', 'r') as f:
        lines = f.readlines()
        message_send_prob = float(lines[0])
        max_message_length = int(lines[1])
    print('Loaded params.')

    print("Logged in as " + bot.user.name + " /---/ " + str(bot.user.id))
    print('Done!')

@bot.event
async def on_message(message):

    # don't process bot's messages
    if message.author == bot.user: return
        
    # look for a command
    await bot.process_commands(message)

    # it was a command - don't process it!
    if str(message.content).startswith(command_prefix): return

    process_message(message)
    write() # save to file

    # the bot may randomly reply!
    if random.random() < message_send_prob:
        await message.channel.send(gen_message())

@bot.event
async def on_disconnect():
    write() # save to file
    print('Markov disconnected.')

@bot.command()
async def talk(ctx):
    try:
        await ctx.send(gen_message())
    except:
        await ctx.send('uh idk what to say yet, you guys need to talk more')

@bot.command()
@commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
async def msg_prob(ctx, arg=None):
    global message_send_prob
    global max_message_length
    if arg == None:
        await ctx.send(f'Markov\'s probability of replying is currently {message_send_prob * 100}%.\nSyntax: m!msg_prob <probability>')
        return
    try:
        arg = float(arg)
    except:
        await ctx.send(f'Argument must be a number between 0 and 100. Arguments outside this range will be interpreted as the closest number in the range.')
    if arg > 100:
        message_send_prob = 1
    elif arg < 0:
        message_send_prob = 0
    else:
        message_send_prob = arg / 100
    with open('params.txt', 'w') as f:
        f.write(str(message_send_prob) + '\n' + str(max_message_length))
    await ctx.send(f'Markov\'s probability of replying is now {message_send_prob * 100}%.')

@bot.command()
@commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
async def max_length(ctx, arg=None):
    global message_send_prob
    global max_message_length
    if arg == None:
        await ctx.send(f'Markov\'s maximum message length is currently {max_message_length}.\nSyntax: m!max_length <length>')
        return
    try:
        arg = abs(int(arg))
        max_message_length = abs(arg)
        with open('params.txt', 'w') as f:
            f.write(str(message_send_prob) + '\n' + str(max_message_length))
        await ctx.send(f'Markov\'s maximum message length is now {arg}.')
    except:
        await ctx.send(f'Argument must be a positive integer. Passing in other numbers will cause the absolute value of the decimal portion to be ignored.')

@bot.command()
@commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
async def read_hist(ctx, arg=None):
    if arg == None:
        await ctx.send(f'Read in chat history so Markov can learn.\nSyntax: m!read_hist <length>')
        return
    try:
        arg = abs(int(arg))
        await ctx.send(f'Reading the history of {ctx.channel.mention}...')
        messages = await ctx.history(limit=arg).flatten()
        for message in messages:
            if message.author == bot.user: continue # don't process bot's messages
            if str(message.content).startswith(command_prefix): continue # it was a command - don't process it!
            process_message(message) # process each message in the history otherwise
        await ctx.send('Done.')
        write() # write to file
        print('Successfully read some history.')
    except:
        await ctx.send(f'{arg} must be a positive integer. Passing in other numbers will use the absolute value and ignore the decimal portion.')
        print('Failed to read history.')

@bot.command()
async def get_link(ctx):
    await ctx.send(f'Add me to your server! You must have the Manage Server permission on your server. + {link}')

@bot.command()
@commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
async def shutdown(ctx):
    print('Shutting down.')
    await bot.close()

@bot.command()
async def help(ctx):
    await ctx.send(read_me)

bot.run(TOKEN)