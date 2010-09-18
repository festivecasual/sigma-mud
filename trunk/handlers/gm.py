from libsigma import *
import feats


#TODO: Requires checking for GM status eventually
#TODO: Integrate with tabulation function
@handler()
def gm(data):
    speaker=data["speaker"]
    args=data["args"]
    if len(args) < 2:
        speaker.send_line("Available GM commands:")
        speaker.send_line("   getstance <stance>       Force stance add")
    elif args[1] == 'getstance':
        data["args"] = data["args"][1:]
        gm_getstance(data)
    elif args[1] == 'recover':
        speaker.HP = speaker.max_HP
        speaker.send_line("Ok.")


def gm_getstance(data):
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
