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
        speaker.send_line("   recover                  Restores all health/magic")
        speaker.send_line("   learnallspells           Gives you knowledge of all spells")
    elif args[1] == 'getstance':
        data["args"] = data["args"][1:]
        gm_getstance(data)
    elif args[1] == 'recover':
        speaker.HP = speaker.max_HP
        speaker.MP = speaker.max_MP
        speaker.send_line("Ok.")
    elif args[1] == 'learnallspells':
        for spell_key in feats.spells:
            if feats.spells[spell_key] not in speaker.spells:
                speaker.spells.append(feats.spells[spell_key])
                speaker.send_line("Learned " + feats.spells[spell_key].name + '!')
def gm_getstance(data):
    speaker=data["speaker"]
    args=data["args"]
    if len(args)<2:
        return
    if args[1] in feats.stances:
        speaker.add_stance(feats.stances[args[1]])
        speaker.send_line("Ok.")
    else:
        speaker.send_line("Could not find that stance, " + args[1] + ".")
    return


