"""Basic Python wrapper for communicating with Kodi over JSON RPC.

This program can play streams on a remote Kodi setup.
Kodi needs to be configured to accept JSON-RPC payload as detailed in the
official Wiki:
https://kodi.wiki/view/JSON-RPC_API

This program requires the youtube_dl package:
https://youtube-dl.org/

Example Usage
-------------

Play YouTube Video:
python3 kodi.py -k 192.168.1.50:8080 play -y "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

Play Stream:
python3 kodi.py -k 192.168.1.50:8080 play -s "http://glzwizzlv.bynetcdn.com/glglz_rock_mp3?awCollectionId=misc&awEpisodeId=glglz_rock"

Play Song by ID:
python3 kodi.py -k 192.168.1.50:8080 play -g 101

Stop Playback:
python3 kodi.py -k 192.168.1.50:8080 stop

Sources:
    https://github.com/Dvd848/macro_keyboard

License:
    LGPL v2.1

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

"""

import argparse
import enum
import requests
import time

from collections import namedtuple
from pprint import pprint

class KodiPlayer():
    """Wrapper for communicating with Kodi over JSON-RPC."""

    Album = namedtuple("Album", "id label")
    Song = namedtuple("Song", "id label")

    def __init__(self, host: str):
        """Initialize class.

        Args:
            host:
                Hostname/IP and port in the format 'host:port'.
        """
        self.host = host

    def play_youtube(self, url: str) -> None:
        """Play a YouTube stream.

        Args:
            url:
                URL of the public video page. Actual stream URL is fetched automatically.
        """
        from youtube_dl import YoutubeDL
        with YoutubeDL({'format': 'bestaudio'}) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            try:
                video_url = info_dict['formats'][0]['url']
                return self.play_stream(video_url)
            except IndexError:
                raise RuntimeError(f"Can't find stream URL for youtube video {url}")

    def play_stream(self, url: str) -> None:
        """Play a stream.

        Args:
            url:
                URL of the stream.
        """
        json_req = {"method": "Player.Open", "id": int(time.time()) , "jsonrpc": "2.0", "params": {"item": {"file": url}}}
        return self._send_request(json_req)

    def play_song(self, songid: int) -> None:
        """Play a song.

        Args:
            songid:
                The song's ID.
        """
        json_req = {"method": "Player.Open", "id": int(time.time()) , "jsonrpc": "2.0", "params": {"item": {"songid": songid}}}
        return self._send_request(json_req)

    def get_active_players(self):
        """Returns a list of active player IDs."""
        json_req = {"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": int(time.time())}
        response = self._send_request(json_req)
        return [result["playerid"] for result in response["result"]]

    def stop(self) -> None:
        """Stop the current active players."""
        active_players = self.get_active_players()
        result = []
        for id in active_players:
            json_req = {"method": "Player.Stop", "id": int(time.time()) , "jsonrpc": "2.0", "params": { "playerid": id }}
            result.append(self._send_request(json_req))
        return result[0] if len(result) == 1 else result

    def _send_request(self, json_req):
        """Send a JSON request to the remote Kodi.

        Args:
            json_req: JSON request to send.
        
        Returns:
            The JSON response if the response code was OK (raises exception otherwise).
        """
        print(json_req)
        r = requests.post(f"http://{self.host}/jsonrpc", json=json_req)
        if (r.status_code != 200):
            raise RuntimeError(f"Got status code {r.status_code}")
        return r.json()

    def get_albums(self):
        """Return a list of albums."""
        json_req = {"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "id": int(time.time())}
        response = self._send_request(json_req)
        result = []
        albums = response["result"]["albums"]
        for album in albums:
            result.append(self.Album(id = album["albumid"], label = album["label"]))
        return result

    def get_songs(self):
        """Return a list of songs."""
        json_req = {"jsonrpc": "2.0", "method": "AudioLibrary.GetSongs", "id": int(time.time())}
        response = self._send_request(json_req)
        result = []
        songs = response["result"]["songs"]
        for song in songs:
            result.append(self.Song(id = song["songid"], label = song["label"]))
        return result
    
    def get_audio_output(self):
        """Return audio output device."""
        json_req = {"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "id": int(time.time()), 
                    "params": {"setting": "audiooutput.audiodevice"}}
        response = self._send_request(json_req)
        return response["result"]["value"]
    
    def set_audio_output(self, device):
        """Set audio output device."""
        json_req = {"jsonrpc": "2.0", "method": "Settings.SetSettingValue", "id": int(time.time()), 
                    "params": {"setting": "audiooutput.audiodevice", "value": device}}
        response = self._send_request(json_req)
        return response["result"]
        

if __name__ == "__main__":
    class Commands(enum.Enum):
        """Commands for argument parsing."""
        PLAY    = "play"
        STOP    = "stop"
        LIST    = "list"
        AUDIO   = "audio"

    parser = argparse.ArgumentParser(description = 'Wrapper for controlling Kodi from remote')
    parser.add_argument("-k", "--kodi-host", required = True, help="Kodi URL in form of host:port")

    subparsers = parser.add_subparsers(dest = 'command', required = True, title = 'subcommands',
                                       description = 'Valid subcommands')

    play_parser = subparsers.add_parser(Commands.PLAY.value, help = 'Play media')
    play_command = play_parser.add_mutually_exclusive_group(required = True)
    play_command.add_argument('-s', '--stream', action = 'store', type = str, help = "Play stream")
    play_command.add_argument('-y', '--youtube', action = 'store', type = str, help = "Play YouTube video")
    play_command.add_argument('-g', '--song', action = 'store', type = int, metavar = "SONG_ID", help = "Play song with given song ID")

    stop_parser = subparsers.add_parser(Commands.STOP.value, help = 'Stop')

    list_parser = subparsers.add_parser(Commands.LIST.value, help = 'List details')
    list_command = list_parser.add_mutually_exclusive_group(required = True)
    list_command.add_argument('--albums', action = 'store_true', help = "List albums")
    list_command.add_argument('--songs', action = 'store_true', help = "List songs")

    audio_parser = subparsers.add_parser(Commands.AUDIO.value, help = 'Audio Settings')
    audio_command = audio_parser.add_mutually_exclusive_group(required = True)
    audio_command.add_argument('--get-output', action = 'store_true', help = "Get Audio Output Device")
    audio_command.add_argument('--set-output', action = 'store', help = "Set Audio Output Device") # "ALSA:@" / "ALSA:sysdefault:CARD=Headphones"

    args = parser.parse_args()

    try:
        player = KodiPlayer(args.kodi_host)
        if args.command == Commands.PLAY.value:
            if args.youtube:
                print(player.play_youtube(args.youtube))
            elif args.stream:
                print(player.play_stream(args.stream))
            elif args.song:
                print(player.play_song(args.song))
        elif args.command == Commands.STOP.value:
            print(player.stop())
        elif args.command == Commands.LIST.value:
            if args.albums:
                pprint(player.get_albums())
            elif args.songs:
                pprint(player.get_songs())
        elif args.command == Commands.AUDIO.value:
            if args.get_output:
                print(player.get_audio_output())
            elif args.set_output:
                print(player.set_audio_output(args.set_output))

    except Exception as e:
        print(f"Error: {str(e)}")
    except KeyboardInterrupt:
        print ("\nQuitting...")