"""Shot plan: Haiti Files part 4 (rebuilt engine)."""
import os
_IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
def I(n): return n if (n == 'dark' or os.path.exists(os.path.join(_IMG, n + '.jpg'))) else 'dark'
def PL(img, w=1, **k): return (w, 'plain', dict(img=I(img), **k))
def Q(lines, w=1, **k): return (w, 'quote', dict(lines=lines, bgimg=I(k.pop('bgimg', 'dark')), **k))
def X(kind, w=1, **k):
    for kk in ('bgimg', 'img'):
        if kk in k: k[kk] = I(k[kk])
    return (w, kind, k)
def G(mode, w=1, **k): return (w, 'geo', dict(**k))

PRON = [('Lanmò Sanjou', 'Lan-mo Sahn-zhoo'), ('Germine Joly', 'Zher-meen Zho-lee'), ('Yonyon', 'Yon-yon'), ('Ti Gabriel', 'Tee Ga-bree-el'), ('Gabriel Jean Pierre', 'Ga-bree-el Zhon Pee-air'), ("Vitel'Homme Innocent", 'Vee-tel-om Ee-no-sahn'), ('Kraze Baryè', 'Kra-zay Bar-yeh'), ('Johnson André', 'Johnson On-dray'), ('Izo', 'Ee-zo'), ('5 Segonn', 'Sank Seh-gon'), ('Village de Dieu', 'Vee-lahzh duh Dyuh'), ('Gran Grif', 'Grahn Greef'), ('Artibonite', 'Ar-tee-bo-neet'), ('Pont Sondé', 'Pon Son-day'), ('Luckson Élan', 'Luckson Eh-lahn'), ('Prophane Victor', 'Pro-fahn Veek-tor'), ('Mathias Saintil', 'Ma-tee-ahs San-teel'), ('Jeff Larose', 'Jeff La-rohz'), ('Canaan', 'Kay-nan'), ('Kempes Sanon', 'Kem-pes Sa-non'), ('Dimitri Hérard', 'Dee-mee-tree Ay-rar'), ('Krisla', 'Krees-lah'), ('Martissant', 'Mar-tee-sahn'),
        ('Port au Prince', 'Port oh Prance'), ('Jimmy Chérizier', 'Jimmy Sheh-ree-zee-ay'), ('Chérizier', 'Sheh-ree-zee-ay'), ('La Saline', 'La Sa-leen'), ('G nine', 'G nine'), ('G Pèp', 'G Pep'), ('Cité Soleil', 'See-teh So-lay'), ('Viv Ansanm', 'Veev On-sahm'), ('Croix des Bouquets', 'Krwah deh Boo-keh'), ('Bukele', 'Boo-keh-leh'), ('Mawozo', 'Ma-wo-zo'), ('Wilson Joseph', 'Wilson Zho-zef'), ('ACLED', 'Ack-led'), ('CECOT', 'Seh-kot')]

VIEWS = {'haiti': (-74.6, -71.4, 17.8, 20.3), 'pap': (-72.75, -71.95, 18.3, 18.85)}
CITIES = {'pap': (-72.34, 18.54), 'cdb': (-72.20, 18.58), 'pontsonde': (-72.61, 19.15), 'canaan': (-72.29, 18.64), 'martissant': (-72.36, 18.52)}
def HMAP(cities, main, view='pap', zoom=(1.0, 1.15)): return G('locate', view=view, zoom=zoom, cities=[(c, l, 22, 12) for c, l in cities], main=main, hl='Haiti')

