# Assemble carnet-grece.html (artifact) and site/index.html (standalone, Netlify)
import json, html, shutil, os
src=open('src.html',encoding='utf-8').read()
maps=open('maps.html',encoding='utf-8').read()
c=json.load(open('credits.json',encoding='utf-8'))
names={'palamidi':'Nauplie depuis Palamidi','nafplio':'Akronauplie','bourtzi':'Bourtzi','canal':'Canal de Corinthe','acrocorinth':'Acrocorinthe','corinth':"Temple d'Apollon",'mycenae':'Porte des Lions','epidaurus':'Épidaure','littlevenice':'Little Venice','windmills':'Moulins de Kato Mili','delos':'Délos','parthenon':'Acropole','anafiotika':'Anafiotika','sounion':'Sounion','lycabettus':'Vue du Lycabette','monastiraki':'Monastiraki','vouliagmeni':'Vouliagmeni','nemea':'Némée'}
cr=''.join(f'<li>{names[k]} : <a href="{v["page"]}">{html.escape(v["author"])}</a>, {v["license"]}</li>' for k,v in c.items())
body=src.replace('{{MAP}}',maps).replace('{{CREDITS}}',cr)
open('carnet-grece.html','w',encoding='utf-8').write(body)
head,rest=body.split('</style>',1)
standalone=('<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
 '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
 '<meta name="robots" content="noindex, nofollow">\n'
 '<style>html{color-scheme:light}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
 + head + '</style>\n</head>\n<body>\n' + rest + '\n</body>\n</html>\n')
os.makedirs('site/img',exist_ok=True)
open('site/index.html','w',encoding='utf-8').write(standalone)
for f in os.listdir('img'): shutil.copy('img/'+f,'site/img/'+f)
print('ok',len(body))
