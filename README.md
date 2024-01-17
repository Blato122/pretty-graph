# pretty-graph
A genetic algorithm program that draws a user-friendly graphical representation of a given graph.

Description in Polish:

0. Grafy testowe:

    Na wstepie, opiszemy grafy wybrane do testowania naszego programu oraz podamy minimalna liczbe przeciez krawedzi dla kazdego z nich.
    
    * simple - bardzo prosty graf z 5 wierzcholkami i 8 krawedziami, 0 przeciec
    * square3x3 - siatka 3x3, 9 wierzcholkow, 12 krawedzi, 0 przeciec
    * triangle10 - siatka trojkatna z 10 wierzcholkami i 18 krawedziami, 0 przeciec
    * medium - wymyslony graf o 18 wierzcholkach i 24 krawedziach, 0 przeciec
    * chatgpt - graf wymyslony przez chatgpt, 25 wierzcholkow i 30 krawedzi, 1 przeciecie
    * star16 - graf "gwiazda", 16 wierzcholkow, 15 krawedzi, 0 przeciec
    * K47 - graf z tresci zadania (https://en.wikipedia.org/wiki/Tur%C3%A1n's_brick_factory_problem), 18 przeciec

1. Reprezentacja:

    Na wejsciu graf jest reprezentowany jako lista krawedzi. Nie trzeba podawac nic wiecej - lista oraz liczba wierzcholkow sa automatycznie wyznaczane na podstawie krawedzi.

    Aby znalezc optymalne rozlozenie wierzcholkow w grafie, potrzebujemy dodatkowo przechowywac informacje o wspolrzednych X i Y kazdego z nich, poniewaz zwykla lista krawedzi i wierzcholkow nie daje nam jeszcze zadnych informacji o graficznej reprezentacji.

    Wspolrzedne te sa inicjalizowane losowo, przyjmujac wartosci miedzy 0, a 1. Trzymam je w zwyklej, "plaskiej" (bez zagniezdzen), liscie o rozmiarze 2*n, gdzie n to liczba wierzcholkow grafu (\*2, bo x oraz y). Celem algorytmu genetycznego jest znalezienie takich wspolrzednych wierzcholkow, dla ktorych dopasowanie jest najlepsze.

    Utworzylismy rowniez funkcje, ktora zwraca calosc w slowniku, ktorego kluczami sa numery wierzcholkow, a wartosciami - krotki z wspolrzednymi. Taka reprezentacja jest wygodna, czytelna, a co wiecej, obslugiwana przez NetworkX, czyli biblioteke, ktora umozliwia w latwy sposob rysowac grafy. Wystarczy podac taki slownik do grafu utworzonego z naszej listy krawedzi i wierzcholkow, zeby po wywolaniu odpowiedniej funkcji, otrzymac graficzna reprezentacje grafu, z wierzcholkami w okreslonych miejscach.

2. Operatory:

    Dobor operatorow nie mial duzego znaczenia. Jesli chodzi o operatory krzyzowania, wszystkie cztery (cxUniform, cxOnePoint, cxTwoPoint, cxBlend) sprawdzaly sie dosc dobrze i trudno mi powiedziec, ktory byl najlepszy. Ostatecznie postawilismy na cxUniform. Jesli chodzi o mutacje, wybralismy mutGaussian z "domyslnymi" parametrami, czyli: mu=0, sigma=1, indpb=0.2. Wydaje nam sie, ze to dosc popularny wybor, ktory rowniez dla tego rozwiazania wydawal nam sie sensowny. Poza tym, z naszych obserwacji wynika, ze to funkcja dopasowania, metoda selekcji, wielkosc populacji i ilosc pokolen mialy najwieksze znaczenie dla wynikow. 

    Parametry, czyli prawdopodobienstwo mutacji i prawdopodobienstwo krzyzowania, rowniez nie mialy krytycznego znaczenia dla dzialania algorytmu. Wydaje nam sie, ze najlepsze wyniki osiaga wysokie pp. mutacji i niskie pp. krzyzowania (np. 0.7 i 0.2). Zgadzaloby sie to z dwoma artykulami, w ktorych autorzy podobnych algorytmow rowniez mieli wysokie pp. mutacji i niskie pp. krzyzowania (jeden z nich: https://www.emis.de/journals/DM/v92/art5.pdf, drugi niestety zgubilismy). Sprawdzalismy rowniez m.in. wartosci 0.2 i 0.7 oraz 0.5 i 0.5 i wydaje nam sie, ze byly one nieco gorszym wyborem niz 0.7 i 0.2, ale wyniki nadal byly przyzwoite. Po wiekszej ilosci testow, wydaje nam sie, ze wysokie pp. mutacji i niskie pp. krzyzowania prowadzi do najlepszych wynikow, ale tylko czasem, z kolei przy ustawieniu tych pp. na odwrot, dostajemy troche gorsze wyniki, ale bardziej spojne na przestrzeni wielu uruchomien programu.

4. Funkcja dopasowania:

    Jest to zdecydowanie najciekawsza i pochlaniajaca najwiecej czasu czesc tego zadania. Znalezienie grafu, dla ktorego
    liczba przeciec jest minimalna bylo dosc prostym zadaniem. Wystarczylo napisac funkcje zwracajaca liczbe przeciec dla
    danego grafu i minimalizowac ten parametr. Trudniejsze bylo znalezienie parametrow (i wag), ktore nadadza grafowi ladnego
    ksztaltu. Ostatecznie padlo na:
      1. minimalizacje wariancji dlugosci krawedzi
      2. maksymalizacje minimalnego dlugosci wierzcholka od krawedzi
      3. minimalizacje wariancji odleglosci miedzy wierzcholkami
      4. maksymalizacje minimalnej odleglosci miedzy wierzcholkami
      5. maksymalizacje minimalnego kata miedzy krawedziami wychodzacymi z danego wierzcholka
    
    Wyniki sa, naszym zdaniem, naprawde dobre i poprawa wzgledem samej minimalizacji przeciec krawedzi jest zauwazalna.

    Dodatkowo, poniewaz liczba krawedzi jest podana jako pierwszy parametr, jest ona najwazniejszym parametrem, wiec
    dla kazdego obliczonego rozlozenia grafu jest ona minimalna. Drugi parametr dotyczy juz wygladu grafu i zawiera sume wazona pozostalych atrybutow, ktora nalezy zmaksymalizowac. Parametry, ktore nalezy zminimalizowac maja ujemna wage, a te, ktore nalezy zmaksymalizowac - dodatnia. Probowalismy wczesniej optymalizacji 6 osobnych parametrow, ale dawalo to o wiele gorsze efekty, wydaje sie, ze kazdy kolejny parametr mial o wiele mniejsze znaczenie.

3. Metoda selekcji:

    Testowalismy dwie metody selekcji: selTournament i selNSGA2. Poczatkowo, korzystalismy z selNSGA2 poniewaz ma byc ona
    bardziej odpowiednia dla optymalizacji wieloparametrowej, ale po zmianie wprowadzonej w poprzednim punkcie (2 zamiast 6 parametrow), wrocilismy do selekcji turniejowej. Majac tylko dwa parametry, z czego pierwszy przyjmuje tylko wartosci calkowite, selekcja wyglada nastepujaco (zrodlo: https://groups.google.com/g/deap-users/c/d9vi86HpypU). Porownywane sa wartosci dla pierwszego parametru. Wybierany jest osobnik z lepsza wartoscia. Jesli wartosci sa takie same, przechodzimy do drugiej (juz przyjmujacej wielkosci rzeczywiste) wartosci i na jej podstawie wybieramy osobnika. Jest to dokladnie cos, czego chcemy. Jako priorytet stawiamy minimalna liczbe przeciec krawedzi. Po jakims czasie zostanie ona zminimalizowana i bedzie ona rowna dla wszystkich/wiekszosci osobnikow (przez wartosci calkowite, o ta rownosc nietrudno). Wtedy przyjdzie czas na optymalizacje grafu pod wzgledem wygladu. Testowalismy k=3 oraz k=5, wyniki sa podobne, zostalismy przy k=3.

5. Warunek stopu:

    Warunkiem stopu jest po prostu wykonanie zadanej liczby generacji. Gdyby z gory wiedziec, jaka jest minimalna liczba przeciec krawedzi w grafie, mozna by ustalic warunek stopu jako osiagniecie tej wartosci. Nie zawsze jednak mamy ta informacje, poza tym, oprocz minimalnej liczby przeciec, graf musi byc czytelny (a dla tego kryterium bardzo trudno wymyslic wartosc, ktora chcemy osiagnac). Stad nasz wybor. Po odpowiedniej liczbie generacji, algorytm, dla grafow na ktorych go testowalismy, i tak zawsze osiaga minimalna liczbe krawedzi (to jest zreszta najwazniejsze kryterium w dopasowaniu).

6. Eksperymenty:

    Wykonalismy bardzo wiele eksperymentow i najlepsze wyniki uzyskujemy przy nastepujacej konfiguracji:
    (indbp - pp. modyfikacji wybranego elementu listy)
    * liczba generacji (NGEN) = 5000
    * wielkosc populacji (MU) = 15
    * pp. krzyzowania (CXPB) = 0.2
    * pp. mutacji (MUTPB) = 0.7
    * operator krzyzowania: cxUniform, indpb=0.2
    * operator mutacji: mutGaussian, mu=0, sigma=1, indpb=0.2
    * metoda selekcji: selTournament(tournsize=3)
    * wagi w funkcji dopasowania:
        * wariancja odleglosci miedzy wierzcholkami: -1
        * minimalna odleglosci miedzy wierzcholkami: +100
        * wariancja dlugosci krawedzi: -100
        * minimalna odleglosc wierzcholka od krawedzi: +1
        * minimalny kat miedzy krawedziami wychodzacymi z danego wierzcholka: +100

    Najlepszy wynik znajduje sie w folderze best-layout.

    Ogolnie, algorytm lepiej sobie radzi przy malej populacji i duzej liczbie generacji. Bardzo duze znaczenie mialo rowniez dobranie odpowiednich wag w funkcji dopasowania. Oczywiscie, juz samo wprowadzenie dodatkowych parametrow, korzystajac z domyslnych wag, [1, 1, 1, 1, 1], mialo duzy wplyw na wyglad utworzonych grafow (wygladaly one znacznie lepiej niz z jedynm parametrem - liczba przeciec krawedzi), ale po przeprowadzeniu wielu eksperymentow, doszlismy do
    kombinacji wag, ktora daje jeszcze lepsze rezultaty ([1, 100, 100, 1, 100]).

    Jako wynik ostateczny, bierzemy pierwszego osobnika z HallOfFame, czyli najlepszego osobnika z wszystkich generacji.

    Wyniki dla innych konfiguracji umieszczone sa w folderach "OLD-RESULTS" i "NEW-RESULTS" oraz "NEW-NEW-RESULTS". W nazwie podfolderu sa wartosci kolejnych parametrow dla okreslonej konfiguracji. W srodku sa grafiki z rozlozeniami roznych grafow po wykonaniu algorytmu. Wyniki sprzed wykonania algorytmu (losowe rozlozenia grafu) i wyniki z gotowej biblioteki (NetworkX) dla porownania sa dostepne w folderach "random-layouts" i "nx-layouts".

    Zdajemy sobie sprawe z tego, ze mozliwych kombinacji jest o wiele wiecej i ze pewnie nie osiagnelismy optimum. Czas wykonania algorytmu dla wszystkich grafow jest jednak na tyle dlugi, ze trzeba bylo sie w jakis sposob ograniczyc. Dlatego tez eksperymentowalismy glownie z roznymi rozmiarami populacji / iloscia generacji / funkcja dopasowania / pp. mutacji i krzyzowania, a operatory mutacji i krzyzowania dobralismy na samym poczatku i zostawili potem bez zmian. Drobnym problemem byl rowniez sam wybor przetestowanych juz wczesniej parametrow. Czasami trudno bylo stwierdzic ktore wyniki sa wlasciwie lepsze i w ktora strone powinnismy podazac. Trudno w koncu jednoznacznie ocenic "ladnosc" grafu. Ostatecznie jednak udalo nam sie znalezc zbior parametrow i operatorow, dla ktorego wyniki sa zadowalajace.

7. Wnioski:

    Podsumowujac, program radzi sobie dobrze. Ze wzgledu na czas wykonania, testowalismy go na grafach malych lub srednich (do kilkudziesieciu krawedzi). Dla grafow bardzo prostych, typu "square3x3", "simple" lub "triangle", wyniki sa perfekcyjne, lecz nie jest to zaden wyczyn - czlowiek z kartka i dlugopisem w reku poradzilby sobie rownie dobrze. Biblioteka NetworkX rowniez rozwiazuje te problemy bezblednie (chociaz akurat dla "square3x3" jej wyniki sa o dziwo bardzo slabe). Ciekawsza jest grupa grafow troche wiekszych i bardziej skomplikowanych.
    
    Dla grafu "K47", wynik jest wlasciwie idealny, taki jak w artykule z Wikipedii: https://en.wikipedia.org/wiki/Tur%C3%A1n's_brick_factory_problem. Graf jest czytelny, osiagnieta zostala tez minimalna liczba przeciec (18). Mysle, ze czlowiek mialby juz duzy problem z ladnym (i szybkim) narysowaniem tego grafu, NetworkX tez poradzil sobie o wiele gorzej. Program dobrze poradzil sobie rowniez z dosc "losowymi" grafami, bez zadnej konkretnej struktury, czyli "chatgpt" (graf wygenerowany przez chat) oraz "medium".

    Myslimy, ze patrzac na ograniczone mozliwosci czasowe testowania i brak wlasnych operatorow mutacji i krzyzowania, wyniki sa naprawde dobre. W przypadku potrzeby narysowania grafu ze srednia liczba wierzcholkow/krawedzi, myslimy, ze skorzystalibysmy wlasnie z tego programu.

Useful stuff:
https://groups.google.com/g/deap-users/c/d9vi86HpypU
https://stackoverflow.com/questions/61539157/fitness-function-with-multiple-weights-in-deap
https://deap.readthedocs.io/en/master/examples/ga_knapsack.html
https://en.wikipedia.org/wiki/Tur%C3%A1n's_brick_factory_problem
https://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
https://tecfa.unige.ch/perso/yvan/GeneticGraph/index.htm
https://stackoverflow.com/a/1076835/22799795
https://www.emis.de/journals/DM/v92/art5.pdf

To do (?):
https://deap.readthedocs.io/en/master/tutorials/basic/part3.html#logging
https://www.youtube.com/watch?v=SL-u_7hIqjA (watch)
refactoring, new functions
