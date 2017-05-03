import tkinter as tk
import random
#==============================================================================
taillejeu="1080x1080"
hauteurcadre=800
largeurcadre=400
l=largeurcadre/11
h=hauteurcadre/11
#==============================================================================
sens="none"        #initialisation de variables et listes utilisées plus tard
direction="none"
casebatx=0
casebaty=0
ships=[]
shipsai=[]
aitotalhits=0
aihits=0
userhits=0

orientation='N' #Orientation par défaut des bateaux à placer
game_mode=False #sépare le moment de placement des bateaux du moment de jeu 
player_turn=False  #Variable booléenne qui vérifie que assure le respect du tour de jeu 
boat_sunk=False #Variable booléenne qui indique si le bateau en question est coulé ou non
#==============================================================================

master = tk.Tk()
master.title("Bataille Navale")
master.geometry(taillejeu)
tk.Frame(master).grid()
cadre=tk.Canvas(master, width=largeurcadre, height=hauteurcadre,bg="white")
cadre.grid(column=0, row=1)


def gamemode():  #fonction qui est appelé une fois que tous les bateaux de l'utilisateur sont placés
    global game_mode 
    global player_turn
    game_mode=True  # active le moment de jeu, les clicks de cases seront désormais exclusivement rattachés à des attaques 
    cadre.configure(cursor='boat')   
    master.configure(cursor='boat') #le changement de curseur offre une représentation visuelle du mode de jeu en cours
    boatframe.configure(cursor='boat')
    player_turn=True   #l'utilisateur commence par défaut

class case: #création des cases du terrainde jeu
    def __init__(self, x, y):
        self.x=x #définition des coordonnées sur le terrain de jeu
        self.y=y
        self.bateau=False #défintion des propriétés de la case
        self.case_attaquee=False        
        self.xdebut=x*l #défintion des coordonnées sur le canvas
        self.xfin=(x+1)*l
        self.ydebut=y*(h/2)+hauteurcadre/2
        self.yfin=y*(h/2)+(h/2)+hauteurcadre/2
        self.draw() #création de la case sur le canvas
        
    def __repr__(self):
        return str(self.x) + ','+str(self.y)
    
    def draw(self): #fonction de création de la case sur le canvas
        global boat_sunk 
        rect=cadre.create_rectangle(self.xdebut,self.ydebut,self.xfin,self.yfin, fill=self.color())
        if boat_sunk==True and self.color()=="red":
            cadre.create_line(self.xdebut,self.ydebut,self.xfin,self.yfin,fill="black") 
            cadre.create_line(self.xdebut,self.yfin,self.xfin,self.ydebut,fill="black")
        
        cadre.tag_bind(rect, "<Button-1>", self.click) #si on clique sur la case, elle se reconnait
        
    def boat(self): #changement de la propriété "bateau présent sur la case"
        if self.bateau==False:
            self.bateau=True
            self.draw()

      
    def attacked(self): #idem, mais pour la propriété "la case a-t-elle étée attaquée"
        if self.case_attaquee==False:
            self.case_attaquee=True
            self.draw()  
    
    def color(self): #fonction qui vérifie l'état de la case et apporte des modifications de couleurs selon cet état
        global player_turn #la fonction assure également le respect des tours de jeu
        couleur="white" #la case est blanche par defaut
        if self.bateau==True: #si un bateau est présent, elle est grise
            couleur="grey"
        if self.case_attaquee and self.bateau: #si un bateau est présent et qu'elle est attaquée, elle est rouge
            couleur="red"
            player_turn=False #si une case du jouer est attaqué est que celle-ci contient un bateau, l'intelligence artificielle rejoue
        elif self.case_attaquee==True and self.bateau==False: #si elle est attaquée sans la présence du bateau, elle est bleue
            couleur="blue"
            player_turn=True #si une case est attaqué est que celle-ci est vide, c'est au tour de l'utilisateur
        return couleur
    
    def click(self, event): #fonction se lançant lorsqu'on clique sur la case, servant à placer les bateaux
        global game_mode
        global orientation
        global bl
        global selectable
        global ships
        global shipsai
        global caseadversaire
        environs=True 
        if game_mode==False: #si game_mode==True, le joueur n'a plus a toucher a ces cases, seulement à celles de l'ia.
            if selectable==False: #si selectable==True, le joueur n'a pas selectionné de bateau, il ne peut donc pas en placer.
                ships.append(ship(bl,orientation)) #maintenant que le joueur est bien en train de placer un bateau, on crée le bateau dans la liste des bateaux
                bateau_selectionne=ships[len(ships)-1] #le bateau lequel on place est donc le dernier élément de la liste à l'indice (longueur-1)
                bateau_selectionne.projet(self.x, self.y, cases) #on crée une liste de cases où on veut placer le bateau
                for i in range(len(bateau_selectionne.projection)): #pour chaque case de la projection on va tester si le bateau peut etre placé légalement, c'est a dire pas directement à coté d'un autre
                    if bateau_selectionne.projection[i].check_surrounding()==False and bateau_selectionne.check_placement(self.x, self.y)!=False:
                        information.itemconfigure(1, text='Boats can not be adjacent.')
                        environs=False
                        ships.pop() #si on ne peut pas, on enleve le bateau de la liste, car il n'est pas réellement créé
                        break
                if environs==True: 
                    if bateau_selectionne.check_placement(self.x, self.y)==False: #on verifie ensuite que le bateau ne sorte pas du cadre
                        information.itemconfigure(1, text='Boat out of area.')
                        ships.pop() #idem que precedemment
                    else: #si toutes les conditions du bon placement son remplies
                        bateau_selectionne.placement(self.x, self.y, cases) #on place le bateau,
                        selectable=True #on rend selectionnables les autres bateaux
                        all_placed() #on regarde si tous les autres bateaux ont été placés
                        actualise() #on actualise les barres de vies, afin qu'elles s'afichent correctement
            else: #affichage des messages d'erreur liées aux conditions initiales neccessaires pour un placement.
                    information.itemconfigure(1, text='Please select a boat to place.')
        else:
             information.itemconfigure(1, text='You are playing on the other field.')
             
            
    def check_surrounding(self): #fonction vérifiant que les cases adjacentes ne soient pas des bateaux
        xcoordinate=[-1,0,0,+1] #liste des coordonées à tester (en combinaison avec ycoordinate)
        ycoordinate=[0,+1,-1,0]
        for i in range(4):
            try:            #la fonction try evite les erreurs d'index
                if cases[(self.x+xcoordinate[i])][self.y+(ycoordinate[i])].bateau==True: #check un par un si la case à coté possède un bateau
                    return False            #si ceci est le cas, la fonction renvoit False
            except IndexError:
                pass
        return True
                
        

                  
