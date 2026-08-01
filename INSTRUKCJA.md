# Instrukcja Obsługi Przepiśnika

Ten plik zawiera krótki przewodnik krok po kroku po architekturze Twojego Przepiśnika.

---

## 1. Jak to wszystko działa?

Twój Przepiśnik składa się z trzech głównych elementów:
1. **Wygląd i logika strony (HTML, CSS, JS):** pliki `index.html`, `style.css` oraz `app.js` na Twoim laptopie. Odpowiadają za interfejs, wyszukiwarkę i podział na kategorie.
2. **Baza danych (recipes.json):** plik tekstowy przechowujący wszystkie Twoje przepisy, składniki, kroki oraz ścieżki do zdjęć.
3. **Serwer lokalny (server.py):** program uruchomiony w tle na Twoim Macu, który obsługuje zapisywanie zmian i wgrywanie zdjęć.

Dzięki temu podziałowi edycję robisz w prywatnym panelu na laptopie (`localhost:8000`), a strona w sieci (`netlify.app`) jest w pełni bezpieczna i nikt inny nie może modyfikować Twoich przepisów.

---

## 2. Codzienna praca (Dodawanie i edycja przepisów)

### Krok 1: Edycja lokalna
Otwórz w przeglądarce na laptopie adres:
👉 **http://localhost:8000/**

Tutaj masz pełne uprawnienia administratora. Zobaczysz czerwony przycisk **„Dodaj Przepis”** oraz ikony edycji i usuwania na kartach dań.

### Krok 2: Używanie filtrów w przepisie (Diety, Szybkość, Pora roku)
W formularzu tworzenia i edycji przepisu znajdziesz trzy rozwijane listy wielokrotnego wyboru:
- **Typ diety**
- **Szybkość przygotowania**
- **Pora roku**

Te opcje są generowane **dynamicznie** na podstawie filtrów, które ustawiasz w panelu bocznym strony. Możesz zaznaczyć dowolną liczbę filtrów dla jednego przepisu. Wybrane filtry wyświetlą się jako estetyczne etykiety (np. `🌱 Wege`, `⏱️ do 30 minut`) w lewej kolumnie przepisu bezpośrednio nad składnikami!

### Krok 3: Grupowanie składników na sekcje (np. Ciasto i Lukier)
Podczas wpisywania składników w formularzu możesz wydzielać osobne sekcje (nagłówki). 
- Aby dodać nagłówek sekcji, wpisz linijkę zaczynającą się od znaku gwiazdki `*`, np. `* Ciasto` lub `* Lukier`.
- Wszystkie kolejne linijki pod tym nagłówkiem będą traktowane jako składniki w tej sekcji.
- W trybie gotowania nagłówki te zostaną wyświetlone jako ładne, pogrubione czerwone napisy bez checkboxów, dzieląc listę na czytelne części.

### Krok 4: Wgrywanie zdjęć
Gdy dodajesz lub zmieniasz przepis i wybierzesz plik zdjęcia z komputera:
- Zdjęcie zostanie automatycznie zapisane w folderze `/images/` wewnątrz projektu na dysku.
- Przycisk zapisu zmieni się na **„Wgrywanie zdjęcia do chmury...”** i zablokuje się. Gdy wgrywanie dobiegnie końca, przycisk odblokuje się automatycznie.

### Krok 5: Publikacja w sieci
Kiedy skończysz edycję, kliknij przycisk **`🚀 Opublikuj w sieci`** w prawym górnym rogu. Serwer w tle:
1. Doda nowe przepisy do `recipes.json`.
2. Doda nowe pliki zdjęć z folderu `/images/`.
3. Wyśle całość (commit & push) do Twojego schowka na **GitHubie**.
4. Serwer **Netlify** automatycznie wykryje zmianę na GitHubie i przebuduje Twoją stronę **gabbyscookbookk.netlify.app** w około 30 sekund!

---

## 3. Rozwiązywanie problemów (Gdy coś nie działa)

### Nie widzę nowych zdjęć lub przepisów na telefonie
Przeglądarka w telefonie zapisała w pamięci (keszu) stary stan witryny. 
- Odśwież stronę na telefonie, zamknij i otwórz kartę ponownie, lub otwórz stronę w **karcie prywatnej/incognito**.
- Zabezpieczyliśmy to za pomocą systemu query-strings (`v=5.6` i timestamp), co drastycznie ogranicza ten problem w przyszłości.

### Strona http://localhost:8000/ nie chce się załadować
Oznacza to, że Twój lokalny serwer na Macu został wyłączony (np. po restarcie komputera). Uruchom go ponownie, pisząc na czacie z asystentem Antigravity prośbę o restart serwera.
