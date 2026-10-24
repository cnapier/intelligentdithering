import numpy as np, random
from PIL import Image, ImageDraw, ImageFilter
random.seed(7); np.random.seed(7)
S=3; W,H=1920//S,720//S
img=Image.new("L",(W,H),0); d=ImageDraw.Draw(img)
G=8  # routing grid
def route(x,y,steps):
    pts=[(x,y)]; dx,dy=random.choice([(1,0),(-1,0),(0,1),(0,-1)])
    for _ in range(steps):
        if random.random()<0.25:
            dx,dy=random.choice([(dx,dy),(dx or random.choice([-1,1]),dy or random.choice([-1,1]))])
            if dx and dy and random.random()<0.5: dx,dy=(dx,0) if random.random()<.5 else (0,dy)
        n=random.randint(2,7); x+=dx*G*n; y+=dy*G*n; pts.append((x,y))
    return pts
for i in range(110):
    x=random.randrange(0,W,G); y=random.randrange(0,H,G)
    pts=route(x,y,random.randint(3,9)); b=random.randint(90,200)
    d.line(pts,fill=b,width=random.choice([1,1,2]))
    for p in (pts[0],pts[-1]):
        r=random.choice([2,3]); d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],outline=255,fill=b//3)
# a few chips
for i in range(7):
    cx,cy=random.randrange(20,W-60),random.randrange(10,H-40); w,h=random.randint(24,56),random.randint(18,36)
    d.rectangle([cx,cy,cx+w,cy+h],fill=60,outline=210)
    for k in range(cx+4,cx+w-2,5): d.line([k,cy-4,k,cy],fill=200); d.line([k,cy+h,k,cy+h+4],fill=200)
a=np.asarray(img,dtype=float)/255
glow=np.asarray(img.filter(ImageFilter.GaussianBlur(6)),dtype=float)/255
yy,xx=np.mgrid[0:H,0:W]
# base gradient: brighter to the edges, darker centre band for title legibility
grad=0.10+0.18*(1-yy/H)
cx=np.abs(xx-W/2)/(W/2); vign=np.clip(0.35+0.65*cx**1.3,0,1)
L=np.clip(grad+ (a*0.9+glow*1.2)*vign ,0,1)
# Bayer 8x8 ordered dither into a 5-colour ramp
def bayer(n):
    m=np.array([[0,2],[3,1]])
    while m.shape[0]<n: m=np.block([[4*m,4*m+2],[4*m+3,4*m+1]])
    return (m+0.5)/m.size
B=np.tile(bayer(8),(H//8+1,W//8+1))[:H,:W]
pal=np.array([(8,12,24),(18,36,58),(24,92,110),(40,170,170),(240,180,70)],dtype=np.uint8)
lv=L*(len(pal)-1); idx=np.floor(lv+ (B-0.5)*0.999 +0.5).astype(int).clip(0,len(pal)-1)
out=Image.fromarray(pal[idx]).resize((W*S,H*S),Image.NEAREST)
out.save("static/img/home-bg-dither.png",optimize=True)
print(out.size)
