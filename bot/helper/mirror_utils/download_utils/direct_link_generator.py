#!/usr/bin/env python3
from threading import Thread
from base64 import b64decode
from json import loads
from os import path
from uuid import uuid4
from hashlib import sha256
from time import sleep
from re import findall, match, search

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from lxml.etree import HTML
from requests import Session, session as req_session, post, get
from urllib.parse import parse_qs, quote, unquote, urlparse, urljoin
from cloudscraper import create_scraper
from lk21 import Bypass
from http.cookiejar import MozillaCookieJar

from bot import LOGGER, config_dict
from bot.helper.ext_utils.bot_utils import (
    get_readable_time,
    is_share_link,
    is_index_link,
    is_magnet,
)
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from bot.helper.ext_utils.help_messages import PASSWORD_ERROR_MESSAGE

_caches = {}
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"

FMED_DOMAINS = [
    "fembed.net",
    "fembed.com",
    "femax20.com",
    "fcdn.stream",
    "feurl.com",
    "layarkacaxxi.icu",
    "naniplay.nanime.in",
    "naniplay.nanime.biz",
    "naniplay.com",
    "mm9842.com",
]

ANONFILES_DOMAINS = [
    "anonfiles.com",
    "hotfile.io",
    "bayfiles.com",
    "megaupload.nz",
    "letsupload.cc",
    "filechan.org",
    "myfile.is",
    "vshare.is",
    "rapidshare.nu",
    "lolabits.se",
    "openload.cc",
    "share-online.is",
    "upvid.cc",
]

DEBRID_SITES = [
    "1fichier.com",
    "2shared.com",
    "4shared.com",
    "alfafile.net",
    "anzfile.net",
    "backin.net",
    "bayfiles.com",
    "bdupload.in",
    "brupload.net",
    "btafile.com",
    "catshare.net",
    "clicknupload.me",
    "clipwatching.com",
    "cosmobox.org",
    "dailymotion.com",
    "dailyuploads.net",
    "daofile.com",
    "datafilehost.com",
    "ddownload.com",
    "depositfiles.com",
    "dl.free.fr",
    "douploads.net",
    "drop.download",
    "earn4files.com",
    "easybytez.com",
    "ex-load.com",
    "extmatrix.com",
    "down.fast-down.com",
    "fastclick.to",
    "faststore.org",
    "file.al",
    "file4safe.com",
    "fboom.me",
    "filefactory.com",
    "filefox.cc",
    "filenext.com",
    "filer.net",
    "filerio.in",
    "filesabc.com",
    "filespace.com",
    "file-up.org",
    "fileupload.pw",
    "filezip.cc",
    "fireget.com",
    "flashbit.cc",
    "flashx.tv",
    "florenfile.com",
    "fshare.vn",
    "gigapeta.com",
    "goloady.com",
    "docs.google.com",
    "gounlimited.to",
    "heroupload.com",
    "hexupload.net",
    "hitfile.net",
    "hotlink.cc",
    "hulkshare.com",
    "icerbox.com",
    "inclouddrive.com",
    "isra.cloud",
    "katfile.com",
    "keep2share.cc",
    "letsupload.cc",
    "load.to",
    "down.mdiaload.com",
    "mediafire.com",
    "mega.co.nz",
    "mixdrop.co",
    "mixloads.com",
    "mp4upload.com",
    "nelion.me",
    "ninjastream.to",
    "nitroflare.com",
    "nowvideo.club",
    "oboom.com",
    "prefiles.com",
    "sky.fm",
    "rapidgator.net",
    "rapidrar.com",
    "rapidu.net",
    "rarefile.net",
    "real-debrid.com",
    "redbunker.net",
    "redtube.com",
    "rockfile.eu",
    "rutube.ru",
    "scribd.com",
    "sendit.cloud",
    "sendspace.com",
    "simfileshare.net",
    "solidfiles.com",
    "soundcloud.com",
    "speed-down.org",
    "streamon.to",
    "streamtape.com",
    "takefile.link",
    "tezfiles.com",
    "thevideo.me",
    "turbobit.net",
    "tusfiles.com",
    "ubiqfile.com",
    "uloz.to",
    "unibytes.com",
    "uploadbox.io",
    "uploadboy.com",
    "uploadc.com",
    "uploaded.net",
    "uploadev.org",
    "uploadgig.com",
    "uploadrar.com",
    "uppit.com",
    "upstore.net",
    "upstream.to",
    "uptobox.com",
    "userscloud.com",
    "usersdrive.com",
    "vidcloud.ru",
    "videobin.co",
    "vidlox.tv",
    "vidoza.net",
    "vimeo.com",
    "vivo.sx",
    "vk.com",
    "voe.sx",
    "wdupload.com",
    "wipfiles.net",
    "world-files.com",
    "worldbytez.com",
    "wupfile.com",
    "wushare.com",
    "xubster.com",
    "youporn.com",
    "youtube.com",
]

