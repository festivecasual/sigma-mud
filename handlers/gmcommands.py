from libsigma import *
import feats



@handler()
def gmcreatestance(data):
    speaker=data["speaker"]
    
    s=feats.stance("doppelsoldner","A two-handed technique that deals great damage.",GREATSWORD)
    t=feats.stance("butcher","A slashing technique that focuses on attacking.",KNIFE)
    b=feats.stance("bare", "Get ready to knuckle up!",BARE_HAND)
    j=feats.stance("jiujitsu","Breaking bones and taking names",BARE_HAND)
    feats.stances[s.name]=s
    feats.stances[t.name]=t
    feats.stances[b.name]=b
    feats.stances[j.name]=j
    speaker.send_line("Ok.")
     
    return

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