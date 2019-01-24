#! /usr/bin/python3
import pygame
import sys
import math
import random
import subprocess
from time import sleep

def screen_size():
    size = (None, None)
    args = ["xrandr", "-q", "-d", ":0"]
    proc = subprocess.Popen(args,stdout=subprocess.PIPE)
    for line in proc.stdout:
        if isinstance(line, bytes):
            line = line.decode("utf-8")
            if "Screen" in line:
                size = (int(line.split()[7]),  int(line.split()[9][:-1]))
    return size

size = screen_size()
WIDTH,HEIGHT = size[0],size[1]
screen = pygame.display.set_mode(screen_size(),pygame.FULLSCREEN,32)

pygame.font.init()
G = 6.67*10**-11


def getRads (delta):
	alpha = 0
	hypot = math.hypot(delta[0],delta[1])
	
	if delta[0] != 0:
		if delta[1] == 0:
			if delta[0] > 0:
				alpha = 0
			elif delta[0] < 0:
				alpha = math.pi
		else:
			if delta[1] > 0 and delta[0] > 0:
				alpha = math.asin(delta[1]/hypot)
			if delta[1] > 0 and delta[0] < 0:
				alpha = math.pi-math.asin(delta[1]/hypot)
			if delta[1] < 0 and delta[0] < 0:
				alpha = math.pi+math.asin(delta[1]/hypot*-1)
			if delta[1] < 0 and delta[0] > 0:
				alpha = math.pi*2- math.asin(delta[1]/hypot*-1)
	else:
		if delta[1] > 0:
			alpha = math.pi/2
		elif delta[1] < 0:
			alpha = math.pi*3/2
	return alpha
def write (string, pos, size=10, color =[255,255,255],font ="Arial",boolean = False):
		font = pygame.font.SysFont(font,size)
		text = font.render(str(string),boolean,color)
		screen.blit(text, pos)
class Button ():
	def __init__(self,pos,text,size = 10, color = [255,255,255]):
		self.color = color
		self.text = text
		self.pos = pos
		self.size = size
		self.rectW = len(text)*size 
		self.rectH = size 
		self.rect = pygame.Rect(pos[0],pos[1],self.rectW,self.rectH)
		self.isAlreadyPressed = True
		self.isIn = False
		self.count = 1
		self.pressed = False	
	def update(self):
		self.draw()
		self.calculate()
	def setPressed(self,val):
		self.pressed = val

	def getPressed (self):
		return self.pressed

	def getIsIn(self):
		return self.isIn
	def reset(self):
		self.count =1
		
	def calculate(self):
		mousePos = pygame.mouse.get_pos()
		mouse = pygame.mouse.get_pressed()[0]
		if mousePos[0] > self.pos[0] and mousePos[0] < self.pos[0]+self.rectW and mousePos[1] > self.pos[1] and mousePos[1] < self.pos[1]+self.rectH:		
			self.isIn = True
			if self.isAlreadyPressed and mouse:
				self.color = [255,0,0]
				self.count+=1
				self.isAlreadyPressed = False
				if self.count%2 ==0:			
					self.pressed = True			
				else:
					self.pressed = False
			if not mouse:
				self.isAlreadyPressed = True
				
		else:
			self.isIn = False
			if mouse:
				self.isAlreadyPressed = False
			else:
				self.isAlreadyPressed = True
			
		if self.pressed == False:
			self.color = [255,255,255]
		else:
			self.color = [255,0,0]
				
	def draw(self):
		pygame.draw.rect(screen, self.color, self.rect,1)
		write(self.text,(self.pos[0]+(self.rectW/4), self.pos[1]+(self.rectH/2)-(self.size/2)-2),self.size,self.color)