DEBRID_LINK_SITES = [
    "1dl.net",
    "1fichier.com",
    "alterupload.com",
    "cjoint.net",
    "desfichiers.com",
    "dfichiers.com",
    "megadl.org",
    "megadl.fr",
    "mesfichiers.fr",
    "mesfichiers.org",
    "piecejointe.net",
    "pjointe.com",
    "tenvoi.com",
    "dl4free.com",
    "apkadmin.com",
    "bayfiles.com",
    "clicknupload.link",
    "clicknupload.org",
    "clicknupload.co",
    "clicknupload.cc",
    "clicknupload.link",
    "clicknupload.download",
    "clicknupload.club",
    "clickndownload.org",
    "ddl.to",
    "ddownload.com",
    "depositfiles.com",
    "dfile.eu",
    "dropapk.to",
    "drop.download",
    "dropbox.com",
    "easybytez.com",
    "easybytez.eu",
    "easybytez.me",
    "elitefile.net",
    "elfile.net",
    "wdupload.com",
    "emload.com",
    "fastfile.cc",
    "fembed.com",
    "feurl.com",
    "anime789.com",
    "24hd.club",
    "vcdn.io",
    "sharinglink.club",
    "votrefiles.club",
    "there.to",
    "femoload.xyz",
    "dailyplanet.pw",
    "jplayer.net",
    "xstreamcdn.com",
    "gcloud.live",
    "vcdnplay.com",
    "vidohd.com",
    "vidsource.me",
    "votrefile.xyz",
    "zidiplay.com",
    "fcdn.stream",
    "femax20.com",
    "sexhd.co",
    "mediashore.org",
    "viplayer.cc",
    "dutrag.com",
    "mrdhan.com",
    "embedsito.com",
    "diasfem.com",
    "superplayxyz.club",
    "albavido.xyz",
    "ncdnstm.com",
    "fembed-hd.com",
    "moviemaniac.org",
    "suzihaza.com",
    "fembed9hd.com",
    "vanfem.com",
    "fikper.com",
    "file.al",
    "fileaxa.com",
    "filecat.net",
    "filedot.xyz",
    "filedot.to",
    "filefactory.com",
    "filenext.com",
    "filer.net",
    "filerice.com",
    "filesfly.cc",
    "filespace.com",
    "filestore.me",
    "flashbit.cc",
    "dl.free.fr",
    "transfert.free.fr",
    "free.fr",
    "gigapeta.com",
    "gofile.io",
    "highload.to",
    "hitfile.net",
    "hitf.cc",
    "hulkshare.com",
    "icerbox.com",
    "isra.cloud",
    "goloady.com",
    "jumploads.com",
    "katfile.com",
    "k2s.cc",
    "keep2share.com",
    "keep2share.cc",
    "kshared.com",
    "load.to",
    "mediafile.cc",
    "mediafire.com",
    "mega.nz",
    "mega.co.nz",
    "mexa.sh",
    "mexashare.com",
    "mx-sh.net",
    "mixdrop.co",
    "mixdrop.to",
    "mixdrop.club",
    "mixdrop.sx",
    "modsbase.com",
    "nelion.me",
    "nitroflare.com",
    "nitro.download",
    "e.pcloud.link",
    "pixeldrain.com",
    "prefiles.com",
    "rg.to",
    "rapidgator.net",
    "rapidgator.asia",
    "scribd.com",
    "sendspace.com",
    "sharemods.com",
    "soundcloud.com",
    "noregx.debrid.link",
    "streamlare.com",
    "slmaxed.com",
    "sltube.org",
    "slwatch.co",
    "streamtape.com",
    "subyshare.com",
    "supervideo.tv",
    "terabox.com",
    "tezfiles.com",
    "turbobit.net",
    "turbobit.cc",
    "turbobit.pw",
    "turbobit.online",
    "turbobit.ru",
    "turbobit.live",
    "turbo.to",
    "turb.to",
    "turb.cc",
    "turbabit.com",
    "trubobit.com",
    "turb.pw",
    "turboblt.co",
    "turboget.net",
    "ubiqfile.com",
    "ulozto.net",
    "uloz.to",
    "zachowajto.pl",
    "ulozto.cz",
    "ulozto.sk",
    "upload-4ever.com",
    "up-4ever.com",
    "up-4ever.net",
    "uptobox.com",
    "uptostream.com",
    "uptobox.fr",
    "uptostream.fr",
    "uptobox.eu",
    "uptostream.eu",
    "uptobox.link",
    "uptostream.link",
    "upvid.pro",
    "upvid.live",
    "upvid.host",
    "upvid.co",
    "upvid.biz",
    "upvid.cloud",
    "opvid.org",
    "opvid.online",
    "uqload.com",
    "uqload.co",
    "uqload.io",
    "userload.co",
    "usersdrive.com",
    "vidoza.net",
    "voe.sx",
    "voe-unblock.com",
    "voeunblock1.com",
    "voeunblock2.com",
    "voeunblock3.com",
    "voeunbl0ck.com",
    "voeunblck.com",
    "voeunblk.com",
    "voe-un-block.com",
    "voeun-block.net",
    "reputationsheriffkennethsand.com",
    "449unceremoniousnasoseptal.com",
    "world-files.com",
    "worldbytez.com",
    "salefiles.com",
    "wupfile.com",
    "youdbox.com",
    "yodbox.com",
    "youtube.com",
    "youtu.be",
    "4tube.com",
    "academicearth.org",
    "acast.com",
    "add-anime.net",
    "air.mozilla.org",
    "allocine.fr",
    "alphaporno.com",
    "anysex.com",
    "aparat.com",
    "www.arte.tv",
    "video.arte.tv",
    "sites.arte.tv",
    "creative.arte.tv",
    "info.arte.tv",
    "future.arte.tv",
    "ddc.arte.tv",
    "concert.arte.tv",
    "cinema.arte.tv",
    "audi-mediacenter.com",
    "audioboom.com",
    "audiomack.com",
    "beeg.com",
    "camdemy.com",
    "chilloutzone.net",
    "clubic.com",
    "clyp.it",
    "daclips.in",
    "dailymail.co.uk",
    "www.dailymail.co.uk",
    "dailymotion.com",
    "touch.dailymotion.com",
    "democracynow.org",
    "discovery.com",
    "investigationdiscovery.com",
    "discoverylife.com",
    "animalplanet.com",
    "ahctv.com",
    "destinationamerica.com",
    "sciencechannel.com",
    "tlc.com",
    "velocity.com",
    "dotsub.com",
    "ebaumsworld.com",
    "eitb.tv",
    "ellentv.com",
    "ellentube.com",
    "flipagram.com",
    "footyroom.com",
    "formula1.com",
    "video.foxnews.com",
    "video.foxbusiness.com",
    "video.insider.foxnews.com",
    "franceculture.fr",
    "gameinformer.com",
    "gamersyde.com",
    "gorillavid.in",
    "hbo.com",
    "hellporno.com",
    "hentai.animestigma.com",
    "hornbunny.com",
    "imdb.com",
    "instagram.com",
    "itar-tass.com",
    "tass.ru",
    "jamendo.com",
    "jove.com",
    "keek.com",
    "k.to",
    "keezmovies.com",
    "khanacademy.org",
    "kickstarter.com",
    "krasview.ru",
    "la7.it",
    "lci.fr",
    "play.lcp.fr",
    "libsyn.com",
    "html5-player.libsyn.com",
    "liveleak.com",
    "livestream.com",
    "new.livestream.com",
    "m6.fr",
    "www.m6.fr",
    "metacritic.com",
    "mgoon.com",
    "m.mgoon.com",
    "mixcloud.com",
    "mojvideo.com",
    "movieclips.com",
    "movpod.in",
    "musicplayon.com",
    "myspass.de",
    "myvidster.com",
    "odatv.com",
    "onionstudios.com",
    "ora.tv",
    "unsafespeech.com",
    "play.fm",
    "plays.tv",
    "playvid.com",
    "pornhd.com",
    "pornhub.com",
    "www.pornhub.com",
    "pyvideo.org",
    "redtube.com",
    "embed.redtube.com",
    "www.redtube.com",
    "reverbnation.com",
    "revision3.com",
    "animalist.com",
    "seeker.com",
    "rts.ch",
    "rtve.es",
    "videos.sapo.pt",
    "videos.sapo.cv",
    "videos.sapo.ao",
    "videos.sapo.mz",
    "videos.sapo.tl",
    "sbs.com.au",
    "www.sbs.com.au",
    "screencast.com",
    "skysports.com",
    "slutload.com",
    "soundgasm.net",
    "store.steampowered.com",
    "steampowered.com",
    "steamcommunity.com",
    "stream.cz",
    "streamable.com",
    "streamcloud.eu",
    "sunporno.com",
    "teachertube.com",
    "teamcoco.com",
    "ted.com",
    "tfo.org",
    "thescene.com",
    "thesixtyone.com",
    "tnaflix.com",
    "trutv.com",
    "tu.tv",
    "turbo.fr",
    "tweakers.net",
    "ustream.tv",
    "vbox7.com",
    "veehd.com",
    "veoh.com",
    "vid.me",
    "videodetective.com",
    "vimeo.com",
    "vimeopro.com",
    "player.vimeo.com",
    "player.vimeopro.com",
    "wat.tv",
    "wimp.com",
    "xtube.com",
    "yahoo.com",
    "screen.yahoo.com",
    "news.yahoo.com",
    "sports.yahoo.com",
    "video.yahoo.com",
    "youporn.com",
    "devupload.com",
]


LINK_GENERATORS = {
    "youtube.com": "ytdl",  # Placeholder, using ytdl cmds as mentioned in the code
    "youtu.be": "ytdl",  # Placeholder
    tuple(DEBRID_LINK_SITES): "debrid_link",
    tuple(DEBRID_SITES): "real_debrid",
    tuple(["filelions.com", "filelions.live", "filelions.to", "filelions.online"]): "filelions",
    "mediafire.com": "mediafire",
    "osdn.net": "osdn",
    "github.com": "github",
    "hxfile.co": "hxfile",
    "1drv.ms": "onedrive",
    "pixeldrain.com": "pixeldrain",
    "antfiles.com": "antfiles",
    "racaty": "racaty",
    "1fichier.com": "fichier",
    "solidfiles.com": "solidfiles",
    "krakenfiles.com": "krakenfiles",
    "upload.ee": "uploadee",
    "akmfiles": "akmfiles",
    "linkbox": "linkbox",
    "shrdsk": "shrdsk",
    "letsupload.io": "letsupload",
    "gofile.io": "gofile",
    "easyupload.io": "easyupload",
    "streamvid.net": "streamvid",
    "instagram.com": "instagram",
    tuple([
        "dood.watch",
        "doodstream.com",
        "dood.to",
        "dood.so",
        "dood.cx",
        "dood.la",
        "dood.ws",
        "dood.sh",
        "doodstream.co",
        "dood.pm",
        "dood.wf",
        "dood.re",
        "dood.video",
        "dooood.com",
        "dood.yt",
        "doods.yt",
        "dood.stream",
        "doods.pro",
    ]): "doods",
    tuple([
        "streamtape.com",
        "streamtape.co",
        "streamtape.cc",
        "streamtape.to",
        "streamtape.net",
        "streamta.pe",
        "streamtape.xyz",
    ]): "streamtape",
    tuple(["wetransfer.com", "we.tl"]): "wetransfer",
    tuple(ANONFILES_DOMAINS): "anonfiles_rip", # Placeholder for Anonfiles R.I.P message
    tuple([
        "terabox.com",
        "nephobox.com",
        "4funbox.com",
        "mirrobox.com",
        "momerybox.com",
        "teraboxapp.com",
        "1024tera.com",
    ]): "terabox",
    tuple(FMED_DOMAINS): "fembed",
    tuple([
        "sbembed.com",
        "watchsb.com",
        "streamsb.net",
        "sbplay.org",
    ]): "sbembed",
    "zippyshare.com": "zippyshare_rip", # Placeholder for Zippyshare R.I.P message
    "gdtot": "gdtot",
    "filepress": "filepress",
    "www.jiodrive": "jiodrive",
    "sharer": "sharer_scraper", # Generic sharer scraper, needs domain check before call
    "devupload.com": "devupload",
}


