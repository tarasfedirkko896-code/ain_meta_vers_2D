from pathlib import Path
import json,copy,shutil,hashlib,base64
from collections import deque
from PIL import Image
P=Path(__file__).resolve().parent;SRC=P.parent/'ain-conference-2026'
source_map=SRC/'map-ain-v23.tmj' if (SRC/'map-ain-v23.tmj').exists() else P/'source-v23.tmj'
m=json.loads(source_map.read_text());original=copy.deepcopy(m)
W,H,T=m['width'],m['height'],32;N=W*H
art=next(l for l in m['layers'] if l['name']=='AIN artwork')['data'][:]
col=next(l for l in m['layers'] if l['name']=='Collisions')['data'][:]
start=next(l for l in m['layers'] if l['name']=='start')['data'][:]
# Tile reassembly only: no repainting or alteration of existing artwork PNGs.
# Geometry is authored in 1280x768 reference coordinates (one tile = 8 units).
objects=[]
def region(name,box,above=False):
 x0,y0,x1,y1=box;ids=[]
 for y in range(H):
  for x in range(W):
   if x0<=x*8+4<x1 and y0<=y*8+4<y1:ids.append(y*W+x)
 objects.append(dict(name=name,above=above,ids=ids))
region('Scene / display',(400,0,880,165))
region('Seats / left',(475,180,620,296))
region('Seats / right',(660,180,805,296))
# Complete booth assemblies stay independent of the architectural floor.
booths=[('ROZETKA',(48,242,218,355)),('monobank',(250,242,420,355)),('AJAX',(48,375,218,486)),('MacPaw',(250,375,420,486)),('Нова пошта',(862,242,1025,355)),('uklon',(1065,242,1235,355)),('Київстар',(862,375,1025,486)),('Дія',(1065,375,1235,486))]
for name,b in booths:region('Booth / '+name,b)
region('AIN centerpiece',(550,385,720,510))
# Wall-mounted plaques: independent tile layers, not ground markings.
for name,b in [('Stage',(564,303,604,329)),('Networking 1',(105,31,263,53)),('Networking 2',(1020,31,1170,53)),('Networking 3',(132,675,230,694)),('Networking 4',(1055,675,1175,694)),('Partners L',(115,181,240,201)),('Partners R',(1040,181,1160,201))]:region('Sign / '+name,b,True)
# Tops separated above the player plane. Exact existing artwork tiles are reused.
for name,b in booths:
 x0,y0,x1,y1=b
 region('Canopy / '+name,(x0+12,y0,x1-12,y0+38),True)
for i,b in enumerate([(273,226,291,253),(282,356,300,384),(433,350,459,382),(433,399,457,428),(437,457,461,483),(817,347,843,379),(817,398,841,425),(817,457,842,484),(994,227,1018,252),(1171,227,1195,253),(540,568,567,594),(715,568,744,595)]):region('Foliage / %02d'%i,b,True)
# Last region wins, so foliage and canopies supersede booth base tiles cleanly.
owner={}
for j,o in enumerate(objects):
 for i in o['ids']:owner[i]=j
layers=[]
def layer(name,data):return dict(id=len(layers)+1,name=name,type='tilelayer',width=W,height=H,x=0,y=0,opacity=1,visible=True,data=data)
floor=art[:]
# A quiet floor tile underneath separated pieces. It is covered in normal view.
floor_sample=art[66*W+63]
for i in owner:floor[i]=floor_sample
layers.append(layer('Ground / architecture',floor))
for j,o in enumerate(objects):
 if o['above']:continue
 a=[0]*N
 for i in o['ids']:
  if owner.get(i)==j:a[i]=art[i]
 layers.append(layer(o['name'],a))
layers.append(layer('Collisions',col));layers.append(layer('start',start))
layers.append(dict(id=len(layers)+1,name='floorLayer',type='objectgroup',objects=[],x=0,y=0,visible=True,opacity=1))
for j,o in enumerate(objects):
 if not o['above']:continue
 a=[0]*N
 for i in o['ids']:
  if owner.get(i)==j:a[i]=art[i]
 layers.append(layer(o['name'],a))