class ship: #creation des bateaux
    def __init__(self,l,orient): #les bateaux sont créés en focntion de leur longueur et de leur orientation
        self.length=l
        self.orientation=orient
        self.endroits=[]
        self.projection=[]
    
    def __repr__(self):
        return str(self.length) #ils sont représentés par leur longueur
    
    def check_placement(self, x, y) :#vérifie que le bateau rentre dans le cadre en fonction de son orientation
        if self.orientation=='S':  
            if y+self.length>10:
                return False
        elif self.orientation=='E':
            if x-self.length<-1:
                return False
        elif self.orientation=='N':
            if y-self.length<-1:
                return False
        elif self.orientation=='W':
                if x+self.length>10:
                    return False
        
    def projet(self, x,y, liste): #création de la projection de la position du bateau
        try:
            for i in range(self.length):
                if self.orientation=='S':  
                    self.cases(self.projection,x,y+i, liste)
                elif self.orientation=='E':
                    self.cases(self.projection,x-i,y, liste)
                elif self.orientation=='N':
                    self.cases(self.projection,x,y-i, liste)
                elif self.orientation=='W':
                    self.cases(self.projection,x+i,y, liste)
        except IndexError:
            return False
                    
    def placement(self,x,y, liste): #placement du bateau en fonction de sa longueur et de son orientation
        for i in range(self.length):
            if self.orientation=='S':  
                liste[x][y+i].boat() #on change la propriété de la case concernée
                self.cases(self.endroits,x,y+i, liste) #on ajoute la case à la liste des cases appartenant au bateau
            elif self.orientation=='E':
                liste[x-i][y].boat()
                self.cases(self.endroits,x-i,y, liste)
            elif self.orientation=='N':
                liste[x][y-i].boat()
                self.cases(self.endroits,x,y-i, liste)
            elif self.orientation=='W':
                liste[x+i][y].boat()
                self.cases(self.endroits,x+i,y, liste)
                
    def placementai(self):   #fonction qui place les bateaux de la liste sur cases
        for i in range(self.length):
            self.projection[i].boat()
                    
    def cases(self,liste,x,y, liste2): #fonction permettant de rajouter une case à une autre liste
        liste.append(liste2[x][y])
        
    def bateau_sunk(self, liste): #fonction qui vérifie si un bateau est coulé
        global boat_sunk
        if self.bateau_en_vie(liste)==0: #si le niveau de vie du bateau est à 0, il est coulé
            boat_sunk=True 
            for i in range(self.length): # modifie l'apparence du bateau case par case
                self.projection[i].draw() 
            boat_sunk=False 
            
    def bateau_en_vie(self, liste): #fonction permettant d'avoir le niveau de vie d'un bateau
        level=0 
        for i in range(self.length): #pour chaque case du bateau, on regarde si elle est attaquée, si non, on augmente "sa vie" de 1
            if liste==ships:
                if self.endroits[i].case_attaquee==False:
                    level=level+1
            else: #cas différent pour les bateaux de l'ia, pour lesquels la liste endroits reste vide.
                if self.projection[i].case_attaquee==False:
                    level=level+1
        return level/self.length #renvoie le niveau de vie du bateau par rapport à sa longueur

        