def direct_link_generator(link):
    """
    Generates a direct download link for various file hosting services.

    Args:
        link (str): The URL to the file hosting service page.

    Returns:
        str: The direct download link, or a dictionary containing direct download links
             and file information for multi-file links.

    Raises:
        DirectDownloadLinkException: If no direct link function is found for the given URL
                                     or if an error occurs during link generation.
    """
    auth = None
    if isinstance(link, tuple):
        link, auth = link

    if is_magnet(link):
        return real_debrid(link, True)

    domain = urlparse(link).hostname
    if not domain:
        raise DirectDownloadLinkException("ERROR: Invalid URL")

    domain_key = None
    for key in LINK_GENERATORS:
        if isinstance(key, tuple):
            if any(x in domain for x in key):
                domain_key = key
                break
        elif key in domain:
            domain_key = key
            break

    if domain_key is None:
        raise DirectDownloadLinkException(f"No direct link function found for {link}")

    generator_function_name = LINK_GENERATORS[domain_key]

    if generator_function_name == "ytdl":
        raise DirectDownloadLinkException("ERROR: Use ytdl cmds for Youtube links")
    elif generator_function_name == "debrid_link" and config_dict["DEBRID_LINK_API"]:
        return debrid_link(link)
    elif generator_function_name == "real_debrid" and config_dict["REAL_DEBRID_API"]:
        return real_debrid(link)
    elif generator_function_name == "filelions":
        return filelions(link)
    elif generator_function_name == "mediafire":
        return mediafire(link)
    elif generator_function_name == "osdn":
        return osdn(link)
    elif generator_function_name == "github":
        return github(link)
    elif generator_function_name == "hxfile":
        return hxfile(link)
    elif generator_function_name == "onedrive":
        return onedrive(link)
    elif generator_function_name == "pixeldrain":
        return pixeldrain(link)
    elif generator_function_name == "antfiles":
        return antfiles(link)
    elif generator_function_name == "racaty":
        return racaty(link)
    elif generator_function_name == "fichier":
        return fichier(link)
    elif generator_function_name == "solidfiles":
        return solidfiles(link)
    elif generator_function_name == "krakenfiles":
        return krakenfiles(link)
    elif generator_function_name == "uploadee":
        return uploadee(link)
    elif generator_function_name == "akmfiles":
        return akmfiles(link)
    elif generator_function_name == "linkbox":
        return linkbox(link)
    elif generator_function_name == "shrdsk":
        return shrdsk(link)
    elif generator_function_name == "letsupload":
        return letsupload(link)
    elif generator_function_name == "gofile":
        return gofile(link, auth)
    elif generator_function_name == "easyupload":
        return easyupload(link)
    elif generator_function_name == "streamvid":
        return streamvid(link)
    elif generator_function_name == "instagram":
        return instagram(link)
    elif generator_function_name == "doods":
        return doods(link)
    elif generator_function_name == "streamtape":
        return streamtape(link)
    elif generator_function_name == "wetransfer":
        return wetransfer(link)
    elif generator_function_name == "anonfiles_rip":
        raise DirectDownloadLinkException("ERROR: R.I.P Anon Sites!")
    elif generator_function_name == "terabox":
        return terabox(link)
    elif generator_function_name == "fembed":
        return fembed(link)
    elif generator_function_name == "sbembed":
        return sbembed(link)
    elif generator_function_name == "zippyshare_rip":
        raise DirectDownloadLinkException("ERROR: R.I.P Zippyshare")
    elif generator_function_name == "gd_index" and is_index_link(link) and link.endswith("/"): # gd_index needs special handling for auth and index link check
        return gd_index(link, auth)
    elif generator_function_name == "gdtot":
        return gdtot(link)
    elif generator_function_name == "filepress":
        return filepress(link)
    elif generator_function_name == "jiodrive":
        return jiodrive(link)
    elif generator_function_name == "sharer_scraper" and is_share_link(link): # sharer_scraper needs share link check
        return sharer_scraper(link)
    elif generator_function_name == "devupload":
        print(f"DEBUG: Calling devupload function for link: {link}") # DEBUG print
        return devupload(link)
    else:
        raise DirectDownloadLinkException(f"No Direct link function found for {link}")


def real_debrid(url: str, tor=False):
    """Real-Debrid Link Extractor (VPN Maybe Needed)
    Based on Real-Debrid v1 API (Heroku/VPS) [Without VPN]"""

    def __unrestrict(url, tor=False):
        cget = create_scraper().request
        resp = cget(
            "POST",
            f"https://api.real-debrid.com/rest/1.0/unrestrict/link?auth_token={config_dict['REAL_DEBRID_API']}",
            data={"link": url},
        )
        resp_json = resp.json()
        if resp.status_code == 200:
            if tor:
                return (resp_json["filename"], resp_json["download"])
            else:
                return resp_json["download"]
        else:
            error_msg = resp_json.get('error', 'Unknown Real-Debrid error')
            raise DirectDownloadLinkException(f"ERROR: Real-Debrid - {error_msg}")

    def __addMagnet(magnet):
        cget = create_scraper().request
        hash_ = search(r"(?<=xt=urn:btih:)[a-zA-Z0-9]+", magnet).group(0)
        resp = cget(
            "GET",
            f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{hash_}?auth_token={config_dict['REAL_DEBRID_API']}",
        )
        if resp.status_code != 200 or not resp.json()[hash_.lower()]["rd"]:
            return magnet # Magnet not available on RD, return original magnet
        resp = cget(
            "POST",
            f"https://api.real-debrid.com/rest/1.0/torrents/addMagnet?auth_token={config_dict['REAL_DEBRID_API']}",
            data={"magnet": magnet},
        )
        resp_json = resp.json()
        if resp.status_code == 201:
            _id = resp_json["id"]
        else:
            error_msg = resp_json.get('error', 'Unknown Real-Debrid error')
            raise DirectDownloadLinkException(f"ERROR: Real-Debrid - {error_msg}")

        _file = cget(
            "POST",
            f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{_id}?auth_token={config_dict['REAL_DEBRID_API']}",
            data={"files": "all"},
        )
        if _file.status_code != 204:
            resp_json = _file.json()
            error_msg = resp_json.get('error', 'Unknown Real-Debrid error')
            raise DirectDownloadLinkException(f"ERROR: Real-Debrid - {error_msg}")

        contents = {"links": []}
        while not contents["links"]: # Wait until links are available
            _res = cget(
                "GET",
                f"https://api.real-debrid.com/rest/1.0/torrents/info/{_id}?auth_token={config_dict['REAL_DEBRID_API']}",
            )
            if _res.status_code == 200:
                contents = _res.json()
            else:
                resp_json = _res.json()
                error_msg = resp_json.get('error', 'Unknown Real-Debrid error')
                raise DirectDownloadLinkException(f"ERROR: Real-Debrid - {error_msg}")
            sleep(0.5)

        details = {
            "contents": [],
            "title": contents["original_filename"],
            "total_size": contents["bytes"],
        }

        for file_info, link in zip(contents["files"], contents["links"]):
            link_info = __unrestrict(link, tor=True)
            item = {
                "path": path.join(
                    details["title"], path.dirname(file_info["path"]).lstrip("/")
                ),
                "filename": unquote(link_info[0]),
                "url": link_info[1],
            }
            details["contents"].append(item)
        return details

    try:
        if tor:
            details = __addMagnet(url)
        else:
            return __unrestrict(url)
    except DirectDownloadLinkException as e:
        raise e # Re-raise the custom exception
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: Real-Debrid - {e.__class__.__name__}: {e}")

    if isinstance(details, dict) and len(details["contents"]) == 1:
        return details["contents"][0]["url"]
    return details


def debrid_link(url):
    cget = create_scraper().request
    try:
        resp = cget(
            "POST",
            f"https://debrid-link.com/api/v2/downloader/add?access_token={config_dict['DEBRID_LINK_API']}",
            data={"url": url},
        ).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: Debrid-Link - {e.__class__.__name__}: {e}")

    if not resp["success"]:
        error_msg = f"{resp.get('error', 'Unknown error')} & ERROR ID: {resp.get('error_id', 'N/A')}"
        raise DirectDownloadLinkException(f"ERROR: Debrid-Link - {error_msg}")

    if isinstance(resp["value"], dict):
        return resp["value"]["downloadUrl"]
    elif isinstance(resp["value"], list):
        details = {
            "contents": [],
            "title": unquote(url.rstrip("/").split("/")[-1]),
            "total_size": 0,
        }
        for dl in resp["value"]:
            if dl.get("expired", False):
                continue
            item = {
                "path": path.join(details["title"]),
                "filename": dl["name"],
                "url": dl["downloadUrl"],
            }
            if "size" in dl:
                details["total_size"] += dl["size"]
            details["contents"].append(item)
        return details
    else:
        raise DirectDownloadLinkException("ERROR: Debrid-Link - Unexpected response format")


def get_captcha_token(session, params):
    recaptcha_api = "https://www.google.com/recaptcha/api2"
    try:
        res = session.get(f"{recaptcha_api}/anchor", params=params)
        res.raise_for_status()
        anchor_html = HTML(res.text)
        if not (anchor_token := anchor_html.xpath('//input[@id="recaptcha-token"]/@value')):
            return None
        params["c"] = anchor_token[0]
        params["reason"] = "q"
        res = session.post(f"{recaptcha_api}/reload", params=params)
        res.raise_for_status()
        if token := findall(r'"rresp","(.*?)"', res.text):
            return token[0]
    except Exception as e:
        LOGGER.error(f"Error getting captcha token: {e}")
        return None
    return None


