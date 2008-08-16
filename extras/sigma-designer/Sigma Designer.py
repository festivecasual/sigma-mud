import wx, wx.stc

def main():
	app = DesignerApp()
	app.MainLoop()

class DesignerApp(wx.App):
	def OnInit(self):
		frame = DesignerFrame(None, title="Sigma Designer")
		self.SetAppName("Sigma Designer")
		self.SetTopWindow(frame)
		
		frame.Show(True)		
		return True

class DesignerFrame(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, -1, title, pos=(150, 50), size=(700, 500))

		splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
		
		tree = wx.TreeCtrl(splitter)
		
		tabs = wx.Notebook(splitter)
		design_tab = wx.NotebookPage(tabs)
		source_tab = wx.NotebookPage(tabs)
		tabs.AddPage(design_tab, "Design")
		tabs.AddPage(source_tab, "Source")
		
		source = wx.stc.StyledTextCtrl(source_tab)
#		source.SetReadOnly(True)
		source.SetLexer(wx.stc.STC_LEX_XML)
		source.SetKeyWords(0, keywords)
		
		source.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "face:%(mono)s,size:%(size)d" % faces)
		source.StyleClearAll()
		
		source.StyleSetSpec(wx.stc.STC_H_TAG, "fore:#808000,bold")
		source.StyleSetSpec(wx.stc.STC_H_ATTRIBUTE, "fore:#000050")
		source.StyleSetSpec(wx.stc.STC_H_DOUBLESTRING, "fore:#d03030")
		
		splitter.SplitVertically(tree, tabs, 200)

keywords = "area room exit populator placement name flag item target id keywords desc denizen dir altmsg focus"

if wx.Platform == '__WXMSW__':
    faces = { 
              'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Arial',
              'size' : 10,
            }
elif wx.Platform == '__WXMAC__':
    faces = {
              'times': 'Times New Roman',
              'mono' : 'Monaco',
              'helv' : 'Arial',
              'size' : 10,
            }
else:
    faces = {
              'times': 'Times',
              'mono' : 'Courier',
              'helv' : 'Helvetica',
              'size' : 10,
            }

if __name__ == "__main__":
	main()