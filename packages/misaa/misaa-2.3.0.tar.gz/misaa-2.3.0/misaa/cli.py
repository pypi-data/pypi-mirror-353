import argparse
import requests
import concurrent.futures

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

PLATFORMS = {
    "500px": "https://500px.com/{username}",
    "9gag": "https://9gag.com/u/{username}",
    "academia.edu": "https://independent.academia.edu/{username}",
    "airbnb": "https://www.airbnb.com/users/show/{username}",
    "aliexpress": "https://www.aliexpress.com/store/{username}",
    "allocine": "https://www.allocine.fr/membre/{username}",
    "amazon": "https://www.amazon.com/gp/profile/{username}",
    "anilist": "https://anilist.co/user/{username}/",
    "anime-planet": "https://www.anime-planet.com/users/{username}",
    "ancestry": "https://www.ancestry.com/profile/{username}",
    "angellist": "https://angel.co/u/{username}",
    "archiveofourown": "https://archiveofourown.org/users/{username}/profile",
    "artstation": "https://www.artstation.com/{username}",
    "asana": "https://app.asana.com/0/{username}/list",
    "audiomack": "https://audiomack.com/{username}",
    "badoo": "https://badoo.com/profile/{username}",
    "baidu": "https://tieba.baidu.com/home/main?un={username}",
    "bandcamp": "https://bandcamp.com/{username}",
    "battle.net": "https://battle.net/{username}",
    "behance": "https://www.behance.net/{username}",
    "betaseries": "https://www.betaseries.com/user/{username}",
    "bitbucket": "https://bitbucket.org/{username}/",
    "blablacar": "https://www.blablacar.fr/member/{username}",
    "bluesky": "https://bsky.app/profile/{username}.bsky.social",
    "buymeacoffee": "https://www.buymeacoffee.com/{username}",
    "cafemom": "https://www.cafemom.com/profile/{username}",
    "caringbridge": "https://www.caringbridge.org/public/{username}",
    "chess.com": "https://www.chess.com/member/{username}",
    "classmates": "https://www.classmates.com/people/{username}",
    "clubhouse": "https://www.clubhouse.com/@{username}",
    "codepen": "https://codepen.io/{username}",
    "codewars": "https://www.codewars.com/users/{username}",
    "couchsurfing": "https://www.couchsurfing.com/people/{username}",
    "crunchbase": "https://www.crunchbase.com/person/{username}",
    "crunchyroll": "https://www.crunchyroll.com/user/{username}",
    "dailymotion": "https://www.dailymotion.com/{username}",
    "deezer": "https://www.deezer.com/profile/{username}",
    "deviantart": "https://www.deviantart.com/{username}",
    "discord": "https://discord.me/{username}",
    "dlive": "https://dlive.tv/{username}",
    "doctissimo": "https://forum.doctissimo.fr/profil-{username}.htm",
    "douban": "https://www.douban.com/people/{username}",
    "dribbble": "https://dribbble.com/{username}",
    "duolingo": "https://www.duolingo.com/profile/{username}",
    "ebay": "https://www.ebay.com/usr/{username}",
    "eharmony": "https://www.eharmony.com/member/{username}",
    "epicgames": "https://www.epicgames.com/id/{username}",
    "fanfiction.net": "https://www.fanfiction.net/u/{username}/",
    "facebook": "https://www.facebook.com/{username}",
    "fitbit": "https://www.fitbit.com/user/{username}",
    "flickr": "https://www.flickr.com/people/{username}",
    "fortnite": "https://fortnitetracker.com/profile/all/{username}",
    "foursquare": "https://foursquare.com/{username}",
    "francetvinfo": "https://www.francetvinfo.fr/{username}",
    "gab": "https://gab.com/{username}",
    "geneanet": "https://en.geneanet.org/profil/{username}",
    "geni": "https://www.geni.com/people/{username}",
    "gettr": "https://gettr.com/user/{username}",
    "github": "https://github.com/{username}",
    "gitlab": "https://gitlab.com/{username}",
    "goodreads": "https://www.goodreads.com/{username}",
    "grindr": "https://grindr.com/{username}",
    "habbo": "https://www.habbo.fr/profile/{username}",
    "hackerrank": "https://www.hackerrank.com/{username}",
    "happn": "https://www.happn.com/en/{username}",
    "hi5": "https://www.hi5.com/{username}",
    "hinge": "https://hinge.co/{username}",
    "imageshack": "https://imageshack.com/user/{username}",
    "imgur": "https://imgur.com/user/{username}",
    "indiehackers": "https://www.indiehackers.com/{username}",
    "instagram": "https://instagram.com/{username}",
    "itchio": "https://{username}.itch.io",
    "issuu": "https://issuu.com/{username}",
    "jeuxvideo.com": "https://www.jeuxvideo.com/profil/{username}?mode=infos",
    "kaggle": "https://www.kaggle.com/{username}",
    "kakao": "https://open.kakao.com/o/{username}",
    "kiwibox": "https://www.kiwibox.com/{username}",
    "ko-fi": "https://ko-fi.com/{username}",
    "last.fm": "https://www.last.fm/user/{username}",
    "leetcode": "https://leetcode.com/{username}",
    "letterboxd": "https://letterboxd.com/{username}",
    "lichess": "https://lichess.org/@/{username}",
    "linkedin": "https://www.linkedin.com/in/{username}",
    "line": "https://line.me/R/ti/p/@{username}",
    "mastodon.social": "https://mastodon.social/@{username}",
    "meetme": "https://www.meetme.com/{username}",
    "meetup": "https://www.meetup.com/members/{username}/",
    "memrise": "https://www.memrise.com/user/{username}/",
    "medium": "https://medium.com/@{username}",
    "minds": "https://www.minds.com/{username}",
    "mix": "https://mix.com/{username}",
    "mixcloud": "https://www.mixcloud.com/{username}",
    "mixi": "https://mixi.jp/show_friend.pl?id={username}",
    "myanimelist": "https://myanimelist.net/profile/{username}",
    "mydramalist": "https://mydramalist.com/profile/{username}",
    "myheritage": "https://www.myheritage.com/site-family-tree/{username}",
    "newgrounds": "https://{username}.newgrounds.com",
    "nextdoor": "https://nextdoor.com/profile/{username}",
    "ning": "https://{username}.ning.com",
    "notion": "https://www.notion.so/{username}",
    "okcupid": "https://www.okcupid.com/profile/{username}",
    "okru": "https://ok.ru/{username}",
    "origin": "https://www.origin.com/{username}",
    "patreon": "https://www.patreon.com/{username}",
    "patientslikeme": "https://www.patientslikeme.com/members/{username}",
    "peertube": "https://peertube.social/accounts/{username}",
    "periscope": "https://www.pscp.tv/{username}",
    "photobucket": "https://photobucket.com/user/{username}/profile",
    "pixiv": "https://www.pixiv.net/en/users/{username}",
    "pinterest": "https://www.pinterest.com/{username}",
    "pof": "https://www.pof.com/viewprofile.aspx?username={username}",
    "pokerstars": "https://www.pokerstars.com/en/players/{username}/",
    "producthunt": "https://www.producthunt.com/@{username}",
    "pubg": "https://pubg.op.gg/user/{username}",
    "quora": "https://www.quora.com/profile/{username}",
    "quizlet": "https://quizlet.com/{username}",
    "ravelry": "https://www.ravelry.com/people/{username}",
    "reddit": "https://www.reddit.com/user/{username}",
    "renren": "http://www.renren.com/{username}/profile",
    "researchgate": "https://www.researchgate.net/profile/{username}",
    "replit": "https://replit.com/@{username}",
    "reverbnation": "https://www.reverbnation.com/{username}",
    "roblox": "https://www.roblox.com/user.aspx?username={username}",
    "scoop.it": "https://www.scoop.it/u/{username}",
    "scribd": "https://www.scribd.com/{username}",
    "slack": "https://{username}.slack.com",
    "slideshare": "https://www.slideshare.net/{username}",
    "snapchat": "https://www.snapchat.com/add/{username}",
    "societe.com": "https://www.societe.com/societe/{username}.html",
    "soundcloud": "https://soundcloud.com/{username}",
    "sourceforge": "https://sourceforge.net/u/{username}/profile",
    "stackexchange": "https://stackexchange.com/users/{username}",
    "stackoverflow": "https://stackoverflow.com/users/{username}",
    "steam": "https://steamcommunity.com/id/{username}",
    "steemit": "https://steemit.com/@{username}",
    "strava": "https://www.strava.com/athletes/{username}",
    "substack": "https://{username}.substack.com",
    "swarm": "https://www.swarmapp.com/user/{username}",
    "tagged": "https://www.tagged.com/{username}",
    "telegram": "https://t.me/{username}",
    "tiktok": "https://www.tiktok.com/@{username}",
    "tinder": "https://www.gotinder.com/@{username}",
    "trello": "https://trello.com/{username}",
    "tripadvisor": "https://www.tripadvisor.com/members/{username}",
    "tumblr": "https://{username}.tumblr.com",
    "twitch": "https://www.twitch.tv/{username}",
    "twitter": "https://twitter.com/{username}",
    "untappd": "https://untappd.com/user/{username}",
    "unsplash": "https://unsplash.com/@{username}",
    "viadeo": "https://www.viadeo.com/en/profile/{username}",
    "vimeo": "https://vimeo.com/{username}",
    "vk": "https://vk.com/{username}",
    "wattpad": "https://www.wattpad.com/user/{username}",
    "weibo": "https://weibo.com/{username}",
    "wechat": "https://www.wechat.com/en/{username}",
    "wikipedia": "https://fr.wikipedia.org/wiki/Utilisateur:{username}",
    "wikitree": "https://www.wikitree.com/wiki/{username}",
    "xing": "https://www.xing.com/profile/{username}",
    "yelp": "https://www.yelp.com/user_details?userid={username}",
    "youtube": "https://www.youtube.com/{username}",
    "zalo": "https://zalo.me/{username}",
    "zoosk": "https://www.zoosk.com/profile/{username}"

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
