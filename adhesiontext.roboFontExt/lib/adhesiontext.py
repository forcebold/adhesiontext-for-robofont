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

scriptsNameList = "Latin Cyrillic Greek Arabic Hebrew Bengali Devanagari Gujarati Odia Sinhala Malayalam Tamil Telugu".split()

langsNameDict = {
"Latin" : "English French German Spanish Catalan Portuguese Dutch Turkish".split(),
"Cyrillic" : "Russian Ukrainian".split(),
"Greek" : ["Greek"],
"Arabic" : "Arabic Persian".split(),
"Hebrew" : ["Hebrew"],
"Bengali" : ["Bengali"],
"Devanagari" : "Hindi Marathi".split(),
"Gujarati" : ["Gujarati"],
"Odia" : ["Odia"],
"Sinhala" : ["Sinhala"],
"Malayalam" : ["Malayalam"],
"Tamil" : ["Tamil"],
"Telugu" : ["Telugu"],
}

scriptsTagDict = {
"Latin" : "latn",
"Cyrillic" : "cyrl",
"Greek" : "grek",
"Arabic" : "arab",
"Hebrew" : "hebr",
"Bengali" : "beng",
"Devanagari" : "deva",
"Gujarati" : "gujr",
"Odia" : "orya",
"Sinhala" : "sinh",
"Malayalam" : "mlym",
"Tamil" : "taml",
"Telugu" : "telu",
}

langsTagDict = {
"English" : "eng",
"French" : "fra",
"German" : "deu",
"Spanish" : "esp",
"Catalan" : "cat",
"Portuguese" : "ptg",
"Dutch" : "nld",
"Turkish" : "tur",
#-----
"Russian" : "rus",
"Ukrainian" : "ukr",
#-----
"Greek" : "ell",
#-----
"Arabic" : "ara",
"Persian" : "fas",
#-----
"Hebrew" : "heb",
#-----
"Bengali" : "ben",
"Hindi" : "hin",
"Marathi" : "mar",
"Gujarati" : "guj",
"Odia" : "ori",
"Sinhala" : "sin",
"Malayalam" : "mal",
"Tamil" : "tam",
"Telugu" : "tel",
}

rightToLeftList = "Arabic Hebrew".split()
disableTrimCheckList = "Arabic Hebrew Bengali Devanagari Gujarati Odia Sinhala Malayalam Tamil Telugu".split()
disableCaseCheckList = "Arabic Hebrew Bengali Devanagari Gujarati Odia Sinhala Malayalam Tamil Telugu".split()

#=============================================================

from mojo.UI import *
from vanilla import *
from AppKit import *
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

msgStr = "***MESSAGE***"
sndStr = "***SECOND***"
wrnStr = "***WARNING***"
rsltStr = "***RESULT***"


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