class intelligence_artificielle: #classe pour casesadversaire (voir classe case)
    
    def __init__(self, x, y):   
        self.x=x
        self.y=y
        self.bateau=False
        self.case_attaquee=False
        self.xdebut=x*l #difference de placement (cases de l'adversaire au dessus)
        self.xfin=(x+1)*l
        self.ydebut=y*(h/2)
        self.yfin=y*(h/2)+(h/2)
        self.draw()
        
    def __repr__(self):
        return str(self.x) + ','+str(self.y)
        
    def boat(self):
        if self.bateau==False:
            self.bateau=True
            self.draw()
        else:
            self.bateau=False
            self.draw()
            
    def attacked(self):
        if self.case_attaquee==False:
            self.case_attaquee=True
            self.draw()
            
            
    def check_surrounding(self): #check s'il n'y a pas de bateau autour et sur sa position, meme methode que dans la classe case
        xcoordinate=[-1,0,0,+1] 
        ycoordinate=[0,+1,-1,0]
        for i in range(4):
            try:
                if caseadversaire[(self.x+xcoordinate[i])][self.y+(ycoordinate[i])].bateau==True:
                    return False
            except IndexError:
                pass
        return True
            
    def draw(self):
        global bateau_en_vie
        rect=cadre.create_rectangle(self.xdebut,self.ydebut,self.xfin,self.yfin, fill=self.color())
        if boat_sunk==True and self.color()=="red":
            cadre.create_line(self.xdebut,self.ydebut,self.xfin,self.yfin,fill="black") 
            cadre.create_line(self.xdebut,self.yfin,self.xfin,self.ydebut,fill="black")

        cadre.tag_bind(rect, "<Button-1>", self.click)
        
    def click(self, event):
        global player_turn
        if userhits==21 or aihits==21:
            return
        if player_turn==True:
            case.attacked(self)

            if self.case_attaquee==True and self.bateau==True:
                player_turn=True #l'utilisateur rejoue si il a touché une case avec un bateau
                shipsai[quel_bateau_ai(caseadversaire[self.x][self.y])].bateau_sunk(shipsai) #vérifie si un bateau entier a été coulé
            else:
                player_turn=False # Si l'utilisateur ne touche pas de bateau, ce n'est plus son tour
                information.itemconfigure(1, text='It is not your turn to play.')
                cadre.after(300, aiattack) # délai avant l'attaque de l'intelligence artificielle, le canevas rafraichie au bout d'un certain moment en éxecutant le fonction
        else:
            information.itemconfigure(1, text='It is not your turn to play.')
        
    def color(self): 
        couleur="white"     #ne pas dessiner les bateaux comme dans la classe case
        if self.case_attaquee and self.bateau:  #seulement s'ils osnt touchés
            couleur="red"
        elif self.case_attaquee==True and self.bateau==False:
            couleur="blue"
        return couleur
       
        
#================== Fonctions Utiles à l'intellingence artificielle ================================
def rancoord(): #renvoie 2 chiffres random
    a=random.randrange(0,10,1)
    b=random.randrange(0,10,1)
    return a,b
                  
def ranai():    #renvoie un chiffre random entre 1 et 4
    return random.randrange(1,5,1)
                  
def attacked_all(): #check si toutes les cases ont été attaqué
    for i in range(9):
        for j in range(9):
            if cases[i][j].case_attaquee==False:
                return False
                
def random_orientation(): #génère une orientation alèatoire (nord, sud, est, ouest)
    random=ranai()
    if random==1:
        orientation="N"
    elif random==2:
        orientation="E"
    elif random==3:
        orientation="S"
    elif random==4:
        orientation="W" 
    return orientation
        

      

def hit():       #détermine si un bateau a été touché par l'ai et le score du joueur et de l'ai
    global userhits #nombre de cases bateaux touché par le joueur
    global aihits   #nombre de cases touchée par l'ai au tours precedent
    global aitotalhits  #nombre de cases touchée par l'ai dans le tour present
    a=0
    b=0
    for i in range(10):
        for j in range(10):
            if caseadversaire[i][j].case_attaquee==True and caseadversaire[i][j].bateau==True: #comptage de case touché par le joueur
                a=a+1
            if cases[i][j].case_attaquee==True and cases[i][j].bateau==True:                    #comptage de case touché par l'ai
                b=b+1     
    userhits=a
    aitotalhits=b
    if b==aihits+1:     #si une case de plus a été touché qu'au tour avant
        aihits=aihits+1 #ajouter a la variable 1 pour pouvoir reverifier au prochain tour
        return True     
    
def winner():   #déterminer le gagnant
    global player_turn 
    if aitotalhits==21: #si l'ai a touché les 21 cases bateaux (5+4+3+3+2+2+2) avant le joueur
        player_turn=0   #le joueur n'a plus le droit de jouer
        information.itemconfigure(1, text='You lost.') #indiquation que le joueur a perdu
        return False    
    if userhits==21: #si le joueur a touché les 21 cases bateaux avant l'ai
        player_turn=0   #le joueur n'a plus le droit de jouer
        information.itemconfigure(1, text='You won.') #indiquation qu'il a gagné
        return False
    
