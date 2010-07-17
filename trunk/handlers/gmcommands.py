from libsigma import *
import feats



@handler()
def gmgetstance(data):
    speaker=data["speaker"]
    args=data["args"]
    if len(args)<2:
        return
    if feats.stances.has_key(args[1]):
        speaker.add_stance(feats.stances[args[1]])
        speaker.send_line("Ok.")
    else:
        speaker.send_line("Could not find that stance, " + args[1] + ".")
    return