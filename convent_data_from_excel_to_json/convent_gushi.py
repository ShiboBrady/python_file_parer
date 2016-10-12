#!/usr/bin/env python3.6
#-*-coding:UTF-8-*-
import xlrd
import traceback
import json
import sys

class ExcelConvent():
    def __init__(self):
        self.alphaMapping = {}; 
        self.alphaMapping[u'ā'] = 'a'
        self.alphaMapping[u'á'] = 'a'
        self.alphaMapping[u'ǎ'] = 'a'
        self.alphaMapping[u'à'] = 'a'
        self.alphaMapping[u'ō'] = 'o'
        self.alphaMapping[u'ó'] = 'o'
        self.alphaMapping[u'ǒ'] = 'o'
        self.alphaMapping[u'ò'] = 'o'
        self.alphaMapping[u'ē'] = 'e'
        self.alphaMapping[u'é'] = 'e'
        self.alphaMapping[u'ě'] = 'e'
        self.alphaMapping[u'è'] = 'e'
        self.alphaMapping[u'ī'] = 'i'
        self.alphaMapping[u'í'] = 'i'
        self.alphaMapping[u'ǐ'] = 'i'
        self.alphaMapping[u'ì'] = 'i'
        self.alphaMapping[u'ū'] = 'u'
        self.alphaMapping[u'ú'] = 'u'
        self.alphaMapping[u'ǔ'] = 'u'
        self.alphaMapping[u'ù'] = 'u'
        self.alphaMapping[u'ǖ'] = 'v'
        self.alphaMapping[u'ǘ'] = 'v'
        self.alphaMapping[u'ǚ'] = 'v'
        self.alphaMapping[u'ǜ'] = 'v'
        self.alphaMapping[u'一声'] = 'tone'
        self.alphaMapping[u'二声'] = 'tone'
        self.alphaMapping[u'三声'] = 'tone'
        self.alphaMapping[u'四声'] = 'tone'

        self.positionMapping = {}
        self.positionMapping['a'] = [u'ā' ,u'á' ,u'ǎ' ,u'à']
        self.positionMapping['o'] = [u'ō' ,u'ó' ,u'ǒ' ,u'ò'] 
        self.positionMapping['e'] = [u'ē' ,u'é' ,u'ě' ,u'è'] 
        self.positionMapping['i'] = [u'ī' ,u'í' ,u'ǐ' ,u'ì'] 
        self.positionMapping['u'] = [u'ū' ,u'ú' ,u'ǔ' ,u'ù'] 
        self.positionMapping['v'] = [u'ǖ' ,u'ǘ' ,u'ǚ' ,u'ǜ']
        self.positionMapping['tone'] = [u'一声', u'二声', u'三声', u'四声']
        
        self.toneMapping = {}
        self.toneMapping[1] = 'tone1'
        self.toneMapping[2] = 'tone2'
        self.toneMapping[3] = 'tone3'
        self.toneMapping[4] = 'tone4'

        self.FileToYunMuMapping = {
            "gs01" : "ai",
            "gs02" : "ei",
            "gs03" : "ui",
            "gs04" : "ao",
            "gs05" : "ou",
            "gs06" : "iu",
            "gs07" : "ie",
            "gs08" : "ve",
            "gs09" : "er",
            "gs10" : "an",
            "gs11" : "en",
            "gs12" : "in",
            "gs13" : "un",
            "gs14" : "vn",
            "gs15" : "ang",
            "gs16" : "eng",
            "gs17" : "ing",
            "gs18" : "ong",
        }

    def OpenExcel(self, filename, tablename):
        try:
            data = xlrd.open_workbook(filename)
            table = data.sheet_by_name(tablename)
            return table
        except Exception as e:
            traceback.print_exc()
            raise e

    def Convent(self, table, beginLine):
        nrows = table.nrows
        beginLine = beginLine - 1;
        result = {}
        for lines in range(nrows):
            if lines <= beginLine:
                continue
            #if line > 40:
            #    break
            line = table.row_values(lines)
            self.ParseLine(line, result)
        return result

    def InsertIntoMap(self, result, key, pinyin, voiceFile, imageFile):
        if key not in result:
            result[key] = {}
        newMap = {}
        newMap['voiceFile'] = voiceFile
        newMap['imageFile'] = imageFile
        tone = self.FindPinYinTone(pinyin)
        if tone not in result[key]:
            result[key][tone] = []
        result[key][tone].append(newMap)

    def FindPinYinTone(self, pinyin):
        if pinyin not in self.alphaMapping:
            alphaList = list(pinyin)
            for alpha in alphaList:
                if alpha in self.alphaMapping:
                    pinyin = alpha
                    break
        return self.toneMapping[self.positionMapping[self.alphaMapping[pinyin]].index(pinyin) + 1]

    def ParseLine(self, line, result):
        voiceFile, pinyin = line[:2]
        print (voiceFile, pinyin)
        voiceFile = voiceFile.strip()
        pinyin = pinyin.strip()
        YunMuKey = voiceFile[:4]
        if YunMuKey not in self.FileToYunMuMapping:
            print ('YunMukey ', YunMukey, ' Doesn\'t in FileToYunMuMapping.')
            return
        YunMu = self.FileToYunMuMapping[YunMuKey]
        voiceFile = voiceFile + '.mp3'
        tone = self.FindPinYinTone(pinyin)
        alphaList = list(pinyin)
        newPinYin = ''.join([alpha if alpha not in self.alphaMapping else self.alphaMapping[alpha] for alpha in alphaList])
        newDict = {
            "pinyin" : newPinYin,
            "tone" : tone,
            "videofile" : voiceFile,
        }
        if YunMu not in result:
            result[YunMu] = []
        result[YunMu].append(newDict);
            
if __name__ == '__main__':
    try:
        excelConvent = ExcelConvent()
        table = excelConvent.OpenExcel(u'拼音录音文档-2016.6.30.xlsx', u'故事表')
        result = excelConvent.Convent(table, 19)  
        result_str = json.dumps(result, ensure_ascii=False)
        with open('gushi.json', 'w', encoding = 'utf-8') as f:
            f.write(result_str)
    except Exception as e:
        traceback.print_exc()
