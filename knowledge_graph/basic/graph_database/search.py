#!/usr/bin/python
#-*-coding:utf-8-*-
import pandas as pd
from py2neo import Graph,Node,walk,Relationship
import re
import jieba
import os
os.chdir('E:/课程/知识图谱/第3周/数据库建立与查询')

g=Graph("http://localhost:7474")  # username="neo4j", password="123456"

#加载字典
jieba.load_userdict("./dict.txt")

#获取英雄列表
heros=[]
hero=g.find(label='hero')
for i in hero:
    heros.append(i.properties['name'])

#获取装备列表
weapons=[]
weapon=g.find(label='weapon')
for i in weapon:
    weapons.append(i.properties['name'])

#属性同义词:数组第一个元素为数据库里属性名，第二个为输出时官方名，后面的是可能的同义词名
HP_all=['HP',u'生命值',u'血量',u'血上限']
MP_all=['MP',u'法力值',u'蓝量',u'蓝']
HP_recover_all=[u'HP_recover',u'每5秒回血','回血']
MP_recover_all=[u'MP_recover',u'每5秒回复法力值',u'每5秒回蓝',u'回蓝']
R_cooling_all=['R_cooling',u'大招冷却时间']
R_cost_all=['R_cost',u'大招消耗']
skill_R_all=['R',u'大招']
attack_all=['attack',u'物理攻击',u'攻击力',u'攻击']
attack_range_all=['attack_range',u'攻击距离',u'近战',u'远程']
aa=['defense',u'护甲',u'物理防御']
bb=['skill_passive',u'被动技能',u'被动']
cc=['skill_1',u'一技能',u'1技能',u'技能一',u'技能1']
dd=['skill_2',u'二技能',u'2技能',u'技能二',u'技能2']
ee=['skill_1_cooling',u'1技能冷却时间',u'技能1冷却时间',u'一技能冷却时间',u'技能一冷却时间']
ff=['skill_2_cooling',u'2技能冷却时间',u'技能2冷却时间',u'二技能冷却时间',u'技能二冷却时间']
gg=['skill_1_cost',u'1技能消耗',u'技能1消耗',u'一技能消耗',u'技能一消耗']
hh=['skill_2_cost',u'2技能消耗',u'技能2消耗',u'二技能消耗',u'技能二消耗']
ii=['speed',u'移动速度',u'移速',u'速度']
jj=['tag',u'类型']

#获取英雄属性列表
property_all_2=[aa,bb,cc,dd,ee,ff,gg,hh,ii,jj,HP_all,MP_all,HP_recover_all,MP_recover_all,R_cooling_all,R_cost_all,skill_R_all,attack_all,attack_range_all]
property_all=aa+bb+cc+dd+ee+ff+gg+hh+ii+jj+HP_all+MP_all+HP_recover_all+MP_recover_all+R_cooling_all+R_cost_all+skill_R_all+attack_all+attack_range_all
property_name=[]
for i in property_all_2:
    property_name.append(i[1])
    
#节点列表    
things_2=[weapons,heros]
things=weapons+heros

#获取英雄tag
m=[]
tags_all=[]
for i in range(0,68):
    a=re.findall('\S+',g.find_one('hero',property_key='name',property_value=heros[i])['tag'])
    m = m + a
for p in m:
    if p not in tags_all:
        tags_all.append(p)

#关系列表
relation=[u'相似',u'克制',u'搭配',u'推荐',u'适合用于对抗']
rel_2=[[u'相似',u'像'],[u'克制'],[u'搭配',u'配合',u'组合'],[u'推荐',u'出装'],[u'用来对抗',u'适合用来对抗',u'适合用于对抗']]
rel_3=[u'相似',u'像',u'克制',u'搭配',u'配合',u'组合',u'推荐',u'出装',u'用来对抗',u'适合用来对抗',u'适合用于对抗']
#用来判断对不对的属性
if_true=[ u'远程',u'近战'+u'近程'] + tags_all
#装备属性  为了提取装备的属性
wsx=[]
for mo in weapons:
    ll=g.find_one(label='weapon',property_key='name',property_value=mo).properties['property']
    temp = re.findall('^\+\d+%?(\S+)\s',ll)
    for la in temp:
        if la not in wsx:
            wsx.append(la)

wsx.append(u'被动')
wsx.append(u'主动')

#定位属性
def ifin(i,a):
    return int(i in a)
# 因为同义词  要定位属性
def find_index(p):
    return list(map(ifin , [p]*len(property_all_2) ,property_all_2)).index(1)
#因为同义词要定位关系
def find_2(p):
    a = list(map(ifin, [p] * len(rel_2), rel_2)).index(1)
    return relation[a]
#find_index('生命值')
def get_att(Node,pro):
    return Node[property_all_2[pro][0]]