def mediafire(url, session=None):
    if "/folder/" in url:
        return mediafireFolder(url)
    if final_link := findall(
        r"https?:\/\/download\d+\.mediafire\.com\/\S+\/\S+\/\S+", url
    ):
        return final_link[0]

    if session is None:
        session = Session()
        parsed_url = urlparse(url)
        url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    try:
        res = session.get(url)
        res.raise_for_status()
        html = HTML(res.text)
    except Exception as e:
        session.close()
        raise DirectDownloadLinkException(f"ERROR: Mediafire - {e.__class__.__name__}: {e}")
    if error := html.xpath('//p[@class="notranslate"]/text()'):
        session.close()
        raise DirectDownloadLinkException(f"ERROR: Mediafire - {error[0]}")
    if not (final_link := html.xpath("//a[@id='downloadButton']/@href")):
        session.close()
        raise DirectDownloadLinkException(
            "ERROR: Mediafire - No links found on this page. Try again."
        )
    link = final_link[0]
    session.close()
    if link.startswith("//"):
        return mediafire(f"https://{link[2:]}", session=Session()) # Create new session for redirect to avoid session close issues
    return link


def osdn(url):
    with create_scraper() as session:
        try:
            res = session.get(url)
            res.raise_for_status()
            html = HTML(res.text)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: OSDN - {e.__class__.__name__}: {e}")
        if not (direct_link := html.xpath('//a[@class="mirror_link"]/@href')):
            raise DirectDownloadLinkException("ERROR: OSDN - Direct link not found")
        return f"https://osdn.net{direct_link[0]}"


def github(url):
    try:
        findall(r"\bhttps?://.*github\.com.*releases\S+", url)[0]
    except IndexError:
        raise DirectDownloadLinkException("ERROR: GitHub - No GitHub Releases links found")
    with create_scraper() as session:
        try:
            _res = session.get(url, stream=True, allow_redirects=False)
            _res.raise_for_status()
            if "location" in _res.headers:
                return _res.headers["location"]
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: GitHub - {e.__class__.__name__}: {e}")
        raise DirectDownloadLinkException("ERROR: GitHub - Can't extract the link")


def hxfile(url):
    try:
        return Bypass().bypass_filesIm(url)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: HXFile - {e.__class__.__name__}: {e}")


def letsupload(url):
    with create_scraper() as session:
        try:
            res = session.post(url)
            res.raise_for_status()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: LetsUpload - {e.__class__.__name__}: {e}")
        if direct_link := findall(r"(https?://letsupload\.io\/.+?)\'", res.text):
            return direct_link[0]
        else:
            raise DirectDownloadLinkException("ERROR: LetsUpload - Direct Link not found")


def anonfilesBased(url):
    with create_scraper() as session:
        try:
            res = session.get(url)
            res.raise_for_status()
            html = HTML(res.text)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: AnonFiles-Based - {e.__class__.__name__}: {e}")
        if sa := html.xpath('//*[@id="download-url"]/@href'):
            return sa[0]
        raise DirectDownloadLinkException("ERROR: AnonFiles-Based - File not found!")


def fembed(link):
    try:
        dl_url = Bypass().bypass_fembed(link)
        if not dl_url:
            raise DirectDownloadLinkException("ERROR: Fembed - No direct links found by bypass.")
        return dl_url[-1] # Return the last available link, usually highest quality
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: Fembed - {e.__class__.__name__}: {e}")


