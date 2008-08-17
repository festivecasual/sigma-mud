# This file synthesizes the auto-generated image code from img2py,
# preceded by the class code from embeddedimage.py that defines
# the embedded image class.

# EMBEDDED FILE
#----------------------------------------------------------------------
# Name:        wx.lib.embeddedimage
# Purpose:     Defines a class used for embedding PNG images in Python
#              code. The primary method of using this module is via
#              the code generator in wx.tools.img2py.
#
# Author:      Anthony Tuininga
#
# Created:     26-Nov-2007
# RCS-ID:      $Id: embeddedimage.py 51013 2008-01-04 22:12:40Z RD $
# Copyright:   (c) 2007 by Anthony Tuininga
# Licence:     wxWindows license
#----------------------------------------------------------------------

import base64
import cStringIO
import wx

class PyEmbeddedImage(object):
    """
    PyEmbeddedImage is primarily intended to be used by code generated
    by img2py as a means of embedding image data in a python module so
    the image can be used at runtime without needing to access the
    image from an image file.  This makes distributing icons and such
    that an application uses simpler since tools like py2exe will
    automatically bundle modules that are imported, and the
    application doesn't have to worry about how to locate the image
    files on the user's filesystem.

    The class can also be used for image data that may be acquired
    from some other source at runtime, such as over the network or
    from a database.  In this case pass False for isBase64 (unless the
    data actually is base64 encoded.)  Any image type that
    wx.ImageFromStream can handle should be okay.
    """

    def __init__(self, data, isBase64=True):
        self.data = data
        self.isBase64 = isBase64

    def GetBitmap(self):
        return wx.BitmapFromImage(self.GetImage())

    def GetData(self):
        return self.data

    def GetIcon(self):
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(self.GetBitmap())
        return icon

    def GetImage(self):
        data = self.data
        if self.isBase64:
            data = base64.b64decode(self.data)
        stream = cStringIO.StringIO(data)
        return wx.ImageFromStream(stream)

    # added for backwards compatibility
    getBitmap = GetBitmap
    getData = GetData
    getIcon = GetIcon
    getImage = GetImage

    # define properties, for convenience
    Bitmap = property(GetBitmap)
    Icon = property(GetIcon)
    Image = property(GetImage)



# ***************** Catalog starts here *******************

catalog = {}
index = []

#----------------------------------------------------------------------
Save = PyEmbeddedImage(
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
Folder = PyEmbeddedImage(
    "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"
    "4it+Vv8b9jfWmVcIVQayqgAAAABJRU5ErkJggg==")
index.append('Folder')
catalog['Folder'] = Folder
getFolderData = Folder.GetData
getFolderImage = Folder.GetImage
getFolderBitmap = Folder.GetBitmap
getFolderIcon = Folder.GetIcon

#----------------------------------------------------------------------
Designer = PyEmbeddedImage(
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

#----------------------------------------------------------------------
New = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAABC5J"
    "REFUWIXllk9oHFUcxz/z3kw2S1M3u+muRGNTAyJV1EBESIVtqBUCvZTaq/RQLHgSFFu9aA8F"
    "b+KhSA+GHgKBxKttwZQWEhVKvYghYNhSUAzV3YTExPyZf8/D7pvOzr5JNunRHzzeY97M+33m"
    "+/u+NwP/97BMF3+YnV2xILeP9aqBUiPlcnn+iQBmZ2ZWhoeHc1gWYRgSBEHU+77f1DzPw3Xd"
    "er+9zcbGxpLtOK8dO3bsz3YARDqa1egshBBRL4RASolt21HvOA6O47DtunQdPNjjue6PMzMz"
    "xf0DKIVlWU1JdbNtO0quE+vW0dFBqVQiXyj0qzC8Oz09vWsZjQBKqYQYFlJKowJxFWzbJpfL"
    "USwW6Tl06OWMbX8/NzfXsWeAMAybILQaGiLea0U0RDabJZ/PUyqVKPX2vlGr1W5OTU3JNAC7"
    "HQU0BIAQgjAMkVJGYHGVADKZDN3d3VqhtwRMAmefCCCuhBDCeL/jOFQqlWh3BEGA53kIId65"
    "c/v2FydOnvx0XwCqYcq4AnEIrUY+n2/aqp7nReNHi4ufAO0BhEHQAqLHcdmTSti2bXwBq3Ge"
    "mMIMkFKCJIgJQvtAzyulEEKkltUMYKCNl0GHlTisktfi6+1JAZMHdoJI+kJ7Qj+X3Na7Amha"
    "00MaInlOxCH0nPaEnmsfoJ7J+IAJLOkL7YP4OM1XRgDCENPtyUT6WrLu2ng6LMtCpSjQbOE5"
    "uljgs48PX+rK/pYlO5+lXClzZfEKa/5aC0iyjxZNfMCklG0oUOGEDOQ3A3Lg+b5iH4NyEEtZ"
    "1LZrTK5MMv77ONdeuMZIYcSY1LT3tQpCiFQF6gALnO0MOr89fuA4BVmom0ABIRTtIsXuIsuZ"
    "ZU7/fJqxl8Y48+yZ1DIkIfQ3Ik0BwQJF4Yvr5WyZgnicfOKZCSb6JgiDENd36RQZhp4b4sK9"
    "C1S3qiilomZSIErQ+JlJ9YDlWh8ckUe6emRPPblujXB9l3V3nb+3qiwFS5CFq79eTd2iyaYh"
    "0j3gcqr/QP9j2RUEjW8BwOzqLMveMgQNMAduVW5x+fXLLdKbSrGbQjYeL+ZFHkKYODzRckN1"
    "qBqN5V0JHfDgrwctSXc6LYEdTLiFVL7Cxzfe0BQBKE/hbrotb9iUzHBapiuwzfziv4uDD4OH"
    "yHsy8kDwZr0M8k79mgpVfe4fOJo72rRo2gEVj/RdsM2N+4v3qW3V6nX2G00vFChUoOpzAahH"
    "itGB0bZMmJwzKqA21ZdqVb0vbFHAoWUX4BOdCaxBoVrg4nsX6ezsNC6YGmm/eQBcZxSf70Sv"
    "kGRicuum6smtXyw+6vuQV3Ov7C15I949dy4HbAJeMwDAV7yNxzjdPG09ZcGBRvLVuuz8wRIV"
    "LnGTn9p530aieGwQucgEAPA5XSjO43MKnyI+EFDF5waKMb5mfU+v3Eb8B1CDZSjcZMibAAAA"
    "AElFTkSuQmCC")
index.append('New')
catalog['New'] = New
getNewData = New.GetData
getNewImage = New.GetImage
getNewBitmap = New.GetBitmap
getNewIcon = New.GetIcon