class Body ():
	def __init__ (self,x,y,mass, vi, color, rad, scale = 10**9,name='body',ing=list()):
		self.x = x
		self.y = y
		self.name = name
		self.dontattract = ing
		self.scale = scale
		self.coor = pygame.math.Vector2(self.x,self.y)
		self.mass = mass #masa del cuerpo
		self.radius = rad
		self.potencialEnegy = 0
		self.color = color #Color del Cuerpo
		self.alpha = 0 #Grados del vector Fuerza/velocidad/aceleracion...
		self.module = 0 #Modulo de la Fuerza Gravitatoria
		self.bodys = list() #Todos los cuerpos que influllen en su movimiento
		self.time = 0 #Tiempo de cada cuerpo, el cual comienza cuando se crea el cuerpo
		self.a = (0,0) #Vector aceleracion del cuerpo
		self.v =  vi #Vector velocidad del cuerpo
		self.union = False #Lineas imaginarias de union entre cuerpos
		self.vector = False #Mostracion grafica de los vectores de fuerza
		self.life = True
		self.points = True
		self.timeStep = 0
		self.step = 10		
		self.lastPos =[]
		self.static = True
		self.colision = True
		self.limitVector = False
		self.ing = False
		self.never = False
		self.Epot = False
	def addBody (self, body):
		self.bodys.append(body)
	def delateBody(self,i):
		self.bodys.pop(i)
	def update (self,bodys):
		self.bodys = bodys
		self.calcule()
		self.attraction()
		self.draw()
		self.act()
	def setUnion(self,f):
		self.union = f
	def setVector(self,v):
		self.vector = v
	def setColision(self,val):
		self.colision = val
	def getLife(self):
		return self.life
	def setPoints(self,p):
		self.points = p
	def setStatic(self,s):
		self.static = s
	def setIngnoreBody(self, name):	
		self.dontattract.append(name)
	def ingnoreAll(self,v):
		self.ing = v
	def setScale(self,v):
		self.scale = v
	def setLimitVector(self,v):
		self.limitVector = v
	def setNeverMove(self,v):
		self.never = v
	def setEpot(self,v):
		self.Epot = v

	def calcule(self):
		radio = 0 #Distancia en px de este cuerpo hasta los demas
		angle = 0 #angulo formado con la h del primer cuadrante del radio anterion
		g = 0 # Fuerza ejercida entre este cuerpo y otro
		resg = pygame.math.Vector2(0.0,0.0) #Vector fuerza de la fuerza anterior
		
		for bodys in self.bodys:
			if not bodys == self:
					
				radio = pygame.math.Vector2(bodys.coor - self.coor) #hallamos el radio
				dis = math.hypot(radio[0],radio[1])
				angle = getRads(radio)#hallamos el angulo
				self.potencialEnegy += -(G*self.mass*bodys.mass)/dis
				if self.union:
					pygame.draw.line(screen,[144,191,208],(self.x,self.y),(bodys.x,bodys.y),1)#pintamos las lineas de union
				
				if self.colision and not self.never and not bodys.never:	
					if dis < self.radius + bodys.radius: #comprobamos si los curpos han colisionado
						if self.mass > bodys.mass:
							self.mass += bodys.mass
							self.v = (self.mass*self.v + bodys.mass*bodys.v)/(self.mass+bodys.mass)
							
							self.radius += bodys.radius/10
							self.bodys.remove(bodys)
						elif self.mass < bodys.mass:
							self.life = False
							bodys.mass += self.mass
							bodys.v = (self.mass*self.v + bodys.mass*bodys.v)/(self.mass+bodys.mass)					
							bodys.radius += self.radius/10
						else:
							self.life = False
							bodys.life = False
				if bodys.name in self.dontattract or self.ing:
					continue
				if not dis < self.radius + bodys.radius:
					g = (bodys.mass*G)/((dis*self.scale)**2)
				resg +=  pygame.math.Vector2(math.cos(angle)*g, math.sin(angle)*g)
			
			self.module = math.hypot(resg[0],resg[1])
			self.alpha = getRads(resg)
			self.a = pygame.math.Vector2(resg[0],resg[1])
	
	def attraction (self):
		if self.static and not self.never:
			self.timeStep +=1

			self.v += self.a
			self.x += self.v[0]
			self.y += self.v[1]

			if self.timeStep == self.step:
				self.timeStep = 0
				self.lastPos.append((self.x, self.y))
		else:
			if len(self.lastPos) > 0:
				l = self.lastPos
				[self.lastPos.remove(i) for i in l]

	def act(self):
		self.coor = pygame.math.Vector2(self.x,self.y)
	def draw (self):
		if  self.x+self.radius*2 < 0 or  self.x-self.radius*2 > WIDTH or   self.y+self.radius*2 < 0 or  self.y-self.radius*2 > HEIGHT:
			pass
		else:
			pygame.draw.circle(screen,self.color,(int(self.x),int(self.y)),self.radius,0)


			if self.vector == True:
				a = math.hypot(self.a[0], self.a[1])*self.scale
				if self.name == 'point':
					a = math.hypot(self.a[0], self.a[1])*self.scale
				else:
					a = math.hypot(self.a[0], self.a[1])*10**5
				
				if a > 100 and self.limitVector:
					a = 100
				pygame.draw.line(screen,[255,0,0],(self.x,self.y),(self.x+a*math.cos(self.alpha),self.y+a*math.sin(self.alpha)),1)
					#write(str(self.module),(self.x+self.radius, self.y+ self.radius))
			if self.Epot:	
				write(str(self.potencialEnegy),(self.x+self.radius, self.y+ self.radius),20)
				self.potencialEnegy=0
			if self.points:
				[screen.set_at((int(poin[0]), int(poin[1])), self.color) for poin in self.lastPos]	
				if len(self.lastPos) >= 500:
					self.lastPos.pop(0)
			else:
				if len(self.lastPos)>0:
					[self.lastPos.remove(poin) for poin in self.lastPos]



		
 