def get_name(Node,pro):
    return property_all_2[pro][1]
def show(a,b):
    return str(a)+ ':'+str(b)
def find_subject_property(word,property,label):
    try:
        node=g.find_one(label,property_key='name',property_value=word)
        property_num=list(map(find_index,property))
        property_show=list(map(get_name,[node]*len(property),property_num))
        value=list(map(get_att,[node]*len(property),property_num))
        return  word+':\n '+str(list(map(show,property_show,value)))

    except ValueError:
        return '查询失败'
#find_subject_property('赵云',['大招','移速'],'hero')
'''
def get_rel(node,rel,yuxu):
    if rel=='克制':
        if yuxu == 1:
            rel_all= g.match(end_node=node,rel_type=rel)
            alll=[]
            for l in rel_all:
                alll.append(l.start_node()['name'])
        else:
            rel_all= g.match(start_node=node,rel_type=rel)
            alll = []
            for l in rel_all:
                alll.append(l.end_node()['name'])
    else:
        rel_all_1=g.match(end_node=node,rel_type=rel)
        rel_all_2=g.match(start_node=node,rel_type=rel)
        alll=[]
        for l in rel_all_1:
            alll.append(l.start_node()['name'])
        for lp in rel_all_2:
            alll.append(lp.end_node()['name'])
    if alll!=[]:
        return list(set(alll)),'|',buildNodes(node),'|',
    else:
        return '查询失败，暂无答案'
def find_rel(word,rel,yuxu,label):
    node = g.find_one(label, property_key='name', property_value=word)
    return list(map(get_rel,[node]*len(rel),rel,[yuxu]*len(rel)))
'''
#find_rel('关羽',['搭配','适合用于对抗'],None,'hero')
#subject rel both list
def find_rel_D(subject , rel ,label):
    node1=g.find_one(label[0], property_key='name', property_value=subject[0])
    node2 = g.find_one(label[1], property_key='name', property_value=subject[1])
    b=g.match_one(start_node=node1,rel_type=rel[0],end_node=node2)
    c=g.match_one(start_node=node2,rel_type=rel[0],end_node=node1)
    if b!=None:
        return '有这种关系'+' '+b.start_node()['name']+rel[0]+b.end_node()['name']
    elif c!=None:
        return '有这种关系' + ' ' + c.start_node()['name'] + rel[0] + b.end_node()['name']
    else:
        return '没有这种关系'

def find_relation(subject,label):
    node_1 = g.find_one(label[0], property_key='name', property_value=subject[0])
    node_2 = g.find_one(label[1], property_key='name', property_value=subject[1])
    node_1
    rel_all = g.match(start_node=node_1 , end_node= node_2)
    rel_all3 =g.match(start_node=node_2 , end_node= node_1)
    rel_all_2=[]
    st=[]
    ed=[]
    xx=[]
    for p in rel_all:
        rel_all_2.append(re.findall("\[\:\`([\u2E80-\u9FFF]+)\`\]", str(p.relationships))[0])
        st.append(p.start_node()['name'])
        ed.append(p.end_node()['name'])
    for p in rel_all3:
        rel_all_2.append(re.findall("\[\:\`([\u2E80-\u9FFF]+)\`\]",str(p.relationships))[0])
        if re.findall("\[\:\`([\u2E80-\u9FFF]+)\`\]",str(p.relationships))[0] not in ['相似','搭配']:
            st.append(p.start_node()['name'])
            ed.append(p.end_node()['name'])
    for i in range(0,len(st)):
        xx.append(st[i] + ' '+rel_all_2[i] +' '+ ed[i] )
    if xx!=[]:
        return xx
    else :
        return '没什么关系'
#find_relation(['赵云','关羽'],['hero','hero'])
def get_att(Node,pro):
    return Node[property_all_2[pro][0]]
def get_name(Node,pro):
    return property_all_2[pro][1]
def show(a,b):
    return str(a)+ ':'+str(b)
def find_subject_property(word,property,label):
    try:
        node=g.find_one(label,property_key='name',property_value=word)
        property_num=list(map(find_index,property ))
        property_show=list(map(get_name,[node]*len(property),property_num))
        value=list(map(get_att,[node]*len(property),property_num))
        return  list(map(show,property_show,value))

    except ValueError:
        return '查询失败'