#================== Intelligence Artificielle ================================

def placeboatsai(): #fonction qui place les bateaux des l'ai
    global shipsai  #liste contenants les objets bateaux de l'ai (future liste)
    global caseadversaire   #liste des objets cases de l'ai
    boatlengths=[5,4,3,3,2,2,2] #nombre et longueur des bateaux

    for i in range(len(boatlengths)): #creation de bateux et de projection aléatoire pour pouvoir vérifier toute les conditions dans la 2ème tant que
        orientation=random_orientation()    #creation d'une orientaion aléatoire
        shipsai.append(ship(boatlengths[i],orientation))    #création des bateaux et les mettre dans la liste shipsai
        x,y=rancoord()
        shipsai[i].projection.append(shipsai[i].projet(x,y,caseadversaire)) #ajouter une projection aléatoire à la liste attribut des bateaux
        for l in range(boatlengths[i]):       
            while  shipsai[i].check_placement(x,y)==False:  #verifier qu'elle soit bien dans le cadre
                del shipsai[i].projection[:]
                x,y=rancoord()
                shipsai[i].projection.append([shipsai[i].projet(x,y,caseadversaire)])
        shipsai[i].projection.pop()
   
    for j in range(len(shipsai)):
        for k in range(len(shipsai[j].projection)):
            while shipsai[j].check_placement(x,y)==False or shipsai[j].projection[k].check_surrounding()==False :    #2ème tant que vérifiant que le bateau qui va ètre placé grace à la liste projection remplise les conditions necessaire
                    shipsai[j].orientation=random_orientation() #donner une orientation, des coordonnées aléatoire
                    del shipsai[j].projection[:]
                    x,y=rancoord()
                    shipsai[j].projection.append([shipsai[j].projet(x,y,caseadversaire)])
                    shipsai[j].projection.pop()
        shipsai[j].placementai()    #si toutes les conditions sont rempli les bateaux sont placés un par un, pour que les nouveaux bateaux n'interfère pas avec les anciens (qu'ils soit placées au même endroit)
                           
                                
        
