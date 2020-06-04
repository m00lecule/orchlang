# Kompilatory

Repository contains excercises for AGH UST compilers course - http://orchel.pl/compilers.php

## 1. Funkcjonalność z laboratorium 1

1. Obsługa tokenów dla liczb całkowitych i rzeczywistych

Wykonanie: 5/5

Testy potwierdzające:

```
TestLexer
   test_float
   test_int
```

2. Obsługa tokenów dla funkcji specjalnych sin, cos, itd

Wykonanie: 5/5

Testy potwierdzające:

```
TestLexer
    test_special_fn
```

3. Obsługa tokenów dla operatora potęgowania, itd

Wykonanie: 5/5

Testy potwierdzające:

```
TestLexer
    test_power
```

4. Automatyczna koretka błędów w tokenach

Wykonanie: 5/5

Testy potwierdzające:

```
TestLexer
    test_special_fn
```

5. Definiowanie wzorów w tekście dla języka Markdown

Wykonanie: 0/5

6. Konwersja tokenów języka html do języka Markdown

Wykonanie: 0/5

7. Lexer dla wybranych fragmentów html

Wykonanie: 0/5

#### SUMA: 20/35pkt

## 2. Funkcjonalność z laboratorium 2

1.  Implementacja działań potęgowania, funkcji specjalnych, działań relacyjnych, zmiany znaku.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_binop_number
    test_special_func
    test_log
    test_rel
    test_unary_minus
```

2.  Implementacja instrukcji oddzielonych średnikiem.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_multiple_lines
```

3.  Kontynuacja parsowania kolejnych instrukcji w przypadku błędu.

Wykonanie: 5/5

Implementacja metod:

```

```

4.  Możliwość wykonywania obliczeń dla odwrotnej notacji polskiej.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_rpn
```

5.  Instrukcje warunkowe i pętle.

Wykonanie: 5/5

Testy potwierdzające:

```
ParserTest
    test_if_else
    test_for
```

6.  Terminowe wgranie zadań na laboratorium.

Wykonanie: 5/5

#### SUMA: 30/30pkt

## 3. Funkcjonalność z laboratorium 3

1. Wizualizacja drzewa składniowego.

Wykonanie: 5/5

Ta funkcjonalność korzysta z modułu `networkx`.
Klasy wykorzystywane przy reprezentacji drzewa składniowego implementują funkcję plot.

Przykłady prostych drzew składniowych:

2. Deklarowanie typów dla zmiennych.

Wykonanie: 5/5

Kalkulator wspiera 4 typy zmiennych:

- BOOL
- STRING
- INT
- FLOAT

Testy potwierdzające:

```
TestParser
    test_variable_init
```

3. Sprawdzanie typów.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_type_control
```

4. Instrukcja przypisania.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_variable_assign
```

5. Przeciążanie operatorów.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_overload_ops
```

6. Sprawdzanie syntaktyczne deklaracji oraz syntaktyczne instrukcji.

Wykonanie: 10/10

Testy potwierdzające:

```

```

8. Konwersja typów za pomocą dodatkowego operatora.

Wykonanie: 5/5

W dalszym etapie, została zaimplementowana funkcjonalność automatycznej konwersji typów

<!-- Testy potwierdzające:

```

``` -->

9. Terminowe wgranie zadań na laboratorium.

Wykonanie: 5/5

#### SUMA: 30/30pkt

## 4. Funkcjonalność z laboratorium 4

1. Definiowanie funkcji.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_fn_definition
    test_nested
```

2. Definiowanie bloków instrukcji.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_global
```

3. Definiowanie zmiennych globalnych i lokalnych.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_global
```

4. Instrukcja wywołania funkcji.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_fn_definition
```

5. Automatyczna konwersja typów.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_conversion
```

6. Terminowe wgranie zadań na laboratorium.

Wykonanie: 5/5

#### SUMA: 30/30pkt

## 5. Funkcjonalność z laboratorium 5

1. Zagnieżdżone wywołania funkcji.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_nested
```

2. Pomijanie zbędnych instrukcji.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_unnecessary
```

3. Optymalizacja wykonania wspólnych podwyrażeń.

Wykonanie: 5/5

4. Optymalizacje algebraiczne.

Wykonanie: 5/5

Testy potwierdzające:

```
TestParser
    test_reverse_opt
    test_constant_opt
    test_algebra_opt
```

5. Przemieszczanie kodu w pętli.

Wykonanie: 0/5

Testy potwierdzające:

```

```

6. Terminowe wgranie zadań na laboratorium.

Wykonanie: 5/5

#### SUMA: 30/30pkt

## 6. Zajęcia zaliczeniowe

1. Integracja wszystkich funkcjonalności z poszczególnych laboratoriów (oprócz zadańdot. języka Markdown i html z lab 1) w jeden program.

Wykonanie: 5/5

Testy potwierdzające:

```

```

2. Dokumentacja do projektu: opis sposobu użycia języka kalkulatora.

Wykonanie: 5/5

Testy potwierdzające:

```

```

3. Dokumentacja do projektu: opis zaimplementowanych funkcjonalności.

Wykonanie: 5/5

Testy potwierdzające:

```

```

4. Dokumentacja do projektu: szczegóły implementacji.

Wykonanie: 5/5

Testy potwierdzające:

```

```

5. Dokumentacja do projektu: ograniczenia języka kalkulatora.

Wykonanie: 5/5

Testy potwierdzające:

```

```

6. Dokumentacja do projektu: przykłady użycia języka kalkulatora.

Wykonanie: 5/5

Testy potwierdzające:

```

```

7. Terminowe wgranie dokumentacji.

Wykonanie: 5/5

Testy potwierdzające:

```

```

#### SUMA: 30/30pkt

## 7. Podsumowanie

### SUMA: 30/30pkt
