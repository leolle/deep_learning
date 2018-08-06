# -*- coding: utf-8 -*-
# import os
# os.chdir('/root/文档/王者荣耀')
from py2neo import Node, Graph, Relationship
import pandas as pd
g = Graph("http://localhost:7474")
g.run("MATCH (n) OPTIONAL MATCH (n)-[r]-()DELETE n,r")
g.find_one('hero')
#建立节点 用的是cypher语言 不知道为什么用Py2neo建立不了
"""
g.run('''LOAD CSV WITH HEADERS  FROM "file:./hero66666.csv" AS data
 MERGE (label:hero{name:data['name'],skill_passive:data['skill_passive'],skill_1:data['skill_1'],skill_1_cooling:data['skill_1_cooling'],skill_1_cost:data['skill_1_cost'],skill_2:data['skill_2'],skill_2_cost:data['skill_2_cost'],skill_2_cooling:data['skill_2_cooling'],R:data['R'],R_cooling:data['R_cooling'],R_cost:data['R_cost'],tag:data['tag'],HP:data['HP'],MP:data['MP'],HP_recover:data['HP_recover'],MP_recover:data['MP_recover'],attack:data['attack'],defense:data['defense'],magic_defense:data['magic_defense'],speed:data['speed'],attack_range:data['attack_range']})''')
"""

hero_data = pd.read_csv('./data/hero66666.csv', header=0, encoding='utf-8')
for i in range(0, len(hero_data)):
    temp = Node(
        'hero',
        name=str(hero_data['name'][i]),
        skill_passive=str(hero_data['skill_passive'][i]),
        skill_1=str(hero_data['skill_1'][i]),
        skill_1_cooling=str(hero_data['skill_1_cooling'][i]),
        skill_1_cost=str(hero_data['skill_1_cost'][i]),
        skill_2=str(hero_data['skill_2'][i]),
        skill_2_cost=str(hero_data['skill_2_cost'][i]),
        skill_2_cooling=str(hero_data['skill_2_cooling'][i]),
        R=str(hero_data['R'][i]),
        R_cooling=str(hero_data['R_cooling'][i]),
        R_cost=str(hero_data['R_cost'][i]),
        tag=str(hero_data['tag'][i]),
        HP=str(hero_data['HP'][i]),
        MP=str(hero_data['MP'][i]),
        HP_recover=str(hero_data['HP_recover'][i]),
        MP_recover=str(hero_data['MP_recover'][i]),
        attack=str(hero_data['attack'][i]),
        defense=str(hero_data['defense'][i]),
        magic_defense=str(hero_data['magic_defense'][i]),
        speed=str(hero_data['speed'][i]),
        attack_range=str(hero_data['attack_range'][i]))
    g.create(temp)
#建立关系，这里用的是Py2neo2
weapon_data = pd.read_excel('./data/data1.xlsx', header=0)
weapon_data[u'物品名称'][0]
for i in range(0, len(weapon_data)):
    temp = Node(
        'weapon',
        price=str(weapon_data[u'价格'][i]),
        name=weapon_data[u'物品名称'][i],
        property=weapon_data[u'属性1'][i] + ' ' + weapon_data[u'属性2'][i] + ' ' +
        weapon_data[u'属性3'][i] + ' ' + weapon_data[u'属性4'][i] + ' ' +
        weapon_data[u'属性5'][i])
    g.create(temp)

data = pd.read_csv('./data/relation6666.csv', header=0, sep=',')
print(len(data))
m = 0
for m in range(0, 1015):
    try:
        rel = Relationship(
            g.find_one(
                label='hero',
                property_key='name',
                property_value=data['name'][m]), data['guanxi'][m],
            g.find_one(
                label='hero',
                property_key='name',
                property_value=data['name2'][m]))
        g.create(rel)
    except AttributeError:
        print(m)
m = 0
for m in range(1015, 1274):
    try:
        rel = Relationship(
            g.find_one(
                label='weapon',
                property_key='name',
                property_value=data['name'][m]), data['guanxi'][m],
            g.find_one(
                label='hero',
                property_key='name',
                property_value=data['name2'][m]))
        g.create(rel)
    except AttributeError:
        print(m)
m = 0
for m in range(1274, 1434):
    rel = Relationship(
        g.find_one(
            label='weapon', property_key='name',
            property_value=data['name'][m]), data['guanxi'][m],
        g.find_one(
            label='weapon',
            property_key='name',
            property_value=data['name2'][m]))
    g.create(rel)
m = 0

for m in range(1434, 1842):
    rel = Relationship(
        g.find_one(
            label='hero', property_key='name', property_value=data['name'][m]),
        data['guanxi'][m],
        g.find_one(
            label='weapon',
            property_key='name',
            property_value=data['name2'][m]))
    g.create(rel)