def aiattack():
    global sens #par default sens="none"
    global direction #par default direction="none"
    global casebatx  #position ou se trouve un bateau (la variable est set plus basse dans "if sens==none")
    global casebaty
    global ships    #liste dans laquel se trouve les objet ships ou l'ordinateur va attauqer
    global player_turn  #la variable qui determine le tour du joueur ou de l'ordinateur
    global userhits     #le nb de case ou se trouvait un bateau touché par l'utilisateur
    global aihits       #le nb de case ou se trouvait un bateau touché par l'ia
    if winner()==False: #si aucun des deux joueurs n'a touché les 21 positions ou se trouvent les bateaux
        return None
    if player_turn==False and game_mode==True:   #si c'est à l'ia de jouer et que les bateaux sont tous placés                          
        if sens=="vertical":                #si le sens est connu et qu'il est "verticale"
            if ships[quel_bateau(cases[casebatx][casebaty])].bateau_en_vie(ships)== 0:  #si le bateau est coulé, l'ia attaque aléatoirement a nouveau
                sens="none"
                direction="none"
                
            else:
                try:
                    essai=False
                    while essai==False:
                        if direction=="haut":           #si la direction (qui est déterminer en dessous) est connue l'ia attaque toutes les cases vers le "haut"jusqu a ce qu le bateau est coulé
                            while essai==False:
                                if cases[casebatx][casebaty-1].case_attaquee==False: 
                                    cases[casebatx][casebaty-1].attacked()
                                    essai=True
                                elif cases[casebatx][casebaty-2].case_attaquee==False:
                                    cases[casebatx][casebaty-2].attacked()
                                    essai=True
                                elif cases[casebatx][casebaty-3].case_attaquee==False: 
                                    cases[casebatx][casebaty-3].attacked()
                                    essai=True
                                elif cases[casebatx][casebaty-4].case_attaquee==False: 
                                    cases[casebatx][casebaty-4].attacked()
                                    essai=True
                                    
                        else:
                            if cases[casebatx][casebaty+1].case_attaquee==False: #l'ia attaque dans une direction jusqu'à ce qu'il n'ait plus de case bateau, elle set donc le direction="haut"
                                cases[casebatx][casebaty+1].attacked()
                                essai=True
                                if cases[casebatx][casebaty+1].bateau==False:
                                    direction="haut"
                                        
                            elif cases[casebatx][casebaty+2].case_attaquee==False: 
                                cases[casebatx][casebaty+2].attacked()
                                essai=True
                                if cases[casebatx][casebaty+2].bateau==False:
                                    direction="haut"
                                    
                            elif cases[casebatx][casebaty+3].case_attaquee==False:
                                cases[casebatx][casebaty+3].attacked()
                                essai=True
                                if cases[casebatx][casebaty+3].bateau==False:
                                    direction="haut"
        
                            elif cases[casebatx][casebaty+4].case_attaquee==False:
                                cases[casebatx][casebaty+4].attacked()
                                essai=True
                                if cases[casebatx][casebaty+4].bateau==False:
                                    direction="haut"
                except IndexError:
                    pass
                                


        
        if sens=="horizontal": #si le sens est connu et qu'il est "horiontal"
            essai=False
            if ships[quel_bateau(cases[casebatx][casebaty])].bateau_en_vie(ships)== 0:  #si le bateau est coulé, l'ia attaque aléatoirement a nouveau
                sens="none"
                direction="none"
            else:
                while essai==False:
                    try:
                        if direction=="gauche":
                            while essai==False:
                                if cases[casebatx-1][casebaty].case_attaquee==False:    # attaque à gauche de la cases[casebatx][casebaty] jusqu'à ce que le bateau soit coulé
                                    cases[casebatx-1][casebaty].attacked()
                                    essai=True
                                elif cases[casebatx-2][casebaty].case_attaquee==False: 
                                    cases[casebatx-2][casebaty].attacked()
                                    essai=True
                                elif cases[casebatx-3][casebaty].case_attaquee==False: 
                                    cases[casebatx-3][casebaty].attacked()
                                    essai=True
                                elif cases[casebatx-4][casebaty].case_attaquee==False:
                                    cases[casebatx-4][casebaty].attacked()
                                    essai=True
                        else:
                            if cases[casebatx+1][casebaty].case_attaquee==False:    #determination de la direction ou seulement attauqe dans un sens
                                cases[casebatx+1][casebaty].attacked()
                                essai=True
                                if cases[casebatx+1][casebaty].bateau==False:
                                    direction="gauche"
                                    
                            elif cases[casebatx+2][casebaty].case_attaquee==False:
                                cases[casebatx+2][casebaty].attacked()
                                essai=True
                                if cases[casebatx+2][casebaty].bateau==False:
                                    direction="gauche"
                            elif cases[casebatx+3][casebaty].case_attaquee==False:
                                cases[casebatx+3][casebaty].attacked()
                                essai=True
                                if cases[casebatx+3][casebaty].bateau==False:
                                    direction="gauche"

                            elif cases[casebatx+4][casebaty].case_attaquee==False: 
                                cases[casebatx+4][casebaty].attacked()
                                essai=True
                                if cases[casebatx+4][casebaty].bateau==False:
                                    direction="gauche"

                    except IndexError:
                        pass
    
        if sens=="unknown":     #si un bateau a été touché mais l'ordinateur ne sait pas dans quel sens se trouve les autres cases
            essai=False     #la variable qui check si une case a été attaqué
            test_gauche=False
            test_droite=False
            test_haut=False
            test_bas=False 
            
            if casebatx==0:
                test_gauche=True
                
            if casebatx==9:
                test_droite=True
                
            if casebaty==0:
                test_haut=True
                
            if casebaty==9:
                test_bas=True
                            
            while essai==False:     #l'ia attaque aléatoirement la case au dessus, en dessous a droite et a gauche pour déterminer le sens
                random=ranai()
                
                if random==1 and test_droite==False:                        #si le random tombe sur cette option et que la case n'est pas au bord
                    if cases[casebatx+1][casebaty].case_attaquee==False:    #seulement attaqué une case non-attaquée
                        cases[casebatx+1][casebaty].attacked()
                        essai=True
                        if cases[casebatx+1][casebaty].bateau==True:        #si un bateau s'y trouve alors le sens="horizontal" car x et non y a changé
                            sens="horizontal"
                        else:
                            sens="unknown"                                  #sinon le sens est encore inconnu et c'est au joueur de jouer car aucune case avec un bateau n'a été touchée

                elif random==2 and test_gauche==False:                      #les 3 autres test et verifie dans les autres directions
                    if cases[casebatx-1][casebaty].case_attaquee==False:
                        cases[casebatx-1][casebaty].attacked()
                        essai=True
                        if cases[casebatx-1][casebaty].bateau==True:
                            sens="horizontal"
                            essai=True
                        else:
                            sens="unknown"

                elif random==3 and test_bas==False:
                    if cases[casebatx][casebaty+1].case_attaquee==False:   
                        cases[casebatx][casebaty+1].attacked()
                        essai=True
                        if cases[casebatx][casebaty+1].bateau==True:
                            sens="vertical"

                        else:
                            sens="unknown"

                elif random==4 and test_haut==False:
                    if cases[casebatx][casebaty-1].case_attaquee==False:
                        cases[casebatx][casebaty-1].attacked()
                        essai=True
                        if cases[casebatx][casebaty-1].bateau==True:
                            sens="vertical"

                        else:
                            sens="unknown"
                else:
                    essai=False
                
        if sens=="none":            #par défault le sens est "none", l'ia n'a aucune information sur la position des bateaux
            a,b=rancoord()          #des coordonnées aléatoire sont données (voir rancoord())
            while cases[a][b].case_attaquee==True: #determination de coordonées aleatoires qui n'ont pas encore été attaquée
                a,b=rancoord()
            cases[a][b].attacked()
            if cases[a][b].bateau==True:    #si un bateau se trouve sur cette case
                sens="unknown"              #le sens="unknown" pour qu'au prochain tour 'l'ia sait où attaquer
                casebatx=a                  #les coordonées sont enregistrées
                casebaty=b
    
        if hit()==True:             #si un bateau a été touché par l'ia (voir hit())
            cadre.after(300, aiattack) #attendre 300ms, puis executer aiattack()
            ships[quel_bateau(cases[casebatx][casebaty])].bateau_sunk(ships)
        else:
            player_turn==True       #sinon c'est au tour du joueur
            information.itemconfigure(1, text='It is your turn to play.')
    
    else:
        information.itemconfigure(1, text='It is your turn to play.')
    actualise()
        

      

    
