import scrapy
import requests
from lxml import etree
def coloredString(str,color):
    colorsObj={
# ---------------------------------- normal ---------------------------------- #c
        "gray":"5;30;40",       "red":"5;31;40",        "green":"5;32;40",
        "yellow":"5;33;40",     "blue":"5;34;40",       "purple":"5;35;40",
        "cyan":"5;36;40",       "white":"5;37;41",
        "green_bg":"5;30;42",        "yellow_bg":"5;30;43",        "blue_bg":"5;30;44",        
        "purple_bg":"5;30;45",        "cyan_bg":"5;30;46",        "white_bg":"5;30;47",
# --------------------------------- underline -------------------------------- #
        "u_gray":"4;30;40",     "u_red":"4;31;40",      "u_green":"4;32;40",
        "u_yellow":"4;33;40",   "u_blue":"4;34;40",     "u_purple":"4;35;40",
        "u_cyan":"4;36;40",     "u_white":"4;37;41",
        "u_green_bg":"4;30;42",        "u_yellow_bg":"4;30;43",        "u_blue_bg":"4;30;44",        
        "u_purple_bg":"4;30;45",        "u_cyan_bg":"4;30;46",        "u_white_bg":"4;30;47",
# ----------------------------------- bold ----------------------------------- #
        "b_gray":"1;30;40",     "b_red":"1;31;40",      "b_green":"1;32;40",
        "b_yellow":"1;33;40",   "b_blue":"1;34;40",     "b_purple":"1;35;40",
        "b_cyan":"1;36;40",     "b_white":"1;37;41",
        "b_green_bg":"1;30;42",        "b_yellow_bg":"1;30;43",        "b_blue_bg":"1;30;44",        
        "b_purple_bg":"1;30;45",        "b_cyan_bg":"1;30;46",        "b_white_bg":"1;30;47",
    }
    colorString= colorsObj[color] if color in colorsObj else "3;30;40"
    return f'\x1b[{colorString}m' + str + '\x1b[0m'

class SalimaSpider(scrapy.Spider):
    name = "salima"
    start_urls = ["http://www.parcours-lmd.salima.tn"    ]
    # start_urls = ["http://www.parcours-lmd.salima.tn/listeueetab.php?parc=UkpQFQskWD4ELVA3BTgALVZt&etab=UzZXYw06"]

    def parse(self, response):

        url = "http://www.parcours-lmd.salima.tn/getparc.php"
        payload='etab=107'
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        responser = requests.request("POST", url, headers=headers, data=payload)
        
        planLinks = etree.HTML(responser.text).xpath('//a[@class="medium orange awesome"]/@href')
        
        

        # yield{ "len":len(planLinks)}
        yield from response.follow_all(planLinks, self.getDetails)


    def getDetails(self, response):
        def cleanup(a): 
            if type(a) ==  list:
                a= " ".join(a)
            if isinstance(a, etree._ElementUnicodeResult): 
                a= str(a)
            if type(a) == str :
                a=a.replace("\n","")
                a=a.replace("\r","")
                a=a.replace("\t","")
                a=a.strip()
                a=a.replace("  "," ")
                a=a.encode().decode('utf8')
                return a
            return 1233456
        def getSubjects(trTags):
            subjects=[]
            for tr in trTags:
                # tdTags=[ etree.HTML(etree.tostring(a)) for a in etree.HTML(etree.tostring(tr)).xpath("//tr/td")]
                # print('\x1b[6;32;40m',[etree.tostring(a) for a in tdTags],'\x1b[0m')
                b =etree.XML(etree.tostring(tr))
                c= [etree.HTML(etree.tostring(ax)) for ax in b.xpath("//tr/td")]
                subjects.append(dict({
                    "code": cleanup(c[0].xpath("/*/*/td/text()")[0]) if len(c[0].xpath("/*/*/td/text()"))>0 else '',
                    "name": cleanup(c[1].xpath("/*/*/td/text()")[0]) if len(c[1].xpath("/*/*/td/text()"))>0 else '',
                    "coef": cleanup(c[2].xpath("/*/*/td/text()")[0]) if len(c[2].xpath("/*/*/td/text()"))>0 else '',
                    "credits": cleanup(c[3].xpath("/*/*/td/text()")[0]) if len(c[3].xpath("/*/*/td/text()"))>0 else '',
                    "Regime": cleanup(c[4].xpath("/*/*/td/text()")[0]) if len(c[4].xpath("/*/*/td/text()"))>0 else '',
                }))
            return subjects

        def getSemesters(ElemArray):
            sems=[]
            modules=[]
            atLeastOneIteration = False
            semName=""
            for stringElem in ElemArray:  
                elem = etree.HTML(stringElem)
                # print('\x1b[7;31;40m',elem.xpath("//tr/@bgcolor")   ,'\x1b[0m') # white on red 
                if len(elem.xpath("//tr/@bgcolor"))> 0 and elem.xpath("//tr/@bgcolor")[0] == "#444444":
                    if len(elem.xpath('//tr/td/div[@class="style8"]/text()'))==0:   
                        # print('\x1b[7;31;40m' + 'hazebiiii!'+ stringElem + '\x1b[0m') # white on red 
                        continue
                    else:
                        if atLeastOneIteration:
                            sems.append({
                                "name":semName,
                                "modules":modules
                            })
                        semName=cleanup(elem.xpath('//tr/td/div[@class="style8"]/text()')[0].split(" : ")[-1])
                    continue
                tdTags= [ etree.HTML(etree.tostring(a)) for a in elem.xpath("/*/*/tr/td")]
                # print('\x1b[6;32;40m',[etree.tostring(a) for a in tdTags],'\x1b[0m')
                modules.append(
                    {
                        "codeModule" : cleanup(tdTags[0].xpath("//td/span[@class='style4']/text()")[0]),
                        "nameModule" : cleanup(tdTags[1].xpath("//td/span[@class='style4']/text()")[0]),
                        "coefModule" : cleanup(tdTags[3].xpath("//td/span[@class='style4']/text()")[0]),
                        "regimeModule" : cleanup(tdTags[5].xpath("//td/span[@class='style4']/text()")[0]),
                        "subjects" :  getSubjects(tdTags[-1].xpath("//td/table/tr")[2:] )                    
                    }
                )
                atLeastOneIteration = True
            return sems
        # -------------------------------- getDetails -------------------------------- #
        trTags= response.xpath('//div[@id="main"]/table[last()]/tr[not(./td/hr) ]').getall()
        title= response.xpath('//span[@class="style5"]/text()').get()
        
        keys= response.xpath('//div[@id="main"]/table[1]/tr[last()]/td/p/strong/text()').getall()
        vals =response.xpath('//div[@id="main"]/table[1]/tr[last()]/td/p/text()').getall()[::2]
        print('\x1b[6;32;40mzaezaeazeazeazeaz',keys,vals,'\x1b[0m')
        if len(title)>0:
            info= {
                    "title":title,
                    "semesters": getSemesters(trTags),
                    "url": response.url,
            }
            for i,kv in enumerate(keys):
                info[kv]=vals[i]
                print('\x1b[6;32;40mzaezaeazeazeazeaz',{info[kv]:vals[i]},'\x1b[0m')
                
            yield info