AUTOTAG = dict(delmas1='VIEW FROM DELMAS, PORT-AU-PRINCE', soleil1='CITÉ SOLEIL FROM THE AIR · 2006 (FILE PHOTO)', soleil2='CITÉ SOLEIL · 2006 (FILE PHOTO)', mss1='SALVADORAN AND GUATEMALAN TROOPS ARRIVE · JAN 2025 (FILE PHOTO)', mrap1='ARMORED VEHICLES FOR THE KENYA-LED MISSION · 2024 (FILE PHOTO)', aer2='CECOT, EL SALVADOR (GOVT PHOTO)', kast24='CECOT CELL BLOCK (GOVT PHOTO)')
EXTRA = dict(o3=1.0, o4=0.8, a4=0.6, b4=1.0, c4=0.8, c6=1.0, d2=0.6, d4=0.6, d5=1.0, e4=0.8, f4=0.8, f5=1.0, g1=0.6, g2=1.0, h1=1.2, h4=1.0, h5=1.0, h6=2.5)
ROLL = ['dark']
_M1 = (1, 'geo', dict(view='haiti', zoom=(1.0, 1.08), cities=[('pap', 'PORT-AU-PRINCE', 22, 12)], main='pap', hl='Haiti'))
_M2 = (1, 'geo', dict(view='pap', zoom=(1.0, 1.12), cities=[('pap', 'PORT-AU-PRINCE', 22, 12)], main='pap', hl='Haiti'))
SEGROLL = dict(o=[_M1], a=[_M1, 'soleil1'], b=[_M2], c=[_M2], d=['soleil2', 'soleil1'], e=[_M1], f=['soleil1', 'soleil2'], g=[_M2], h=[_M1, _M2])

D = lambda a, b, col='#d9a441', bg='dark': X('dial', items=[(a, b, col)], bgimg=bg)
L = lambda head, items, img='dark': X('list', img=img, head=head, items=items)
IT = [('BARBECUE', 'G9 · VIV ANSANM'), ('LANMÒ SANJOU', '400 MAWOZO'), ('YONYON', '400 MAWOZO'), ('TI GABRIEL', 'G-PÈP'), ("VITEL'HOMME", 'KRAZE BARYÈ'), ('IZO', '5 SEGONN'), ('LUCKSON ÉLAN', 'GRAN GRIF'), ('PROPHANE VICTOR', 'GRAN GRIF'), ('MATHIAS SAINTIL', 'BOSTON'), ('JEFF LAROSE', 'TALIBAN'), ('KEMPES SANON', 'BEL AIR'), ('KRISLA', 'GANG LEADER')]
FIN = {1: 'S', 2: 'C', 8: 'D', 9: 'S'}
def BD(st=None, hl=(), new=(), w=1.2, **k): return X('hboard', w, items=IT, st=dict(st or {}), hl=list(hl), new=list(new), **k)
def FG(num, alias, name, lines, st): return X('fugitive', num=num, alias=alias, name=name, lines=lines, stamp=st, stamp_t=2.2)