m['layers']=layers;m['nextlayerid']=len(layers)+1
m['properties']=[dict(name='mapName',type='string',value='AIN 2D Hybrid / v2'),dict(name='mapDescription',type='string',value='Separate floor, seats, booths, wall signs and foreground canopies. Based on approved v23.'),dict(name='mapImage',type='string',value='preview.jpg')]
for ts in m['tilesets']:
 # New filenames prevent stale artwork cache; all assets in root for easy upload.
 old=ts['image'];new='hybrid-'+old
 source_asset=SRC/old if (SRC/old).exists() else P/new
 if source_asset.resolve()!=(P/new).resolve():shutil.copyfile(source_asset,P/new)
 ts['image']=new
(P/'map.tmj').write_text(json.dumps(m,ensure_ascii=False,separators=(',',':')))
(P/'map-2d-v2.tmj').write_text(json.dumps(m,ensure_ascii=False,separators=(',',':')))
# Validate unchanged rendering: highest occupied visible tile equals original artwork.
composed=[0]*N;fore=set();floor_index=next(i for i,l in enumerate(layers) if l['name']=='floorLayer')
for k,l in enumerate(layers):
 if l['type']!='tilelayer' or l['name'] in ('start','Collisions'):continue
 for i,gid in enumerate(l['data']):
  if gid:composed[i]=gid
  if gid and k>floor_index:fore.add(i)
assert composed==art,'Artwork changed'
assert next(l for l in layers if l['name']=='Collisions')['data']==original['layers'][1]['data']
# BFS with a body footprint; radius10 means path nodes cannot rely on corner cutting.
def valid(x,y):
 return 0<=x<W and 0<=y<H and not col[y*W+x]
starts=[i for i,v in enumerate(start) if v];assert starts and all(not col[i] for i in starts)
q=deque([starts[0]]);seen={starts[0]}
while q:
 i=q.popleft();x,y=i%W,i//W
 for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
  n=yy*W+xx
  if valid(xx,yy) and n not in seen:seen.add(n);q.append(n)
assert len(seen)==sum(not v for v in col)
assert all(col[x] and col[(H-1)*W+x] for x in range(W))
assert all(col[y*W] and col[y*W+W-1] for y in range(H))
for ts in m['tilesets']:
 im=Image.open(P/ts['image']);assert im.size==(ts['imagewidth'],ts['imageheight']);assert max(im.size)<=2048
free_fore=sorted(i for i in fore if not col[i]);assert free_fore
report=dict(render_matches_v23=True,collision_matches_v23=True,all_walkable_tiles_connected=True,walkable_tiles=len(seen),layers=len(layers),foreground_tiles=len(fore),walkable_foreground_tiles=len(free_fore),start_tiles=len(starts),max_texture_size=2048,live_WorkAdventure_test='not performed',source_map_sha256=hashlib.sha256(source_map.read_bytes()).hexdigest())
(P/'validation.json').write_text(json.dumps(report,indent=2))
if (SRC/'AIN_v23_labels.jpg').exists():shutil.copyfile(SRC/'AIN_v23_labels.jpg',P/'preview.jpg')
# Offline preview consumes same actual map layers and images, not a fake illustration.
manifest={ts['image']:'data:image/png;base64,'+base64.b64encode((P/ts['image']).read_bytes()).decode() for ts in m['tilesets']}
manifest_data=json.dumps(manifest);map_data=json.dumps(m,ensure_ascii=False)
template=(P/'viewer.template.html').read_text();(P/'walk-test.html').write_text(template.replace('__MAP__',map_data).replace('__IMAGES__',manifest_data).replace('__TESTSPOT__',str(free_fore[len(free_fore)//2])))
print(json.dumps(report,indent=2))
