# pretty-graph
A genetic algorithm program that draws a user-friendly graphical representation of a given graph.

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

1. Reprezentacja:
    Na wejsciu graf jest reprezentowany jako lista krawedzi. Nie trzeba podawac nic wiecej - lista oraz liczba wierzcholkow sa automatycznie wyznaczane na podstawie krawedzi.

    Aby znalezc optymalne rozlozenie wierzcholkow w grafie, potrzebuje dodatkowo przechowywac informacje o wspolrzednych X i Y kazdego z nich, poniewaz zwykla lista krawedzi i wierzcholkow nie daje nam zadnych informacji o graficznej reprezentacji.

    Wspolrzedne te sa inicjalizowane losowo, przyjmujac wartosci miedzy 0, a 1. Trzymam je w zwyklej, "plaskiej" (bez zagniezdzen), liscie o rozmiarze 2*n, gdzie n to liczba wierzcholkow grafu (2, bo x oraz y). Celem algorytmu genetycznego jest znalezienie takich wspolrzednych wierzcholkow, dla ktorych dopasowanie jest najlepsze.

    Utworzylem rowniez funkcje, ktora zwraca calosc w slowniku, ktorego kluczami sa numery wierzcholkow, a wartosciami - krotki z wspolrzednymi. Taka reprezentacja jest wygodna, czytelna, a co wiecej, obslugiwana przez NetworkX, czyli biblioteke, ktora umozliwia w latwy sposob rysowac grafy. Wystarczy podac taki slownik do grafu utworzonego z naszej listy krawedzi i wierzcholkow, zeby po wywolaniu odpowiedniej funkcji, otrzymac graficzna reprezentacje grafu, z wierzcholkami w okreslonych miejscach.

2. Operatory:
    Dobor operatorow nie mial duzego znaczenia. Jesli chodzi o operatory krzyzowania, wszystkie cztery (cxUniform, cxOnePoint, cxTwoPoint, cxBlend) sprawdzaly sie dosc dobrze i trudno mi powiedziec, ktory byl najlepszy. Ostatecznie postawilem na cxUniform. Jesli chodzi o mutacje, wybralem mutGaussian z "domyslnymi" parametrami, czyli: mu=0, sigma=1, indpb=0.2. Wydaje mi sie, ze to dosc popularny wybor, ktory rowniez dla tego rozwiazania wydawal mi sie sensowny. Poza tym, z moich obserwacji wynika, ze to funkcja dopasowania, metoda selekcji, wielkosc populacji i ilosc pokolen mialy najwieksze znaczenie dla wynikow. 

    Parametry, czyli prawdopodobienstwo mutacji i prawdopodobienstwo krzyzowania, rowniez nie mialy krytycznego znaczenia dla dzialania algorytmu. Wydaje mi sie, ze najlepsze wyniki osiaga wysokie pp. mutacji i niskie pp. krzyzowania (np. 0.7 i 0.2). Zgadzaloby sie to z dwoma artykulami, w ktorych autorzy podobnych algorytmow rowniez mieli wysokie pp. mutacji i niskie pp. krzyzowania (jeden z nich: https://www.emis.de/journals/DM/v92/art5.pdf, drugi niestety zgubilem). Sprawdzalem rowniez  m.in. wartosci 0.2 i 0.7 oraz 0.5 i 0.5 i wydaje mi sie, ze byly one nieco gorszym wyborem niz 0.7 i 0.2, ale wyniki nadal byly przyzwoite.

3. Metoda selekcji:
    Testowalismy dwie metody selekcji: selTournament i selNSGA2.
    ...
    lalala

4. Funkcja dopasowania:
    Jest to zdecydowanie najciekawsza i pochlaniajaca najwiecej czasu czesc tego zadania. 

    napisac o zmianie z dzisiaj rana

5. Warunek stopu:
    Warunkiem stopu jest po prostu wykonanie zadanej liczby generacji. Gdyby w gory wiedziec, jaka jest minimalna liczba przeciec krawedzi w grafie, mozna by ustalic warunek stopu jako osiagniecie tej wartosci. Nie zawsze jednak mamy ta informacje, poza tym, oprocz minimalnej liczby przeciec, graf musi byc czytelny (a dla tego kryterium bardzo trudno wymyslic wartosc, ktora chcemy osiagnac). Stad moj wybor. Po odpowiedniej liczbie generacji, algorytm, dla grafow na ktorych go testowalem, zawsze osiaga minimalna liczbe krawedzi (to jest zreszta najwazniejsze kryterium w dopasowaniu).

6. Eksperymenty:
    Wykonalismy bardzo wiele eksperymentow i najlepsze wyniki uzyskuje przy nastepujacej konfiguracji:
    ..
    ...
    ..

    Wyniki dla innych konfiguracji umieszczone sa w folderach. W nazwie folderu sa wartosci kolejnych parametrow dla okreslonej konfiguracji. W srodku sa grafiki z rozlozeniami roznych grafow, przed i po wykonaniu algorytmu oraz wyniki z gotowej biblioteki (NetworkX) dla porownania.

    Zdajemy sobie sprawe z tego, ze mozliwych kombinacji jest o wiele wiecej i ze pewnie nie osiagnelismy optimum. Czas wykonania algorytmu dla wszystkich grafow jest jednak na tyle dlugi, ze trzeba bylo sie w jakis sposob ograniczyc. Dlatego tez eksperymentowalismy glownie z roznymi rozmiarami populacji / iloscia generacji / funkcja dopasowania / pp. mutacji i krzyzowania, a operatory mutacji i krzyzowania dobralismy na samym poczatku i zostawili potem bez zmian.

    poeksperymentowac jeszcze z wagami w eval?

7. Wnioski:
    lepiej niz gotowy spring czasami, a nawet czesto w sumie
    ale nie jest idealny, duze roznice miedzy roznymi "runs"
    no i dla triangle graph slabo np. i star tez - ale to sa
    rozwiazania dla ktorych latwo znalezc rozlozenie grafu korzystajac z bibliotek innych. a dla trudnych grafow moj alg radzi sobie dobrze, a gotowiec juz nie (chyba ze inne layouty gotowe lepsze beda - przetestowac!!!)
    ja bym korzystal xd