PLAN = {
    'o1': [BD({}, count=False), L('ACCUSED OF (U.S. / UN)', ['MASSACRES', 'MASS KIDNAPPINGS', 'A CAPITAL IN COLLAPSE'], 'delmas1')],
    'o2': [BD(FIN, new=list(FIN), stamp_t=1.2, title='ONE MONTH LATER')],
    'o3': [BD(FIN, hl=[2]), BD(FIN, hl=[8]), BD(FIN, hl=[1, 9]), BD(FIN, hl=[0, 3, 4, 5, 6, 7, 10, 11])],
    'o4': [X('title', title='HAITI FILES', sub='PART 4 · ONE BY ONE', size=160)],
    'ch1': [X('chapter', num=1, title='The Alliance', bgimg='soleil1')],
    'a1': [X('dial', items=[('G9', '', '#d9a441'), ('G-PÈP', '', '#b3302a')], vs=True, bgimg='soleil1')],
    'a2': [X('title', title='VIV ANSANM', sub='"LIVE TOGETHER" · FEB 2024', size=150), L('WITHIN WEEKS', ['POLICE STATIONS ATTACKED', 'AIRPORT BESIEGED', 'TWO LARGEST PRISONS EMPTIED'], 'delmas1')],
    'a3': [X('doc', head='UNITED STATES · MAY 2025', lines=['VIV ANSANM + GRAN GRIF', '*FOREIGN TERRORIST ORGANIZATIONS']), D('12,000-20,000', 'VIV ANSANM MEMBERS (CRISIS GROUP)', '#b3302a')],
    'a4': [X('title', title='SUBSCRIBE', sub="EVERY NEW CHAPTER OF BUKELE'S WAR IN HAITI", size=150)],
    'ch2': [X('chapter', num=2, title='Barbecue', bgimg='delmas1')],
    'b1': [BD({}, hl=[0], count=False), FG('01', 'BARBECUE', 'JIMMY CHÉRIZIER', ['G9 · VIV ANSANM', 'FORMER POLICE OFFICER'], None)],
    'b2': [L('U.S. / UN', ['ACCUSED: LA SALINE 2018 (DENIES)', 'U.S. SANCTIONS 2020', 'UN SANCTIONS 2022', 'U.S. CHARGES 2025']), D('$5,000,000', 'U.S. REWARD')],
    'b3': [D('JAN 14, 2026', '3 HOMES DESTROYED BY DRONES (REUTERS)', '#b3302a')],
    'b4': [FG('01', 'BARBECUE', 'JIMMY CHÉRIZIER', ['NO SALVADORAN STRIKE REPORTED'], 'AT LARGE')],
    'ch3': [X('chapter', num=3, title='400 Mawozo', bgimg='mrap1')],
    'c1': [HMAP([('cdb', 'CROIX-DES-BOUQUETS'), ('pap', 'PORT-AU-PRINCE')], 'cdb'), D('OCT 2021', 'MISSIONARIES KIDNAPPED · INCLUDING CHILDREN', '#b3302a')],
    'c2': [BD({}, hl=[1], count=False), FG('02', 'LANMÒ SANJOU', 'WILSON JOSEPH', ['400 MAWOZO', 'U.S. REWARD UP TO $1,000,000'], None)],
    'c3': [Q(['"I WILL', '*NOT RUN"']), D('NOV 8', 'HOUSE STRUCK · UP TO 20 KILLED (MIAMI HERALD)', '#b3302a')],
    'c4': [X('dial', items=[('TALKS?', '400 MAWOZO', '#cfcfcf'), ('NO', 'EL SALVADOR', '#b3302a')], vs=True), FG('02', 'LANMÒ SANJOU', 'WILSON JOSEPH', ['HOUSE DESTROYED', 'HIS FATE: UNKNOWN'], 'HOUSE STRUCK')],
    'c5': [BD({}, hl=[2], count=False), L('GERMINE JOLY · "YONYON"', ['EXTRADITED TO THE U.S.', 'PLEADED GUILTY: ARMS, MONEY', 'CONVICTED 2025: KIDNAPPING'])],
    'c6': [FG('03', 'YONYON', 'GERMINE JOLY', ['400 MAWOZO', 'SENTENCED TO LIFE (DOJ)'], 'LIFE · U.S.')],
    'ch4': [X('chapter', num=4, title='The Rivals Who Made Peace', bgimg='soleil2')],
    'd1': [FG('04', 'TI GABRIEL', 'GABRIEL JEAN-PIERRE', ['G-PÈP · BROOKLYN, CITÉ SOLEIL', 'ENEMY OF G9, THEN ALLY'], None), PL('soleil1')],
    'd2': [X('doc', head='EUROPEAN UNION · DEC 2024', lines=['ROBBERY · KIDNAPPING · EXTORTION', '*MURDER · RAPE']), FG('04', 'TI GABRIEL', 'GABRIEL JEAN-PIERRE', ['NO RECENT REPORTS'], 'UNKNOWN')],
    'd3': [FG('05', "VITEL'HOMME", "VITEL'HOMME INNOCENT", ['KRAZE BARYÈ', 'U.S. CHARGES 2023'], None), D('NOV 2023', 'FBI TEN MOST WANTED', '#b3302a')],
    'd4': [D('JULY 2025', 'REMOVED FROM THE LIST · "NO LONGER FIT"', '#cfcfcf'), FG('05', "VITEL'HOMME", "VITEL'HOMME INNOCENT", ['NOT REPORTED CAUGHT'], 'UNKNOWN')],
    'd5': [FG('06', 'IZO', 'JOHNSON ANDRÉ', ['5 SEGONN · VILLAGE DE DIEU'], 'UNKNOWN')],
    'ch5': [X('chapter', num=5, title='Gran Grif', bgimg='delmas1')],
    'e1': [HMAP([('pontsonde', 'ARTIBONITE · PONT-SONDÉ'), ('pap', 'PORT-AU-PRINCE')], 'pontsonde', view='haiti')],
    'e2': [D('OCT 3, 2024', 'PONT-SONDÉ ATTACKED', '#b3302a'), X('counter', a=0, b=115, label='KILLED (AT LEAST)', sub='ASSOCIATED PRESS')],
    'e3': [BD({}, hl=[6, 7], count=False), L('GRAN GRIF', ['LUCKSON ÉLAN: THE EXPANSION', 'PROPHANE VICTOR: EX-LAWMAKER, FOUNDER', 'WHO LEADS TODAY: DISPUTED'])],
    'e4': [L('BOTH', ['U.S. SANCTIONS', 'UN SANCTIONS', 'STATUS: UNKNOWN'])],
    'ch6': [X('chapter', num=6, title='From the Sky', bgimg='soleil1')],
    'f1': [Q(['NOT ONLY', '*GANG MEMBERS'], bgimg='soleil1')],
    'f2': [D('SEPT 2025', 'DRONE STRIKE ON A BIRTHDAY PARTY · CITÉ SOLEIL', '#b3302a'), X('dial', items=[('13', 'KILLED', '#b3302a'), ('8', 'CHILDREN', '#b3302a')])],
    'f3': [FG('09', 'MATHIAS SAINTIL', '', ['BOSTON GANG · CITÉ SOLEIL', 'LOITERING MUNITION · NOV 2026'], None), PL('soleil1', z0=1.05, z1=1.15)],
    'f4': [X('dial', items=[('KILLED', "HAITI'S PRIME MINISTER", '#b3302a'), ('WOUNDED?', 'ONE HAITIAN RADIO', '#cfcfcf')], vs=True), FG('09', 'MATHIAS SAINTIL', '', ['NOT INDEPENDENTLY CONFIRMED'], 'DEAD')],
    'f5': [HMAP([('canaan', 'CANAAN'), ('pap', 'PORT-AU-PRINCE')], 'canaan', zoom=(1.0, 1.3)), FG('10', 'JEFF LAROSE', '', ['TALIBAN GANG · CANAAN', 'NOV 18: HOUSE DESTROYED'], 'HOUSE STRUCK')],
    'ch7': [X('chapter', num=7, title='The Last Two', bgimg='delmas1')],
    'g1': [FG('11', 'KEMPES SANON', '', ['BEL AIR', 'U.S. + UN SANCTIONS · OCT 2025'], None), D('DIMITRI HÉRARD', 'EX-PALACE GUARD CHIEF · ESCAPED 2024', '#cfcfcf'), FG('11', 'KEMPES SANON', '', ['BEL AIR'], 'UNKNOWN')],
    'g2': [Q(['"WE DIDN\'T ASK', '*BUKELE TO COME"']), FG('12', 'KRISLA', '', ['"WE WILL FIGHT TO THE END"'], 'AT LARGE')],
    'ch8': [X('chapter', num=8, title='The Scoreboard')],
    'h1': [BD(FIN, title='ONE MONTH IN'), BD(FIN, hl=[0, 3, 4, 5, 6, 7, 10, 11], title='STILL AT LARGE OR UNKNOWN', count=False)],
    'h2': [HMAP([('martissant', 'MARTISSANT')], 'martissant', zoom=(1.0, 1.3)), X('counter', a=0, b=54, label='KILLED IN TWO DAYS', sub='HAITIAN POLICE, VIA HAITIAN TIMES')],
    'h3': [D('NOV 20', 'FIRST SALVADORAN DEATHS · 2 OR 3 (REPORTS DIFFER)', '#b3302a')],
    'h4': [Q(['THE FOUR TECHNICIANS:', '*STILL MISSING'])],
    'h5': [X('counter', a=0, b=3, label='NEW PRISONS', sub='HAITI + EL SALVADOR · NOV 20', bgimg='kast24'), PL('aer2')],
    'h6': [X('title', title='WHO IS NEXT?', sub='TELL US IN THE COMMENTS', size=150), L('HAITI FILES', ["PART 1: HAITI'S PRISON BREAK", 'PART 2: BARBECUE', "PART 3: BUKELE'S FIRST MONTH"], 'delmas1')],
}
