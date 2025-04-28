# Nyx Builder 🔧


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.0%2B-blue.svg)](https://github.com/Rapptz/discord.py)

A powerful Discord bot that allows authorized users to build custom executable stubs with integrated Discord webhooks. Perfect for educational purposes and authorized security testing.

## ✨ Features

- **Custom Stub Building** - Create personalized Windows executables with integrated Discord webhooks
- **Role-Based Access Control** - Admin commands for managing user access to the builder
- **User Management** - Easily add or remove users from the access list
- **Blacklist System** - Prevent specific users from accessing the builder
- **Comprehensive Logging** - Track build history and user activity
- **Statistics Tracking** - View usage metrics and system activity
- **Secure Distribution** - Files delivered via DMs or GoFile for larger builds
- **Clean UI** - Beautiful embeds for all interactions

## 📋 Commands

### User Commands
| Command | Description |
|---------|-------------|
| `/build` | Opens a modal to build a custom executable with your webhook |
| `/stats` | View statistics about the build system |
| `/help` | Display help information about available commands |

### Admin Commands
| Command | Description |
|---------|-------------|
| `/build-access add @user` | Grant a user access to use the builder |
| `/build-access remove @user` | Remove a user's access to the builder |
| `/build-access list` | List all users with build access |
| `/blacklist @user [reason]` | Blacklist a user from using the builder |
| `/unblacklist @user` | Remove a user from the blacklist |
| `/build-logs [limit] [@user]` | View build logs with optional filters |
| `/clear-logs` | Clear all build logs from the system |

## 🚀 Setup Guide

### Prerequisites
- Python 3.8 or higher
- Discord Developer Account
- Discord Bot Token
- GoFile API Token (for large file uploads)

### Installation

1. **Install the repository**

2. **Create a .env file with the following variables**
   ```env
   TOKEN=your_discord_bot_token
   GUILD_ID=your_guild_id
   SUPER_ADMIN=your_user_id
   GOFILE_API_TOKEN=your_gofile_api_token
   DEBUG=false  # Set to true for verbose logging
   ```

3. **Create the source.py template file**
   This file will be used as a template for building the stubs, with %webhook% placeholder for the webhook URL.

4. **Start the bot**
   ```bash
   python main.py
   ```

## 🛠️ How It Works

1. **Authentication**: Only authorized users can access the build functionality
2. **Build Process**: 
   - User provides a webhook URL and desired filename
   - The bot compiles a Python script into an executable using PyInstaller
   - The webhook URL is embedded directly into the executable
3. **Distribution**:
   - For smaller files: Direct Discord DM delivery
   - For larger files: Upload to GoFile with a download link
4. **Logging**:
   - All builds are logged with user info, file details, and timestamps
   - Admins can review logs to monitor system usage

## 🔒 Security Features

- **Role-Based Access**: Only authorized users can build executables
- **Blacklist System**: Permanently block problematic users
- **DM Delivery**: Files are sent via private messages for confidentiality
- **Activity Logging**: All build requests are logged for admin review
- **Super Admin**: Special permissions reserved for the system owner

## 📊 Statistics System

The `/stats` command provides insights into:
- Total number of builds
- Unique users using the system
- Authorized and blacklisted user counts
- Daily build activity over the past week
- Server-specific metrics

## 🧩 Project Structure

```
discord-stub-builder/
├── main.py            # Main bot code
├── source.py          # Stub template
├── .env               # Environment variables
├── requirements.txt   # Dependencies
├── users/             # User data
│   ├── allowed.rsc    # Authorized users list
│   └── blacklisted.rsc # Blacklisted users list
└── logs/              # Build logs
    └── builds.json    # Build history
```

## TODO
- Add a stealer implemented into the source.py
- Create an easier way to setup the bot.
- Sleep.

## 📝 Notes for Developers

- The system uses PyInstaller to compile Python scripts into standalone executables
- Files are compiled with the --noconsole flag to hide terminal window
- User data is stored in simple text files for easy maintenance
- The build logs use JSON for structured data storage

## ⚠️ Important Notice

This tool is intended for **educational purposes** and **authorized security testing only**. Using this stub builder on systems without explicit permission may be illegal and unethical. Users are solely responsible for how they use the software created with this tool.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔄 Updates & Maintenance

- **Regular Updates**: Check back for new features and improvements
- **Bug Reports**: Please report any issues via GitHub issues
- **Feature Requests**: Open to suggestions for new functionality

---

<p align="center">
  Created with ❤️ for the Discord community
  <br>
  © 2025 rescore.lol
</p>
