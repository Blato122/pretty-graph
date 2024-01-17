# pretty-graph
A genetic algorithm program that draws a user-friendly graphical representation of a given graph.

Description in Polish:

### 0. Grafy testowe:
Na wstępie, opiszemy grafy wybrane do testowania naszego programu oraz podamy minimalną liczbę przecięć krawędzi dla każdego z nich.
* simple - bardzo prosty graf z 5 wierzchołkami i 8 krawędziami, 0 przecięć
* square3x3 - siatka 3x3, 9 wierzchołków, 12 krawędzi, 0 przecięć
* triangle10 - siatka trójkątna z 10 wierzchołkami i 18 krawędziami, 0 przecięć
* medium - wymyślony graf o 18 wierzchołkach i 24 krawędziach, 0 przecięć
* chatgpt - graf wymyślony przez ChatGPT, 25 wierzchołków i 30 krawędzi, 1 przecięcie
* star16 - graf "gwiazda", 16 wierzchołków, 15 krawędzi, 0 przecięć
* K47 - graf z treści zadania (https://en.wikipedia.org/wiki/Tur%C3%A1n's_brick_factory_problem), 18 przecięć

### 1. Reprezentacja:
Na wejściu graf jest reprezentowany jako lista krawędzi. Nie trzeba podawać nic więcej - lista oraz liczba wierzchołków są automatycznie wyznaczane na podstawie krawędzi.

Aby znaleźć optymalne rozmieszczenie wierzchołków w grafie, potrzebujemy dodatkowo przechowywać informację o współrzędnych X i Y każdego z nich, ponieważ zwykła lista krawędzi i wierzchołków nie daje nam jeszcze żadnych informacji o graficznej reprezentacji.

Współrzędne te są inicjalizowane losowo, przyjmując wartości między 0 a 1. Są trzymane w zwykłej, "płaskiej" (bez zagnieżdżeń) liście o rozmiarze 2 * n, gdzie n to liczba wierzchołków grafu (*2, bo x oraz y). Celem algorytmu genetycznego jest znalezienie takich współrzędnych wierzchołków, dla których dopasowanie jest najlepsze.

Utworzyliśmy również funkcję, która zwraca całość w słowniku, którego kluczami są numery wierzchołków, a wartościami - krotki z współrzędnymi. Taka reprezentacja jest wygodna, czytelna, a co więcej, obsługiwana przez NetworkX, czyli bibliotekę, która umożliwia w łatwy sposób rysować grafy. Wystarczy podać taki słownik do grafu utworzonego z naszej listy krawędzi i wierzchołków, żeby po wywołaniu odpowiedniej funkcji, otrzymać graficzną reprezentację grafu, z wierzchołkami w określonych miejscach.

### 2. Operatory:
Dobór operatorów nie miał dużego znaczenia. Jeśli chodzi o operatory krzyżowania, wszystkie cztery (cxUniform, cxOnePoint, cxTwoPoint, cxBlend) sprawdzały się dosyć dobrze i trudno powiedzieć, który był najlepszy. Ostatecznie postawiliśmy na cxUniform. Jeśli chodzi o mutacje, wybraliśmy mutGaussian z "domyślnymi" parametrami, czyli: mu=0, sigma=1, indpb=0.2. Wydaje nam się, że to dosyć popularny wybór, który również dla tego rozwiązania wydawał nam się sensowny. Poza tym, z naszych obserwacji wynika, że to funkcja dopasowania, metoda selekcji, wielkość populacji i ilość pokoleń miały największe znaczenie dla wyników.

Parametry, czyli prawdopodobieństwo mutacji i prawdopodobieństwo krzyżowania, również nie miały krytycznego znaczenia dla działania algorytmu. Wydaje nam się, że najlepsze wyniki osiąga wysokie pp. mutacji i niskie pp. krzyżowania (np. 0.7 i 0.2). Zgadzałoby się to z dwoma artykułami, w których autorzy podobnych algorytmów również wybrali wysokie pp. mutacji i niskie pp. krzyżowania (jeden z nich: https://www.emis.de/journals/DM/v92/art5.pdf, drugi niestety zgubiliśmy). Testowaliśmy również m.in. wartości 0.2 i 0.7 oraz 0.5 i 0.5, i wydaje nam się, że były one nieco gorszym wyborem niż 0.7 i 0.2, ale wyniki nadal były przyzwoite. Po większej ilości testów, wydaje nam się, że wysokie pp. mutacji i niskie pp. krzyżowania prowadzą do najlepszych wyników, ale tylko czasem, z kolei przy ustawieniu tych pp. na odwrót, dostajemy trochę gorsze wyniki, ale bardziej spójne na przestrzeni wielu uruchomień programu.

### 4. Funkcja dopasowania:
Jest to zdecydowanie najciekawsza i pochłaniająca najwięcej czasu część tego zadania. Znalezienie grafu, dla którego liczba przecięć jest minimalna, było dosyć prostym zadaniem. Wystarczyło napisać funkcję zwracającą liczbę przecięć dla danego grafu i minimalizować ten parametr. Trudniejsze było znalezienie parametrów (i wag), które nadadzą grafowi ładnego kształtu. Ostatecznie padło na:

1. Minimalizację wariancji długości krawędzi
2. Maksymalizację minimalnej długości wierzchołka od krawędzi
3. Minimalizację wariancji odległości między wierzchołkami
4. Maksymalizację minimalnej odległości między wierzchołkami
5. Maksymalizację minimalnego kąta między krawędziami wychodzącymi z danego wierzchołka

Wyniki są, naszym zdaniem, naprawdę dobre, a poprawa względem samej minimalizacji przecięć krawędzi jest zauważalna.

Dodatkowo, ponieważ liczba krawędzi jest podana jako pierwszy parametr, jest ona najważniejszym parametrem, więc dla każdego obliczonego rozmieszczenia grafu jest ona minimalna. Drugi parametr dotyczy już wyglądu grafu i zawiera sumę ważoną pozostałych atrybutów, którą należy zmaksymalizować. Parametry, które należy zminimalizować mają ujemną wagę, a te, które należy zmaksymalizować - dodatnią. Próbowaliśmy wcześniej optymalizacji 6 osobnych parametrów, ale dawało to o wiele gorsze efekty - wydaje się, że każdy kolejny parametr miał o wiele mniejsze znaczenie.

### 3. Metoda selekcji:
Testowaliśmy dwie metody selekcji: selTournament i selNSGA2. Początkowo, korzystaliśmy z selNSGA2, ponieważ ma być ona bardziej odpowiednia dla optymalizacji wieloparametrowej, ale po zmianie wprowadzonej w poprzednim punkcie (2 zamiast 6 parametrów), wróciliśmy do selekcji turniejowej. Mając tylko dwa parametry, z czego pierwszy przyjmuje tylko wartości całkowite, selekcja wygląda następująco (źródło: https://groups.google.com/g/deap-users/c/d9vi86HpypU). Porównywane są wartości dla pierwszego parametru. Wybierany jest osobnik z lepszą wartością. Jeśli wartości są takie same, przechodzimy do drugiej (już przyjmującej wartości rzeczywiste) wartości i na jej podstawie wybieramy osobnika. Jest to dokładnie to, czego chcemy. Jako priorytet stawiamy minimalną liczbę przecięć krawędzi. Po jakimś czasie zostanie ona zminimalizowana i będzie ona równa dla wszystkich/większości osobników (przez wartości całkowite, o tę równość nietrudno). Wtedy przyjdzie czas na optymalizację grafu pod względem wyglądu. Tournsize (liczba osobników uczestniczących w turnieju) ustawiliśmy na 3.

### 5. Warunek stopu:
Warunkiem stopu jest po prostu wykonanie zadanej liczby generacji. Gdyby z góry wiedzieć, jaka jest minimalna liczba przecięć krawędzi w grafie, można by ustalić warunek stopu jako osiągnięcie tej wartości. Nie zawsze jednak mamy tę informację, poza tym, oprócz minimalnej liczby przecięć, graf musi być czytelny (a dla tego kryterium bardzo trudno wymyślić wartość, którą chcemy osiągnąć). Stąd nasz wybór. Po odpowiedniej liczbie generacji, algorytm, dla grafów na których go testowaliśmy, i tak zawsze osiąga minimalną liczbę krawędzi (to jest zresztą najważniejsze kryterium w dopasowaniu).

### 6. Eksperymenty:
Wykonaliśmy bardzo wiele eksperymentów i najlepsze wyniki uzyskujemy przy następującej konfiguracji:

* liczba generacji (NGEN) = 5000
* wielkość populacji (MU) = 15
* pp. krzyżowania (CXPB) = 0.2
* pp. mutacji (MUTPB) = 0.7
* operator krzyżowania: cxUniform, indpb=0.2  (indpb - pp. modyfikacji wybranego elementu listy)
* operator mutacji: mutGaussian, mu=0, sigma=1, indpb=0.2
* metoda selekcji: selTournament(tournsize=3)
* wagi w funkcji dopasowania:
    * wariancja odleglości między wierzchołkami: -1
    * minimalna odleglości między wierzchołkami: +100
    * wariancja długości krawędzi: -100
    * minimalna odleglość wierzchołka od krawędzi: +1
    * minimalny kąt miedzy krawędziami wychodzącymi z danego wierzchołka: +100

Najlepszy wynik znajduje się w folderze "best-layout".

Ogólnie, algorytm lepiej sobie radzi przy małej populacji i dużej liczbie generacji. Bardzo duże znaczenie miało również dobranie odpowiednich wag w funkcji dopasowania. Oczywiście, już samo wprowadzenie dodatkowych parametrów, korzystając z domyślnych wag, [1, 1, 1, 1, 1], miało duży wpływ na wygląd utworzonych grafów (wyglądały one znacznie lepiej niż z jednym parametrem - liczba przecięć krawędzi), ale po przeprowadzeniu wielu eksperymentów, doszliśmy do kombinacji wag, która daje jeszcze lepsze rezultaty ([1, 100, 100, 1, 100]).

Jako wynik ostateczny, bierzemy pierwszego osobnika z HallOfFame, czyli najlepszego osobnika z wszystkich generacji.

Wyniki dla innych konfiguracji umieszczone są w folderach "OLD-RESULTS" i "NEW-RESULTS" oraz "NEW-NEW-RESULTS". W nazwie podfolderu są wartości kolejnych parametrów dla określonej konfiguracji. W środku są grafiki z rozłożeniami różnych grafów po wykonaniu algorytmu. Wyniki sprzed wykonania algorytmu (losowe rozłożenia grafu) i wyniki z gotowej biblioteki (NetworkX) dla porównania są dostępne w folderach "random-layouts" i "nx-layouts".

Zdajemy sobie sprawę z tego, że pewnie nie osiągnęliśmy optimum, możliwych kombinacji jest zresztą nieskończenie wiele. Czas wykonania algorytmu dla wszystkich grafów jest jednak na tyle długi, że trzeba było się w jakiś sposób ograniczyć. Dlatego też eksperymentowaliśmy głównie z różnymi rozmiarami populacji, ilością generacji, funkcją dopasowania, pp. mutacji i krzyżowania, a operatory mutacji i krzyżowania dobraliśmy na samym początku i zostawiliśmy potem bez zmian. Drobnym problemem był również sam wybór przetestowanych już wcześniej parametrów. Czasami trudno było stwierdzić, które wyniki są właściwie lepsze i w którą stronę powinniśmy podążać. Trudno w końcu jednoznacznie ocenić "ładność" grafu. Ostatecznie jednak udało nam się znaleźć zbiór parametrów i operatorów, dla których wyniki są zadowalające.

### 7. Wnioski:
Podsumowując, program radzi sobie dobrze. Ze względu na czas wykonania, testowaliśmy go na grafach małych lub średnich (do kilkudziesięciu krawędzi). Dla grafów bardzo prostych, typu "square3x3", "simple" lub "triangle", wyniki są perfekcyjne, lecz nie jest to żaden wyczyn - człowiek z kartką i długopisem w ręku poradziłby sobie równie dobrze. Biblioteka NetworkX również rozwiązuje te problemy bezbłędnie (choć akurat dla "square3x3" jej wyniki są o dziwo bardzo słabe). Ciekawsza jest grupa grafów trochę większych i bardziej skomplikowanych.

Dla grafu "K47", wynik jest właściwie idealny, taki jak w artykule z Wikipedii: https://en.wikipedia.org/wiki/Tur%C3%A1n's_brick_factory_problem. Graf jest czytelny, osiągnięta została też minimalna liczba przecięć (18). Myślę, że człowiek miałby już duży problem z ładnym (i szybkim) narysowaniem tego grafu, NetworkX również poradził sobie o wiele gorzej. Program dobrze poradził sobie również z dość "losowymi" grafami, bez żadnej konkretnej struktury, czyli "chatgpt" (graf wygenerowany przez chat) oraz "medium".

Myślimy, że patrząc na ograniczone możliwości czasowe testowania i brak własnych operatorów mutacji i krzyżowania, wyniki są naprawdę dobre. W przypadku potrzeby narysowania grafu ze średnią liczbą wierzchołków/krawędzi, myślimy, że skorzystalibyśmy właśnie z tego programu.

---

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
