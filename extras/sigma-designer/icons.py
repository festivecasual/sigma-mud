import embeddedimage

# ***************** Catalog starts here *******************

catalog = {}
index = []

#----------------------------------------------------------------------
Save = embeddedimage.PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAz1J"
    "REFUWIXll0FLI0kUx3+liensxgwiZCNsDsllh5z0EyjjbS6CH2CFOXjczZfwLHOc+BX8ACLs"
    "woJHEZTgJWjEm0qWjY0m6aquzGGsnupOp9MZve0fHl1d9XjvX//3uuiC/zuEGezu7v4FfDDv"
    "X5rNVAEkMBSCPjAEpBCxfn98/IjW2tjfx8fHmwAZy+dDs9kUAI1GY/RWiQ0cx+Hw8FAAbG5u"
    "BvFtAuHEI3s4Cp5mLEYjcqMRCy9zSaa1xv/0ia2trZHWGtd1g9ghAlHYiW0Cs5rWGt/38X0f"
    "rTVKqXECcUnOzs4SZQV47PUS1xcWFvjt/XuUUkEP+L4/TsAs2gRWV1dDsiftcJoCqQikCfaj"
    "BIz8E0tgfSIzE0njm0oB3/eDgFprWq3Wq3sgm81SrdVCTZjYA/Zu6vV6aoln6YHYEhiGtgKz"
    "JEhaB36sBLPU2PaB8S/GbsJYAnEKtNvtV/dAJpPh10plugJ2kxir1WpTFSiXy7GSR8epFYhr"
    "xjQliMpu3u34b05gUlI7sYEpgVEjloBdp52dnRCZKLlp85MskUBUprdIOBMBW4G32L39RUXf"
    "ExWwA1erVba3t6lUKiwuLlIsFikUCjiOw/z8PEopHh8f6Xa73N/f8/DwQLfb5fr6mlarhVIK"
    "KSW9Xo+bm5vJCiilxhQAKBQKLC0tAXBwcECn00EIQblcZn9/f6zZDPL5PKenp2ityefzlEql"
    "sdixCti7F0KEnI+OjoK1i4sL7u7uKJVKE0mYg811XYrF4nQCnucB349lEfnRjNZ8Guza9/v9"
    "UB8YzJmBlPLz8/MznuehlArUiBKwLQnR088QiJIPCJyfnzeklJ/7/X5AwhAxsOeMvGkU0Foz"
    "GAwC/1gCAJeXlwEJKSW+7yOlDNaFEKHdO44zVQVjw+EwNG8w9lvebrcb1WoVKeWfuVwu6AuA"
    "vb09Tk5OyGQybGxssLy8HPq5iFPAwPM8stnsmH+UwE/Au06ns7+ysrKktf7ddV1ub2+p1+us"
    "ra2xvr4enANJuLq64unpKdjt3Nwcg8HALP8D/AL8F71P/Qy8A7JAnm93R/Eyfi2eX54aGAAe"
    "8G/yhS4Z80AuZr4PTL1bGnwFAT821rECXFYAAAAASUVORK5CYII=")
index.append('Save')
catalog['Save'] = Save
getSaveData = Save.GetData
getSaveImage = Save.GetImage
getSaveBitmap = Save.GetBitmap
getSaveIcon = Save.GetIcon

#----------------------------------------------------------------------
Folder = embeddedimage.PyEmbeddedImage(
    "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"
    "4it+Vv8b9jfWmVcIVQayqgAAAABJRU5ErkJggg==")
index.append('Folder')
catalog['Folder'] = Folder
getFolderData = Folder.GetData
getFolderImage = Folder.GetImage
getFolderBitmap = Folder.GetBitmap
getFolderIcon = Folder.GetIcon

