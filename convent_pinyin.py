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

    def OpenExcel(self, filename, tablename):
        try:
            data = xlrd.open_workbook(filename)
            table = data.sheet_by_name(tablename)
            return table
        except Exception,e:
            print str(e)
            raise e

    def Convent(self, table, beginLine):
        nrows = table.nrows
        beginLine = beginLine - 1;
        imageFileHistory = ''
        #voiceExplainHistory = ''
        voiceListHistory = []
        result = {}
        for line in xrange(nrows):
            if line <= beginLine:
                continue
            #if line > 40:
            #    break
            voiceFile, pinyin, imageFile, voiceExplain = table.row_values(line)
            #print pinyin, imageFile
            voiceFile = voiceFile.strip()
            pinyin = pinyin.strip()
            imageFile = imageFile.strip()
            voiceExplain = voiceExplain.strip()
            voiceFile = voiceFile + '.mp3'
            voiceList = [] 
            key = ''
            if pinyin in self.alphaMapping:
                key = self.alphaMapping[pinyin]
            else:
                alphaList = list(pinyin)
                key = ''.join([alpha if alpha not in self.alphaMapping else self.alphaMapping[alpha] for alpha in alphaList])

            if imageFile == "" or imageFile == None:
                if voiceExplain == "" or voiceExplain == None: 
                    #voiceExplain = voiceExplainHistory
                    voiceList = voiceListHistory[:]
                else:
                    #voiceExplainHistory = voiceExplain
                    voiceList = voiceExplain.split()
                    voiceListHistory = voiceList[:]
                #if -1 != voiceExplain.find(key):
                if pinyin in voiceList or key in voiceList: 
                    imageFile = imageFileHistory
            else:
                imageFile = imageFile + '.png'
                imageFileHistory = imageFile 
                #voiceExplainHistory = voiceExplain
                voiceList = voiceExplain.split()
                voiceListHistory = voiceList[:]

            if "" == imageFile:
                imageFile = u"空白.png"

            self.InsertIntoMap(result, key, pinyin, voiceFile, imageFile)
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
        print pinyin
        if pinyin not in self.alphaMapping:
            alphaList = list(pinyin)
            for alpha in alphaList:
                if alpha in self.alphaMapping:
                    pinyin = alpha
                    break
        return self.toneMapping[self.positionMapping[self.alphaMapping[pinyin]].index(pinyin) + 1]
            
if __name__ == '__main__':
    try:
        excelConvent = ExcelConvent()
        table = excelConvent.OpenExcel(u'拼音录音文档-2016.6.30.xlsx', u'拼音表')
        result = excelConvent.Convent(table, 1)  
        result_str = json.dumps(result, ensure_ascii=False)
        print result_str
        #with open('result.json', 'w') as f:
        #        f.write(result_str)
    except Exception, e:
        print e
        print traceback.print_exc()