#================== Selectable boats ================================
boatframe=tk.Canvas(master, width=450, height=300)
boatframe.grid(column=1,row=1, sticky="N")

selectable=True #variable qui assure que seulement un bateau soit séléctionné à la fois
bl=0 #variable à laquelle on associe la longeur du bateau à placer 

b5_coord = (l+300),(h-40), (l+300),h, (l+50),h, (l+50),(h-40)
b4_coord = (l+270),(h+30), (l+270),(h+70), (l+80),(h+70), (l+80),(h+30)
b3_coord = (l+240),(h+100), (l+240),(h+140), (l+110),(h+140), (l+110),(h+100)
b2_coord = (l+210),(h+170), (l+210),(h+210), (l+140),(h+210), (l+140),(h+170)
        
b5=boatframe.create_polygon(b5_coord, fill="blue")  #représentation visuelle des tailles de bateaux à placer
b4=boatframe.create_polygon(b4_coord, fill="blue")
b3=boatframe.create_polygon(b3_coord, fill="blue")
b2=boatframe.create_polygon(b2_coord, fill="blue")

compteur_b5=1  #  Certaines tailles de bateaux ont plusieurs bateaux à placer de leurs types.
compteur_b4=1  #  Les compteurs ci-contre permettent d'assurer que le bon nombre de bateaux
compteur_b3=2  #  soit placé. 
compteur_b2=3

nb_5=boatframe.create_text((l+320),(h-20), text='x 1')  # Indicateurs du nombre restant de bateaux à placer
nb_4=boatframe.create_text((l+290),(h+50), text='x 1')
nb_3=boatframe.create_text((l+260),(h+120), text='x 2')
nb_2=boatframe.create_text((l+230),(h+190), text='x 3')
   
def clicked_b5(event): #fonction associé au bateau de taille 5 
    global bl
    global selectable 
    info()  # appel une fonction qui donne à l'utilisateur des instructions pour placer les bateaux
    global compteur_b5 
    if compteur_b5==0: # vérifie que l'utilisateur n'as pas déjà placé tous les bateaux de cette taille
        information.itemconfigure(1, text='Tous les bateaux de cette categorie ont ete places')
    else:
        if selectable==True: #vérifie qu'un autre bateau n'as pas déjà été sélectionné 
            selectable=False # cela permettra de selectionner un nouveau bateau par la suite
            print("Boat 5 selected")
            boatframe.itemconfigure(1, fill="grey") #1 correspond à l'identité du polygone représentant le bateau 5, cela le rend gris
            rotate_north(event) #orientation du bateau à placé par défaut 
            bl=5 #défini la longeur du bateau à placer 
            compteur_b5=compteur_b5-1 #actualise la valeur du compteur, il y en à unde moins à placer 
            boatframe.itemconfigure(5, text='x '+str(compteur_b5)) #actualise également le compteur visuel (5 étant l'id du text widget)
        else:
            information.itemconfigure(1, text="Veuillez placer le bateau avant de selectionner un autre.")# vérifie que l'utilisateur n'ait pas fait une erreur 
                                                                                  # de saisie du type sélectionner plusiers bateaux simultanément et l'informe dans le cas contraire
def clicked_b4(event): #fonction associé au bateau de taille 4                                       
    global bl
    global selectable 
    info()   # appel une fonction qui donne à l'utilisateur des instructions pour placer les bateaux
    global compteur_b4
    if compteur_b4==0: # vérifie que l'utilisateur n'as pas déjà placé tous les bateaux de cette taille
        information.itemconfigure(1, text='Tous les bateaux de cette categorie ont ete places')
    else:
        if selectable==True: #vérifie qu'un autre bateau n'as pas déjà été sélectionné 
            selectable=False  # cela permettra de selectionner un nouveau bateau par la suite
            print("Boat 4 selected")
            boatframe.itemconfigure(2, fill="grey")# 2 correspond à l'identité du polygone représentant le bateau 4, cela le rend gris
            rotate_north(event)  #orientation du bateau à placé par défaut 
            bl=4 #défini la longeur du bateau à placer 
            compteur_b4=compteur_b4-1 #actualise la valeur du compteur, il y en à unde moins à placer 
            boatframe.itemconfigure(6, text='x '+str(compteur_b4))
        else:
            information.itemconfigure(1, text="Veuillez placer le bateau avant de selectionner un autre.") # vérifie que l'utilisateur n'ait pas fait une erreur 
                                                                            # de saisie du type sélectionner plusiers bateaux simultanément et l'informe dans le cas contraire            
