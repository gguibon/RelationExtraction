#python3

"""
This script format the SemEval2018 Relation Extraction/Classification corpus (Task8 subtasks 1 and 2) to the SemEval2010 Relation Extraction corpus format (Task7). 
@author Gaël Guibon (gael.guibon@lis-lab.fr ; gael.guibon@gmail.com)
@organization LIS-CNRS UMR 7020

CLI usage : python3 semeval2018to2010format.py -h

API usage : 
import semeval2018to2010format as semf
semf.run([relationfile path], [xml file path], [out path])

"""

import xml.etree.ElementTree as ET
from collections import OrderedDict, Counter
import os, pprint, re, argparse, html
# import bs4 as BeautifulSoup
# from bs4 import BeautifulStoneSoup



# import spacy
# nlp = spacy.load('en')

res = list()

trainrelationfile = "1.1.relations.txt"
traintextfile = "1.1.text.xml"

testrelationfile = "keys.test.2.txt"
testtextfile = "2.test.text.xml"


def HTMLEntitiesToUnicode(text):
    """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
    text = BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES)
    return text

def getRelationDict(relationtxtpath):
    def parseLine(line):
        vals = line.strip('\n').strip(')').split('(')
        idRev = vals[1].split(',')
        reverse = False
        if len(idRev) > 2 and 'REVERSE' in idRev[2]: reverse = True
        if reverse: return ( '&&'.join(line.strip('\n').strip(')').split('(')[1].split(',')[:2]), ( vals[0], idRev[1], idRev[0] ) )
        else: return ( '&&'.join(line.strip('\n').strip(')').split('(')[1].split(',')[:2]) ,( vals[0], idRev[0], idRev[1] ) )
    return OrderedDict( [parseLine(line) for line in open(relationtxtpath, 'r').readlines()] )


def parseAbstract(abstract):
    entities = abstract.findall('.//entity')
    text = "".join(abstract.itertext())
    if len(entities) > 0:
        for entity in entities : entity.text = entity.text.replace('(', '&&lpar&&').replace(')', '&&rpar&&')
    xmlstr = ET.tostring(abstract).decode("utf-8")  #, encoding='utf8', method='xml') )
    if len(entities) > 0:
        for entity in entities: xmlstr = xmlstr.replace('<entity id="'+entity.get('id')+'">', '<entity id="'+entity.get('id').replace('-', '&&macr&&').replace('.', '&&middot&&') + '">')

    #################
    ### With SPACY : works fine until it split some sentences inside a entity .... I switched to a rule based sentence split because the patterns are quite easy. ###
    """# doc = nlp( xmlstr.replace('\n', '').replace('<entity id=','<entity_id=').replace('<', '&&lt&&').replace('>', '&&gt&&') )
    # sentences = [s.text.replace('&&lt&&', '<').replace('&&gt&&', '>').replace('\\n', '').replace('<abstract>', '').replace('</abstract>', '').replace('<entity_id=', '<entity id=').replace('&&middot&&','.').replace('&&macr&&', '-').replace( '&&lpar&&', '(').replace('&&rpar&&', ')').replace('&&', '') for s in doc.sents]
    """
    ################

    ################
    ### Rule based corpus oriented sentence split : quick and easy peasy ###
    sentSep = ['. ', ' . ']
    exceptionSent = ['i.e.','e.g.', 'U.S.A','U.S.','cf.', '. (']
    exceptions = {'i.e.':'&&ie&&', 'i.e':'&&ieee&&', 'e.g.':'&&eg&&', 'U.S.': '&&us&&', 'cf.': '&&cf&&'}
    xmlstr = xmlstr.replace('i.e. ', '&&ie&& ')
    xmlstr = xmlstr.replace('i.e', '&&ieee&&')
    for o, r in exceptions.items(): xmlstr = xmlstr.replace(o, r)
    for sep in sentSep: xmlstr = xmlstr.replace(sep,'&&SEPsepSEP&&')
    sentences = xmlstr.split('&&SEPsepSEP&&')
    sentences = [s.replace('&&lt&&', '<').replace('&&gt&&', '>').replace('\\n', '').replace('<abstract>', '').replace('</abstract>', '').replace('<entity_id=', '<entity id=').replace('&&middot&&','.').replace('&&macr&&', '-').replace( '&&lpar&&', '(').replace('&&rpar&&', ')') for s in sentences]
    def replaceExceptions(txt):
        for o, r in exceptions.items() : txt = txt.replace(r, o)
        return txt
    sentences = [ replaceExceptions(s) for s in sentences ]
    # sentences = [ s.replace('&&', '') for s in sentences ]
    ###############

    def check(s):
        '''checker for entity tags closure isolated. useful with the Spacy approach but i still apply it just in case =)'''
        tokens = list()
        found = False
        for t in s.split(' '):
            if '<entity' in t :
                found = True
                tokens.append(t)
                continue
            if '</entity>' in t and '<entity' not in t and not found: 
                tokens.append(t.replace('</entity>', ''))
                continue
            else: tokens.append(t)
        return ' '.join(tokens)
    sentences = [check(s) for s in sentences]
    return sentences


def parseXml2(xmlpath):
    dom= ET.parse(open(xmlpath,'r'),parser=None)
    root=dom.getroot()
    print( 'num of texts', len(root.findall('.//text')) )
    text_dict = OrderedDict( [ (t.get('id'), {'title':t.findtext('title') , 'abstract':parseAbstract(t.find('abstract')) } ) for t in root.findall('.//text') ] )
    return text_dict

def sent2semevalTags(relInSent,sent):
    for rel in relInSent:
        txtOrder = rel[0].split('&&')
        relOrder = list(rel[1][1:])
        
        tree = ET.ElementTree(ET.fromstring('<el>{}</el>'.format( sent ) ) )
        root = tree.getroot()
        for i ,eid in enumerate(txtOrder):
            e = root.find('.//entity[@id="{}"]'.format(eid))
            e.tag = 'e{}'.format(i+1)
            e.attrib.pop('id')
        # for entity in root.findall('.//entity'):   #entity.tag = 'ENTITYTODELETE' #root.remove(entity) ### way to delete an entity.. but it also delete its content =(
        
        xmlstr =  ET.tostring(root).decode("utf-8") 
        xmlstr = xmlstr.replace('&&middot&&','.').replace('&&macr&&', '-')
        for entity in root.findall('.//entity'): xmlstr = xmlstr.replace('<entity id="'+ entity.get('id') +'">', '')
        xmlstr = xmlstr.replace('<el>','').replace('</el>', '').replace('</entity>', '')
        if txtOrder == relOrder: label = '{}(e1,e2)'.format(rel[1][0] )
        else: label = '{}(e2,e1)'.format(rel[1][0] )
        xmlstr = xmlstr.replace('\n', ' ')
        if args.dq: xmlstr = '"'+xmlstr+'"'
        if args.escape: 
            xmlstr = html.unescape(xmlstr)
            xmlstr = xmlstr.replace('&&lpar&&', '(').replace('&&rpar&&', ')')
        if args.nc: res.append( '{}\n{}\n'.format(xmlstr.strip('\n'), label) )
        else: res.append( '{}\n{}\nComment:\n'.format(xmlstr.strip('\n'), label) )

def run(relpath, xmlpath, outpath):
    dict_rel = getRelationDict(relpath)
    dict_text = parseXml2(xmlpath)

    for numtext,(k, v) in enumerate(dict_text.items()):
        for s in v['abstract']:
            # print('S', s)
            relInSent = list()
            num_occurrences = len([m.start() for m in re.finditer('<entity id=', s)] )
            if num_occurrences > 1:
                s = '<el>{}</el>'.format( s )
                tree = ET.ElementTree(ET.fromstring( s ) )
                root = tree.getroot()
                entityIds = [e.get('id') for e in root.findall('.//entity')]
                for k, rel in dict_rel.items(): 
                    if rel[1] in entityIds and rel[2] in entityIds: relInSent.append( (k,rel) ) 
                if len(relInSent) > 0: sent2semevalTags(relInSent, s)  #print(relInSent, s)
    
    out = open( outpath ,'w')
    if args.ni: out.write( '\n'.join( [ r  for r in res] ) )
    else: out.write( '\n'.join( ['{}\t{}'.format(i, r)  for i,r in enumerate(res)] ) )
    out.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Transform a semeval2018 task7 subtask2 and 1 corpus to a semeval2010 task8 format.')
    parser.add_argument('-xml', '--xmlpath', help='XML file path containing the text : example : 1.1.text.xml')
    parser.add_argument('-rel', '--relationspath', help='TXT file path containing the relations info : example : 1.1.relations.txt')
    parser.add_argument('-out', '--outputpath', help='path for the output TXT file : example : TRAIN.TXT')
    parser.add_argument('-nc', action='store_true', help='remove the comment line')
    parser.add_argument('-ni', action='store_true', help='remove the index indication')
    parser.add_argument('-dq', action='store_true', help='add doublequote for text column')
    parser.add_argument('-escape', action='store_true', help='escape html entities')
    args = parser.parse_args()

    run(args.relationspath, args.xmlpath, args.outputpath)

    print('SUCCESS')
    
