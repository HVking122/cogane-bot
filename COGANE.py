import os
import discord
from discord.ext import commands, tasks
import aiohttp
import feedparser

# Intents 설정
intents = discord.Intents.default()
intents.message_content = True  # !테스트 명령어용
intents.members = True          # 입장/퇴장 이벤트 감지용
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== 설정 정보 ====================
YOUTUBE_DISCORD_CHANNEL_ID = 1559208476289404990  # 유튜브 알림용 채널 ID
CHZZK_DISCORD_CHANNEL_ID = 1559208487680999505    # 치지직 알림용 채널 ID
TWITTER_DISCORD_CHANNEL_ID = 1559208558296436857  # 트위터 알림용 채널 ID
WELCOME_DISCORD_CHANNEL_ID = 1559223499426365511   # 입장/퇴장 알림 채널 ID
AUTO_ROLE_ID = 1559210002458091743

# ==================== [수정] 플랫폼별 알림 역할 ID 각각 입력 ====================
YOUTUBE_ROLE_ID = 1559225819388448889  # 유튜브알림 역할 ID
CHZZK_ROLE_ID   = 1559225972723548231  # 치지직알림 역할 ID
TWITTER_ROLE_ID = 1559226052658593943  # 트윗알림 역할 ID

# (서버정보 등에 사용할 대표 역할 ID - 필요시 아무거나 지정)
ROLE_ID = 1559210002458091743

YOUTUBE_CHANNEL_ID = "UCQ6LlsI7Bbj2yhSqLMI1gGA"
CHZZK_HASH = "c657aa3592260a2b59669a72ec151936"
TWITTER_USER = "CoganeRang"

last_states = {
    "youtube_latest": None,
    "chzzk_live": False,
    "twitter_latest": None
}

@bot.event
async def on_ready():
    print(f'로그인 성공: {bot.user}')
    check_all_alerts.start()

# ==================== 입장 / 퇴장 이벤트 ====================
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_DISCORD_CHANNEL_ID)
    if channel:
        msg = f"👋 {member.mention} 님이 **코가네 랑** 서버에 오신 것을 환영합니다! 🎉"
        await channel.send(msg)

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(WELCOME_DISCORD_CHANNEL_ID)
    if channel:
        msg = f"👋 {member.display_name} 님이 서버를 떠나셨습니다."
        await channel.send(msg)

@bot.event
async def on_member_join(member):
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        await member.add_roles(role)

# ==================== [수정] 플랫폼별 맞춤 핑 테스트 명령어 ====================
@bot.command(name="테스트")
async def test_alert(ctx, platform: str = ""):
    platform = platform.lower()
    
    if platform == "유튜브" or platform == "yt":
        channel = bot.get_channel(YOUTUBE_DISCORD_CHANNEL_ID)
        if channel:
            ping_text = f"<@&{YOUTUBE_ROLE_ID}>"
            target_url = "https://www.youtube.com/@coganerang"
            await channel.send(content=f"{ping_text} 새 영상이 올라왔다구!\n{target_url}")
            await ctx.send("유튜브 테스트 알림을 보냈어!")
            
    elif platform == "치지직" or platform == "chzzk":
        channel = bot.get_channel(CHZZK_DISCORD_CHANNEL_ID)
        if channel:
            ping_text = f"<@&{CHZZK_ROLE_ID}>"
            target_url = f"https://chzzk.naver.com/live/{CHZZK_HASH}"
            await channel.send(content=f"{ping_text} 뱅온!\n{target_url}")
            await ctx.send("치지직 테스트 알림을 보냈어!")
            
    elif platform == "트위터" or platform == "twitter":
        channel = bot.get_channel(TWITTER_DISCORD_CHANNEL_ID)
        if channel:
            ping_text = f"<@&{TWITTER_ROLE_ID}>"
            target_url = "https://x.com/CoganeRang"
            await channel.send(content=f"{ping_text} 새 트윗이 올라왔어!\n{target_url}")
            await ctx.send("트위터 테스트 알림을 보냈어!")
    else:
        await ctx.send("사용법: `!테스트 유튜브`, `!테스트 치지직`, `!테스트 트위터` 중에서 입력해줘!")

