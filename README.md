# Klasyfikacja Statusu Życia u Pacjentek z Rakiem Piersi

### Opis Projektu  
Projekt dotyczy analizy danych pacjentek z rakiem piersi w celu identyfikacji czynników wpływających na przeżywalność i rokowania. Celem jest stworzenie modelu do klasyfikacji stanu zdrowia pacjentek (żyje/zmarła) na podstawie danych klinicznych i histopatologicznych.

### Problemy do Rozwiązania  
1. Jakie cechy kliniczne i demograficzne mają największy wpływ dla przewidywania przeżywalności pacjentki?
2. Czy można przewidzieć status pacjentki (żywa/zmarła) na podstawie dostępnych danych?
3. Jakie wzorce można zaobserwować w danych demograficznych i ich wpływie na wyniki leczenia?  

### Źródło Danych
Zestaw danych: "Breast Cancer" 
Link: https://www.kaggle.com/datasets/reihanenamdari/breast-cancer/data

### Dane
Zbiór danych obejmuje 4024 rekordy zawierające informacje demograficzne, kliniczne i histopatologiczne. Kluczowe zmienne:
- Dane podstawowe (wiek, pochodzenie etniczne, stan cywilny).
- Informacje techniczne o guzie i węzłach chłonnych (stopień zaawansowania, wielkość guza, zróżnicowanie histopatologiczne).
- Aktualny Status Pacjentki (żyje/zmarła).

### Charakterystyka Danych  

| **Atrybut**               | **Opis**                                                                |
|---------------------------|-------------------------------------------------------------------------|
| `Age`                     | Wiek pacjentki.                                                         |
| `Race`                    | Pochodzenie etniczne pacjentki.                                         |
| `Marital Status`          | Stan cywilny pacjentki.                                                 |
| `T Stage`                 | Stopień zaawansowania guza pierwotnego.                                 |
| `N Stage`                 | Stopień zaawansowania nowotworu w węzłach chłonnych.                    |
| `6th Stage`               | Klasyfikacja zaawansowania raka (wg. 6 stopnia AJCC).                   |
| `Differentiate`           | Stopień zróżnicowania histopatologicznego (np. dobrze, średnio, słabo). |
| `Grade`                   | Stopień złośliwości raka.                                               |
| `A Stage`                 | Lokalizacja i rozprzestrzenienie guza: (lokalny/przerzuty).             |
| `Tumor Size`              | Wielkość guza (mm).                                                     |
| `Estrogen Status`         | Status receptorów estrogenowych (pozytywny/negatywny).                  |
| `Progesterone Status`     | Status receptorów progesteronowych (pozytywny/negatywny).               |
| `Regional Node Examined`  | Liczba węzłów chłonnych zbadanych podczas diagnozy lub leczenia.        |
| `Regional Node Positive`  | Liczba węzłów chłonnych z potwierdzoną obecnością komórek nowotworowych |
| `Survival Months`         | Czas przeżycia od momentu wykrycia (miesiące).                          |
| `Status`                  | Aktualny status pacjentki (żyje/zmarła).                                |

### Uzasadnienie Wyboru Zbioru Danych
Zbiór danych jest kompleksowy, zawiera zarówno informacje kliniczne, jak i histopatologiczne. Dzięki temu umożliwia budowę precyzyjnego modelu klasyfikacyjnego, który może wspierać procesy decyzyjne w onkologii.

### Cele Projektu  
1. Zidentyfikowanie kluczowych czynników wpływających na status życia pacjentek.  
2. Stworzenie modeli klasyfikacyjnych do przewidywania statusu życia pacjentek.  
3. Prognozowanie czasu przeżycia na podstawie danych klinicznych.  

### Struktura Projektu  
1. **Wstępna Analiza Danych**:  
   - Importowanie i wstępna obróbka danych.  
   - Analiza statystyczna i wizualizacja kluczowych cech związanych ze stanem pacjentek (np. wiek, stopień zaawansowania guza, liczba zaatakowanych węzłów chłonnych).  
2. **Przygotowanie Danych**:  
   - Uzupełnianie brakujących lub usunięcie powtarzalnych danych.
   - Skalowanie danych liczbowych oraz kodowanie zmiennych kategorycznych.  
   - Podział danych na zestaw treningowy (70%) i testowy (30%).
3. **Wybór i Budowa Modelu**:
   - Testowanie różnych algorytmów uczenia maszynowego, takich jak: Regresja logistyczna, Drzewa Decyzyjne, Lasy Losowe, SVM.  
4. **Uczenie Modelu**:
   - Trenowanie wybranych algorytmów na zestawie treningowym.
   - Obliczanie podstawowych metryk skuteczności, takich jak: Dokładność, Precyzja, Czułość, Miara F1
5. **Walidacja i Testowanie Modelu**:
   - Ocena wyników i porównanie skuteczności modelów.
   - Wybranie najlepszego modelu na podstawie uzyskanych wyników.
6. **Optymalizacja Modelu**: 
   - Optymalizacja hiperparametrów wybranego modelu przy użyciu: Grid Search, Random Search.
7. **Analiza Wyników i Wnioski**: 
   - Identyfikacja kluczowych czynników wpływających na status pacjentek (żyje/zmarła).
   - Wyciągnięcie wniosków na podstawie wyników oraz znaczenia cech w modelu.
8. **Prezentacja i Raport Końcowy**:
   - Przygotowanie raportu z wizualizacjami wyników analizy i predykcji.

### Opis Modelu
Do rozwiązania problemu klasyfikacji statusu życia pacjentek z rakiem piersi, wybrano model **RandomForestClassifier**.

**Dlaczego wybrano RandomForestClassifier?**
- **Wysoka skuteczność**: Model osiągnął dokładność wynoszącą 0.9141, co czyni go bardzo efektywnym w przewidywaniu statusu pacjentek.
- **Odporność na przeuczenie**: RandomForest jest odporny na przeuczenie dzięki losowemu doborowi próbek oraz cech, co pozwala na lepszą generalizację wyników.
- **Elastyczność**: Mechanizm łączenia wielu drzew decyzyjnych umożliwia analizę nieliniowych zależności w danych, co zwiększa dokładność prognoz.
- **Parametry wybrane przez TPOT**:
  - `bootstrap=False`
  - `criterion=entropy`
  - `max_features=0.9`
  - `min_samples_leaf=16`
  - `min_samples_split=3`
  - `n_estimators=100`

### Instrukcje Użytkowania
#### Jak pobrać aplikację:

1. **Pobranie repozytorium:**
   Aplikacje pobierz za pomocą komendy:
   ```bash
   git clone https://github.com/PJATK-ASI-2024/s25098_Breast-Cancer-Classifier.git
2. **Zbudowanie obrazu Dockera:**
   Z katalogu głównego aplikacji, uruchom poniższą komende, która zbuduje obraz Dockera i wszystkie potrzebne kontenery:
   ```bash
   docker-compose up --build
3. **Korzystanie z modelu**
   Po uruchomieniu kontenera, aplikacja jest dostępna pod adresem http://localhost:5000.
   Aby sklasyfikować dane wejściowe, wyślij zapytanie POST do aplikacji:
   ```bash
   curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d '{
   "Age": 61,
   "Race": "White",
   "Marital Status": "Married",
   "T Stage": "T2",
   "N Stage": "N1",
   "6th Stage": "IIB",
   "differentiate": "Poorly differentiated",
   "Grade": 3,
   "Tumor Size": 26,
   "Progesterone Status": "Positive",
   "Regional Node Examined": 11,
   "Reginol Node Positive": 2,
   "Survival Months": 172
   }'