def sbembed(link):
    """Sbembed direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        dl_url = Bypass().bypass_sbembed(link)
        if not dl_url:
            raise DirectDownloadLinkException("ERROR: Sbembed - No direct links found by bypass.")
        return dl_url[-1] # Return the last available link, usually highest quality
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: Sbembed - {e.__class__.__name__}: {e}")


def onedrive(link):
    with create_scraper() as session:
        try:
            link = session.get(link).url
            parsed_link = urlparse(link)
            link_data = parse_qs(parsed_link.query)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: OneDrive - {e.__class__.__name__}: {e}")
        if not link_data:
            raise DirectDownloadLinkException("ERROR: OneDrive - Unable to find link_data")
        folder_id = link_data.get("resid")
        if not folder_id:
            raise DirectDownloadLinkException("ERROR: OneDrive - folder id not found")
        folder_id = folder_id[0]
        authkey = link_data.get("authkey")
        if not authkey:
            raise DirectDownloadLinkException("ERROR: OneDrive - authkey not found")
        authkey = authkey[0]
        boundary = uuid4()
        headers = {"content-type": f"multipart/form-data;boundary={boundary}"}
        data = f"--{boundary}\r\nContent-Disposition: form-data;name=data\r\nPrefer: Migration=EnableRedirect;FailOnMigratedFiles\r\nX-HTTP-Method-Override: GET\r\nContent-Type: application/json\r\n\r\n--{boundary}--"
        try:
            resp = session.get(
                f'https://api.onedrive.com/v1.0/drives/{folder_id.split("!", 1)[0]}/items/{folder_id}?$select=id,@content.downloadUrl&ump=1&authKey={authkey}',
                headers=headers,
                data=data,
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: OneDrive API - {e.__class__.__name__}: {e}")
    if "@content.downloadUrl" not in resp:
        raise DirectDownloadLinkException("ERROR: OneDrive API - Direct link not found")
    return resp["@content.downloadUrl"]


def pixeldrain(url):
    url = url.strip("/ ")
    file_id = url.split("/")[-1]
    if url.split("/")[-2] == "l":
        info_link = f"https://pixeldrain.com/api/list/{file_id}"
        dl_link = f"https://pixeldrain.com/api/list/{file_id}/zip?download"
    else:
        info_link = f"https://pixeldrain.com/api/file/{file_id}/info"
        dl_link = f"https://pixeldrain.com/api/file/{file_id}?download"
    with create_scraper() as session:
        try:
            resp = session.get(info_link).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: PixelDrain API - {e.__class__.__name__}: {e}")
    if resp["success"]:
        return dl_link
    else:
        error_msg = resp.get('message', 'Unknown PixelDrain error')
        raise DirectDownloadLinkException(
            f"ERROR: PixelDrain API - Can't download due to {error_msg}."
        )


def antfiles(url):
    try:
        return Bypass().bypass_antfiles(url)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: Antfiles - {e.__class__.__name__}: {e}")


def streamtape(url):
    splitted_url = url.split("/")
    _id = splitted_url[4] if len(splitted_url) >= 6 else splitted_url[-1]
    try:
        with Session() as session:
            res = session.get(url)
            res.raise_for_status()
            html = HTML(res.text)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: Streamtape - {e.__class__.__name__}: {e}")
    if not (script := html.xpath("//script[contains(text(),'ideoooolink')]/text()")):
        raise DirectDownloadLinkException("ERROR: Streamtape - Requeries script not found")
    if not (link := findall(r"(&expires\S+)'", script[0])):
        raise DirectDownloadLinkException("ERROR: Streamtape - Download link not found")
    return f"https://streamtape.com/get_video?id={_id}{link[-1]}"


def racaty(url):
    with create_scraper() as session:
        try:
            url = session.get(url).url
            json_data = {"op": "download2", "id": url.split("/")[-1]}
            res = session.post(url, data=json_data)
            res.raise_for_status()
            html = HTML(res.text)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: Racaty - {e.__class__.__name__}: {e}")
    if direct_link := html.xpath("//a[@id='uniqueExpirylink']/@href"):
        return direct_link[0]
    else:
        raise DirectDownloadLinkException("ERROR: Racaty - Direct link not found")


def fichier(link):
    regex = r"^([http:\/\/|https:\/\/]+)?.*1fichier\.com\/\?.+"
    if not match(regex, link):
        raise DirectDownloadLinkException("ERROR: 1Fichier - Invalid link format!")

    password = None
    if "::" in link:
        parts = link.split("::")
        if len(parts) == 2:
            url, password = parts
        else:
            raise DirectDownloadLinkException("ERROR: 1Fichier - Invalid link format with password.")
    else:
        url = link

    cget = create_scraper().request
    try:
        data = {"pass": password} if password else None
        req = cget("post", url, data=data)
        req.raise_for_status()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: 1Fichier - {e.__class__.__name__}: {e}")

    if req.status_code == 404:
        raise DirectDownloadLinkException(
            "ERROR: 1Fichier - File not found or invalid link!"
        )

    html = HTML(req.text)
    if dl_url := html.xpath('//a[@class="ok btn-general btn-orange"]/@href'):
        return dl_url[0]

    ct_warn = html.xpath('//div[@class="ct_warn"]')
    if not ct_warn:
        raise DirectDownloadLinkException(
            "ERROR: 1Fichier - Error generating direct link (No ct_warn found)."
        )

    if len(ct_warn) >= 3: # Handle wait time limit and password protected
        last_warn_text = ct_warn[-1].text.lower()
        if "you must wait" in last_warn_text:
            if numbers := [int(word) for word in last_warn_text.split() if word.isdigit()]:
                wait_minutes = numbers[0]
                raise DirectDownloadLinkException(
                    f"ERROR: 1Fichier - Limit reached. Please wait {wait_minutes} minute(s)."
                )
            else:
                raise DirectDownloadLinkException(
                    "ERROR: 1Fichier - Limit reached. Please wait a few minutes/hour."
                )
        elif "protect access" in last_warn_text:
            raise DirectDownloadLinkException(
                f"ERROR: 1Fichier - {PASSWORD_ERROR_MESSAGE.format(link)}"
            )

    if len(ct_warn) >= 4: # Handle wrong password
        last_warn_text = ct_warn[-1].text.lower()
        if "bad password" in last_warn_text:
            raise DirectDownloadLinkException(
                "ERROR: 1Fichier - The password you entered is wrong!"
            )

    raise DirectDownloadLinkException(
        "ERROR: 1Fichier - Failed to generate Direct Link (Unhandled ct_warn condition)."
    )


def solidfiles(url):
    with create_scraper() as session:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
            }
            res = session.get(url, headers=headers)
            res.raise_for_status()
            pageSource = res.text
            mainOptions_match = search(r"viewerOptions\'\,\ (.*?)\)\;", pageSource)
            if not mainOptions_match:
                raise DirectDownloadLinkException("ERROR: Solidfiles - viewerOptions not found in page source.")
            mainOptions = str(mainOptions_match.group(1))
            return loads(mainOptions)["downloadUrl"]
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: Solidfiles - {e.__class__.__name__}: {e}")


def krakenfiles(url):
    with Session() as session:
        try:
            _res = session.get(url)
            _res.raise_for_status()
            html = HTML(_res.text)
            post_url_list = html.xpath('//form[@id="dl-form"]/@action')
            if not post_url_list:
                raise DirectDownloadLinkException("ERROR: Krakenfiles - Unable to find post link.")
            post_url = f"https:{post_url_list[0]}"
            token_list = html.xpath('//input[@id="dl-token"]/@value')
            if not token_list:
                raise DirectDownloadLinkException("ERROR: Krakenfiles - Unable to find token for post.")
            data = {"token": token_list[0]}
            _json = session.post(post_url, data=data).json()
            if _json["status"] != "ok":
                error_msg = _json.get('message', 'Unknown Krakenfiles error')
                raise DirectDownloadLinkException(
                    f"ERROR: Krakenfiles API - Unable to find download after post request. Status: {_json['status']}, Message: {error_msg}"
                )
            return _json["url"]
        except DirectDownloadLinkException as e:
            raise e
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: Krakenfiles - {e.__class__.__name__} While processing: {e}"
            )


def uploadee(url):
    with create_scraper() as session:
        try:
            res = session.get(url)
            res.raise_for_status()
            html = HTML(res.text)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: Uploadee - {e.__class__.__name__}: {e}")
    if link := html.xpath("//a[@id='d_l']/@href"):
        return link[0]
    else:
        raise DirectDownloadLinkException("ERROR: Uploadee - Direct Link not found")


def terabox(url):
    if not path.isfile("terabox.txt"):
        raise DirectDownloadLinkException("ERROR: Terabox - terabox.txt not found")
    try:
        jar = MozillaCookieJar("terabox.txt")
        jar.load()
    except Exception as e:
        raise DirectDownloadLinkException("ERROR: Terabox - Cookie file error: {e.__class__.__name__}: {e}")
    cookies = {}
    for cookie in jar:
        cookies[cookie.name] = cookie.value
    details = {"contents": [], "title": "", "total_size": 0}
    details["header"] = " ".join(f"{key}: {value}" for key, value in cookies.items())

    def __fetch_links(session, dir_="", folderPath=""):
        params = {"app_id": "250528", "jsToken": jsToken, "shorturl": shortUrl}
        if dir_:
            params["dir"] = dir_
        else:
            params["root"] = "1"
        try:
            _json = session.get(
                "https://www.1024tera.com/share/list", params=params, cookies=cookies
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: Terabox API - {e.__class__.__name__}: {e}")
        if _json["errno"] not in [0, "0"]:
            error_msg = _json.get('errmsg', 'Unknown Terabox error')
            raise DirectDownloadLinkException(f"ERROR: Terabox API - {error_msg}")

        if "list" not in _json:
            return
        contents = _json["list"]
        for content in contents:
            if content["isdir"] in ["1", 1]:
                if not folderPath:
                    if not details["title"]:
                        details["title"] = content["server_filename"]
                        newFolderPath = path.join(details["title"])
                    else:
                        newFolderPath = path.join(
                            details["title"], content["server_filename"]
                        )
                else:
                    newFolderPath = path.join(folderPath, content["server_filename"])
                __fetch_links(session, content["path"], newFolderPath)
            else:
                if not folderPath:
                    if not details["title"]:
                        details["title"] = content["server_filename"]
                    folderPath = details["title"]
                item = {
                    "url": content["dlink"],
                    "filename": content["server_filename"],
                    "path": path.join(folderPath),
                }
                if "size" in content:
                    size = content["size"]
                    if isinstance(size, str) and size.isdigit():
                        size = float(size)
                    details["total_size"] += size
                details["contents"].append(item)

    with Session() as session:
        try:
            _res = session.get(url, cookies=cookies)
            _res.raise_for_status()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: Terabox - Initial request failed: {e.__class__.__name__}: {e}")
        jsToken_search = findall(r"window\.jsToken.*%22(.*)%22", _res.text)
        if not jsToken_search:
            raise DirectDownloadLinkException("ERROR: Terabox - jsToken not found!.")
        jsToken = jsToken_search[0]
        shortUrl_parse = parse_qs(urlparse(_res.url).query).get("surl")
        if not shortUrl_parse:
            raise DirectDownloadLinkException("ERROR: Terabox - Could not find surl")
        shortUrl = shortUrl_parse[0]
        try:
            __fetch_links(session)
        except DirectDownloadLinkException as e:
            raise e # Re-raise the custom exception
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: Terabox - Fetching links failed: {e.__class__.__name__}: {e}")

    if len(details["contents"]) == 1:
        return details["contents"][0]["url"]
    return details


def gofile(url, auth):
    try:
        _password = sha256(auth[1].encode("utf-8")).hexdigest() if auth else ""
        _id = url.split("/")[-1]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: GoFile - URL Parsing error: {e.__class__.__name__}: {e}")

    def __get_token(session):
        headers = {
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }
        __url = "https://api.gofile.io/accounts"
        try:
            __res = session.post(__url, headers=headers).json()
            if __res["status"] != "ok":
                error_msg = __res.get('status', 'Failed to get token')
                raise DirectDownloadLinkException(f"ERROR: GoFile API - {error_msg}")
            return __res["data"]["token"]
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: GoFile API - Token retrieval error: {e.__class__.__name__}: {e}")

    def __fetch_links(session, _id, folderPath=""):
        _url = f"https://api.gofile.io/contents/{_id}?wt=4fd6sg89d7s6&cache=true"
        headers = {
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Authorization": "Bearer" + " " + token,
        }
        if _password:
            _url += f"&password={_password}"
        try:
            _json = session.get(_url, headers=headers).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: GoFile API - Content request error: {e.__class__.__name__}: {e}")

        status = _json["status"]
        if status in "error-passwordRequired":
            raise DirectDownloadLinkException(
                f"ERROR: GoFile - {PASSWORD_ERROR_MESSAGE.format(url)}"
            )
        elif status in "error-passwordWrong":
            raise DirectDownloadLinkException("ERROR: GoFile - This password is wrong !")
        elif status in "error-notFound":
            raise DirectDownloadLinkException(
                "ERROR: GoFile - File not found on gofile's server"
            )
        elif status in "error-notPublic":
            raise DirectDownloadLinkException("ERROR: GoFile - This folder is not public")
        elif status != "ok":
             error_msg = _json.get('status', 'Unknown GoFile error')
             raise DirectDownloadLinkException(f"ERROR: GoFile API - {error_msg}")


        data = _json["data"]

        if not details["title"]:
            details["title"] = data["name"] if data["type"] == "folder" else _id

        contents = data["children"]
        for content in contents.values():
            if content["type"] == "folder":
                if not content["public"]:
                    continue
                if not folderPath:
                    newFolderPath = path.join(details["title"], content["name"])
                else:
                    newFolderPath = path.join(folderPath, content["name"])
                __fetch_links(session, content["id"], newFolderPath)
            else:
                if not folderPath:
                    folderPath = details["title"]
                item = {
                    "path": path.join(folderPath),
                    "filename": content["name"],
                    "url": content["link"],
                }
                if "size" in content:
                    size = content["size"]
                    if isinstance(size, str) and size.isdigit():
                        size = float(size)
                    details["total_size"] += size
                details["contents"].append(item)

    details = {"contents": [], "title": "", "total_size": 0}
    with Session() as session:
        try:
            token = __get_token(session)
        except DirectDownloadLinkException as e:
            raise e # Re-raise custom exception
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: GoFile - Token error: {e.__class__.__name__}: {e}")
        details["header"] = f"Cookie: accountToken={token}"
        try:
            __fetch_links(session, _id)
        except DirectDownloadLinkException as e:
            raise e # Re-raise custom exception
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: GoFile - Link fetching error: {e.__class__.__name__}: {e}")

    if len(details["contents"]) == 1:
        return (details["contents"][0]["url"], details["header"])
    return details


def gd_index(url, auth):
    if not auth:
        auth = ("admin", "admin")
    try:
        _title = url.rstrip("/").split("/")[-1]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: GDIndex - URL parsing error: {e.__class__.__name__}: {e}")

    details = {"contents": [], "title": unquote(_title), "total_size": 0}

    def __fetch_links(url, folderPath, username, password):
        with create_scraper() as session:
            payload = {
                "id": "",
                "type": "folder",
                "username": username,
                "password": password,
                "page_token": "",
                "page_index": 0,
            }
            try:
                res = session.post(url, json=payload)
                res.raise_for_status()
                data = res.json()
            except Exception as e:
                raise DirectDownloadLinkException(f"ERROR: GDIndex API - Request error, Use Latest Bhadoo Index Link: {e.__class__.__name__}: {e}")

        if "data" in data:
            for file_info in data["data"]["files"]:
                if (
                    file_info.get("mimeType", "")
                    == "application/vnd.google-apps.folder"
                ):
                    if not folderPath:
                        newFolderPath = path.join(details["title"], file_info["name"])
                    else:
                        newFolderPath = path.join(folderPath, file_info["name"])
                    __fetch_links(
                        f"{url}{file_info['name']}/", newFolderPath, username, password
                    )
                else:
                    if not folderPath:
                        folderPath = details["title"]
                    item = {
                        "path": path.join(folderPath),
                        "filename": unquote(file_info["name"]),
                        "url": urljoin(url, file_info.get("link", "") or ""),
                    }
                    if "size" in file_info:
                        details["total_size"] += int(file_info["size"])
                    details["contents"].append(item)

    try:
        __fetch_links(url, "", auth[0], auth[1])
    except DirectDownloadLinkException as e:
        raise e # Re-raise custom exception
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: GDIndex - Link fetching error: {e.__class__.__name__}: {e}")

    if len(details["contents"]) == 1:
        return details["contents"][0]["url"]
    return details


def filepress(url):
    with create_scraper() as session:
        try:
            url = session.get(url).url
            raw = urlparse(url)
            json_data = {
                "id": raw.path.split("/")[-1],
                "method": "publicDownlaod",
            }
            api = f"{raw.scheme}://{raw.hostname}/api/file/downlaod/"
            res = session.post(
                api,
                headers={"Referer": f"{raw.scheme}://{raw.hostname}"},
                json=json_data,
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: Filepress API - {e.__class__.__name__}: {e}")
    if "data" not in res:
        error_msg = res.get('statusText', 'Unknown Filepress error')
        raise DirectDownloadLinkException(f'ERROR: Filepress API - {error_msg}')
    return f'https://drive.google.com/uc?id={res["data"]}&export=download'


def jiodrive(url):
    with create_scraper() as session:
        try:
            url = session.get(url).url
            cookies = {"access_token": config_dict["JIODRIVE_TOKEN"]}

            data = {"id": url.split("/")[-1]}

            resp = session.post(
                "https://www.jiodrive.xyz/ajax.php?ajax=download",
                cookies=cookies,
                data=data,
            ).json()

        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: JioDrive API - {e.__class__.__name__}: {e}")
        if resp["code"] != "200":
            error_msg = resp.get('msg', 'Unknown JioDrive error')
            raise DirectDownloadLinkException(
                f"ERROR: JioDrive API - The user's Drive storage quota has been exceeded. Message: {error_msg}"
            )
        return resp["file"]


def gdtot(url):
    cget = create_scraper().request
    try:
        res = cget("GET", f'https://gdtot.pro/file/{url.split("/")[-1]}')
        res.raise_for_status()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: GDTot - Initial request failed: {e.__class__.__name__}: {e}")

    token_url_list = HTML(res.text).xpath(
        "//a[contains(@class,'inline-flex items-center justify-center')]/@href"
    )
    if not token_url_list:
        try:
            url = cget("GET", url).url
            p_url = urlparse(url)
            res = cget(
                "POST",
                f"{p_url.scheme}://{p_url.hostname}/ddl",
                data={"dl": str(url.split("/")[-1])},
            )
            res.raise_for_status()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: GDTot - DDL request failed: {e.__class__.__name__}: {e}")

        drive_link_search = findall(r"myDl\('(.*?)'\)", res.text)
        if drive_link_search and "drive.google.com" in drive_link_search[0]:
            return drive_link_search[0]
        elif config_dict["GDTOT_CRYPT"]:
            try:
                cget("GET", url, cookies={"crypt": config_dict["GDTOT_CRYPT"]})
                p_url = urlparse(url)
                js_script = cget(
                    "POST",
                    f"{p_url.scheme}://{p_url.hostname}/dld",
                    data={"dwnld": url.split("/")[-1]},
                )
                js_script.raise_for_status()
                g_id = findall("gd=(.*?)&", js_script.text)
                decoded_id = b64decode(str(g_id[0])).decode("utf-8")
                return f"https://drive.google.com/open?id={decoded_id}"
            except Exception as e:
                raise DirectDownloadLinkException(
                    "ERROR: GDTot - Crypt bypass failed, Try in browser, possible file not found or user limit exceeded: {e.__class__.__name__}: {e}"
                )
        else:
            raise DirectDownloadLinkException(
                "ERROR: GDTot - Drive Link not found, Try in browser! GDTOT_CRYPT not Provided, it increases efficiency!"
            )

    token_url = token_url_list[0]
    try:
        token_page = cget("GET", token_url)
        token_page.raise_for_status()
    except Exception as e:
        raise DirectDownloadLinkException(
            f"ERROR: GDTot - Token page request failed for {token_url}: {e.__class__.__name__}: {e}"
        )

    path_search = findall('\("(.*?)"\)', token_page.text)
    if not path_search:
        raise DirectDownloadLinkException("ERROR: GDTot - Cannot bypass token page.")
    path_ = path_search[0]
    raw = urlparse(token_url)
    final_url = f"{raw.scheme}://{raw.hostname}{path_}"
    return sharer_scraper(final_url)


def sharer_scraper(url):
    cget = create_scraper().request
    try:
        url = cget("GET", url).url
        raw = urlparse(url)
        header = {
            "useragent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/7.0.548.0 Safari/534.10"
        }
        res = cget("GET", url, headers=header)
        res.raise_for_status()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: Sharer - Initial request failed: {e.__class__.__name__}: {e}")

    key_search = findall('"key",\s+"(.*?)"', res.text)
    if not key_search:
        raise DirectDownloadLinkException("ERROR: Sharer - Key not found!")
    key = key_search[0]

    if not HTML(res.text).xpath("//button[@id='drc']"):
        raise DirectDownloadLinkException(
            "ERROR: Sharer - This link doesn't have direct download button"
        )

    boundary = uuid4()
    headers = {
        "Content-Type": f"multipart/form-data; boundary=----WebKitFormBoundary{boundary}",
        "x-token": raw.hostname,
        "useragent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/7.0.548.0 Safari/534.10",
    }

    data = (
        f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="action"\r\n\r\ndirect\r\n'
        f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="key"\r\n\r\n{key}\r\n'
        f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="action_token"\r\n\r\n\r\n'
        f"------WebKitFormBoundary{boundary}--\r\n"
    )
    try:
        res = cget("POST", url, cookies=res.cookies, headers=headers, data=data).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: Sharer API - Post request failed: {e.__class__.__name__}: {e}")

    if "url" not in res:
        raise DirectDownloadLinkException(
            "ERROR: Sharer API - Drive Link not found in response, Try in browser"
        )

    if "drive.google.com" in res["url"]:
        return res["url"]

    try:
        res = cget("GET", res["url"])
        res.raise_for_status()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: Sharer - Redirect GET request failed: {e.__class__.__name__}: {e}")

    drive_link_list = HTML(res.text).xpath("//a[contains(@class,'btn')]/@href")
    if drive_link_list and "drive.google.com" in drive_link_list[0]:
        return drive_link_list[0]
    else:
        raise DirectDownloadLinkException(
            "ERROR: Sharer - Drive Link not found after redirect, Try in browser"
        )


def wetransfer(url):
    with create_scraper() as session:
        try:
            url = session.get(url).url
            splited_url = url.split("/")
            json_data = {"security_hash": splited_url[-1], "intent": "entire_transfer"}
            res = session.post(
                f"https://wetransfer.com/api/v4/transfers/{splited_url[-2]}/download",
                json=json_data,
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: WeTransfer API - {e.__class__.__name__}: {e}")

    if "direct_link" in res:
        return res["direct_link"]
    elif "message" in res:
        error_msg = res.get('message', 'Unknown WeTransfer error')
        raise DirectDownloadLinkException(f"ERROR: WeTransfer API - {error_msg}")
    elif "error" in res:
        error_msg = res.get('error', 'Unknown WeTransfer error')
        raise DirectDownloadLinkException(f"ERROR: WeTransfer API - {error_msg}")
    else:
        raise DirectDownloadLinkException("ERROR: WeTransfer API - Cannot find direct link")


def akmfiles(url):
    with create_scraper() as session:
        try:
            url = session.get(url).url
            json_data = {"op": "download2", "id": url.split("/")[-1]}
            res = session.post("POST", url, data=json_data)
            res.raise_for_status()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: Akmfiles - {e.__class__.__name__}: {e}")
    direct_link_list = HTML(res.text).xpath("//a[contains(@class,'btn btn-dow')]/@href")
    if direct_link_list:
        return direct_link_list[0]
    else:
        raise DirectDownloadLinkException("ERROR: Akmfiles - Direct link not found")


def shrdsk(url):
    with create_scraper() as session:
        try:
            url = session.get(url).url
            res = session.get(
                f'https://us-central1-affiliate2apk.cloudfunctions.net/get_data?shortid={url.split("/")[-1]}'
            )
            res.raise_for_status()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: Shrdsk API - {e.__class__.__name__}: {e}")
    if res.status_code != 200:
        raise DirectDownloadLinkException(f"ERROR: Shrdsk API - Status Code {res.status_code}")
    res_json = res.json()
    if "type" in res_json and res_json["type"].lower() == "upload" and "video_url" in res_json:
        return res_json["video_url"]
    raise DirectDownloadLinkException("ERROR: Shrdsk API - Cannot find direct link")


def linkbox(url):
    with create_scraper() as session:
        try:
            url = session.get(url).url
            res = session.get(
                f'https://www.linkbox.to/api/file/detail?itemId={url.split("/")[-1]}'
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: Linkbox API - {e.__class__.__name__}: {e}")
    if "data" not in res:
        raise DirectDownloadLinkException("ERROR: Linkbox API - Data not found!!")
    data = res["data"]
    if not data:
        raise DirectDownloadLinkException("ERROR: Linkbox API - Data is None!!")
    if "itemInfo" not in data:
        raise DirectDownloadLinkException("ERROR: Linkbox API - itemInfo not found!!")
    itemInfo = data["itemInfo"]
    if "url" not in itemInfo:
        raise DirectDownloadLinkException("ERROR: Linkbox API - url not found in itemInfo!!")
    if "name" not in itemInfo:
        raise DirectDownloadLinkException("ERROR: Linkbox API - Name not found in itemInfo!!")
    name = quote(itemInfo["name"])
    raw = itemInfo["url"].split("/", 3)[-1]
    return f"https://wdl.nuplink.net/{raw}&filename={name}"


def mediafireFolder(url):
    try:
        raw = url.split("/", 4)[-1]
        folderkey = raw.split("/", 1)[0]
        folderkey = folderkey.split(",")
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: Mediafire Folder - Could not parse folder key: {e.__class__.__name__}: {e}")
    if len(folderkey) == 1:
        folderkey = folderkey[0]
    details = {"contents": [], "title": "", "total_size": 0, "header": ""}

    session = req_session()
    adapter = HTTPAdapter(
        max_retries=Retry(total=10, read=10, connect=10, backoff_factor=0.3)
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session = create_scraper(
        browser={"browser": "firefox", "platform": "windows", "mobile": False},
        delay=10,
        sess=session,
    )
    folder_infos = []

    def __get_info(folderkey):
        try:
            if isinstance(folderkey, list):
                folderkey = ",".join(folderkey)
            _json = session.post(
                "https://www.mediafire.com/api/1.5/folder/get_info.php",
                data={
                    "recursive": "yes",
                    "folder_key": folderkey,
                    "response_format": "json",
                },
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: Mediafire Folder API - Get info request failed: {e.__class__.__name__}: {e}"
            )
        _res = _json["response"]
        if "folder_infos" in _res:
            folder_infos.extend(_res["folder_infos"])
        elif "folder_info" in _res:
            folder_infos.append(_res["folder_info"])
        elif "message" in _res:
            error_msg = _res.get('message', 'Unknown Mediafire Folder error')
            raise DirectDownloadLinkException(f"ERROR: Mediafire Folder API - {error_msg}")
        else:
            raise DirectDownloadLinkException("ERROR: Mediafire Folder API - Something went wrong during get info!")

    try:
        __get_info(folderkey)
    except DirectDownloadLinkException as e:
        raise e # Re-raise custom exception
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: Mediafire Folder - Info retrieval error: {e.__class__.__name__}: {e}")

    details["title"] = folder_infos[0]["name"]

    def __scraper(url):
        try:
            res = session.get(url)
            res.raise_for_status()
            html = HTML(res.text)
        except Exception:
            return None # Return None if scraping fails, handle in __get_content
        if final_link := html.xpath("//a[@id='downloadButton']/@href"):
            return final_link[0]
        return None # Return None if downloadButton link not found

    def __get_content(folderKey, folderPath="", content_type="folders"):
        try:
            params = {
                "content_type": content_type,
                "folder_key": folderKey,
                "response_format": "json",
            }
            _json = session.get(
                "https://www.mediafire.com/api/1.5/folder/get_content.php",
                params=params,
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: Mediafire Folder API - Get content request failed: {e.__class__.__name__}: {e}"
            )
        _res = _json["response"]
        if "message" in _res:
            error_msg = _res.get('message', 'Unknown Mediafire Folder error')
            raise DirectDownloadLinkException(f"ERROR: Mediafire Folder API - {error_msg}")
        _folder_content = _res["folder_content"]
        if content_type == "folders":
            folders = _folder_content["folders"]
            for folder in folders:
                if folderPath:
                    newFolderPath = path.join(folderPath, folder["name"])
                else:
                    newFolderPath = path.join(folder["name"])
                __get_content(folder["folderkey"], newFolderPath)
            __get_content(folderKey, folderPath, "files")
        else:
            files = _folder_content["files"]
            for file in files:
                item = {}
                _url = __scraper(file["links"]["normal_download"])
                if not _url: # Handle scraping failure gracefully
                    LOGGER.warning(f"Mediafire Folder - Failed to scrape direct link for file: {file['filename']}")
                    continue # Skip to the next file
                item["filename"] = file["filename"]
                if not folderPath:
                    folderPath = details["title"]
                item["path"] = path.join(folderPath)
                item["url"] = _url
                if "size" in file:
                    size = file["size"]
                    if isinstance(size, str) and size.isdigit():
                        size = float(size)
                    details["total_size"] += size
                details["contents"].append(item)

    try:
        for folder in folder_infos:
            __get_content(folder["folderkey"], folder["name"])
    except DirectDownloadLinkException as e:
        raise e # Re-raise custom exception
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: Mediafire Folder - Content processing error: {e.__class__.__name__}: {e}")
    finally:
        session.close()

    if len(details["contents"]) == 1:
        return (details["contents"][0]["url"], details["header"])
    return details


def doods(url):
    if "/e/" in url:
        url = url.replace("/e/", "/d/")
    parsed_url = urlparse(url)
    with create_scraper() as session:
        try:
            res = session.get(url)
            res.raise_for_status()
            html = HTML(res.text)
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: Doods - Token link fetch failed: {e.__class__.__name__}: {e}"
            )
        link_list = html.xpath("//div[@class='download-content']//a/@href")
        if not link_list:
            raise DirectDownloadLinkException(
                "ERROR: Doods - Token Link not found or download not allowed! Open in browser."
            )
        link = f"{parsed_url.scheme}://{parsed_url.hostname}{link_list[0]}"
        sleep(2) # Wait for 2 seconds as suggested in original code
        try:
            _res = session.get(link)
            _res.raise_for_status()
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: Doods - Download link fetch failed: {e.__class__.__name__}: {e}"
            )
    link_search = search(r"window\.open\('(\S+)'", _res.text)
    if not link_search:
        raise DirectDownloadLinkException("ERROR: Doods - Download link not found in page source, try again")
    return (link_search.group(1), f"Referer: {parsed_url.scheme}://{parsed_url.hostname}/")


def easyupload(url):
    password = ""
    if "::" in url:
        parts = url.split("::")
        if len(parts) == 2:
            url, password = parts
        else:
            raise DirectDownloadLinkException("ERROR: EasyUpload - Invalid link format with password.")

    file_id = url.split("/")[-1]
    with create_scraper() as session:
        try:
            _res = session.get(url)
            _res.raise_for_status()
            first_page_html = HTML(_res.text)
            if first_page_html.xpath("//h6[contains(text(),'Password Protected')]") and not password:
                raise DirectDownloadLinkException(
                    f"ERROR: EasyUpload - {PASSWORD_ERROR_MESSAGE.format(url)}"
                )
            match_obj = search(
                r"https://eu(?:[1-9][0-9]?|100)\.easyupload\.io/action\.php", _res.text
            )
            if not match_obj:
                raise DirectDownloadLinkException(
                    "ERROR: EasyUpload - Failed to get server for EasyUpload Link"
                )
            action_url = match_obj.group()
            session.headers.update({"referer": "https://easyupload.io/"})
            recaptcha_params = {
                "k": "6LfWajMdAAAAAGLXz_nxz2tHnuqa-abQqC97DIZ3",
                "ar": "1",
                "co": "aHR0cHM6Ly9lYXN5dXBsb2FkLmlvOjQ0Mw..",
                "hl": "en",
                "v": "0hCdE87LyjzAkFO5Ff-v7Hj1",
                "size": "invisible",
                "cb": "c3o5vbaxbmwe",
            }
            captcha_token = get_captcha_token(session, recaptcha_params)
            if not captcha_token:
                raise DirectDownloadLinkException("ERROR: EasyUpload - Captcha token not found")
            data = {
                "type": "download-token",
                "url": file_id,
                "value": password,
                "captchatoken": captcha_token,
                "method": "regular",
            }
            json_resp = session.post(url=action_url, data=data).json()
            if "download_link" in json_resp:
                return json_resp["download_link"]
            elif "data" in json_resp:
                error_msg = json_resp["data"]
                raise DirectDownloadLinkException(
                    f"ERROR: EasyUpload API - Failed to generate direct link due to: {error_msg}"
                )
            else:
                raise DirectDownloadLinkException(
                    "ERROR: EasyUpload API - Failed to generate direct link (Unknown response)."
                )

        except DirectDownloadLinkException as e:
            raise e # Re-raise custom exception
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: EasyUpload - General processing error: {e.__class__.__name__}: {e}")


def filelions(url):
    if not config_dict["FILELION_API"]:
        raise DirectDownloadLinkException(
            "ERROR: FileLions - FILELION_API is not provided. Get it from https://filelions.com/?op=my_account"
        )
    file_code = url.split("/")[-1]
    quality = ""
    if file_code.endswith(("_o", "_h", "_n", "_l")):
        spited_file_code = file_code.rsplit("_", 1)
        quality = spited_file_code[1]
        file_code = spited_file_code[0]
    parsed_url = urlparse(url)
    url = f"{parsed_url.scheme}://{parsed_url.hostname}/{file_code}"
    with Session() as session:
        try:
            _res = session.get(
                "https://api.filelions.com/api/file/direct_link",
                params={
                    "key": config_dict["FILELION_API"],
                    "file_code": file_code,
                    "hls": "1",
                },
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: FileLions API - Request failed: {e.__class__.__name__}: {e}")

    if _res["status"] != 200:
        error_msg = _res.get('msg', 'Unknown FileLions error')
        raise DirectDownloadLinkException(f"ERROR: FileLions API - {error_msg}")
    result = _res["result"]
    if not result["versions"]:
        raise DirectDownloadLinkException("ERROR: FileLions - No versions available")
    error = "\nProvide a quality to download the video\nAvailable Quality:"
    for version in result["versions"]:
        if quality == version["name"]:
            return version["url"]
        elif version["name"] == "l":
            error += f"\nLow"
        elif version["name"] == "n":
            error += f"\nNormal"
        elif version["name"] == "o":
            error += f"\nOriginal"
        elif version["name"] == "h":
            error += f"\nHD"
        error += f" <code>{url}_{version['name']}</code>"
    raise DirectDownloadLinkException(f"ERROR: FileLions - {error}")


def streamvid(url: str):
    file_code = url.split("/")[-1]
    parsed_url = urlparse(url)
    url = f"{parsed_url.scheme}://{parsed_url.hostname}/d/{file_code}"
    quality_defined = url.endswith(("_o", "_h", "_n", "_l"))
    with create_scraper() as session:
        try:
            res = session.get(url)
            res.raise_for_status()
            html = HTML(res.text)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: StreamVid - Initial request failed: {e.__class__.__name__}: {e}")

        if quality_defined:
            data = {}
            inputs_list = html.xpath('//form[@id="F1"]//input')
            if not inputs_list:
                raise DirectDownloadLinkException("ERROR: StreamVid - No inputs found in form F1")
            for i in inputs_list:
                if key := i.get("name"):
                    data[key] = i.get("value")
            try:
                res = session.post(url, data=data)
                res.raise_for_status()
                html = HTML(res.text)
            except Exception as e:
                raise DirectDownloadLinkException(f"ERROR: StreamVid - Post request failed: {e.__class__.__name__}: {e}")

            script_list = html.xpath(
                '//script[contains(text(),"document.location.href")]/text()'
            )
            if not script_list:
                error_list = html.xpath(
                    '//div[@class="alert alert-danger"][1]/text()[2]'
                )
                if error_list:
                    raise DirectDownloadLinkException(f"ERROR: StreamVid - {error_list[0]}")
                raise DirectDownloadLinkException(
                    "ERROR: StreamVid - Direct link script not found!"
                )
            directLink_search = findall(r'document\.location\.href="(.*)"', script_list[0])
            if directLink_search:
                return directLink_search[0]
            raise DirectDownloadLinkException(
                "ERROR: StreamVid - Direct link not found! in the script"
            )
        elif (qualities_urls := html.xpath('//div[@id="dl_versions"]/a/@href')) and (
            qualities := html.xpath('//div[@id="dl_versions"]/a/text()[2]')
        ):
            error = "\nProvide a quality to download the video\nAvailable Quality:"
            for quality_url, quality in zip(qualities_urls, qualities):
                error += f"\n{quality.strip()} <code>{quality_url}</code>"
            raise DirectDownloadLinkException(f"ERROR: StreamVid - {error}")
        elif error_list := html.xpath('//div[@class="not-found-text"]/text()'):
            raise DirectDownloadLinkException(f"ERROR: StreamVid - {error_list[0]}")
        else:
            raise DirectDownloadLinkException("ERROR: StreamVid - Something went wrong")

def instagram(link: str) -> str:
    """
    Fetches the direct video download URL from an Instagram post.

    Args:
        link (str): The Instagram post URL.

    Returns:
        str: The direct video URL.

    Raises:
        DirectDownloadLinkException: If any error occurs during the process.
    """

    full_url = f"https://instagramcdn.vercel.app/api/video?postUrl={link}"

    try:
        response = get(full_url)
        response.raise_for_status()
        data = response.json()

        if (
            data.get("status") == "success"
            and "data" in data
            and "videoUrl" in data["data"]
        ):
            return data["data"]["videoUrl"]

        raise DirectDownloadLinkException("ERROR: Instagram API - Failed to retrieve video URL.")

    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: Instagram API - {e.__class__.__name__}: {e}")

def devupload(url):
    """
    Extracts direct download link from devupload.com.

    Args:
        url (str): Devupload URL.

    Returns:
        str: Direct download link.

    Raises:
        DirectDownloadLinkException: If direct link extraction fails.
    """
    print(f"DEBUG: Entered devupload function for url: {url}") # DEBUG print
    with create_scraper() as session:
        try:
            res = session.get(url)
            res.raise_for_status()
            html = HTML(res.text)

            # Find the download form
            form = html.xpath('//form[@id="form-download"]')
            if not form:
                raise DirectDownloadLinkException("ERROR: Devupload - Download form not found.")
            form = form[0]

            # Extract form action URL and data
            action_url = urljoin(url, form.get('action', '.')) # Use urljoin to handle relative URLs
            data = {}
            for input_field in form.xpath('.//input'):
                name = input_field.get('name')
                value = input_field.get('value')
                if name:
                    data[name] = value

            print(f"DEBUG: Devupload form action_url: {action_url}") # DEBUG print
            print(f"DEBUG: Devupload form data: {data}") # DEBUG print

            # Simulate form submission
            res = session.post(action_url, data=data, headers={'Referer': url}) # Add Referer header
            res.raise_for_status()
            html = HTML(res.text)

            # Find the direct download link
            dl_button = html.xpath('//a[@id="download_link"]/@href') # Check for download_link again after form submission
            if dl_button:
                print(f"DEBUG: Devupload direct link found: {dl_button[0]}") # DEBUG print
                return dl_button[0]
            else:
                # Check for alternative download button or error messages
                dl_button_alt = html.xpath('//a[contains(@class, "btn-primary") and contains(@href, "download")]/@href') # Look for a primary button with download in href
                if dl_button_alt:
                    dl_link_alt_url = urljoin(url, dl_button_alt[0])
                    print(f"DEBUG: Devupload alternative direct link found: {dl_link_alt_url}") # DEBUG print
                    return dl_link_alt_url

                error_message = html.xpath('//div[@class="alert alert-danger"]/text()') # Check for error messages
                if error_message:
                    raise DirectDownloadLinkException(f"ERROR: Devupload - {error_message[0].strip()}")

                raise DirectDownloadLinkException("ERROR: Devupload - Direct download link not found after form submission.")

        except DirectDownloadLinkException as e:
            raise e
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: Devupload - {e.__class__.__name__}: {e}")