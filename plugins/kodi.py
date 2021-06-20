from youtube_dl import YoutubeDL
import argparse
import enum
import requests
import time

class KodiPlayer():
    def __init__(self, host: str):
        self.host = host

    def play_youtube(self, url: str) -> None:
        with YoutubeDL({'format': 'bestaudio'}) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            try:
                video_url = info_dict['formats'][0]['url']
                return self.play_stream(video_url)
            except IndexError:
                raise RuntimeError(f"Can't find stream URL for youtube video {url}")

    def play_stream(self, url: str) -> None:
        json_req = {"method": "Player.Open", "id": int(time.time()) , "jsonrpc": "2.0", "params": {"item": {"file": url}}}
        return self._send_request(json_req)

    def get_active_players(self):
        json_req = {"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": int(time.time())}
        response = self._send_request(json_req)
        return [result["playerid"] for result in response["result"]]

    def stop(self) -> None:
        active_players = self.get_active_players()
        result = []
        for id in active_players:
            json_req = {"method": "Player.Stop", "id": int(time.time()) , "jsonrpc": "2.0", "params": { "playerid": id }}
            result.append(self._send_request(json_req))
        return result[0] if len(result) == 1 else result

    def _send_request(self, json_req):
        r = requests.post(f"http://{self.host}/jsonrpc", json=json_req)
        if (r.status_code != 200):
            raise RuntimeError(f"Got status code {r.status_code}")
        return r.json()

if __name__ == "__main__":
    class Commands(enum.Enum):
        """Commands for argument parsing."""
        PLAY    = "play"
        STOP    = "stop"

    parser = argparse.ArgumentParser(description = 'Wrapper for controlling Kodi from remote')
    parser.add_argument("-k", "--kodi-host", required = True, help="Kodi URL in form of host:port")

    subparsers = parser.add_subparsers(dest = 'command', required = True, title = 'subcommands',
                                       description = 'Valid subcommands')

    play_parser = subparsers.add_parser(Commands.PLAY.value, help = 'Play media')
    play_command = play_parser.add_mutually_exclusive_group(required = True)
    play_command.add_argument('-s', '--stream', action = 'store', type = str, help = "Play stream")
    play_command.add_argument('-y', '--youtube', action = 'store', type = str, help = "Play YouTube video")

    stop_parser = subparsers.add_parser(Commands.STOP.value, help = 'Stop')

    args = parser.parse_args()

    try:
        player = KodiPlayer(args.kodi_host)
        if args.command == Commands.PLAY.value:
            if args.youtube:
                print(player.play_youtube(args.youtube))
            elif args.stream:
                print(player.play_stream(args.stream))
        elif args.command == Commands.STOP.value:
            print(player.stop())

    except Exception as e:
        print(f"Error: {str(e)}")
    except KeyboardInterrupt:
        print ("\nQuitting...")