#find_subject_property('赵云',['大招','移速'],'hero')
#mm用来使这个函数既可以原来写下面的函数也可以用来输出节点是否是起始点
def get_rel(node,rel,yuxu,mm):
    if rel=='克制':
        if yuxu == 1:
            rel_all= g.match(end_node=node,rel_type=rel)
            alll=[]
            for l in rel_all:
                alll.append(l.start_node()['name'])
            iff = 0
        else:
            rel_all= g.match(start_node=node,rel_type=rel)
            alll = []
            for l in rel_all:
                alll.append(l.end_node()['name'])
            iff=1
    else:
        rel_all_1=g.match(end_node=node,rel_type=rel)
        rel_all_2=g.match(start_node=node,rel_type=rel)
        alll=[]
        for l in rel_all_1:
            alll.append(l.start_node()['name'])
        if alll==[]:
            #iff=1则说明这个关系中 该节点作为起始点
            iff=1
            for lp in rel_all_2:
                alll.append(lp.end_node()['name'])
        else:
            iff=0
    if alll!=[]:
        if mm==0:
            return list(set(alll))
        else :
            return iff
    else:
        return '查询失败，暂无答案'

def find_rel(word,rel,yuxu,label):
    node = g.find_one(label, property_key='name', property_value=word)
    subject_rel= list(map(get_rel,[node]*len(rel),rel,[yuxu]*len(rel),[0]*len(rel)))
    subject_rel_2=list(map(get_rel,[node]*len(rel),rel,[yuxu]*len(rel),[1]*len(rel)))
    rel_json=[]
    node_json=[buildNodes(node)]
    for i in range(0,len(subject_rel)):
        if subject_rel_2[i]==0:
            for m in range(0,len(subject_rel[i])):
                if subject_rel[i][m] in weapon:
                    temp = g.find_one('weapon',property_key='name',property_value=subject_rel[i][m])
                else:
                    temp = g.find_one('hero', property_key='name', property_value=subject_rel[i][m])
                nodea = buildNodes(temp)
                data={'data':{
                    'relationship': rel[i],
                    'source': subject_rel[i][m],
                    'target': word
                }}
                rel_json.append(data)
                node_json.append(nodea)
        else:
            for m in range(0,len(subject_rel[i])):
                if subject_rel[i][m] in weapons:
                    temp = g.find_one('weapon',property_key='name',property_value=subject_rel[i][m])
                else:
                    temp = g.find_one('hero', property_key='name', property_value=subject_rel[i][m])
                nodea = buildNodes(temp)
                data = {'data': {
                    'relationship': rel[i],
                    'source': word,
                    'target': subject_rel[i][m]
                }}
                rel_json.append(data)
                node_json.append(nodea)
    return  subject_rel ,'|' , node_json ,'|',rel_json
#print(main('赵云被克制'))



#main('赵云吕布技能')

def get_label(thing):
    a = things.index(thing)
    if a <=91:
        return 'weapon'
    else :
        return 'hero'
#search('赵云','hero')
######x下面有改动  多返回一个json数组，里面应该是所有关系的json形式
#search('赵云','hero')
def buildNodes(nodeRecord):
    try:
        data = {"id": nodeRecord['name'], "name": nodeRecord['name']}
        return {"data": data}
    #data.update(nodeRecord.properties)
    except TypeError:
        return u'暂时查询不到'


#buildNodes(a)
def buildEdges(relationRecord):
    data = {"source": relationRecord.start_node()['name'],
            "target": relationRecord.end_node()['name'],
            "relationship": re.findall("[\x80-\xff]+",str(relationRecord))[0]}

    return {"data": data}
#buildEdges(i)

def search(name,label):
    temp_node = g.find_one(label,property_key='name',property_value=name)
    node=buildNodes(temp_node)
    #df = pd.DataFrame()
    #df['name']=[name]
    df=name+':\n'
    if label=='hero':
        for  i in range(0,len(property_all_2)):
            #df[property_name[i]]=[temp_node[property_all_2[i][0]]]
            df=df+property_name[i]+temp_node[property_all_2[i][0]]
    else:
        #df['价格'] = [temp_node['price']]
        #df['属性'] = [temp_node['property']]
        df=df+ '价格:'+ temp_node['price']+'\n'+'属性:'+temp_node['property']
    rel_all = g.match(start_node=temp_node)
    rel_all_2= g.match(end_node = temp_node)
    rel_json=[]
    node_json=[buildNodes(temp_node)]
    for r in rel_all:
        rel_json.append(buildEdges(r))
        node_json.append(buildNodes(r.end_node()))

    for r2 in rel_all_2:
        rel_json.append(buildEdges(r2))
        node_json.append(buildNodes(r2.end_node()))
    #node_json放的是每一个有关系的节点
    return  df ,'|',node_json,'|', rel_json


