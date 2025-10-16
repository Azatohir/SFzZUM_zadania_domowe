"""
    do wykonania zadania program korzysta z twierdzenia 2.16, 2.18, twierdzenie 3.10 oraz innych faktow z wykladu

    Plan dzialania:
        - na poczatku znajdujemy odpowiednie parametry n oraz k do naszej konfiguracji, oczywiscie znajdujemy je
            w taki sposob aby spelnialy warunki twierdzen (oraz widzimy ze konfiguracja w twierdzeniu 2.16 jest
            symetryczna wiec korzystamy z twierdzenia 3.10 takze do znalezienia wartosci n i k)
        - posiadajac nasze n, wiemy ze jest potega liczby pierwszej, wiec znajdujemy jaka to
            liczba pierwsza oraz jej potega
        - nastepnie znajdujemy nierozkladalny wielomian o odpowiednim stopniu oraz wartosciach (na podstawie n)
        - dzieki n oraz naszemu wielomianowi generujemy cialo skonczone i wszystkie jego elementy
        - znajdujemy generator naszej grupy
        - korzystajac z twierdzenia 2.18 dostajemy zbior roznicowy, wiec z twierdzenia 2.16 tworzymy
            konfiguracje i wypisujemy wymagana ilosc naszych blowkow
"""
from itertools import product
import numpy as np
import sys

# tworzymy klase dla ciala skonczonego
class GFElement:
    def __init__(self, coeffs, p, mod_poly):
        self.p = p  # liczba pierwsza
        self.mod_poly = mod_poly    # wielomian nierozkladalny
        self.coeffs, _ = poly_mod([c % p for c in coeffs], mod_poly, p) # dla pewnosci reszta

    def __add__(self, other):
        return GFElement(poly_add(self.coeffs, other.coeffs, self.p), self.p, self.mod_poly)

    def __mul__(self, other):
        product = poly_mul(self.coeffs, other.coeffs, self.p)
        remainder, _ = poly_mod(product, self.mod_poly, self.p)
        return GFElement(remainder, self.p, self.mod_poly)

    def __eq__(self, other):
        return self.coeffs == other.coeffs and self.p == other.p and self.mod_poly == other.mod_poly

    def __hash__(self):
        return hash(tuple(self.coeffs))

    def __repr__(self):
        return f"GF({self.p}^n): {self.coeffs}"



def poly_add(a, b, p):   # git
    # dodaje dwa wielomiany modulo p
    return [(ai + bi) % p for ai, bi in zip(a + [0]*(len(b)-len(a)), b + [0]*(len(a)-len(b)))]


