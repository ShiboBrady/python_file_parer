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
        for line in range(nrows):
            if line <= beginLine:
                continue
            voiceFile, pinyin = table.row_values(line)[:2]
            #print voiceFile, pinyin

            alphalist = list(pinyin)
            newPinyin = ''.join([alpha if alpha != u'ü' else 'v' for alpha in alphalist])
            result[newPinyin] = voiceFile + '.mp3'
        return result

if __name__ == '__main__':
    try:
        excelConvent = ExcelConvent()
        table = excelConvent.OpenExcel(u'拼音录音文档-2016.6.30.xlsx', u'字母表')
        result = excelConvent.Convent(table, 1)  
        result_str = json.dumps(result, ensure_ascii=False)
        with open('./zimu.json', 'w', encoding ='utf-8') as file:
            file.write(result_str)
        #print result_str
    except Exception as e:
        traceback.print_exc()
