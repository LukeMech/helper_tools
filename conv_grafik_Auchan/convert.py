import csv
from datetime import datetime
from icalendar import Calendar, Event
import sys

def convert_grafik_to_ics(input_file, target_name, output_file="moj_grafik.ics"):
    print(f"--- START: Przetwarzanie dla '{target_name}' ---")
    cal = Calendar()
    cal.add('prodid', '-//Grafik Converter//PL//')
    cal.add('version', '2.0')

    target_name = target_name.strip().lower()
    
    # Próba odczytu z różnymi kodowaniami (ważne dla polskich znaków)
    content = None
    for enc in ['utf-8', 'cp1250', 'iso-8859-2']:
        try:
            with open(input_file, mode='r', encoding=enc) as f:
                content = f.read()
                print(f"Log: Otwarto plik używając kodowania {enc}")
                break
        except:
            continue
    
    if not content:
        print("BŁĄD: Nie udało się otworzyć pliku. Sprawdź czy ścieżka jest poprawna.")
        return

    delimiter = ';' if ';' in content[:500] else ','
    lines = content.splitlines()
    reader = list(csv.reader(lines, delimiter=delimiter))

    all_rows = [[c.strip() for c in r] for r in reader if any(r)]
    date_blocks = []
    
    # 1. Mapowanie dat
    for idx, row in enumerate(all_rows):
        date_count = sum(1 for c in row if '.' in c and len(c) >= 8)
        if date_count > 3:
            try:
                d_map = {i: datetime.strptime(c, "%d.%m.%Y") for i, c in enumerate(row) if '.' in c}
                date_blocks.append((idx, d_map))
                print(f"Log: Znaleziono blok dat w wierszu {idx}")
            except:
                continue

    if not date_blocks:
        print("BŁĄD: Nie znaleziono żadnych dat w pliku! Sprawdź czy format daty to DD.MM.YYYY")
        return

    processed_entries = set()

    # 2. Analiza wierszy
    for row_idx, row in enumerate(all_rows):
        if not row: continue
        label = row[0].lower()
        
        # Sprawdzamy czy Twoje nazwisko jest w ogóle w tym wierszu
        if not any(target_name in cell.lower() for cell in row):
            continue

        h_start, h_end, shift_tag = None, None, ""

        if "1 zmiana" in label:
            h_start, h_end, shift_tag = 6, 14, "Z1"
        elif "2 zmiana" in label:
            h_start, h_end, shift_tag = 14, 22, "Z2"
        else:
            # LOGIKA REZERWY: Szukamy najbliższej kotwicy Z1 (dół) lub Z2 (góra)
            dist_z1 = 999
            dist_z2 = 999
            
            # Szukamy Z1 w dół (max 10 wierszy)
            for i in range(row_idx + 1, min(row_idx + 10, len(all_rows))):
                if "1 zmiana" in all_rows[i][0].lower():
                    dist_z1 = i - row_idx
                    break
            
            # Szukamy Z2 w górę (max 10 wierszy)
            for i in range(row_idx - 1, max(0, row_idx - 10), -1):
                if "2 zmiana" in all_rows[i][0].lower():
                    dist_z2 = row_idx - i
                    break

            # Wybieramy to co bliżej
            if dist_z1 < dist_z2:
                h_start, h_end, shift_tag = 6, 14, "REZERWA Z1"
            elif dist_z2 != 999:
                h_start, h_end, shift_tag = 14, 22, "REZERWA Z2"
            else:
                continue # Nie znaleziono kontekstu zmiany

        # Szukamy najbliższego nagłówka dat
        closest_dates = None
        min_dist = 999
        for b_idx, d_map in date_blocks:
            dist = row_idx - b_idx
            if -5 < dist < 35: # Rozszerzony zakres
                if abs(dist) < min_dist:
                    min_dist = abs(dist)
                    closest_dates = d_map
        
        if not closest_dates:
            continue

        # Dodawanie do kalendarza
        for col_idx, dt in closest_dates.items():
            if col_idx < len(row) and target_name in row[col_idx].lower():
                entry_id = (dt.date(), h_start)
                if entry_id in processed_entries: continue

                event = Event()
                prefix = "REZERWA: " if "REZERWA" in shift_tag else ""
                event.add('summary', f"{prefix}Praca Auchan ({shift_tag.replace('REZERWA ', '')})")
                event.add('dtstart', dt.replace(hour=h_start, minute=0))
                event.add('dtend', dt.replace(hour=h_end, minute=0))
                event.add('dtstamp', datetime.now())
                
                cal.add_component(event)
                processed_entries.add(entry_id)
                print(f"DODANO: {dt.strftime('%d.%m.%Y')} - {shift_tag}")

    with open(output_file, 'wb') as f:
        f.write(cal.to_ical())
    print(f"--- SUKCES: Wygenerowano {len(processed_entries)} wpisów w {output_file} ---")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Użycie: python main.py plik.csv 'Imię Nazwisko'")
    else:
        convert_grafik_to_ics(sys.argv[1], sys.argv[2])