def poly_mul(a, b, p):   # mnozenie
    res = [0]*(len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            res[i+j] = (res[i+j] + a[i]*b[j]) % p
    return res


def poly_mod(a, mod, p):     # dzielenie z reszta
    a = a[:]
    wsp = []
    while len(a) >= len(mod):
        if a[-1] == 0:
            a.pop()
            continue
        coeff = (a[-1] * pow(mod[-1], -1, p)) % p   # odwrotnosc ale w tej grupie a nie jeden przez wartosci
        wsp.append(coeff)
        for i in range(len(mod)):
            a[len(a)-len(mod)+i] = (a[len(a)-len(mod)+i] - coeff * mod[i]) % p
        while a and a[-1] == 0:
            a.pop()
    return a, wsp    # chcemy a i wsp


def generate_all_elements(p, n):     # wszystkie mozliwosci wielomianow - sa one jak tablica
    return [list(t) for t in product(range(p), repeat=n)]


def is_irreducible(poly, p):     # sprawdzanie nierozkladalnosci
    deg = len(poly) - 1
    for d in range(1, deg):
        for candidate in product(range(p), repeat=d+1):
            if candidate[-1] == 0: continue
            remainder, _ = poly_mod(poly, list(candidate), p)
            if remainder == [] or all(c == 0 for c in remainder):
                return False
    return True


def generate_irreducible_polynomial(p, n):   # generowanie wszystkich wiel o wiekszym stp i sprawdzanie rozkladalnosci
    for coeffs in product(range(p), repeat=n+1):
        if coeffs[-1] == 0: continue  # najwyzszy wspolczynnik =/= 0
        if is_irreducible(list(coeffs), p):
            return list(coeffs)
    return None


def is_integer_number(x):    # czy int
    return isinstance(x, int) or (isinstance(x, float) and x.is_integer())


def is_prime(x):     # sprawdzenie pierwszosci
    if x < 2:
        return False
    for i in range(2, int(x**0.5) + 2):
        if x % i == 0:
            return False
    return True


def is_power_of_prime(n):    # sprawdzamy czy jest to liczba pierwsza do potegi
    if n < 2:
        return False
    for base in range(2, n+1):
        if is_prime(base):
            exp = 1
            power = base
            while power < n:
                power *= base
                exp += 1
            if power == n:
                return base, exp
    return 0, 0


def finding_params_of_n_and_k(n_start, korygacja_co_najmniej_x_bledow):  # znajdowanie n i k do plaszczyzny
    n_akt = n_start
    i = 0
    while i < 100000:    # ograniczone aby nie bylo nieskonczonosci przypadkiem (dla pewnosci)
        k_akt = 1
        base, exp = is_power_of_prime(n_akt)
        if n_akt % 4 == 3 and base != 0 and exp != 0:     # warunki
            while k_akt < n_akt:    # kolejny warunek z twierdzenia
                r_two = k_akt * (k_akt - 1) / (n_akt-1)  # chcemy r2, bo jest potrzebne do bledow
                # w tym ifie sprawdzamy czy korygacja bledow odpowiada temu co chcemy
                if is_integer_number(r_two) and k_akt - r_two > korygacja_co_najmniej_x_bledow and r_two != 0:
                    return n_akt, k_akt, int(r_two), base, exp
                k_akt += 1
        n_akt += 1
        i += 1
    return 0, 0, 0, 0


def finding_generator(list_of_elements_gfe):     # znajdowanie generatora
    n = len(list_of_elements_gfe)
    for candidate in list_of_elements_gfe:
        powers = set()
        current = candidate
        for _ in range(n):
            powers.add(current)
            current = current * candidate
        if len(powers) == n-1:
            return candidate
    return None


def ending_generating_sets(generator, list_of_elements_gfe, obliczone_k, given_m_from_start):    # wynik
    n = len(list_of_elements_gfe)
    first_element = generator * generator
    lista_zbiorow = []
    zbior = []
    for i in range(obliczone_k):
        zbior.append(first_element)
        first_element = first_element * generator


    for k in range(n):
        element_which_we_add = list_of_elements_gfe[k]
        temp_zbior = []
        for element in zbior:
            temp_zbior.append(element_which_we_add + element)
        lista_zbiorow.append(temp_zbior)
    # mamy wszystkie zbiory teraz trza przerobic na macierz
    macierz_incy = []
    for i in range(given_m_from_start): #given_m_from_start
        kolumna = np.zeros(n)
        for j in lista_zbiorow[i]:
            kolumna[list_of_elements_gfe.index(j)] = 1
        macierz_incy.append(kolumna)
        print(kolumna)


def dzialanie_programu(given_m_from_start, b1):  # polaczenie wszystkiego
    n_akt, k_akt, t_two, base, exp = finding_params_of_n_and_k(given_m_from_start, b1)
    irr_poly = generate_irreducible_polynomial(base, exp)
    all_field_elements = [
        GFElement(list(coeffs), base, irr_poly)
        for coeffs in generate_all_elements(base, exp)
    ]
    generator_of_our_group = finding_generator(all_field_elements)
    ending_generating_sets(generator_of_our_group, all_field_elements, k_akt, given_m_from_start)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uzycie: python main.py <m> <d>")
        sys.exit(1)

    m = int(sys.argv[1])
    d = int(sys.argv[2])
    dzialanie_programu(m, d)
