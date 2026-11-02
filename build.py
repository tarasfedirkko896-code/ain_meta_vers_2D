from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json, base64, hashlib
P=Path(__file__).parent; S=32; W=40; H=32
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def rect(d,b,c):d.rectangle(b,fill=c)
# Original code-native tile assets, each independently reusable.
tiles=[]
def tile(kind):
 im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
 if kind in ('floor','stage','aisle'):
  c={'floor':'#223645','stage':'#393858','aisle':'#284457'}[kind];rect(d,(0,0,31,31),c);rect(d,(0,31,31,31),'#192937');rect(d,(31,0,31,31),'#192937');rect(d,(2,2,29,2),'#304758' if kind!='stage' else '#4b4969')
 if kind=='wall':
  rect(d,(0,0,31,31),'#101c30');rect(d,(1,1,30,6),'#7893b1');rect(d,(1,7,30,24),'#344963');rect(d,(2,9,29,10),'#516c88');rect(d,(1,26,30,28),'#55d4de')
 if kind=='chair':
  rect(d,(5,8,27,30),'#132337');rect(d,(5,4,25,17),'#637cd1');rect(d,(7,6,23,15),'#8f9ee2');rect(d,(7,18,24,25),'#47589a');rect(d,(4,16,7,25),'#b8c8e0');rect(d,(24,16,27,25),'#b8c8e0');rect(d,(8,26,10,29),'#0d1728');rect(d,(22,26,24,29),'#0d1728')
 if kind=='plant':
  rect(d,(9,20,23,29),'#ac9366');rect(d,(7,20,25,23),'#e0c58b');
  for b,c in [((13,2,18,22),'#4eaa82'),((5,6,13,14),'#387e66'),((19,5,27,13),'#67c399'),((2,13,14,19),'#62bb8a'),((18,14,29,20),'#398f73')]:rect(d,b,c)
 if kind=='steps':
  rect(d,(0,0,31,31),'#364964')
  for y in (2,10,18,26):rect(d,(0,y,31,y+2),'#a1bddd');rect(d,(0,y+3,31,y+4),'#192b43')
 if kind=='light':
  rect(d,(10,0,21,31),'#1a2540');rect(d,(12,2,19,29),'#8277df');rect(d,(14,3,17,28),'#d2bfff')
 if kind=='desk':
  rect(d,(2,7,29,26),'#101d30');rect(d,(2,5,29,20),'#a7bbcc');rect(d,(4,7,27,17),'#3d526e');rect(d,(5,19,26,21),'#67dcd6')
 return im
names=['floor','stage','aisle','wall','chair','plant','steps','light','desk']
for n in names:tiles.append(tile(n))
# Independently editable stage display and sign, sliced into tiles for Tiled.
def panel(w,h,title,subtitle=''):
 im=Image.new('RGBA',(w,h),'#111d35');d=ImageDraw.Draw(im);d.rectangle((1,1,w-2,h-2),outline='#7186bb',width=3);d.rectangle((7,7,w-8,h-8),outline='#363e6c',width=2)
 for x in (14,w-18):d.rectangle((x,14,x+3,h-15),fill='#9d8bff')
 f=ImageFont.truetype(font,28 if h>50 else 13); bb=d.textbbox((0,0),title,font=f);d.text(((w-bb[2])/2,20 if h>50 else 7),title,font=f,fill='#f4f1ff')
 if subtitle:d.text((w/2,67),subtitle,font=ImageFont.truetype(font,16),fill='#8adbdc',anchor='mm')
 return im
screen=panel(384,96,'ain','КІБЕРБЕЗПЕКА');screen.save(P/'assets/display.png')
sign=panel(192,32,'ГОЛОВНА СЦЕНА');sign.save(P/'assets/sign.png')
def addpanel(im):
 first=len(tiles)+1
 for y in range(0,im.height,32):
  for x in range(0,im.width,32):tiles.append(im.crop((x,y,x+32,y+32)))
 return first