class Adhesiontext(BaseWindowController):

	def __init__(self):
		flushAlign = 76
		firstRowY = 12
		rowOffsetY = 30
		firstCheckY = 135
		checkOffsetY = 27
		rightMarginX = -12
		self.windowWidth = 410
		self.withoutOptionsHeight = 45
		self.withOptionsHeight = 280
		self.scriptIsRTL = False
		
		self.w = FloatingWindow((self.windowWidth, self.withoutOptionsHeight), "adhesiontext")
		
		# 1st row
		self.w.labelChars = TextBox((10, firstRowY, flushAlign, 20), "Characters:", alignment="right")
		self.w.chars = EditText((flushAlign +15, firstRowY -1, 199, 22), callback=self.charsCallback)
		self.w.button = Button((300, firstRowY, 68, 20), "Get text", callback=self.buttonCallback)
		self.w.spinner = FixedSpinner((325, firstRowY, 20, 20), displayWhenStopped=False)
		self.w.optionsButton = SquareButton((378, firstRowY +1, 18, 18), "+", sizeStyle="small", callback=self.optionsCallback)
		# set the initial state of the button according to the content of the chars EditText
		if len(self.w.chars.get()): self.w.button.enable(True)
		else: self.w.button.enable(False)
		# keep track of the content of chars EditText
		self.previousChars = self.w.chars.get()
		
		# 2nd row
		self.w.labelWords = TextBox((10, firstRowY + rowOffsetY, flushAlign, 20), "Words:", alignment="right")
		self.w.wordCount = TextBox((flushAlign +12, firstRowY + rowOffsetY, 40, 20), alignment="left")
		self.w.slider = Slider((flushAlign +47, firstRowY + rowOffsetY +1, 165, 20), value=25, minValue=5, maxValue=200, callback=self.sliderCallback)
		# set the initial wordCount value according to the position of the slider
		self.w.wordCount.set(int(self.w.slider.get()))
		
		# 3rd row
		self.w.labelScripts = TextBox((10, firstRowY + rowOffsetY *2, flushAlign, 20), "Script:", alignment="right")
		self.w.scriptsPopup = PopUpButton((flushAlign +15, firstRowY + rowOffsetY *2, 150, 20), scriptsNameList, callback=self.scriptsCallback)
		
		# 4th row
		self.w.labelLangs = TextBox((10, firstRowY + rowOffsetY *3, flushAlign, 20), "Language:", alignment="right")
		self.w.langsPopup = PopUpButton((flushAlign +15, firstRowY + rowOffsetY *3, 150, 20), [])
		# set the initial list of languages according to the script value
		self.w.langsPopup.setItems(langsNameDict[scriptsNameList[self.w.scriptsPopup.get()]])
		
		# 1st checkbox
		self.w.punctCheck = CheckBox((flushAlign +15, firstCheckY, 130, 20), "Add punctuation")
		
		# 2nd checkbox
		self.w.figsCheck = CheckBox((flushAlign +15, firstCheckY + checkOffsetY, 120, 20), "Insert numbers")
		
		# 3rd checkbox
		self.w.trimCheck = CheckBox((flushAlign +15, firstCheckY + checkOffsetY *2, 120, 20), "Trim accents")
		
		# 4th checkbox
		self.w.caseCheck = CheckBox((flushAlign +15, firstCheckY + checkOffsetY *3, 120, 20), "Ignore casing")
		
		# 5th checkbox
		self.w.casingCheck = CheckBox((flushAlign +15, firstCheckY + checkOffsetY *4, 115, 20), "Change casing", callback=self.casingCallback)
		self.w.casingPopup = PopUpButton((210, firstCheckY + checkOffsetY *4, 80, 20), casingNameList)
		# enable or disable the casing PopUp depending on the casing CheckBox
		if self.w.casingCheck.get(): self.w.casingPopup.enable(True)
		else: self.w.casingPopup.enable(False)
		
		self.nsTextField = self.w.chars.getNSTextField()
		self.w.setDefaultButton(self.w.button)
		self.w.center()
		self.w.open()
	
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
			self.w.resize(self.windowWidth, self.withOptionsHeight, animate=True)
		else:
			sender.setTitle("+")
			self.w.resize(self.windowWidth, self.withoutOptionsHeight, animate=True)
		
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
		# toggle trimCheck
		if scriptsNameList[sender.get()] in disableTrimCheckList: self.w.trimCheck.enable(False)
		else: self.w.trimCheck.enable(True)
		# toggle caseCheck and casingCheck
		if scriptsNameList[sender.get()] in disableCaseCheckList:
			self.w.caseCheck.enable(False)
			self.w.casingCheck.enable(False)
			self.w.casingPopup.enable(False)
		else:
			self.w.caseCheck.enable(True)
			self.w.casingCheck.enable(True)
			if self.w.casingCheck.get():
				self.w.casingPopup.enable(True)
	
	def casingCallback(self, sender):
		if sender.get(): self.w.casingPopup.enable(True)
		else: self.w.casingPopup.enable(False)
	
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
		
		if (self.w.punctCheck.get()): values['punct'] = True
		if (self.w.figsCheck.get()): values['figs'] = True
		if (self.w.trimCheck.get()): values['trim'] = True
		if (self.w.caseCheck.get()): values['case'] = True
		if (self.w.casingCheck.get()): values['casing'] = casingNameList[self.w.casingPopup.get()].lower()
		
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

