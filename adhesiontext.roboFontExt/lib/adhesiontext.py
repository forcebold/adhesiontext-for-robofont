__copyright__ =  """
Copyright (c) 2012-2013, Miguel Sousa
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this list of
  conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice, this list of
  conditions and the following disclaimer in the documentation and/or other materials
  provided with the distribution.
- Neither the name adhesiontext nor the names of its contributors may be used to endorse
  or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

__doc__ = """
adhesiontext for RoboFont

v1.0 - Dec 03 2012 - First release
v1.1 - Dec 26 2012 - Enabled Space Center's RTL-LTR toggling. Improvements and bug fixes in charsCallback()
v1.2 - Mar 16 2013 - Added Indian scripts and languages
"""

#=============================================================

scriptsNameList = "Latin Cyrillic Greek Armenian \
                   Arabic Hebrew \
                   Bengali Devanagari Gujarati Gurmukhi Odia Sinhala Kannada Malayalam Tamil Telugu \
                   Burmese Thai Khmer \
                   Hangul".split()

langsNameDict = {
"Latin"    : "English French German Spanish Catalan Portuguese Dutch Turkish Slovene".split(),
"Cyrillic" : "Russian Ukrainian".split(),
"Greek"    : ["Greek"],
"Armenian" : ["Armenian"],
#-----
"Arabic" : "Arabic Persian".split(),
"Hebrew" : ["Hebrew"],
#-----
"Bengali"    : ["Bengali"],
"Devanagari" : "Hindi Marathi".split(),
"Gujarati"   : ["Gujarati"],
"Gurmukhi"   : ["Punjabi"],
"Odia"       : ["Odia"],
"Sinhala"    : ["Sinhala"],
"Kannada"    : ["Kannada"],
"Malayalam"  : ["Malayalam"],
"Tamil"      : ["Tamil"],
"Telugu"     : ["Telugu"],
#-----
"Burmese" : ["Burmese"],
"Thai"    : ["Thai"],
"Khmer"   : ["Khmer"],
#-----
"Hangul"  : ["Korean"],
}

scriptsTagDict = {
"Latin"    : "latn",
"Cyrillic" : "cyrl",
"Greek"    : "grek",
"Armenian" : "armn",
#-----
"Arabic" : "arab",
"Hebrew" : "hebr",
#-----
"Bengali"    : "beng",
"Devanagari" : "deva",
"Gujarati"   : "gujr",
"Gurmukhi"   : "guru",
"Odia"       : "orya",
"Sinhala"    : "sinh",
"Kannada"    : "knda",
"Malayalam"  : "mlym",
"Tamil"      : "taml",
"Telugu"     : "telu",
#-----
"Burmese" : "mymr",
"Thai"    : "thai",
"Khmer"   : "khmr",
#-----
"Hangul"  : "hang",
}

langsTagDict = {
#--Latin--
"English"    : "eng",
"French"     : "fra",
"German"     : "deu",
"Spanish"    : "esp",
"Catalan"    : "cat",
"Portuguese" : "ptg",
"Dutch"      : "nld",
"Turkish"    : "tur",
"Slovene"    : "slv",
#--Cyrillic--
"Russian"   : "rus",
"Ukrainian" : "ukr",
#-----
"Greek"     : "ell",
"Armenian"  : "hye",
#--Arabic--
"Arabic"    : "ara",
"Persian"   : "fas",
#-----
"Hebrew"    : "heb",
#--Indian--
"Bengali"   : "ben",
"Hindi"     : "hin",
"Marathi"   : "mar",
"Gujarati"  : "guj",
"Punjabi"   : "pan",
"Odia"      : "ori",
"Sinhala"   : "sin",
"Kannada"   : "kan",
"Malayalam" : "mal",
"Tamil"     : "tam",
"Telugu"    : "tel",
#-----
"Burmese" : "brm",
"Thai"    : "tha",
"Khmer"   : "khm",
#-----
"Korean"  : "kor",
}

rightToLeftList = "Arabic Hebrew".split()
enableTrimCheckList = "Latin Cyrillic Greek".split()
enableCaseCheckList = "Latin Cyrillic Greek Armenian".split()
enableFigOptionList = "Arabic \
                       Bengali Devanagari Gujarati Gurmukhi Odia Kannada Malayalam Tamil Telugu \
                       Burmese Thai Khmer".split()

#=============================================================

from mojo.UI import CurrentSpaceCenter, OpenSpaceCenter
from mojo.extensions import getExtensionDefault, setExtensionDefault
from vanilla import FloatingWindow, TextBox, EditText, Button, SquareButton, Slider, ProgressSpinner, PopUpButton, CheckBox
from AppKit import NSBeep, NSWritingDirectionLeftToRight, NSWritingDirectionRightToLeft, NSLeftTextAlignment, NSRightTextAlignment
from defconAppKit.windows.baseWindow import BaseWindowController
import urllib, urllib2
import re

xmlHeader = '<?xml version="1.0" encoding="UTF-8"?>'
re_glyph = re.compile(r'<\?xml version="1\.0" encoding="UTF-8"\?>\s+<glyph[\s\S]+</glyph>\s+')
re_glyphUnicode = re.compile(r'<\s*unicode\s*hex\s*=\s*"([0-9A-Fa-f]{4,5})"\s*/>')
re_glyphName = re.compile(r'<\s*glyph\s*name\s*=\s*"(.+)"\s*format\s*=\s*"\d+"\s*>')
re_numeral = re.compile(r'[0-9]')

url = 'http://remote.adhesiontext.com/'

maxChars = 100

casingNameList = ["UPPER", "lower", "Title"]
figOptionsList = ["Default", "Localized"]

msgStr = "***MESSAGE***"
sndStr = "***SECOND***"
wrnStr = "***WARNING***"
rsltStr = "***RESULT***"

extensionKey = "com.forcebold.adhesiontext"

## vanilla patch by Frederik Berlaen for issue in Lion and Mountain Lion
class FixedSpinner(ProgressSpinner):
	
	def __init__(self, *args, **kwargs):
		super(FixedSpinner, self).__init__(*args, **kwargs)
		self.show(False)
	
	def start(self):
		self.show(True)
		super(FixedSpinner, self).start()
	
	def stop(self):
		self.show(False)
		super(FixedSpinner, self).stop()
## end vanilla patch


class CheckBoxPlus(CheckBox):
	"""
	Same as CheckBox but with isEnable() method.
	"""
	def __init__(self, *args, **kwargs):
		super(CheckBoxPlus, self).__init__(*args, **kwargs)
	
	def isEnable(self):
		"""
		Return a bool indicating if the object is enable or not.
		"""
		return self._nsObject.isEnabled()


class Adhesiontext(BaseWindowController):

	def __init__(self):
		flushAlign = 76
		firstRowY = 12
		rowOffsetY = 30
		firstCheckY = 135
		checkOffsetY = 27
		rightMarginX = -12
		self.windowWidth = 410
		self.windowHeightWithoutOptions = 45
		self.windowHeightWithOptions = 280
		self.scriptIsRTL = False

		windowPos = getExtensionDefault("%s.%s" % (extensionKey, "windowPos"))
		if not windowPos:
			windowPos = (100, 100)
		
		self.optionsVisible = getExtensionDefault("%s.%s" % (extensionKey, "optionsVisible"))
		if self.optionsVisible:
			optionsButtonSign = '-'
			windowHeight = self.windowHeightWithOptions
		else:
			self.optionsVisible = False # needs to be set because the first time the extension runs self.optionsVisible will be None
			optionsButtonSign = '+'
			windowHeight = self.windowHeightWithoutOptions

		self.chars = getExtensionDefault("%s.%s" % (extensionKey, "chars"))
		if not self.chars:
			self.chars = ''
		
		self.sliderValue = getExtensionDefault("%s.%s" % (extensionKey, "sliderValue"))
		if not self.sliderValue:
			self.sliderValue = 25
		
		self.scriptsIndex = getExtensionDefault("%s.%s" % (extensionKey, "scriptsIndex"))
		if not self.scriptsIndex:
			self.scriptsIndex = 0
		
		self.langsIndex = getExtensionDefault("%s.%s" % (extensionKey, "langsIndex"))
		if not self.langsIndex:
			self.langsIndex = 0
		
		
		self.w = FloatingWindow((windowPos[0], windowPos[1], self.windowWidth, windowHeight), "adhesiontext")
		
		# 1st row
		self.w.labelChars = TextBox((10, firstRowY, flushAlign, 20), "Characters:", alignment="right")
		self.w.chars = EditText((flushAlign +15, firstRowY -1, 199, 22), self.chars, callback=self.charsCallback)
		self.w.button = Button((300, firstRowY, 68, 20), "Get text", callback=self.buttonCallback)
		self.w.spinner = FixedSpinner((325, firstRowY, 20, 20), displayWhenStopped=False)
		self.w.optionsButton = SquareButton((378, firstRowY +1, 18, 18), optionsButtonSign, sizeStyle="small", callback=self.optionsCallback)
		# set the initial state of the button according to the content of the chars EditText
		if len(self.w.chars.get()): self.w.button.enable(True)
		else: self.w.button.enable(False)
		# keep track of the content of chars EditText
		self.previousChars = self.w.chars.get()
		
		# 2nd row
		self.w.labelWords = TextBox((10, firstRowY + rowOffsetY, flushAlign, 20), "Words:", alignment="right")
		self.w.wordCount = TextBox((flushAlign +12, firstRowY + rowOffsetY, 40, 20), alignment="left")
		self.w.slider = Slider((flushAlign +47, firstRowY + rowOffsetY +1, 165, 20), value=self.sliderValue, minValue=5, maxValue=200, callback=self.sliderCallback)
		# set the initial wordCount value according to the position of the slider
		self.w.wordCount.set(int(self.w.slider.get()))
		
		# 3rd row
		self.w.labelScripts = TextBox((10, firstRowY + rowOffsetY *2, flushAlign, 20), "Script:", alignment="right")
		self.w.scriptsPopup = PopUpButton((flushAlign +15, firstRowY + rowOffsetY *2, 150, 20), scriptsNameList, callback=self.scriptsCallback)
		self.w.scriptsPopup.set(self.scriptsIndex)
		
		# 4th row
		self.w.labelLangs = TextBox((10, firstRowY + rowOffsetY *3, flushAlign, 20), "Language:", alignment="right")
		self.w.langsPopup = PopUpButton((flushAlign +15, firstRowY + rowOffsetY *3, 150, 20), [])
		# set the initial list of languages according to the script value
		self.w.langsPopup.setItems(langsNameDict[scriptsNameList[self.w.scriptsPopup.get()]])
		self.w.langsPopup.set(self.langsIndex)
		
		self.punctCheck = getExtensionDefault("%s.%s" % (extensionKey, "punctCheck"))
		if not self.punctCheck:
			self.punctCheck = 0
		
		self.figsCheck = getExtensionDefault("%s.%s" % (extensionKey, "figsCheck"))
		if not self.figsCheck:
			self.figsCheck = 0
		
		self.figsPopup = getExtensionDefault("%s.%s" % (extensionKey, "figsPopup"))
		if not self.figsPopup:
			self.figsPopup = 0
		
		self.trimCheck = getExtensionDefault("%s.%s" % (extensionKey, "trimCheck"))
		if not self.trimCheck:
			self.trimCheck = 0
		
		self.caseCheck = getExtensionDefault("%s.%s" % (extensionKey, "caseCheck"))
		if not self.caseCheck:
			self.caseCheck = 0
		
		self.casingCheck = getExtensionDefault("%s.%s" % (extensionKey, "casingCheck"))
		if not self.casingCheck:
			self.casingCheck = 0
		
		self.casingPopup = getExtensionDefault("%s.%s" % (extensionKey, "casingPopup"))
		if not self.casingPopup:
			self.casingPopup = 0
		
		# 1st checkbox
		self.w.punctCheck = CheckBox((flushAlign +15, firstCheckY, 130, 20), "Add punctuation")
		self.w.punctCheck.set(self.punctCheck)
		
		# 2nd checkbox
		self.w.figsCheck = CheckBox((flushAlign +15, firstCheckY + checkOffsetY, 120, 20), "Insert numbers", callback=self.figsCallback)
		self.w.figsCheck.set(self.figsCheck)
		self.w.figsPopup = PopUpButton((210, firstCheckY + checkOffsetY, 90, 20), figOptionsList)
		self.w.figsPopup.set(self.figsPopup)
		# enable or disable the figure options PopUp depending on the figures CheckBox
		if scriptsNameList[self.w.scriptsPopup.get()] in enableFigOptionList:
			self.w.figsPopup.show(True)
			if self.w.figsCheck.get():
				self.w.figsPopup.enable(True)
			else:
				self.w.figsPopup.enable(False)
		else:
			self.w.figsPopup.show(False)
		
		# 3rd checkbox
		self.w.trimCheck = CheckBoxPlus((flushAlign +15, firstCheckY + checkOffsetY *2, 120, 20), "Trim accents")
		self.w.trimCheck.set(self.trimCheck)
		if scriptsNameList[self.w.scriptsPopup.get()] in enableTrimCheckList:
			self.w.trimCheck.enable(True)
		else:
			self.w.trimCheck.enable(False)
		
		# 4th checkbox
		self.w.caseCheck = CheckBoxPlus((flushAlign +15, firstCheckY + checkOffsetY *3, 120, 20), "Ignore casing")
		self.w.caseCheck.set(self.caseCheck)
		if scriptsNameList[self.w.scriptsPopup.get()] in enableCaseCheckList:
			self.w.caseCheck.enable(True)
		else:
			self.w.caseCheck.enable(False)
		
		# 5th checkbox
		self.w.casingCheck = CheckBoxPlus((flushAlign +15, firstCheckY + checkOffsetY *4, 115, 20), "Change casing", callback=self.casingCallback)
		self.w.casingCheck.set(self.casingCheck)
		if scriptsNameList[self.w.scriptsPopup.get()] in enableCaseCheckList:
			self.w.casingCheck.enable(True)
		else:
			self.w.casingCheck.enable(False)
		self.w.casingPopup = PopUpButton((210, firstCheckY + checkOffsetY *4, 90, 20), casingNameList)
		self.w.casingPopup.set(self.casingPopup)
		# enable or disable the casing PopUp depending on the casing CheckBox
		if self.w.casingCheck.get() and self.w.casingCheck.isEnable():
			self.w.casingPopup.enable(True)
		else:
			self.w.casingPopup.enable(False)
		
		self.nsTextField = self.w.chars.getNSTextField()
		self.w.setDefaultButton(self.w.button)
		self.w.bind("close", self.windowClose)
		self.w.open()
	
	def windowClose(self, sender):
		self.saveExtensionDefaults()

	def saveExtensionDefaults(self):
		setExtensionDefault("%s.%s" % (extensionKey, "windowPos"), self.w.getPosSize()[0:2])
		setExtensionDefault("%s.%s" % (extensionKey, "optionsVisible"), self.optionsVisible)
		setExtensionDefault("%s.%s" % (extensionKey, "chars"), self.w.chars.get())
		setExtensionDefault("%s.%s" % (extensionKey, "sliderValue"), int(self.w.slider.get()))
		setExtensionDefault("%s.%s" % (extensionKey, "scriptsIndex"), int(self.w.scriptsPopup.get()))
		setExtensionDefault("%s.%s" % (extensionKey, "langsIndex"), int(self.w.langsPopup.get()))
		setExtensionDefault("%s.%s" % (extensionKey, "punctCheck"), self.w.punctCheck.get())
		setExtensionDefault("%s.%s" % (extensionKey, "figsCheck"), self.w.figsCheck.get())
		setExtensionDefault("%s.%s" % (extensionKey, "figsPopup"), self.w.figsPopup.get())
		setExtensionDefault("%s.%s" % (extensionKey, "trimCheck"), self.w.trimCheck.get())
		setExtensionDefault("%s.%s" % (extensionKey, "caseCheck"), self.w.caseCheck.get())
		setExtensionDefault("%s.%s" % (extensionKey, "casingCheck"), self.w.casingCheck.get())
		setExtensionDefault("%s.%s" % (extensionKey, "casingPopup"), self.w.casingPopup.get())

	def buttonCallback(self, sender):
		sender.enable(False)
		self.w.spinner.start()
		self.getText()
		self.w.spinner.stop()
		sender.enable(True)
		
	def optionsCallback(self, sender):
		sign = sender.getTitle()
		if sign == "+":
			sender.setTitle("-")
			self.w.resize(self.windowWidth, self.windowHeightWithOptions, animate=True)
			self.optionsVisible = True
		else:
			sender.setTitle("+")
			self.w.resize(self.windowWidth, self.windowHeightWithoutOptions, animate=True)
			self.optionsVisible = False
		
	def charsCallback(self, sender):
		charsContent = sender.get()
		if len(charsContent):
			self.w.button.enable(True)
			nsTextView = self.nsTextField.currentEditor() # NOTE: the field editor is only available when NSTextField is in editing mode.
			
			# when only one glyph is selected and copied, the contents of the clipboard are the glyph's XML
			# instead of its unicode character or its name; therefore, post-process the pasted content.
			if xmlHeader in charsContent:
				caretIndex = charsContent.index(xmlHeader)
				codepointString = re_glyphUnicode.search(charsContent)
				glyphName = re_glyphName.search(charsContent)
			
				if codepointString:
					replacement = unichr(eval('0x' + codepointString.group(1)))
				elif glyphName:
					replacement = '/' + glyphName.group(1)
				else:
					replacement = ''
			
				# replace the glyph's XML by its unicode character or its name
				self.w.chars.set(re_glyph.sub(replacement, charsContent))
				# restore the location of the caret
				location = caretIndex + len(replacement)
				nsTextView.setSelectedRange_((location, 0))
				# update the variable
				charsContent = sender.get()
				
			caretIndex = nsTextView.selectedRanges()[0].rangeValue().location
			
			# Limit the number of characters
			numeralWasFound = self.stringHasNumeral(charsContent)
			if len(charsContent) > maxChars or numeralWasFound:
				NSBeep()
				if numeralWasFound:
					self.showMessage("Sorry, numerals are not allowed.", "")
				else:
					self.showMessage("You've reached the maximum \rnumber of characters.", "The limit is %d." % maxChars)
				# restore the content of chars EditText to the previous string
				sender.set(self.previousChars)
				# restore the focus on the chars EditText and restore the location of the caret
				caretIndexAdjust = len(self.previousChars) - len(charsContent)
				self.w.getNSWindow().makeFirstResponder_(self.nsTextField)
				nsTextView.setSelectedRange_((caretIndex + caretIndexAdjust, 0))
			
			# update the stored string
			self.previousChars = sender.get()
		
		else:
			self.w.button.enable(False)
	
	def sliderCallback(self, sender):
		self.w.wordCount.set(int(sender.get()))
	
	def scriptsCallback(self, sender):
		self.w.langsPopup.setItems(langsNameDict[scriptsNameList[sender.get()]])
		# toggle RTL/LTR
		if scriptsNameList[sender.get()] in rightToLeftList:
			self.scriptIsRTL = True
			self.nsTextField.setBaseWritingDirection_(NSWritingDirectionRightToLeft)
			self.nsTextField.setAlignment_(NSRightTextAlignment)
		else:
			self.scriptIsRTL = False
			self.nsTextField.setBaseWritingDirection_(NSWritingDirectionLeftToRight)
			self.nsTextField.setAlignment_(NSLeftTextAlignment)
		# restore the focus on the chars EditText
		self.w.getNSWindow().makeFirstResponder_(self.nsTextField)
		# toggle figsPopup
		if scriptsNameList[sender.get()] in enableFigOptionList:
			self.w.figsPopup.show(True)
			if self.w.figsCheck.get():
				self.w.figsPopup.enable(True)
			else:
				self.w.figsPopup.enable(False)
		else:
			self.w.figsPopup.show(False)
		# toggle trimCheck
		if scriptsNameList[sender.get()] in enableTrimCheckList:
			self.w.trimCheck.enable(True)
		else:
			self.w.trimCheck.enable(False)
		# toggle caseCheck and casingCheck
		if scriptsNameList[sender.get()] in enableCaseCheckList:
			self.w.caseCheck.enable(True)
			self.w.casingCheck.enable(True)
			if self.w.casingCheck.get():
				self.w.casingPopup.enable(True)
		else:
			self.w.caseCheck.enable(False)
			self.w.casingCheck.enable(False)
			self.w.casingPopup.enable(False)
	
	def figsCallback(self, sender):
		if sender.get():
			self.w.figsPopup.enable(True)
		else:
			self.w.figsPopup.enable(False)
	
	def casingCallback(self, sender):
		if sender.get():
			self.w.casingPopup.enable(True)
		else:
			self.w.casingPopup.enable(False)
	
	def stringHasNumeral(self, string):
		if re_numeral.search(string):
			return True
		return False

	def isConnected(self):
		try:
			urllib2.urlopen(url, timeout=3)
			return True
		except urllib2.URLError:
			pass
		return False

	def getText(self):
		if CurrentFont() is None:
			NSBeep()
			self.showMessage("Open a font first.", "")
			return
		
		if not self.isConnected():
			NSBeep()
			self.showMessage("Required internet connection not found.", "")
			return
		
		values = {'chars' : self.w.chars.get().encode('utf-8'),
				  'script' : scriptsTagDict[scriptsNameList[self.w.scriptsPopup.get()]],
				  'tb' : langsTagDict[langsNameDict[scriptsNameList[self.w.scriptsPopup.get()]][self.w.langsPopup.get()]] }
		
		if self.w.punctCheck.get():
			values['punct'] = True
		if self.w.figsCheck.get():
			values['figs'] = True
			if self.w.figsPopup.isVisible():
				figsOptTagsList = ["dflt", "locl"]
				values['figsOpt'] = figsOptTagsList[self.w.figsPopup.get()]
		if self.w.trimCheck.get() and self.w.trimCheck.isEnable():
			values['trim'] = True
		if self.w.caseCheck.get() and self.w.caseCheck.isEnable():
			values['case'] = True
		if self.w.casingCheck.get() and self.w.casingCheck.isEnable():
			values['casing'] = casingNameList[self.w.casingPopup.get()].lower()
		
		data = urllib.urlencode(values)
		request = urllib2.Request(url, data)
		response = urllib2.urlopen(request)
		text = response.read()
		textU = unicode(text, 'utf-8')
		
		if (msgStr in textU):
			textU = textU.replace(msgStr, "")
			NSBeep()
			self.showMessage(textU, "")
			return
		
		elif (wrnStr in textU):
			resultIndex = textU.find(rsltStr)
			secmsgIndex = textU.find(sndStr)
			frstmsgU = textU[:secmsgIndex].replace(wrnStr, "")
			scndmsgU = textU[secmsgIndex:resultIndex].replace(sndStr, "")
			textU = textU[resultIndex:].replace(rsltStr, "")
			NSBeep()
			self.showMessage(frstmsgU, scndmsgU)
		
		textList = textU.split()
		trimmedText = ' '.join(textList[:int(self.w.slider.get())])

		if CurrentSpaceCenter() is None:
			OpenSpaceCenter(CurrentFont(), newWindow=False)
		
		sp = CurrentSpaceCenter()
		
		sp.setRaw(trimmedText)
		
		# Toggle RTL-LTR
		try:
			sp.setLeftToRight(not self.scriptIsRTL)
			sp.setInputWritingDirection('Right to Left' if self.scriptIsRTL else 'Left to Right')
		except AttributeError:
			pass

		return
		
Adhesiontext()
