import json
import random
import warnings
from discord import Activity
from discord.ext import commands

warnings.simplefilter("ignore")

start_bigrams_seen = 0
start_counts = dict() # bigram dictionary, counts of start words

trigrams_seen = 0
counts = dict() # trigram dictionary, counts of trigrams

TOKEN = ""
link = "https://discord.com/api/oauth2/authorize?client_id=951690562694676500&permissions=67584&scope=bot"
read_me = '**Commands**\n'
command_prefix = "m!"
message_send_prob = 0.05
max_message_length = 30

bot = commands.Bot(command_prefix=command_prefix, status='Cлава Україні!')
bot.remove_command('help')

def write():
    # access dictionaries
    global start_counts
    global counts
    with open('start_counts.json', 'w') as f:
        json.dump(start_counts, f)
    with open('counts.json', 'w') as f:
        json.dump(counts, f)

def gen_message():

    message = ''

    length = random.randrange(1,max_message_length+1) # choose a random message length

    bigrams = []
    bigram_counts = []

    for x in start_counts:
        for y in start_counts[x]:
            bigrams.append([x, y])
            bigram_counts.append(start_counts[x][y])
    
    start = random.choices(bigrams, weights=bigram_counts)[0]
    message += start[0] + ' ' + start[1] + ' '
    for i in range(length):
        try:
            next = random.choices(list(counts[start[0]][start[1]].keys()), weights=list(counts[start[0]][start[1]].values()))[0]
            message += next + ' '
            start = [start[1], next]
        except:
            break

    return message

def process_message(message):

    global start_bigrams_seen
    global start_counts

    global trigrams_seen
    global counts

    words = str(message.content).split() # split message

    # include unigrams as start bigrams too!
    if len(words) == 1: words.append('')

    # count new start bigram
    if words[0] not in start_counts:
        start_counts[words[0]] = dict()
        start_counts[words[0]][words[1]] = 1
    elif words[1] not in start_counts[words[0]]:
        start_counts[words[0]][words[1]] = 1
    else:
        start_counts[words[0]][words[1]] += 1
    start_bigrams_seen += 1

    # count new trigrams and update counts
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
        trigrams_seen += 1

@bot.event
async def on_ready():

    # access dictionaries
    global start_counts
    global counts
    try:
        f = open('start_counts.json', 'r')
        start_counts = json.load(f)
        print('Found and loaded start_counts.json.')
    except:
        print('Coult not find start_counts.json. Starting fresh!')
    try:
        f = open('counts.json', 'r')
        counts = json.load(f)
        print('Found and loaded counts.json.')
    except:
        print('Coult not find counts.json. Starting fresh!')

    await bot.change_presence(activity=Activity(name='Слава Україні!', type=2))

    global read_me
    lines = open('README.md').readlines()[12:]
    for line in lines:
        read_me += line

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
    print('Connection interrupted. Markov disconnected.')

@bot.command()
async def talk(ctx):
    await ctx.send(gen_message())

@bot.command()
async def msg_prob(ctx, arg=None):
    global message_send_prob
    if arg == None:
        await ctx.send(f'Markov\'s probability of replying is currently {message_send_prob}.\nSyntax: m!msg_prob <probability>')
        return
    try:
        arg = abs(float(arg)) % 100.0
        message_send_prob = abs(arg) / 100.0
        await ctx.send(f'Markov\'s probability of replying is now {arg}.')
    except:
        await ctx.send(f'Argument must be a number between 0 and 100. Passing in other numbers will cause the absolute value of the decimal portion to be used.')

@bot.command()
async def max_length(ctx, arg=None):
    global max_message_length
    if arg == None:
        await ctx.send(f'Markov\'s maximum message length is currently {max_message_length}.\nSyntax: m!max_length <length>')
        return
    try:
        arg = abs(int(arg))
        max_message_length = abs(arg)
        await ctx.send(f'Markov\'s maximum message length is now {arg}.')
    except:
        await ctx.send(f'Argument must be a positive integer. Passing in other numbers will cause the absolute value of the decimal portion to be ignored.')

@bot.command()
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
    except:
        await ctx.send(f'{arg} must be a positive integer. Passing in other numbers will use the absolute value and ignore the decimal portion.')

@bot.command()
async def get_link(ctx):
    await ctx.send(f'Add me to your server! You must have the Manage Server permission on your server.')

@bot.command()
async def shutdown():
    write()
    exit(0)

@bot.command()
async def help(ctx):
    await ctx.send(read_me)

bot.run(TOKEN)