class World ():
	def __init__(self):
		
		self.bodys = []
		
		self.TerrestOrbit = False
		 #A la escala que trabajamos equivale a 149 millones de Km
		self.mode = 'ORB'
		
		self.mouseFinal = (0,0)
		self.mouseInit = (0,0)
		self.isPressed = False
		self.shot = False
		self.buttons = []
		

		self.scale = 10**9
		
		
		
		self.neuron = Button((10,25),'Union',15,[255,255,255])
		self.vectors = Button((10,45),'Vectors',15,[255,255,255])
		self.cola = Button((10,65),'Travel',15,[255,255,255])
		
		self.static = Button((10,85),'Static',15,[255,255,255])
		
		
		self.sun = Button((10,105),'Sun',15,[255,255,255])
		self.earth= Button((10,125),'Earth',15,[255,255,255])
		self.moon = Button((10,145),'moon',15,[255,255,255])

		self.girld = Button((10,165),'Girld',15,[255,255,255])
		self.colision = Button((10,185),'colision',15,[255,255,255])
		self.modeButton = Button((10,205),self.mode,15,[0,255,255])
		self.plus = Button((10,225),' +',15,[255,255,255])
		self.res = Button((45,225),' -',15,[255,255,255])
		self.plusNum = Button((10,245),' +',15,[255,255,255])
		self.resNum = Button((45,245),' -',15,[255,255,255])
		self.limitVec = Button((10,265),'LimitVec',15,[255,255,255])
		self.Epot = Button((10,285),'Ept',15,[255,255,255])
		
		self.Rs = 30
		self.Rl = 3
		self.Rt = 6
		
		self.Ms = 2*10**30
		self.Mt = 5.9*10**24
		self.Ml = 7.6*10**22
		
		self.buttons.append(self.neuron)
		self.buttons.append(self.Epot)
		self.buttons.append(self.vectors)
		self.buttons.append(self.cola)
		self.buttons.append(self.limitVec)
		self.buttons.append(self.sun)
		self.buttons.append(self.earth)
		self.buttons.append(self.moon)
		self.buttons.append(self.static)
		self.buttons.append(self.girld)
		self.buttons.append(self.colision)
		self.buttons.append(self.modeButton)
		self.buttons.append(self.plus)
		self.buttons.append(self.res)
		self.buttons.append(self.plusNum)
		self.buttons.append(self.resNum)		
		
		#Objects:
		self.sun.setPressed(True)
		self.createBody((WIDTH/2,HEIGHT/2),self.Ms,(0,0),self.Rs)	
		self.KeyPressE = False
		self.KeyPressS = False
		self.system = False
		
		self.step_girld = 10
		
		
		
		#--------CVG---------#
		self.c = False
		self.step = 130
		self.numPoints =((WIDTH+self.step)/self.step, (HEIGHT+self.step)/self.step)
		self.points = list()
	
	def update (self):
		self.butsFunc()
		if self.mode == 'orb':
			if self.c:
				[self.delateAll() for i in range(len(self.bodys))]
				self.c = False
				self.scale = 10**9
				self.static.setPressed(False)
				self.colision.setPressed(True)
				self.sun.setPressed(True)
				self.createBody((WIDTH/2,HEIGHT/2),self.Ms,(0,0),self.Rs)	
		
		elif self.mode == 'cvg':
			if not self.c:
				self.stateCVG()
			write('1px * %e'% self.scale, (WIDTH-400,HEIGHT-100), 15,[225,255,255],'Courier')
			
			
			
		self.putBody()		
		write('Orbits Simulator', (WIDTH/2-150,20), 30,[225,255,255],'Courier')
		write('Author: Pablo Fernandez Lucas', (WIDTH-400,30), 11,[225,255,255],'Courier')
		for body in self.bodys:
			body.update(self.bodys)
			if not body.getLife():
				self.bodys.remove(body)
		
				
				
	def stateCVG(self):
		[self.delateAll() for i in range(len(self.bodys))]
		self.numPoints =((WIDTH+self.step)/self.step, (HEIGHT+self.step)/self.step)
		self.static.setPressed(True)
		self.sun.setPressed(False)
		self.earth.setPressed(False)
		self.moon.setPressed(False)		
		self.colision.setPressed(False)
		self.scale = 10**9
		self.createCVG()
		self.c = True
	def createCVG (self):
		for i in range(int(self.numPoints[1])):
			for x in range(int(self.numPoints[0])):
				body = self.createBody((self.step*x,self.step*i),1,(0,0),2,[255,255,255],'point',ing=['point'])
				body.setNeverMove(True)

			 
	def draw_girld(self):
		for i in range(WIDTH/self.step_girld):
			pygame.draw.line(screen,(20,20,20),(-self.step_girld/2,self.step_girld*i),(WIDTH,self.step_girld*i))
		for x in range(WIDTH/self.step_girld):
			pygame.draw.line(screen,(20,20,20),(self.step_girld*x,-self.step_girld/2),(self.step_girld*x,HEIGHT))
	
		
	

	def butsFunc (self):
		k = pygame.key.get_pressed()
		if self.neuron.getPressed():
			for body in self.bodys:
				body.setUnion(True)		
		else: 
			for body in self.bodys:
				body.setUnion(False)

		if self.vectors.getPressed():
			for body in self.bodys:
				body.setVector(True)		
		else: 
			for body in self.bodys:
				body.setVector(False)
		if self.cola.getPressed():
			for body in self.bodys:
				body.setPoints(True)		
		else: 
			for body in self.bodys:
				body.setPoints(False)

		if self.static.getPressed():
			for body in self.bodys:
				body.setStatic(False)		
		else: 
			for body in self.bodys:
				body.setStatic(True)
				
		if self.colision.getPressed():
			for body in self.bodys:
				body.setColision(False)		
		else: 
			for body in self.bodys:
				body.setColision(True)
				
		if self.Epot.getPressed():
			for body in self.bodys:
				body.setEpot(True)		
		else: 
			for body in self.bodys:
				body.setEpot(False)
				
		if self.modeButton.getPressed():
			self.mode = 'cvg'
		else:
			
			self.mode = 'orb'
		self.modeButton.text = self.mode
		if self.mode=='cvg':
		
			if self.limitVec.getPressed():
				for body in self.bodys:
					if body.name == 'point':
						body.setLimitVector(True)
			else:
				for body in self.bodys:
					if body.name == 'point':
						body.setLimitVector(False)
					
			if self.plus.getPressed():
				self.scale *=10
				for body in self.bodys:
					body.setScale(self.scale)
				
				self.plus.setPressed(False)
				self.plus.reset()
				
			if self.res.getPressed():
				self.scale /=10
				for body in self.bodys:
					body.setScale(self.scale)
				self.res.setPressed(False)
				self.res.reset()
		
			if self.plusNum.getPressed():
				self.step +=5
				self.stateCVG()
				self.plusNum.setPressed(False)
				self.plusNum.reset()
				
			if self.resNum.getPressed():
				self.step -=5
				self.stateCVG()
				self.resNum.setPressed(False)
				self.resNum.reset()
		else:
			self.plus.setPressed(False)
			self.res.setPressed(False)
			self.plusNum.setPressed(False)
			self.resNum.setPressed(False)
			self.limitVec.setPressed(False)
			
		if k[pygame.K_SPACE]:
			if self.mode ==  'cvg':
				[self.delateAll(['point']) for i in range(len(self.bodys))]
				
			else:
				[self.delateAll() for i in range(len(self.bodys))]
		
		if self.girld.getPressed():
			self.draw_girld()
		
				
		for button in self.buttons:
			button.update()

		else:
			self.KeyPressE = False
	
		if k[pygame.K_e] and self.mode == 'orb' :
			if not self.KeyPressE:
				[self.delateAll() for i in range(len(self.bodys))]
				self.KeyPressE = True
				self.sun.setPressed(False)
				self.earth.setPressed(True)
				self.moon.setPressed(False)
				self.colision.setPressed(False)
				self.scale = 10**6
				self.createBody((WIDTH/2,HEIGHT/2),self.Mt,(0,0),[100,255,100],int(self.Rt), self.scale)
				
				
		else:
			self.system = False
		if k[pygame.K_w] and self.mode == 'orb':
			if not self.system:
				[self.delateAll() for i in range(len(self.bodys))]
				self.scale = 10**9
				self.sun.setPressed(True)
				self.earth.setPressed(False)
				self.moon.setPressed(False)
				self.colision.setPressed(True)
				self.createBody((WIDTH/2,HEIGHT/2),self.Ms,(0,0),self.Rs)
				self.sun.setPressed(False)
				self.earth.setPressed(True)
				self.moon.setPressed(False)
				self.createBody((WIDTH/2,HEIGHT/2+149),self.Mt,(1,0),self.Rt)
				self.sun.setPressed(False)
				self.earth.setPressed(False)
				self.moon.setPressed(False)
				self.createBody((WIDTH/2,HEIGHT/2+149+70),self.Ml,(2,0),self.Rl,[255,255,255],'body',['body','sun'],10**6.2)
				for i in range(5):
					self.createBody((WIDTH/2,HEIGHT/2+149+70+50+50*i),self.Ml,(0.5,0),self.Rl,[random.randint(0,255),random.randint(0,255),random.randint(0,255)])
				
		else:
			self.system = False

		if k[pygame.K_s] and self.mode == 'orb':
			if not self.KeyPressS:
				
				[self.delateAll() for i in range(len(self.bodys))]

				self.KeyPressS = True
				self.sun.setPressed(True)
				self.earth.setPressed(False)
				self.moon.setPressed(False)
				self.colision.setPressed(False)
				self.scale = 10**9
				self.createBody((WIDTH/2,HEIGHT/2),self.Ms,(0,0),self.Rs)
		
		else:
			self.KeyPressS = False

	def delateAll(self,l = ['all']):
		for b in self.bodys:
			for i in l:
				if i == 'all':
					self.bodys.remove(b)
				elif not b.name == i:
					self.bodys.remove(b)

	def createBody(self, pos, mass, vel,radius = 5,color = [255,255,255],name='body',ing = [],scale=None):
		if scale == None:
			scale = self.scale
		if self.sun.getPressed():
			body = Body(int(pos[0]),int(pos[1]),int(self.Ms),pygame.math.Vector2(vel[0],vel[1]),[255,255,0],int(self.Rs), scale,'sun',ing)
		elif self.earth.getPressed():
			body = Body(int(pos[0]),int(pos[1]),int(self.Mt),pygame.math.Vector2(vel[0],vel[1]),[100,255,100],int(self.Rt), scale,'earth',ing)
		elif self.moon.getPressed():
			body = Body(int(pos[0]),int(pos[1]),int(self.Ml),pygame.math.Vector2(vel[0],vel[1]),[255,255,255],int(self.Rl), scale,'moon',ing)
		else:
			body = Body(int(pos[0]),int(pos[1]),int(mass),pygame.math.Vector2(vel[0],vel[1]),color,int(radius), scale,name,ing)
		self.bodys.append(body)
		return body

	def putBody(self):
		mouse = pygame.mouse.get_pressed()
		mousePos = pygame.mouse.get_pos()
		if not self.shot:
			 self.mouseInit = pygame.math.Vector2(mousePos)
		isIn = True
		for button in self.buttons:
			if button.getIsIn():
				isIn = True
				break
			else:
				isIn = False	
		if not isIn:
			if mouse[0] and self.isPressed:
				if not self.shot:
					self.mouseInit = pygame.math.Vector2(mousePos)
				self.isPressed = False
		        	self.mouseFinal = pygame.math.Vector2(mousePos)
				self.shot = True
				pygame.draw.line(screen,[255,255,255],(self.mouseInit[0], self.mouseInit[1]),(self.mouseFinal[0],self.mouseFinal[1]),1)
			if not mouse[0]:
				self.mouseFinal = pygame.math.Vector2(mousePos)
				if self.shot:
					res = self.mouseFinal - self.mouseInit
					vel = pygame.math.Vector2(res[0]*(-1)/100,res[1]*(-1)/100)
					if self.mode =='cvg':
						body = self.createBody(mousePos,random.randint(10**20,10**26),vel,random.randint(4,15),[random.randint(0,255),random.randint(0,255),random.randint(0,255)])
						body.ingnoreAll(True)
					else:
						self.createBody(mousePos,random.randint(10**20,10**24),vel,random.randint(2,9),[random.randint(0,255),random.randint(0,255),random.randint(0,255)])
					self.shot = False
	
			else:
				self.isPressed = True
				self.shot = True
		
			
	

world =	World()
time = pygame.time
clock = time.Clock()
FPS = 400
while(True):
	
	screen.fill([0,0,0])
	world.update()
	pygame.display.flip()
	clock.tick(FPS)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	
	key =pygame.key.get_pressed()
	if key[pygame.K_ESCAPE]:
		sys.exit()
		pygame.quit()




pygame.quit()
