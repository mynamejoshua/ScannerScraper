import subprocess
from bs4 import BeautifulSoup
import requests
import whisper


def transcribe_day(filedir, year, month, day):
    model = whisper.load_model("tiny.en")

    for h in range(0, 1): # change 1 to 24 when ready for mass download
        hour = f"{h:02d}"
        response = requests.get(f"https://scanwc.com/assets/php/archives/getfields.php?y={year}&m={month}&d={day}&h={hour}&g=undefined&f=undefined&s=undefined")

        soup = BeautifulSoup(response.content, 'html.parser')
        # print(soup)

        options = soup.find_all('option')
        last_4 = options[-4:]

        for option in last_4:
            value = option['value']
            if(len(value) < 10): continue

            print(value)


            filename = f"file_{value.replace('/', '_')}.mp3" # chatgpt told me to watch out for '/'
            url = f"https://scanwc.com/assets/php/archives/archive_download.php?id={value}"

            try:
                result = subprocess.run(["curl", url, "--output", f"{filedir}/{filename}"], capture_output=True, text=True)

                # Check if the command was successful
                if result.returncode != 0:
                    print(f"Error downloading {url}: {result.stderr}")
                else:
                    print(f"Downloaded {url} to {filename}")

                    result = model.transcribe(f"{filedir}/{filename}", word_timestamps=True, verbose=False)
                    transcription_text = result["text"]

                    with open(f"{filedir}/{year}_{month}_{day}_transcription", 'a') as file:
                        file.write(transcription_text)
                    print(f"transcribed {filename}")
                    
                    try: 
                        subprocess.run(["rm ", {filedir}/{filename}])
                        print(f"deleted {filename}")
                    except:
                        print(f"failed to delete {filedir}/{filename}")

            except Exception as e:
                print(f"An error occurred: {e}")


transcribe_day("test_day", "24", "01", "03")