def clicked_b3(event):
    global bl
    global selectable 
    global compteur_b3
    info()
    if compteur_b3==0:
        information.itemconfigure(1, text='Tous les bateaux de cette categorie ont ete places')
    else:
        if selectable==True: #vérifie qu'un autre bateau n'as pas déjà été sélectionné 
            print("Boat 3 selected")
            selectable=False # cela permettra de selectionner un nouveau bateau par la suite
            if compteur_b3==2: 
                boatframe.itemconfigure(3, fill='#A9CCE3') #3 correspond à l'identité du polygone représentant le bateau 3, cela le rend gris
                boatframe.itemconfigure(7, text='x 1')  #actualise également le compteur visuel (7 étant l'id du text widget)
            elif compteur_b3==1:
                boatframe.itemconfigure(3, fill='grey')
                boatframe.itemconfigure(7, text='x 0')
            rotate_north(event)  #orientation du bateau à placé par défaut 
            bl=3    #défini la longeur du bateau à placer 
            compteur_b3=compteur_b3-1  #actualise la valeur du compteur, il y en à unde moins à placer 
        else: 
            information.itemconfigure(1, text="Veuillez placer le bateau avant de selectionner un autre.")# vérifie que l'utilisateur n'ait pas fait une erreur 
                                                                           # de saisie du type sélectionner plusiers bateaux simultanément et l'informe dans le cas contraire           
def clicked_b2(event):
    global bl
    global selectable 
    global compteur_b2
    info()
    if compteur_b2==0:
        information.itemconfigure(1, text='Tous les bateaux de cette categorie ont ete places')
    else:
        if selectable==True:
            print("Boat 2 selected")
            selectable=False
            if compteur_b2==3: 
                boatframe.itemconfigure(4, fill='#5DADE2') #4 correspond à l'identité du polygone représentant le bateau 2, cela le rend gris
                boatframe.itemconfigure(8, text='x 2')
            elif compteur_b2==2:
                boatframe.itemconfigure(4, fill='#A9CCE3')
                boatframe.itemconfigure(8, text='x 1')
            elif compteur_b2==1:
                boatframe.itemconfigure(4, fill='grey')
                boatframe.itemconfigure(8, text='x 0')        
            rotate_north(event)  #orientation du bateau à placé par défaut 
            bl=2    #défini la longeur du bateau à placer 
            compteur_b2=compteur_b2-1  #actualise la valeur du compteur, il y en à unde moins à placer 
        else: 
            information.itemconfigure(1, text="Veuillez placer le bateau avant de selectionner un autre.") # vérifie que l'utilisateur n'ait pas fait une erreur 
                                                                # de saisie du type sélectionner plusiers bateaux simultanément et l'informe dans le cas contraire

def rotate_north(event): #Fonction respective de l'orientation Nord (orientation par défaut)
    global orientation
    cadre.configure(cursor='sb_up_arrow') # Modifie le curseur en flèche pour représenter visuellement le choix d'orientation à l'utilisateur
    boatframe.configure(cursor='sb_up_arrow')
    orientation='N' #défini l'orientation du bateau à placé
def rotate_east(event): #Fonction respective de l'orientation Est
    global orientation
    cadre.configure(cursor='sb_left_arrow') # Modifie le curseur en flèche pour représenter visuellement le choix d'orientation à l'utilisateur
    boatframe.configure(cursor='sb_left_arrow')
    orientation='E' #défini l'orientation du bateau à placé
def rotate_south(event): #Fonction respective de l'orientation Sud
    global orientation
    cadre.configure(cursor='sb_down_arrow') # Modifie le curseur en flèche pour représenter visuellement le choix d'orientation à l'utilisateur
    boatframe.configure(cursor='sb_down_arrow')
    orientation='S' #défini l'orientation du bateau à placé
def rotate_west(event): #Fonction respective de l'orientation Ouest
    global orientation
    cadre.configure(cursor='sb_right_arrow') # Modifie le curseur en flèche pour représenter visuellement le choix d'orientation à l'utilisateur
    boatframe.configure(cursor='sb_right_arrow')
    orientation='W' #défini l'orientation du bateau à placé

