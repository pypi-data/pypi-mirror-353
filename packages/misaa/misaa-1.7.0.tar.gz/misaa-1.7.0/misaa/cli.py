import argparse
import requests
import concurrent.futures

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

PLATFORMS = {
    "facebook": "https://www.facebook.com/{username}",
    "youtube": "https://www.youtube.com/{username}",
    "instagram": "https://instagram.com/{username}",
    "twitter": "https://twitter.com/{username}",
    "tiktok": "https://www.tiktok.com/@{username}",
    "linkedin": "https://www.linkedin.com/in/{username}",
    "snapchat": "https://www.snapchat.com/add/{username}",
    "reddit": "https://www.reddit.com/user/{username}",
    "pinterest": "https://www.pinterest.com/{username}",
    "tumblr": "https://{username}.tumblr.com",
    "discord": "https://discord.me/{username}",
    "twitch": "https://www.twitch.tv/{username}",
    "soundcloud": "https://soundcloud.com/{username}",
    "mix": "https://mix.com/{username}",
    "flickr": "https://www.flickr.com/people/{username}",
    "vimeo": "https://vimeo.com/{username}",
    "dailymotion": "https://www.dailymotion.com/{username}",
    "mastodon.social": "https://mastodon.social/@{username}",
    "bluesky": "https://bsky.app/profile/{username}.bsky.social",
    "gab": "https://gab.com/{username}",
    "minds": "https://www.minds.com/{username}",
    "steemit": "https://steemit.com/@{username}",
    "deviantart": "https://www.deviantart.com/{username}",
    "9gag": "https://9gag.com/u/{username}",
    "imgur": "https://imgur.com/user/{username}",
    "medium": "https://medium.com/@{username}",
    "substack": "https://{username}.substack.com",
    "goodreads": "https://www.goodreads.com/{username}",
    "letterboxd": "https://letterboxd.com/{username}",
    "wattpad": "https://www.wattpad.com/user/{username}",
    "myanimelist": "https://myanimelist.net/profile/{username}",
    "crunchyroll": "https://www.crunchyroll.com/user/{username}",
    "anime-planet": "https://www.anime-planet.com/users/{username}",
    "last.fm": "https://www.last.fm/user/{username}",
    "bandcamp": "https://bandcamp.com/{username}",
    "reverbnation": "https://www.reverbnation.com/{username}",
    "mixcloud": "https://www.mixcloud.com/{username}",
    "audiomack": "https://audiomack.com/{username}",
    "badoo": "https://badoo.com/profile/{username}",
    "tinder": "https://www.gotinder.com/@{username}",
    "bumble": "https://bumble.com/en/{username}",
    "okcupid": "https://www.okcupid.com/profile/{username}",
    "hinge": "https://hinge.co/{username}",
    "grindr": "https://grindr.com/{username}",
    "happn": "https://www.happn.com/en/{username}",
    "pof": "https://www.pof.com/viewprofile.aspx?username={username}",
    "zoosk": "https://www.zoosk.com/profile/{username}",
    "eharmony": "https://www.eharmony.com/member/{username}",
    "meetme": "https://www.meetme.com/{username}",
    "tagged": "https://www.tagged.com/{username}",
    "hi5": "https://www.hi5.com/{username}",
    "classmates": "https://www.classmates.com/people/{username}",
    "nextdoor": "https://nextdoor.com/profile/{username}",
    "xing": "https://www.xing.com/profile/{username}",
    "viadeo": "https://www.viadeo.com/en/profile/{username}",
    "researchgate": "https://www.researchgate.net/profile/{username}",
    "academia.edu": "https://independent.academia.edu/{username}",
    "behance": "https://www.behance.net/{username}",
    "dribbble": "https://dribbble.com/{username}",
    "artstation": "https://www.artstation.com/{username}",
    "500px": "https://500px.com/{username}",
    "unsplash": "https://unsplash.com/@{username}",
    "photobucket": "https://photobucket.com/user/{username}/profile",
    "imageshack": "https://imageshack.com/user/{username}",
    "kiwibox": "https://www.kiwibox.com/{username}",
    "ning": "https://{username}.ning.com",
    "cafemom": "https://www.cafemom.com/profile/{username}",
    "ravelry": "https://www.ravelry.com/people/{username}",
    "caringbridge": "https://www.caringbridge.org/public/{username}",
    "patientslikeme": "https://www.patientslikeme.com/members/{username}",
    "myheritage": "https://www.myheritage.com/site-family-tree/{username}",
    "geni": "https://www.geni.com/people/{username}",
    "ancestry": "https://www.ancestry.com/profile/{username}",
    "geneanet": "https://en.geneanet.org/profil/{username}",
    "wikitree": "https://www.wikitree.com/wiki/{username}",
    "foursquare": "https://foursquare.com/{username}",
    "swarm": "https://www.swarmapp.com/user/{username}",
    "yelp": "https://www.yelp.com/user_details?userid={username}",
    "tripadvisor": "https://www.tripadvisor.com/members/{username}",
    "couchsurfing": "https://www.couchsurfing.com/people/{username}",
    "travellerspoint": "https://www.travellerspoint.com/users/{username}/",
    "stackoverflow": "https://stackoverflow.com/users/{username}",
    "stackexchange": "https://stackexchange.com/users/{username}",
    "github": "https://github.com/{username}",
    "gitlab": "https://gitlab.com/{username}",
    "bitbucket": "https://bitbucket.org/{username}/",
    "sourceforge": "https://sourceforge.net/u/{username}/profile",
    "codepen": "https://codepen.io/{username}",
    "hackerrank": "https://www.hackerrank.com/{username}",
    "leetcode": "https://leetcode.com/{username}",
    "kaggle": "https://www.kaggle.com/{username}",
    "producthunt": "https://www.producthunt.com/@{username}",
    "indiehackers": "https://www.indiehackers.com/{username}",
    "angellist": "https://angel.co/u/{username}",
    "crunchbase": "https://www.crunchbase.com/person/{username}",
    "slideshare": "https://www.slideshare.net/{username}",
    "scribd": "https://www.scribd.com/{username}",
    "issuu": "https://issuu.com/{username}",
    "peertube": "https://peertube.social/accounts/{username}",
    "dlive": "https://dlive.tv/{username}",
    "periscope": "https://www.pscp.tv/{username}",
    "clubhouse": "https://www.clubhouse.com/@{username}",
    "medium": "https://medium.com/@{username}",
    "substack": "https://{username}.substack.com",
    "quora": "https://www.quora.com/profile/{username}",
    "baidu": "https://tieba.baidu.com/home/main?un={username}",
    "douban": "https://www.douban.com/people/{username}",
    "vkontakte": "https://vk.com/{username}",
    "okru": "https://ok.ru/{username}",
    "weibo": "https://weibo.com/{username}",
    "wechat": "https://www.wechat.com/en/{username}",
    "line": "https://line.me/R/ti/p/@{username}",
    "kakao": "https://open.kakao.com/o/{username}",
    "mixi": "https://mixi.jp/show_friend.pl?id={username}",
    "renren": "http://www.renren.com/{username}/profile",
    "zalo": "https://zalo.me/{username}",
    "meetup": "https://www.meetup.com/members/{username}/",
    "patreon": "https://www.patreon.com/{username}",
    "buymeacoffee": "https://www.buymeacoffee.com/{username}",
    "ko-fi": "https://ko-fi.com/{username}",
    "pixiv": "https://www.pixiv.net/en/users/{username}",
    "newgrounds": "https://{username}.newgrounds.com",
    "itchio": "https://{username}.itch.io",
    "roblox": "https://www.roblox.com/user.aspx?username={username}",
    "steam": "https://steamcommunity.com/id/{username}",
    "epicgames": "https://www.epicgames.com/id/{username}",
    "origin": "https://www.origin.com/{username}",
    "battle.net": "https://battle.net/{username}",
    "fortnite": "https://fortnitetracker.com/profile/all/{username}",
    "pubg": "https://pubg.op.gg/user/{username}",
    "chess.com": "https://www.chess.com/member/{username}",
    "lichess": "https://lichess.org/@/{username}",
    "pokerstars": "https://www.pokerstars.com/en/players/{username}/",
    "strava": "https://www.strava.com/athletes/{username}",
    "fitbit": "https://www.fitbit.com/user/{username}",
    "untappd": "https://untappd.com/user/{username}",
    "anilist": "https://anilist.co/user/{username}/",
    "mydramalist": "https://mydramalist.com/profile/{username}",
    "fanfiction.net": "https://www.fanfiction.net/u/{username}/",
    "archiveofourown": "https://archiveofourown.org/users/{username}/profile",
    "quizlet": "https://quizlet.com/{username}",
    "duolingo": "https://www.duolingo.com/profile/{username}",
    "memrise": "https://www.memrise.com/user/{username}/",
    "codewars": "https://www.codewars.com/users/{username}",
    "replit": "https://replit.com/@{username}",
    "dev.to": "https://dev.to/{username}",
    "hashnode": "https://hashnode.com/@{username}",
    "notion": "https://www.notion.so/{username}",
    "slack": "https://{username}.slack.com",
    "trello": "https://trello.com/{username}",
    "asana": "https://app.asana.com/0/{username}/list",
}

def check_platform(args):
    name, url_template, username = args
    url = url_template.format(username=username)
    try:
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            return (name, url, True)
        else:
            return (name, url, False)
    except Exception:
        return (name, url, False)

def search_username(username):
    found = 0
    not_found = 0
    print(f"*******************")
    print(f"       {username}")
    print(f"*******************\n")
    args_list = [(name, url_template, username) for name, url_template in PLATFORMS.items()]
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        results = executor.map(check_platform, args_list)
        for name, url, exists in results:
            if exists:
                print(f"{GREEN}[+] {name} : {url}{RESET}")
                found += 1
            else:
                print(f"{RED}[-] {name} : Aucun résultat{RESET}")
                not_found += 1
    print()
    print(f"*******************")
    print(f"{GREEN}[+] {found} Résultat{'s' if found != 1 else ''} trouvé{'s' if found != 1 else ''}{RESET}")
    print(f"{RED}[-] {not_found} Aucun résultat{'' if not_found == 1 else 's'}{RESET}")
    print(f"*******************")

def main():
    parser = argparse.ArgumentParser(description="Recherche OSINT par pseudo")
    parser.add_argument("username", help="Nom d'utilisateur à rechercher")
    args = parser.parse_args()
    search_username(args.username)
