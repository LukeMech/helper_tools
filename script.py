import os
import sys
import subprocess
import urllib.request

def process_file(url, audio_bit, vid_quality, output_name, vfr_enabled):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    req = urllib.request.Request(url, headers=headers)
    input_file =  f"{output_name}.in"
    output_dir = "out"
    
    os.makedirs(output_dir, exist_ok=True)
    # Pobierz rozmiar pliku
    with urllib.request.urlopen(req) as response:
        total_size = int(response.getheader('Content-Length').strip())
        bytes_downloaded = 0
        chunk_size = 1024  # Rozmiar fragmentu
        last_percent_reported = 0  # Do śledzenia ostatniego pokazanego procentu

        # Otwórz plik do zapisu
        with open(input_file, 'wb') as f:
            while True:
                # Odczytaj fragmenty danych
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                bytes_downloaded += len(chunk)
                
                # Oblicz aktualny procent pobranego pliku
                percent_downloaded = bytes_downloaded / total_size * 100

                # Wyświetl postęp tylko co 1%
                if int(percent_downloaded) >= last_percent_reported + 1:
                    last_percent_reported = int(percent_downloaded)
                    print(f"Pobrano: {bytes_downloaded} / {total_size} bajtów ({percent_downloaded:.2f}%)", flush=True)
                    
    print(f"\nPobrano plik: {input_file}", flush=True)
        
    # Wyciągnij nazwę pliku bez rozszerzenia
    file_name_without_ext = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_dir, f"{file_name_without_ext}.mp4")  # Wynikowy plik w formacie .mp4

    # Wykonaj konwersję wideo za pomocą ffmpeg
    print(f"Processing {input_file}...", flush=True)
    
    # Podstawowa komenda ffmpeg
    ffmpeg_command = ['ffmpeg', '-i', input_file, '-c:v', 'libx264', 
                      '-preset', 'veryslow', '-crf', vid_quality, 
                      '-c:a', 'aac', '-b:a', audio_bit]

    # Warunek dodający flagę VFR
    if vfr_enabled:
        ffmpeg_command.extend(['-vsync', 'vfr'])

    # Dodaj output file na końcu i uruchom
    ffmpeg_command.append(output_file)
    subprocess.run(ffmpeg_command)
    
    print(f"Processed file saved as: {output_file}", flush=True)
    return output_file  # Zwróć ścieżkę do pliku wyjściowego

# Pobieranie danych wejściowych z linii poleceń
if __name__ == "__main__":
    d_url = sys.argv[1]  # URL podany przez użytkownika
    a_bit = sys.argv[2]  # Bitrate audio podany przez użytkownika
    vid_q = sys.argv[3]  # Jakość wideo podana przez użytkownika
    out_n = sys.argv[4]  # Nazwa pliku wyjściowego
    vfr_e = sys.argv[5].lower() == 'true' # Włączenie vfr
        
    # Uruchom przetwarzanie pliku
    process_file(d_url, a_bit, vid_q, out_n, vfr_e)