boatframe.tag_bind(b5,"<Button-1>",clicked_b5)  # Associe le click des polygones représentant les bateaux
boatframe.tag_bind(b4,"<Button-1>",clicked_b4)  # à leurs fonctions respectives. 
boatframe.tag_bind(b3,"<Button-1>",clicked_b3)
boatframe.tag_bind(b2,"<Button-1>",clicked_b2)
master.bind('<Left>', rotate_east)  # Associe les touches directionelles à leurs fonctions respectives 
master.bind('<Up>', rotate_north)
master.bind('<Down>', rotate_south)
master.bind('<Right>', rotate_west)

#====================================================================
def switch_turn():     #change le tour de jeu 
    global player_turn
    if player_turn==False:
        player_turn=True
    else:
        player_turn=False       
#======================== Info box ==================================
# Ces informations serviront à informer l'utilisateur des instructions, de la manipulation de l'interface et d'erreurs éventuelles de saisies 
information=tk.Canvas(master, width=300, height=300)  #définition d'une partie de canvas dédié aux informations pour l'utilisateur
information.grid(column=1,row=1, sticky='S') #placement en bas à droite de ce panneau d'informations 

info=information.create_text(150,20, text='Select boats above to begin.') #text par défaut 

def info(): #fonction qui modifie le panneau pour apporter plus d'instructions sur le jeu
    information.itemconfigure(1, text='Use arrow keys to modify the orientation of the boat. \n Place boats on the bottom grid, this one is yours.')
#======================= Barres de vie ==============================
barres=tk.Canvas(master, height=150,width=1080)#creation d'un Canvas pour les barres de vie
barres.grid(row=0,column=0, columnspan=2)

def calcul_vie(liste): #fonction calculant la "vie" d'un joueur
    longueur_totale=0
    vie=0
    for i in range(len(liste)): #pour chaque bateau du joueur, on somme les longueurs et la vie
        longueur_totale=longueur_totale+liste[i].length
        vie=vie+(liste[i].bateau_en_vie(liste)*liste[i].length)
    if longueur_totale!=0: #afin d'eviter des erreurs à l'initialisation
        return vie/longueur_totale*100 #on renvoie la vie du joueuer sous forme de pourcentage
        
class barre(): #creation des barres de vie
    def __init__(self, x,liste, nom):
        self.x=x #coordonnée de départ sur l'axe x, permettant de positionner les barres l'une a coté de l'autre
        barres.create_rectangle(self.x,0,self.x+300,50, fill='grey') #création du fond de la barre, qui ne changera pas
        self.bar=barres.create_rectangle(self.x,0,self.x+300,50, fill='blue') #la barre elle-même
        self.name=nom
        self.liste=liste
        self.texte=barres.create_text(self.x+150,25, text=str(self.name)+': '+str(calcul_vie(self.liste))+'%')
        self.draw()
        
        
    def draw(self): #dessin de la barre
        barres.delete(self.bar) #on efface la barre précedente, pour pas que les barres se superposent
        barres.delete(self.texte)
        if calcul_vie(self.liste)!=None:#pour eviter encore des erreurs
            self.bar=barres.create_rectangle(self.x,0,self.x+3*calcul_vie(self.liste),50, fill='blue') #recréation de la barre, cette fois en fonction du pourcentage de vie
            self.texte=barres.create_text(self.x+150,25, text=str(self.name)+': '+str(int(calcul_vie(self.liste)))+'%') #affichage de la valeur numérique pour plus de clarté

barre_joueur=barre(0, ships, 'Joueur')
barre_ai=barre(350, shipsai, 'AI')
#===================================================================

def actualise(): #fonction permettant d'actualiser les barres
    barre_joueur.draw()
    barre_ai.draw()

def quel_bateau(case): #fonction permettant de "parler" au bateau cliqué, en testant si la case appartient a chaque bateau
    for i in range(len(ships)):
        for j in range(len(ships[i].endroits)):
            if ships[i].endroits[j]==case:
                return i #renvoi de l'indice du bateau dans la liste, permettant de lui faire référence plus tard.

def quel_bateau_ai(ai):
    for i in range(len(shipsai)):
        for j in range(len(shipsai[i].projection)):
            try:
                if type(shipsai[i].projection[j])==intelligence_artificielle:
                    return i
            except:
                TypeError
            
def all_placed(): # test si tous les bateaux du joueur ont bien été placés.
    if compteur_b5==0 and compteur_b4==0 and compteur_b3==0 and compteur_b2==0:
        gamemode() #on change le mode jeu
        boatframe.destroy() #on enlève le selectionneur de bateaux
        information.itemconfigure(1, text='It is your turn to play.')
        return True #on renvoie que les bateaux ont bien été placés
    else:
        return False


#Création de deux grilles de 10*10 cases                 
def creation():                
    caseadversaire=[]   
    cases=[]
    for i in range(10):
        cases.append([])
        caseadversaire.append([])
        for j in range(10):
            cases[i].append(case(i,j))
            caseadversaire[i].append(intelligence_artificielle(i,j))

creation()
placeboatsai()
master.mainloop()
