# DFA indirgeme uygulaması
# DFA.txtnin içinde
# İlk satırda alfabe
# İkinci satırda durum sayısı
# Üçüncü satırda başlangıç durumu
# Dördüncü satırda kabul durumları





# DFA'yı dosyadan okuma

#-
automata = open("test1.txt")
alphabet = [x for x in automata.readline().split()] # 1. Satır: Alfabe (input alfabesi)
nrStates = int(automata.readline()) # 2. Satır: Durum sayısı
initialState = automata.readline().strip('\n') # 3. Satır: Başlangıç durumu
finalStates = [x for x in automata.readline().split()] # 4. Satır: Kabul durumları


# 5. ve sonrası: Geçiş fonksiyonu (delta tablosu)


#DFA okuma
#-
delta = {}
line = automata.readline()
while line:
    aux = line.split()
    state1 = aux[0] # Şu anki durum
    state2 = aux[1] # Geçiş sonrası durum
    transition = aux[2] # Hangi harf ile geçiş yapılıyor

    # Eğer şu anki durum daha önce eklenmemişse, yeni bir giriş oluştur

    if state1 not in delta:
        delta[state1] = {transition: state2}
    else:
        delta[state1][transition] = state2
    line = automata.readline()
#-


# Ulaşılamaz durumların kaldırılması
# 'r' kümesi başlangıçta sadece başlangıç durumunu içerir
r = set(initialState)
ok = True

# Bu döngü, başlangıç durumundan ulaşılabilir tüm durumları bulur
while ok:
    ok = False
    new_states = set()
    # Şu anda ulaşılabilir olan her durum için
    for s in r.copy():
        for letter in alphabet:
            new_states.add(delta[s][letter])  # Bu durumdan ulaşılabilen yeni durumları bul

            # Eğer yeni bir durum keşfedildiyse 'r' kümesini güncelle
    if new_states - r:
        r.update(new_states)
        ok = True



# Tablo güncelleme
# Ulaşılamaz durumlar varsa, onları kaldır ve delta tablosunu güncelle
if len(r) != nrStates:
    nrStates = len(r)  # Yeni toplam durum sayısı
    new_delta = {}
    for state in delta:
        if state in r:
            new_delta[state] = delta[state]
    delta = new_delta

# Bundan sonra ulaşılamayan durumlar kaldırıldı

find_state_from_index = {i: state for i, state in enumerate(delta)} # Her duruma index atar
find_index_of_state = {state: i for i, state in enumerate(delta)}

# Minimizasyon için Myhill-Nerode Teoremi kullanımı

# Adım 1: Tablonun oluşturulması
# Bu tablo, iki durumun eşdeğer olup olmadığını anlamak için kullanılır
table = [[0 for j in range(i)] for i in range(nrStates)] # Yeni tablo oluştur

# Adım 2: Kabul durumu ile kabul olmayan durumları işaretleme
# Eğer bir durum kabul durumunda ve diğeri değilse, bunlar eşdeğer değildir
for i in range(1, nrStates):
    for j in range(i):
        if (find_state_from_index[i] in finalStates and find_state_from_index[j] not in finalStates) or (
                find_state_from_index[i] not in finalStates and find_state_from_index[j] in finalStates):
            table[i][j] = 1 # İşaretle (eşdeğer değil)
        else:
            table[i][j] = 0 # İşaretleme yok (henüz eşdeğer olabilirler)

# Adım 3: Tablonun doldurulması
# Eğer bir çift (p, q), başka bir işaretlenmiş çifte bağlıysa, işaretlenir

marked = True
while marked:
    marked = False
    for i in range(1, nrStates):
        for j in range(i):
            if table[i][j] == 0:   # Henüz işaretlenmemiş çiftler
                for letter in alphabet:

                    state1 = delta[find_state_from_index[i]][letter]
                    state2 = delta[find_state_from_index[j]][letter]
                    # İki durumun tablodaki indekslerini bul
                    x = find_index_of_state[state1]
                    y = find_index_of_state[state2]
                    try:
                        check = table[x][y] if x > y else table[y][x]
                        if check == 1: # Eğer ilgili çift işaretliyse
                            table[i][j] = 1 # Şu anki çifti de işaretle
                            marked = True
                            break
                    except:
                        pass