#----------------------------------------------------------------------
Designer = embeddedimage.PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAABJ1J"
    "REFUWIXt1k9o21YcB/DvcyQF23ImOXFqx21G/pe2WTbYDh2DmG6HhLKSbaSjsMFGD4OQ9dZR"
    "GE0vCzv1VOgh7SDNCjmtGWpKEhZW2ymDUrLVJNCULsWOyWK3jezG1pOsSH47LAmlpGvzx6ft"
    "e5P0++l9eE/vIeD//NdDXrUwGo36CCG1tm0LAPKhUGim5ICbN282OhyO0wCOAgiu319aWoKi"
    "KHokEhm3LOuHdDp9Y9cBkUjkU8bYkCRJwt69e+FyuTA7O4vp6Wlcu3btz1gs9pTn+aAsy36/"
    "3z9TU1PTOTQ0tLhVAPeCwXsJIReampoQCAQAAPPz85iYmICiKB/fuXNnZL22ra3N39jYeKyu"
    "rs63HcBmg383NTXFMpkMW0+xWGTj4+Osubn5wY4HeC6OZy+i0egBAN8GAgFIkgQAsCwLqqri"
    "4MGDqK2trW9paWkpGYAxJgJAVVUVHj16hFgshpGREdy7dw+CIODSpUuOzs7O6z09PeJuAQgA"
    "hMPhYwC+J4T4KysrvblcDpOTk6aiKAOJROJXp9P5UWtr6+f9/f3w+XyYmpqKEUIOHz9+XN+x"
    "IBqNHohEIlYqlWK6rrN4PM5OnTr1R0NDQ+OzdV1dXe/19fWlHz58yDKZDFMU5fb58+edOwYA"
    "QDgcvjAzM8NyuRwbGBhgwWDwzGZ1Fy9ebBkcHPwrHo+zXC7HhoeHfzt37pywk7EdABAKhb6+"
    "devWj729vTh79iwAbLqdenp67lNKP1QUxVxeXobb7T6cTCbnuru7y7YL2DiIuru7yyKRyGWn"
    "0xlJJBKD/9bU19d3MpVKXc5ms1hdXcWTJ08WFxYW3k4kEqltA7aaI0eO/L68vPyW1+sFIQSL"
    "i4tPs9lsVzqdDm/lPY6Xl2ye1dXVo/l8ns7Pz8OyLASDwdfcbveYz+f7Zivv2fbaLSws5GVZ"
    "vmsYxolsNkskSYLX6+UopSGe5yVK6SQAVjIAAGQymQcej8djWda7uVwOsizD6/WWUUrf4Xk+"
    "QCkdexliRwAAyOfzv4ii+IFlWbXrCFmWHbquv8lx3OtriGLJAABQVVU1bNv2F5ZlVWiaBlmW"
    "IUmSQ9f1Vo7jmmpqam6oqmpv1rvtXfB8/H6/r1gs3gcgi6KIuro6MMYQj8etlZWVnwkhXz5+"
    "/Dj/fN+uzAAA5PN56nK5fiKEnDRNUzAMA5Ikrc9Es2mab/A8P1EoFIySAACAUqq6XK4wIeSz"
    "QqHAmaa5gaCUNti23ebxeCY1TdNKAlhDJN1u9wyATwzDKLNtGxUVFZAkyWEYxj5d1/dRSkex"
    "9mHuOgAANE27L4piEsAxSilhjMHj8cDpdHKqqlY7nU6DUnq7ZIA1xF1RFAsA3tc0jdi2jVQq"
    "Bdu2CSEkTSm9DuziLmhvb+c8Ho8AAJWVlcUrV64YALBnz55+xtgZ/HPsM8bYmG3bJ1RVXdkS"
    "oL29nfN6vT5BEFwABNM0yziOK39Z39zcHJLJZAfP81/xPD996NCh09XV1UtXr17VgBf8lr8o"
    "5eXlhLGNk/WVlm///v0AMFZfX68IgmACMJ99vmtL0NHRUc5x3AZqdHSUvkrf30s2HqBNhECX"
    "AAAAAElFTkSuQmCC")
index.append('Designer')
catalog['Designer'] = Designer
getDesignerData = Designer.GetData
getDesignerImage = Designer.GetImage
getDesignerBitmap = Designer.GetBitmap
getDesignerIcon = Designer.GetIcon