# ==================== 서버 정보 명령어 ====================
@bot.command(name="서버정보")
async def server_info(ctx):
    embed = discord.Embed(
        title="✨ 코가네 랑 공식 팬 커뮤니티 서버 ✨",
        description=(
            "**코가네 랑** 님의 공식 디스코드 팬 서버에 오신 것을 환영합니다! 🎉\n"
            "쾌적하고 즐거운 커뮤니티 활동을 위해 아래 안내 사항을 확인해 주세요.\n\n"
            "──────────────────────────────"
        ),
        color=0xFFB6C1
    )
    
    embed.add_field(
        name="🔗 OFFICIAL LINKS",
        value=(
            "🔴 **YouTube** : [코가네 랑 유튜브](https://www.youtube.com/@coganerang)\n"
            "🟢 **Chzzk** : [코가네 랑 치지직](https://chzzk.naver.com/live/c657aa3592260a2b59669a72ec151936)\n"
            "🐦 **Twitter (X)** : [코가네 랑 트위터](https://x.com/CoganeRang)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📜 SERVER RULES",
        value=(
            "1. **상호 존중** : 타인에 대한 비방, 욕설, 과도한 친목은 자제해 주세요.\n"
            "2. **스포일러 방지** : 방송 및 콘텐츠 스포일러는 지정된 채널에서만!\n"
            "3. **주제에 맞는 채널 이용** : 각 채널의 목적에 맞는 글을 올려주세요."
        ),
        inline=False
    )
    
    embed.add_field(
        name="🔔 ROLE & NOTIFICATION",
        value=(
            f"알림 역할(<@&{YOUTUBE_ROLE_ID}>, <@&{CHZZK_ROLE_ID}>, <@&{TWITTER_ROLE_ID}>)을 선택하고 맞춤 알림을 받아보세요!"
        ),
        inline=False
    )
    
    embed.set_footer(text="코가네 랑 커뮤니티 • 오늘도 즐거운 하루 되세요!")
    
    await ctx.send(embed=embed)
    try:
        await ctx.message.delete()
    except:
        pass

# ==================== [수정] 주기적 체크 루프 (플랫폼별 맞춤 핑) ====================
@tasks.loop(minutes=2)
async def check_all_alerts():
    async with aiohttp.ClientSession() as session:
        
        # 1. 유튜브 체크
        try:
            yt_rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
            async with session.get(yt_rss_url) as resp:
                if resp.status == 200:
                    feed = feedparser.parse(await resp.text())
                    if feed.entries:
                        latest = feed.entries[0]
                        vid = latest.get("yt_videoid")
                        video_link = latest.get("link")
                        
                        if last_states["youtube_latest"] is None:
                            last_states["youtube_latest"] = vid
                        elif last_states["youtube_latest"] != vid:
                            last_states["youtube_latest"] = vid
                            channel = bot.get_channel(YOUTUBE_DISCORD_CHANNEL_ID)
                            if channel:
                                ping_text = f"<@&{YOUTUBE_ROLE_ID}>"
                                await channel.send(content=f"{ping_text} 새 영상이 올라왔다구!\n{video_link}")
        except Exception as e:
            print(f"유튜브 체크 에러: {e}")

        # 2. 치지직 체크
        try:
            chzzk_url = f"https://api.chzzk.naver.com/service/v1/channels/{CHZZK_HASH}/live-detail"
            headers = {"User-Agent": "Mozilla/5.0"}
            async with session.get(chzzk_url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data.get("content")
                    if content is not None:
                        status = content.get("status")
                        stream_url = f"https://chzzk.naver.com/live/{CHZZK_HASH}"
                        
                        if status == "OPEN" and not last_states["chzzk_live"]:
                            last_states["chzzk_live"] = True
                            channel = bot.get_channel(CHZZK_DISCORD_CHANNEL_ID)
                            if channel:
                                ping_text = f"<@&{CHZZK_ROLE_ID}>"
                                await channel.send(content=f"{ping_text} 뱅온!\n{stream_url}")
                        elif status == "CLOSE":
                            last_states["chzzk_live"] = False
        except Exception as e:
            print(f"치지직 체크 에러: {e}")

        # 3. 트위터 체크
        try:
            twitter_rss_url = f"https://rsshub.app/twitter/user/{TWITTER_USER}"
            headers = {"User-Agent": "Mozilla/5.0"}
            async with session.get(twitter_rss_url, headers=headers) as resp:
                if resp.status == 200:
                    feed = feedparser.parse(await resp.text())
                    if feed.entries:
                        latest_tweet = feed.entries[0]
                        tweet_id = latest_tweet.get("id") or latest_tweet.get("link")
                        tweet_link = latest_tweet.get("link")
                        
                        if last_states["twitter_latest"] is None:
                            last_states["twitter_latest"] = tweet_id
                        elif last_states["twitter_latest"] != tweet_id:
                            last_states["twitter_latest"] = tweet_id
                            channel = bot.get_channel(TWITTER_DISCORD_CHANNEL_ID)
                            if channel:
                                ping_text = f"<@&{TWITTER_ROLE_ID}>"
                                await channel.send(content=f"{ping_text} 새 트윗이 올라왔어!\n{tweet_link}")
        except Exception as e:
            print(f"트위터 체크 에러: {e}")

@check_all_alerts.before_loop
async def before_loop():
    await bot.wait_until_ready()

import os

from aiohttp import web

# Render 웹 서비스용 가짜 웹 서버 (잠자기 방지용)
async def handle(request):
    return web.Response(text="Cogane-Bot is running 24/7!")

app = web.Application()
app.router.add_get('/', handle)

async def start_web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

# 기존 on_ready 이벤트에 웹 서버 실행 추가
@bot.event
async def on_ready():
    print(f'로그인 성공: {bot.user}')
    await start_web_server()  # 웹 서버 구동 추가
    check_all_alerts.start()

# ==================== 반응 역할(이모지 역할) 시스템 ====================

# 이모지와 역할 ID를 매칭합니다 (유튜브, 치지직, 트위터)
ROLE_EMOJIS = {
    "🔴": YOUTUBE_ROLE_ID,  # 빨간색 동그라미 누르면 유튜브 역할
    "🟢": CHZZK_ROLE_ID,    # 초록색 동그라미 누르면 치지직 역할
    "🐦": TWITTER_ROLE_ID   # 파란새/트위터 이모지 누르면 트위터 역할
}

@bot.command(name="역할메시지")
@commands.has_permissions(administrator=True)
async def setup_reaction_roles(ctx):
    embed = discord.Embed(
        title="🔔 알림 역할 셀프 자판기",
        description=(
            "원하는 플랫폼의 이모지를 누르시면 알림 역할을 받으실 수 있습니다!\n\n"
            "🔴 **YouTube 알림 역할**\n"
            "🟢 **Chzzk 알림 역할**\n"
            "🐦 **Twitter (X) 알림 역할**\n\n"
            "(이모지를 다시 누르면 역할이 해제됩니다!)"
        ),
        color=0xFFB6C1
    )
    embed.set_footer(text="코가네 랑 팬 커뮤니티")
    
    msg = await ctx.send(embed=embed)
    
    # 사용할 이모지들을 메시지에 자동으로 반응(Reaction)으로 달아줍니다
    for emoji in ROLE_EMOJIS.keys():
        await msg.add_reaction(emoji)
        
    try:
        await ctx.message.delete()
    except:
        pass

# 사용자가 이모지를 추가(클릭)했을 때 역할 부여
@bot.event
async def on_raw_reaction_add(payload):
    # 봇이 누른 건 무시
    if payload.member.bot:
        return
        
    role_id = ROLE_EMOJIS.get(payload.emoji.name)
    if role_id:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(role_id)
        if role:
            await payload.member.add_roles(role)

# 사용자가 이모지를 취소(제거)했을 때 역할 회수
@bot.event
async def on_raw_reaction_remove(payload):
    role_id = ROLE_EMOJIS.get(payload.emoji.name)
    if role_id:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(role_id)
        if role:
            member = guild.get_member(payload.user_id)
            if member and not member.bot:
                await member.remove_roles(role)

# 맨 밑줄을 이렇게 변경 (토큰을 코드에 직접 적지 않고 환경 변수에서 가져옴)
bot.run(os.environ.get('DISCORD_TOKEN'))
