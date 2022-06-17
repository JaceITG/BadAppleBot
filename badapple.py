import discord, asyncio
import apple_secrets

import skvideo.io
import skvideo.utils


intents = discord.Intents.all()
client = discord.Client(intents=intents)
compressed = None

#Take pixel data from mp4 and grab every 10th frame
def decode_video():
    global compressed

    viddat = skvideo.io.vread("Data\\badappledownscale.mp4", as_grey=True)
    print(f"Parsed video with shape {viddat.shape}")

    print(f"Compressing to 1FPS")
    compressed = viddat[1::10]

#convert 32x42 frame of bad apple to string of emojis
def as_emojis(frame):
    #ndarray (32,42,1) frame

    out = []

    for r in frame:
        row = []
        for c in r:
            #grayscale value
            value = c
            row.append( '⚫' if value < 126 else '⚪' )
        out.append(row)
    
    #append to message string row by row
    message = ""
    for r in out:
        message += ''.join(r)
        message += '\n'

    return message
    

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

#edit a 60x33 array of emojis according to pixel information transcribed from Bad Apple
async def animate(messages):
    global compressed

    async def editpart(i):
        await messages[i].edit(content=str(frame[43*i*4:43*(i+1)*4]))

    fcount = 3

    #flush API Limit
    await asyncio.sleep(6)
    for f in compressed[3:]:
        print(f"Frame {fcount}", end='\r')

        frame = as_emojis(f)

        #Loop through the 8 message parts
        for i in range(8):

            #Pause on 2nd and 6th frames for API ratelimiting
            if i == 2 or i == 6:
                await asyncio.sleep(2.6)

            await editpart(i)
        
        fcount += 1

@client.event
async def on_message(msg):
    global compressed

    author = msg.author
    channel = msg.channel
    cnt = msg.content
    args = cnt.split(' ')

    #test for message editing, ratelimiting
    if args[0] == "$test":
        sent = await channel.send('⚪')

        for i in range(10):
            await asyncio.sleep(1)
            await sent.edit(content='⚫')
            await asyncio.sleep(1)
            await sent.edit(content='⚪')
        
    if args[0] == "$badapple" or args[0] == "$ba":
        
        #Print initial frame to grab message part objects
        frame = as_emojis(compressed[2])
        parts = []
        for i in range(8):
            parts.append(await channel.send(frame[43*i*4:43*(i+1)*4]))
        
        await animate(parts)



if __name__ == "__main__":
    print("Reformatting video...")
    decode_video()
    print("Starting bot")
    client.run(apple_secrets.TOKEN)