from archive import Archive
from libsigma import *


@handler()
def player_quit(data):
    speaker = data["speaker"]

    if is_player(speaker):
        speaker.send_line("Goodbye.")
        speaker.socket.handle_close()
    else:
        speaker.send_line("Only players can quit.")


@handler()
def player_save(data):
    speaker = data["speaker"]

    if is_player(speaker):
        a = Archive()
        a.save(speaker)
        data["speaker"].send_line("Game saved.")
    else:
        speaker.send_line("Only players can save.")
