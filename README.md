# markov.py

## A Discord Bot by Dan DeGenaro

`markov.py` employs a Markovian trigram model of natural language. Through Discord's API, markov.py can access chat messages, read them, and develop frequency counts of sequences of words of length three or fewer. It can then generate random messages of custom length based on these frequency counts, which will approximate the writing and style of the server's users.

This project is open-source, and just for fun. I built it to replace a beloved bot that my friends and I added to our Discord server. That bot has since shut down, and mine probably isn't as good, but I think it still functions pretty well!

I hope to maintain this project and update it regularly, probably with added features and optimizations. Enjoy!

### Add me to your server

<https://discord.com/api/oauth2/authorize?client_id=951690562694676500&permissions=67584&scope=bot>

### List of Commands

- `m!get_link` - Wanna add Markov to another server? Click this link (it's not a scam, promise.)
- `m!help` - Display this command list.
- `m!max_length <length>` - Censor Markov. He'll only be allowed to say up to `length` words at a time. Default 30.
- `m!msg_prob <probability>` - Censor Markov. He'll have a `probability` chance of replying to each message. I recommend keeping this low, as he can be quite annoying. Default 5% (~ every 20 messages).
- `m!read_hist <length>` - Let Markov bring up ancient history (well, the most recent `length` messages at least.)
- `m!shutdown` - Send Markov to bed.
- `m!talk` - See what Markov thinks about all this.