# İşaretlenmemiş çiftler eşdeğer durumları temsil eder
# Adım 4: Durumları gruplandırma (eşdeğer durumlar tek bir durum olarak alınır)

components = []
for i in range(1, nrStates):
    for j in range(i):
        if table[i][j] == 0:

            components.append(set([find_state_from_index[i], find_state_from_index[j]]))

# Grupları birleştirerek son halini oluştur
for i in range(len(components)):
    try:
        current_pair = components[i]
        j = i + 1
        while j < len(components):
            if current_pair.intersection(components[j]):
                current_pair = current_pair.union(components[j])
                components.pop(j)
            else:
                j += 1
        components[i] = current_pair
    except IndexError:
        pass

# Gruplarda olmayan tekil durumları ekle
components_flat = []
nr = 0
for comp in components:
    for state in comp:
        nr += 1
        components_flat.append(state)

if nr != nrStates:
    for i in range(nrStates):
        if find_state_from_index[i] not in components_flat:
            new_comp = find_state_from_index[i]
            components.append(new_comp)

components = [''.join(comp) for comp in components]
# Yeni başlangıç durumunu belirle

found = False
for comp in components: # Yeni kabul durumlarını belirle
    for state in comp:
        if state == initialState:
            initialComponent = comp
            found = True
            break
    if found:
        break

finalComponents = []
for comp in components:
    for state in comp:
        if state in finalStates:
            finalComponents.append(comp)
            break

def build_minimized_delta(components): # Yeni gruplar için tablo oluştur
    global alphabet, delta
    minimized_delta = {}
    for i, comp in enumerate(components):
        for letter in alphabet:
            for state in comp:
                if delta[state][letter] in comp:
                    if comp not in minimized_delta:
                        minimized_delta[comp] = {letter: comp}
                    else:
                        minimized_delta[comp][letter] = comp
                else:
                    for j in range(len(components)):
                        if delta[state][letter] in components[j]:
                            if comp not in minimized_delta:
                                minimized_delta[comp] = {letter: components[j]}
                            else:
                                minimized_delta[comp][letter] = components[j]
    return minimized_delta

minimized_delta = build_minimized_delta(components)

# Minimize edilmiş DFA'yı yazdır
def print_minimized_dfa(components):
    global alphabet, initialComponent, finalComponents, minimized_delta
    print("DFA Son hali: \n")
    print("Durumlar:", *components)
    print("Başlangıç Durumu", initialComponent)
    print("Sonuç Durumları:", *finalComponents)
    print("Değişim tablosu:")
    for comp in minimized_delta:
        for letter in minimized_delta[comp]:
            print(f"\t{comp} -> {letter} -> {minimized_delta[comp][letter]}")


print("İndirgeme işlemi için 0 giriniz: ")
choice = int(input())

if choice == 0:

    componentsUpdated = [] #Ölü durumları kaldırır
    for state in components:
        deadState = True
        reachableStates = [state]

        while True: # Yeni durumları bul
            next = []
            for s in reachableStates:
                for letter in alphabet:
                    next.append(minimized_delta[s][letter])
            newStates = list(set(next))
            if newStates == reachableStates:
                break
            reachableStates = newStates
        for rs in reachableStates: #Ölü durumları belirle
            if rs in finalComponents:
                deadState = False
        if not deadState:
            componentsUpdated.append(state)

    #Yeni DFA yı yazdır
    componentsUpdated = list(set(componentsUpdated))
    minimized_delta = build_minimized_delta(componentsUpdated)
    print_minimized_dfa(componentsUpdated)
else:
    print("Invalid command")
