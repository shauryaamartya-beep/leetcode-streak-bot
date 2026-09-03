import json
import urllib.request
from datetime import datetime, timezone, timedelta

USERNAME = "shauryaamartya2611"
TELEGRAM_TOKEN = "8959367898:AAH_B23OjPwMJEgsmZA3mt4c9-PUgTOY6OE"
CHAT_ID = "6286593551"

def send_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            print("Telegram alert sent successfully!")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def get_tier(solved_count):
    if solved_count < 50:
        return "🟤 BRONZE I", "Push for 50 problems to reach Silver!"
    elif solved_count < 150:
        return "⚪ SILVER II", "Keep grinding to reach Gold!"
    elif solved_count < 300:
        return "🟡 GOLD III", "Strong progress! Next target: Platinum."
    elif solved_count < 500:
        return "🟣 PLATINUM IV", "You are in the elite club! Push for Diamond."
    elif solved_count < 750:
        return "💎 DIAMOND V", "Mastery level coding! Master tier is close."
    elif solved_count < 1000:
        return "👑 MASTER VI", "Exceptional! Legend status is within reach."
    else:
        return "⚡ LEGENDARY VII", "God Tier Coder! 🚀"

def check_streak():
    url = "https://leetcode.com/graphql"
    query = """
    query userCombinedStats($username: String!) {
      matchedUser(username: $username) {
        profile {
          ranking
        }
        submitStats {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
      recentAcSubmissionList(username: $username, limit: 1) {
        title
        timestamp
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"username": USERNAME}}).encode("utf-8")
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://leetcode.com/{USERNAME}/"
    }
    
    req = urllib.request.Request(url, data=payload, headers=headers)

    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode("utf-8")).get("data", {})
            user_data = data.get("matchedUser")
            
            if not user_data:
                send_alert("⚠️ *LEETCODE ERROR*: User profile fetch nahi ho paya. Username check karo!")
                return

            # Stats extraction
            ranking = user_data.get("profile", {}).get("ranking", "N/A")
            ac_num = user_data.get("submitStats", {}).get("acSubmissionNum", [])
            
            total_solved = 0
            easy = 0
            medium = 0
            hard = 0
            
            for item in ac_num:
                if item["difficulty"] == "All":
                    total_solved = item["count"]
                elif item["difficulty"] == "Easy":
                    easy = item["count"]
                elif item["difficulty"] == "Medium":
                    medium = item["count"]
                elif item["difficulty"] == "Hard":
                    hard = item["count"]

            tier, tier_msg = get_tier(total_solved)
            submissions = data.get("recentAcSubmissionList", [])

            # Time calculation
            ist_offset = timedelta(hours=5, minutes=30)
            current_time = datetime.now(timezone.utc) + ist_offset

            has_solved_today = False
            last_solved_title = "None"

            if submissions:
                last_solved_title = submissions[0]["title"]
                latest_time = datetime.fromtimestamp(int(submissions[0]["timestamp"]), tz=timezone.utc) + ist_offset
                if latest_time.date() == current_time.date():
                    has_solved_today = True

            # Telegram Card Generation
            if has_solved_today:
                msg = (
                    f"🔥 *LEETCODE STREAK SAFE!* 🔥\n\n"
                    f"🎯 *Today's Solved:* `{last_solved_title}`\n\n"
                    f"🏆 *Current Tier:* `{tier}`\n"
                    f"🌍 *Global Rank:* `#{ranking:,}`\n"
                    f"📊 *Total Solved:* `{total_solved}` (🟢 `{easy}` | 🟡 `{medium}` | 🔴 `{hard}`)\n\n"
                    f"✨_{tier_msg}_"
                )
            else:
                msg = (
                    f"🚨 *STREAK AT RISK! STREAK TOOTNE WALI HAI!* 🚨\n\n"
                    f"⏰ *Time Remaining:* Aaj ka din khatam hone me bohot kam waqt bacha hai!\n"
                    f"📌 *Last Solved:* `{last_solved_title}`\n\n"
                    f"🏆 *Current Tier:* `{tier}`\n"
                    f"🌍 *Global Rank:* `#{ranking:,}`\n"
                    f"📊 *Total Solved:* `{total_solved}` (🟢 `{easy}` | 🟡 `{medium}` | 🔴 `{hard}`)\n\n"
                    f"💪 *Action Required:* Jaldi se kam se kam 1 Easy/Medium problem solve karo aur streak bachao!"
                )

            send_alert(msg)

    except Exception as e:
        send_alert(f"⚠️ *LEETCODE CHECKER ALERT*: Error checking stats! ({e})")

if __name__ == "__main__":
    check_streak()