def find_relation(subject,label):
    node_1 = g.find_one(label[0], property_key='name', property_value=subject[0])
    node_2 = g.find_one(label[1], property_key='name', property_value=subject[1])
    node_1
    rel_all = g.match(start_node=node_1 , end_node= node_2)
    rel_all3 =g.match(start_node=node_2 , end_node= node_1)
    rel_all_2=[]
    st=[]
    ed=[]
    xx=[]
    for p in rel_all:
        rel_all_2.append(re.findall("\[\:\`([\u2E80-\u9FFF]+)\`\]", str(p.relationships))[0])
        st.append(p.start_node()['name'])
        ed.append(p.end_node()['name'])
    for p in rel_all3:
        rel_all_2.append(re.findall("[\x80-\xff]+",str(p.relationships))[0])
        if re.findall("[\x80-\xff]+",str(p.relationships))[0] not in ['相似','搭配']:
            st.append(p.start_node()['name'])
            ed.append(p.end_node()['name'])
    for i in range(0,len(st)):
        xx.append(st[i] + ' '+rel_all_2[i] +' '+ ed[i] )
    if xx!=[]:
        return xx
    else :
        return '没什么关系'

#判断是不是类型问题
def tell_him_yes(subject,ask_if):
    if '近战' in ask_if:
        ask_if[ask_if.index('近战')]='近程'
    temp_node = g.find_one('hero',property_key='name',property_value= subject)
    op = temp_node['attack_range'] + temp_node['tag']
    s=''
    for i in ask_if:
        if i in op:
            s=s+ subject + '是' + i + '英雄' + '\n'
        else:
            s=subject + '不是' + i + '英雄' + '\n'
    return s
#tell_him_yes('赵云',['近战'])
def compare (subject , property):
    temp_node_1 = g.find_one('hero',property_key='name',property_value= subject[0])
    temp_node_2 = g.find_one('hero',property_key='name',property_value= subject[1])
    pro = property_all_2[find_index(property)][0]
    property_1 = temp_node_1[pro]
    property_2 = temp_node_2[pro]
    if len(property_1) >10:
        return '这个不太好比较哦'
    else:
        if property_1 > property_2:
            return subject[0]
        else:
            return subject[1]
def all_skills(subject,label):
    answer=[]
    for i in range(0,len(subject)):
        temp_node=g.find_one(label[i],property_key='name',property_value=subject[i])
        if label[i]=='hero':
            m= subject[i]+'被动技能:' + temp_node['skill_passive']+'\n'+'一技能:'+temp_node['skill_1'] +'\n'+ '二技能:'+temp_node['skill_2']+'\n'+'大招:'+temp_node['R']
            answer.append(m)
    return answer

def main(a):
    words = jieba.cut(a)
    word = []
    for m in words:
        word.append(m)
    subject = []
    sentence=pd.DataFrame(word,columns=['a'])
    subject=list(sentence['a'][(sentence['a']).isin(things)])
    property = list(sentence['a'][(sentence['a']).isin(property_all)])
    rel_1=list(sentence['a'][(sentence['a']).isin(rel_3)])
    rel = list(map(find_2 , rel_1))
    label = list(map(get_label, subject))
    ask_if = list(sentence['a'][(sentence['a']).isin(if_true)])
    #关于比较的这个还没想好更精确的模板
    if (len(subject)==2)&(len(property)>=1)&('更' in a) :
        return compare(subject,property[0]),'||'
    #if (len(subject)>2)&(len(property)>=1)&('最' in a) :
        #return  compare_2(subject,property)



    if (len(subject) == 1 )& (len(property) != 0):
        return find_subject_property(subject[0], property , label[0]),'|','|'
    if '技能' in word:
        return all_skills(subject,label),'|','|'
    if (len(subject) == 2):
        return find_relation(subject, label),'|','|'
    if (len(subject) == 1) & (len(rel) != 0):
        if '克制' in word:
            if '被' in word:
                yuxu = word.index(subject[0]) < word.index('被')
            else:
                yuxu = word.index(subject[0]) > word.index('克制')
        else:
            yuxu = None
        return find_rel(subject[0],rel,yuxu, label[0])
    if len(subject) == 2 & len(rel) != 0:
        return find_rel_D(subject, rel, label),'|','|'
    if (ask_if!=[]) & (label==['hero']):
        return  tell_him_yes(subject[0],ask_if),'|','|'
    if (len(subject) == 1) & (len(property) == 0)& (rel ==[] ):
        return search(subject[0],label[0])
    else:
        return ('???'),'|','|'
#find_rel('赵云', ['克制'], None, 'hero')


#find_relation(['赵云','关羽'],['hero','hero'])
#a=g.find_one('hero',property_key='name',property_value='赵云')
#b=g.find_one('hero',property_key='name',property_value='关羽')
#c=g.match(start_node=a,end_node=b)

#main('赵云移速')
#print '\xe7\xa7\xbb\xe5\x8a\xa8\xe9\x80\x9f\xe5\xba\xa6:380'
'''
#生成可视化需要的节点
for i in heros:
    temp = g.find_one('hero',property_key='name',property_value=i)
    buildNodes(temp)
for j in weapons:
    temp = g.find_one('weapon',property_key='name',property_value=j)
    buildNodes(temp)

'''
keywords = sys.argv[1]
for i in main(keywords):
	for j in i:
		print j
