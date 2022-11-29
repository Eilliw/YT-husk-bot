from contextvars import Context
from http.server import executable
from pydoc import describe
import discord
from discord.ext import commands
import logging
import youtube_dl
import itertools
from scripts.music_player import MusicPlayer
from scripts.music_player import YTDLSource


ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn',
    'executable':'.ffmpeg-5.1.2-essentials_build//bin//'
}


class Audio_cmds(commands.Cog):
    
    __slots__ = ('bot', 'players')
    
    def __init__(self, bot):
        self.bot = bot
        self.playing = False
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass
    
    def get_player(self, ctx : commands.Context):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player
    
    
        
    async def audio_player_object(self,ctx):
        pass
    
    
    
    async def disconnect_(self,ctx : commands.Context):
        await ctx.voice_client.cleanup()
        await ctx.voice_client.disconnect()
        
    async def join_channel(self,ctx : commands.Context):
        voice_channel = ctx.author.voice.channel
        #await voice_channel.connect()
        in_vc = await self.vc_check(ctx)
        if not in_vc:
            channel = voice_channel.name
            vc = await voice_channel.connect()
        else:
            if ctx.author.voice.channel == ctx.voice_client.channel: #ctx.voice_client.channel:
                pass
            else:
                await self.disconnect_(ctx)
                channel = voice_channel.name
                vc = await voice_channel.connect()
            
    async def join_on_command(self,ctx : commands.Context):
        pass
    
    async def vc_check(self, ctx : commands.Context):
        '''
        checks if already in a vc
        returns true or false
        '''
        if ctx.voice_client != None:
            return True
        else:
            return False
    
    async def play_pause(self, ctx: commands.Context):
        if self.voice_check(ctx):
            pass
    
    # async def play_audio( self, link, ctx : commands.Context):
    #     vc = ctx.voice_client
    #     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            
    #         song_info = ydl.extract_info(str(link), download=False)
    #         #print(song_info)
            
    #         if '_type' in song_info.keys():
    #             if song_info['_type'] == 'playlist':
    #                 vc.play(discord.FFmpegPCMAudio(song_info["entries"][0]['formats'][0]["url"]))
    #                 vc.source = discord.PCMVolumeTransformer(vc.source)
    #                 vc.source.volume = 1
    #             elif song_info['type_'] == None:
    #                 pass
    #         else:
                    
    #             vc.play(discord.FFmpegPCMAudio(song_info["formats"][0]["url"]))
    #             vc.source = discord.PCMVolumeTransformer(vc.source)
    #             vc.source.volume = .5
        
    
    
    @commands.hybrid_command(name= 'play', with_app_command= True, description="play a youtube link")
    async def play(self,ctx :commands.Context ,query):
        #await ctx.defer(ephemeral=True)
        # player = await MusicPlayer(ctx)
        # url = query
        # await ctx.reply("queing"+url)
        

        if ctx.author.voice != None:
            
            voice_channel = ctx.author.voice.channel
            if voice_channel != None:
                
                await self.join_channel(ctx)
                
                player = self.get_player(ctx)

                # If download is False, source will be a dict which will be used later to regather the stream.
                # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
                source = await YTDLSource.create_source(ctx, query, loop=self.bot.loop, download=False)

                await player.queue.put(source)
                
                #await self.play_audio(url,ctx)
        
        else:
            await ctx.reply(str(ctx.author.name) + "is not in a channel.")
        
        


    @commands.hybrid_command(name='pause', with_app_command=True, description="pause player.")
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            embed = discord.Embed(title="", description="I am currently not playing anything", color=discord.Color.green())
            return await ctx.send(embed=embed)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send("Paused ⏸️")






    @commands.hybrid_command(name='resume',with_app_command=True , description="resumes music")
    async def resume(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send("Resuming ⏯️")



    @commands.hybrid_command(name='skip', description="skips to next song in queue")
    async def skip_(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send("skipped")



    
    
    
    @commands.hybrid_command(name='remove', aliases=['rm', 'rem'], description="removes specified song from queue")
    async def remove_(self, ctx, pos : int=None):
        """Removes specified song from queue"""

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        if pos == None:
            player.queue._queue.pop()
        else:
            try:
                s = player.queue._queue[pos-1]
                del player.queue._queue[pos-1]
                embed = discord.Embed(title="", description=f"Removed [{s['title']}]({s['webpage_url']}) [{s['requester'].mention}]", color=discord.Color.green())
                await ctx.send(embed=embed)
            except:
                embed = discord.Embed(title="", description=f'Could not find a track for "{pos}"', color=discord.Color.green())
                await ctx.send(embed=embed)
    
    
    @commands.hybrid_command(name='volume', description="sets the volume of the player")
    async def volume_(self, ctx, vol: int):
        """"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.reply(embed=embed)
        
        player = self.get_player(ctx)
        if vol <=100 and vol >=0:
            player.volume= vol/100
            print(player.volume)
            embed = discord.Embed(title="", description="volume set to "+str(vol), color=discord.Color.green())
            return await ctx.reply(embed=embed)
    
    
    @commands.hybrid_command(name='clear', aliases=['clr', 'cl', 'cr'], description="clears entire queue")
    async def clear_(self, ctx):
        """Deletes entire queue of upcoming songs."""

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        player.queue._queue.clear()
        return await ctx.send('💣 **Cleared**')
    
    
    
    @commands.hybrid_command(name='queue', aliases=['q', 'playlist', 'que'], description="shows the queue")
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        if player.queue.empty():
            embed = discord.Embed(title="", description="queue is empty", color=discord.Color.green())
            return await ctx.send(embed=embed)

        seconds = vc.source.duration % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        # Grabs the songs in the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, int(len(player.queue._queue))))
        fmt = '\n'.join(f"`{(upcoming.index(_)) + 1}.` [{_['title']}]({_['webpage_url']}) | ` {duration} Requested by: {_['requester']}`\n" for _ in upcoming)
        fmt = f"\n__Now Playing__:\n[{vc.source.title}]({vc.source.web_url}) | ` {duration} Requested by: {vc.source.requester}`\n\n__Up Next:__\n" + fmt + f"\n**{len(upcoming)} songs in queue**"
        embed = discord.Embed(title=f'Queue for {ctx.guild.name}', description=fmt, color=discord.Color.green())
        #old discord.py rewrite ctx.author.avatar_url now ctx.member.avatar
        #embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Audio_cmds(bot))
    print("| Audio_cmds |")