screenid=addpanel(screen);signid=addpanel(sign)
cols=16;rows=(len(tiles)+15)//16;atlas=Image.new('RGBA',(cols*32,rows*32))
for i,im in enumerate(tiles):atlas.paste(im,((i%cols)*32,(i//cols)*32))
atlas.save(P/'assets/tiles.png')
floor=[1]*(W*H);obj=[0]*(W*H);start=[0]*(W*H)
def put(a,x,y,v):a[y*W+x]=v
def fill(a,x,y,w,h,v):
 for yy in range(y,y+h):
  for xx in range(x,x+w):put(a,xx,yy,v)
fill(floor,4,3,32,8,2);fill(floor,18,11,4,20,3)
for x in range(W):put(obj,x,0,4);put(obj,x,H-1,4)
for y in range(H):put(obj,0,y,4);put(obj,W-1,y,4)
for x in range(4,36):put(obj,x,3,4);put(obj,x,10,4)
fill(obj,18,10,4,1,0);fill(floor,18,10,4,1,7)
for y in range(4,10):put(obj,4,y,4);put(obj,35,y,4)
for y in range(3):
 for x in range(12):put(obj,14+x,4+y,screenid+y*12+x)
for x in range(6):put(obj,9+x,10,signid+x)
for x in [8,12,16,23,27,31]:put(obj,x,8,9)
for x in [5,34]:
 for y in [5,6,7]:put(obj,x,y,8)
for y in [13,15,17,19,21]:
 for x in list(range(7,17))+list(range(23,33)):put(obj,x,y,5)
for x in [4,35]:
 for y in [12,17,22,27]:put(obj,x,y,6)
for x in list(range(5,15))+list(range(25,35)):put(obj,x,24,4)
for x in [6,33]:put(obj,x,24,6)
fill(start,18,28,4,2,1)
# Collision is per object tile, seats intentionally walkable for event seating.
blocked={4,6,8,9}|set(range(screenid,screenid+36))|set(range(signid,signid+6))
def layer(name,data,id):return dict(id=id,name=name,type='tilelayer',width=W,height=H,x=0,y=0,visible=True,opacity=1,data=data)
layers=[layer('floor',floor,1),layer('start',start,2),dict(id=3,name='floorLayer',type='objectgroup',objects=[],visible=True,opacity=1,x=0,y=0),layer('furniture',obj,4)]
layers[1]['visible']=False
m=dict(type='map',version='1.10',tiledversion='1.11.2',orientation='orthogonal',renderorder='right-down',width=W,height=H,tilewidth=32,tileheight=32,infinite=False,nextlayerid=5,nextobjectid=1,layers=layers,tilesets=[dict(firstgid=1,name='AIN modular tiles',image='assets/tiles.png',imagewidth=atlas.width,imageheight=atlas.height,tilewidth=32,tileheight=32,columns=cols,tilecount=len(tiles),margin=0,spacing=0,tiles=[dict(id=i-1,properties=[dict(name='collides',type='bool',value=True)]) for i in sorted(blocked)])])
(P/'map.tmj').write_text(json.dumps(m,ensure_ascii=False),encoding='utf-8')
preview=Image.new('RGBA',(W*32,H*32))
for a in [floor,obj]:
 for i,v in enumerate(a):
  if v:preview.alpha_composite(tiles[v-1],((i%W)*32,(i//W)*32))
preview.convert('RGB').save(P/'preview.png')
# Connectivity: stage, both seating blocks and entrance must connect.
from collections import deque
seen={(20,28)};q=deque(seen)
while q:
 x,y=q.popleft()
 for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
  if 0<=xx<W and 0<=yy<H and (xx,yy) not in seen and obj[yy*W+xx] not in blocked:seen.add((xx,yy));q.append((xx,yy))
for p in [(20,9),(8,13),(31,21),(20,25)]:assert p in seen,p
assert all(len(a)==W*H for a in [floor,obj,start])
(P/'validation.json').write_text(json.dumps({'reachable_tiles':len(seen),'stage_and_seats_reachable':True,'tile_atlas_size':[atlas.width,atlas.height]},indent=2))
DATA=json.dumps(dict(w=W,h=H,floor=floor,objects=obj,blocked=list(blocked)))
B64=base64.b64encode((P/'assets/tiles.png').read_bytes()).decode()
html='''<!doctype html><html lang="uk"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AIN 2D · Stage Prototype</title><style>*{box-sizing:border-box}body{margin:0;background:#0c1523;color:#e4eaf5;font:15px system-ui}header{padding:20px 4vw;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #304156}b{font-size:22px}small{display:block;color:#98afc6;margin-top:5px}button{background:#253a50;color:white;border:1px solid #68839b;padding:10px 16px;border-radius:6px;cursor:pointer}main{padding:20px;display:flex;justify-content:center}canvas{max-width:100%;height:auto;max-height:78vh;image-rendering:pixelated;outline:none;border:1px solid #40516a}footer{text-align:center;color:#9aadc4;padding:0 12px 20px}</style><header><div><b>AIN <span style="color:#9a8aff">2D</span> / Сцена</b><small>Окремий прототип · 01</small></div><button id="collision">Показати перешкоди</button></header><main><canvas id="map" width="1280" height="1024" tabindex="0" aria-label="Карта. Рух стрілками або WASD"></canvas></main><footer>Рух: WASD / стрілки · Клікни на карту, щоб почати · Крісла прохідні для розміщення глядачів</footer><script>const D=__DATA__,img=new Image();img.src='data:image/png;base64,__IMG__';const c=document.querySelector('canvas'),ctx=c.getContext('2d');ctx.imageSmoothingEnabled=false;let p={x:656,y:920},keys={},show=false,last=0;document.querySelector('button').onclick=()=>{show=!show;document.querySelector('button').textContent=show?'Сховати перешкоди':'Показати перешкоди'};window.onkeydown=e=>{if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key))e.preventDefault();keys[e.key.toLowerCase()]=true};window.onkeyup=e=>keys[e.key.toLowerCase()]=false;window.onblur=()=>keys={};function free(x,y){for(const dx of [-7,7])for(const dy of [-4,4]){let a=Math.floor((x+dx)/32),b=Math.floor((y+dy)/32);if(a<0||b<0||a>=D.w||b>=D.h||D.blocked.includes(D.objects[b*D.w+a]))return false}return true}function draw(t){let dt=Math.min((t-last)/1000,.04);last=t;let dx=(keys.d||keys.arrowright?1:0)-(keys.a||keys.arrowleft?1:0),dy=(keys.s||keys.arrowdown?1:0)-(keys.w||keys.arrowup?1:0),len=Math.hypot(dx,dy)||1;if(free(p.x+dx/len*140*dt,p.y))p.x+=dx/len*140*dt;if(free(p.x,p.y+dy/len*140*dt))p.y+=dy/len*140*dt;ctx.clearRect(0,0,c.width,c.height);for(const arr of [D.floor,D.objects])arr.forEach((v,i)=>{if(v)ctx.drawImage(img,(v-1)%16*32,Math.floor((v-1)/16)*32,32,32,i%D.w*32,Math.floor(i/D.w)*32,32,32)});if(show)D.objects.forEach((v,i)=>{if(D.blocked.includes(v)){ctx.fillStyle='#fa426b88';ctx.fillRect(i%D.w*32,Math.floor(i/D.w)*32,32,32)}});let x=Math.round(p.x),y=Math.round(p.y);ctx.fillStyle='#0b142a88';ctx.fillRect(x-10,y-2,20,8);ctx.fillStyle='#101b2d';ctx.fillRect(x-7,y-24,14,24);ctx.fillStyle='#e2b18c';ctx.fillRect(x-5,y-23,10,9);ctx.fillStyle='#68d6cf';ctx.fillRect(x-7,y-13,14,10);ctx.fillStyle='#a4b4d8';ctx.fillRect(x-6,y-3,4,5);ctx.fillRect(x+2,y-3,4,5);requestAnimationFrame(draw)}img.onload=()=>requestAnimationFrame(draw);c.focus();</script></html>'''
(P/'index.html').write_text(html.replace('__DATA__',DATA).replace('__IMG__',B64),encoding='utf-8')
print('Built',P,'tiles:',len(tiles),'reachable:',len(seen))
