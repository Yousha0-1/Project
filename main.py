import os
from datetime import datetime
from gtts import gTTS
import playsound
import speech_recognition as sr
import google.generativeai as genai
from dotenv import load_dotenv
import tkinter as tk
from PIL import Image, ImageTk

# .env dosyasındaki gizli bilgileri içe aktar
load_dotenv()
API_KEY = os.getenv("API_KEY")

genai.configure(api_key=API_KEY)

# Yapay zekaya rol tanımlama
model = genai.GenerativeModel(
    model_name="gemini-3.5-flash-lite",
    system_instruction=(
        "Sen küresel ısınma, çevre ve iklim krizi konularında uzman, son derece yardımsever ve kibar bir asistansın. "
        "Kullanıcının sorduğu dilde (Türkçe, İngilizce, Japonca, Hollandaca, Rusça vb.) en fazla 2 veya 3 cümleyle, net ve sesli okunmaya uygun akıcı cevaplar ver. "
        "Eğer kullanıcı küresel ısınma veya çevre dışı bir şey sorarsa, nazikçe sadece çevre ve iklim konularında yardımcı olabileceğini belirt."
    )
)

# Global olarak seçilen dili tutacağımız değişken
secilen_dil_kodu = "tr"
# Arka plan görsel durumu (1: art.png, 2: art2.png)
arkaplan_durumu = 1


def gecmise_kaydet(soru, cevap):
    """Kullanıcının sorusunu ve yapay zekanın cevabını zaman damgasıyla bir dosyaya kaydeder."""
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open("sohbet_gecmisi.txt", "a", encoding="utf-8") as dosya:
            dosya.write(f"[{zaman}] Soru: {soru}\n")
            dosya.write(f"[{zaman}] Cevap: {cevap}\n")
            dosya.write("-" * 60 + "\n")
    except Exception as e:
        print(f"Geçmiş kaydedilirken bir hata oluştu: {e}")


def sesli_soyle(metin, lang='tr'):
    """Metni gTTS ile MP3 ses dosyasına çevirir ve playsound ile hoparlörden okur."""
    print(f"\nAsistan: {metin}")
    try:
        tts = gTTS(text=metin, lang=lang, slow=False)
        dosya_adi = "gecici_cevap.mp3"
        tts.save(dosya_adi)
        
        playsound.playsound(dosya_adi)
        
        if os.path.exists(dosya_adi):
            os.remove(dosya_adi)
    except Exception as e:
        print(f"Seslendirme sırasında bir hata oluştu: {e}")


def yapay_zekaya_sor(soru_metni):
    """Gelen soruyu Gemini yapay zeka modeline gönderir ve cevabı döndürür."""
    print("\n🧠 Yapay zeka düşünüyor...")
    try:
        response = model.generate_content(soru_metni)
        return response.text.strip()
    except Exception as e:
        print(f"API Hatası: {e}")
        return "Üzgünüm, şu anda yapay zeka servisine bağlanırken bir sorun oluştu."


def sesli_soru_al(dil_kodu='tr-TR', sure=10):
    """Mikrofonu dinler, konuşmayı algılar ve seçilen süre boyunca (phrase_time_limit) metne çevirir."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"\n🎤 Sizi dinliyorum ({dil_kodu}) - Süre: {sure} saniye...")
        r.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = r.listen(source, timeout=6, phrase_time_limit=sure)
            soru = r.recognize_google(audio, language=dil_kodu)
            print(f"👤 Siz: '{soru}'")
            return soru
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""



# ÖZEL DİL SEÇİM EKRANI

def ozel_dil_secim_penceresi():
    secim_penceresi = tk.Tk()
    secim_penceresi.title("Dil Seçimi / Language Selection")
    secim_penceresi.geometry("450x380")
    secim_penceresi.resizable(False, False)
    secim_penceresi.configure(bg="#e8f5e9")

    secim_penceresi.update_idletasks()
    genislik = secim_penceresi.winfo_width()
    yukseklik = secim_penceresi.winfo_height()
    x = (secim_penceresi.winfo_screenwidth() // 2) - (genislik // 2)
    y = (secim_penceresi.winfo_screenheight() // 2) - (yukseklik // 2)
    secim_penceresi.geometry(f'{genislik}x{yukseklik}+{x}+{y}')

    secilen = {"deger": "tr"}

    tk.Label(secim_penceresi, text="🌍 Lütfen Bir Dil Seçin\nPlease Select a Language", font=("Arial", 13, "bold"), bg="#e8f5e9", fg="#2e7d32").pack(pady=20)

    def dil_sec(kod):
        secilen["deger"] = kod
        secim_penceresi.destroy()

    diller = [
        ("🇹🇷 Türkçe", "tr"),
        ("🇬🇧 English", "en"),
        ("🇯🇵 日本語", "ja"),
        ("🇳🇱 Nederlands", "nl"),
        ("🇷🇺 Русский", "ru")
    ]

    for yazi, kod in diller:
        btn = tk.Button(secim_penceresi, text=yazi, font=("Arial", 11, "bold"), bg="#4caf50", fg="white", width=20, pady=4, bd=0, command=lambda k=kod: dil_sec(k))
        btn.pack(pady=4)

    def uygulamadan_cik():
        secim_penceresi.destroy()
        exit()

    btn_cikis = tk.Button(secim_penceresi, text="❌ Çıkış / Exit", font=("Arial", 10, "bold"), bg="#c0392b", fg="white", width=20, pady=3, bd=0, command=uygulamadan_cik)
    btn_cikis.pack(pady=10)

    secim_penceresi.mainloop()
    return secilen["deger"]



#  ÖZEL VE DİLE DUYARLI KONUŞMA SÜRESİ PENCERESİ

def sure_secim_penceresi(dil_kodu):
    sure_penceresi = tk.Toplevel()
    sure_penceresi.geometry("400x350")
    sure_penceresi.resizable(False, False)
    sure_penceresi.configure(bg="#e8f8f5")
    sure_penceresi.grab_set()

    sure_penceresi.update_idletasks()
    w = sure_penceresi.winfo_width()
    h = sure_penceresi.winfo_height()
    x = (sure_penceresi.winfo_screenwidth() // 2) - (w // 2)
    y = (sure_penceresi.winfo_screenheight() // 2) - (h // 2)
    sure_penceresi.geometry(f'{w}x{h}+{x}+{y}')

    sure_metinleri = {
        "en": {"baslik": "Listening Duration", "soru": "Please select microphone duration:", "sn": "Seconds", "iptal": "❌ Cancel"},
        "ja": {"baslik": "録音時間の設定", "soru": "マイクの録音時間を選択してください:", "sn": "秒", "iptal": "❌ キャンセル"},
        "nl": {"baslik": "Luisterduur", "soru": "Selecteer microfoontijd:", "sn": "Seconden", "iptal": "❌ Annuleren"},
        "ru": {"baslik": "Время записи", "soru": "Выберите время записи микрофона:", "sn": "Секунд", "iptal": "❌ Отмена"},
        "tr": {"baslik": "Dinleme Süresi", "soru": "Lütfen Dinleme Süresini Seçin:", "sn": "Saniye", "iptal": "❌ İptal"}
    }

    aktif_metin = sure_metinleri.get(dil_kodu, sure_metinleri["tr"])
    sure_penceresi.title(aktif_metin["baslik"])

    tk.Label(sure_penceresi, text=aktif_metin["soru"], font=("Arial", 11, "bold"), bg="#e8f8f5", fg="#16a085").pack(pady=20)

    secilen_sure = {"deger": None}

    def sure_sec(saniye):
        secilen_sure["deger"] = saniye
        sure_penceresi.destroy()

    def iptal_et():
        secilen_sure["deger"] = None
        sure_penceresi.destroy()

    for sn in [5, 10, 15, 20]:
        btn = tk.Button(sure_penceresi, text=f"{sn} {aktif_metin['sn']}", font=("Arial", 11, "bold"), bg="#1abc9c", fg="white", width=22, pady=4, bd=0, command=lambda s=sn: sure_sec(s))
        btn.pack(pady=4)

    btn_iptal = tk.Button(sure_penceresi, text=aktif_metin["iptal"], font=("Arial", 10, "bold"), bg="#7f8c8d", fg="white", width=22, pady=3, bd=0, command=iptal_et)
    btn_iptal.pack(pady=8)

    sure_penceresi.wait_window()
    return secilen_sure["deger"]



# ÖZEL YAZILI SORU PENCERESİ

def ozel_yazi_penceresi(baslik, soru_metni_txt):
    yazi_penceresi = tk.Toplevel()
    yazi_penceresi.title(baslik)
    yazi_penceresi.geometry("450x220")
    yazi_penceresi.resizable(False, False)
    yazi_penceresi.configure(bg="#e1f5fe")
    yazi_penceresi.grab_set()

    yazi_penceresi.update_idletasks()
    w = yazi_penceresi.winfo_width()
    h = yazi_penceresi.winfo_height()
    x = (yazi_penceresi.winfo_screenwidth() // 2) - (w // 2)
    y = (yazi_penceresi.winfo_screenheight() // 2) - (h // 2)
    yazi_penceresi.geometry(f'{w}x{h}+{x}+{y}')

    tk.Label(yazi_penceresi, text=soru_metni_txt, font=("Arial", 11, "bold"), bg="#e1f5fe", fg="#01579b").pack(pady=15)

    giris_kutusu = tk.Entry(yazi_penceresi, font=("Arial", 12), width=35, relief="solid", bd=1)
    giris_kutusu.pack(pady=10)
    giris_kutusu.focus()

    sonuc = {"metin": None}

    def gonder():
        sonuc["metin"] = giris_kutusu.get().strip()
        yazi_penceresi.destroy()

    btn_gonder = tk.Button(yazi_penceresi, text="Gönder / Send", font=("Arial", 11, "bold"), bg="#0277bd", fg="white", padx=15, pady=5, bd=0, command=gonder)
    btn_gonder.pack(pady=10)

    yazi_penceresi.wait_window()
    return sonuc["metin"]


# SOHBET GEÇMİŞİ PENCERESİ
def gecmis_penceresi_ac(baslik):
    gecmis_penceresi = tk.Toplevel()
    gecmis_penceresi.title(baslik)
    gecmis_penceresi.geometry("600x450")
    gecmis_penceresi.configure(bg="#f4f6f7")
    gecmis_penceresi.grab_set()

    gecmis_penceresi.update_idletasks()
    w = gecmis_penceresi.winfo_width()
    h = gecmis_penceresi.winfo_height()
    x = (gecmis_penceresi.winfo_screenwidth() // 2) - (w // 2)
    y = (gecmis_penceresi.winfo_screenheight() // 2) - (h // 2)
    gecmis_penceresi.geometry(f'{w}x{h}+{x}+{y}')

    tk.Label(gecmis_penceresi, text=baslik, font=("Arial", 13, "bold"), bg="#f4f6f7", fg="#2c3e50").pack(pady=10)

    text_frame = tk.Frame(gecmis_penceresi)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_box = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=("Consolas", 10), bg="#ffffff", fg="#333333")
    text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_box.yview)

    try:
        if os.path.exists("sohbet_gecmisi.txt"):
            with open("sohbet_gecmisi.txt", "r", encoding="utf-8") as dosya:
                icerik = dosya.read()
                if icerik.strip() == "":
                    text_box.insert(tk.END, "Henüz kaydedilmiş bir sohbet geçmişi yok.")
                else:
                    text_box.insert(tk.END, icerik)
        else:
            text_box.insert(tk.END, "sohbet_gecmisi.txt dosyası henüz oluşturulmadı.")
    except Exception as e:
        text_box.insert(tk.END, f"Geçmiş okunurken hata oluştu: {e}")

    text_box.config(state=tk.DISABLED)

    btn_kapat = tk.Button(gecmis_penceresi, text="Kapat / Close", font=("Arial", 11, "bold"), bg="#7f8c8d", fg="white", padx=15, pady=5, bd=0, command=gecmis_penceresi.destroy)
    btn_kapat.pack(pady=10)


# ==========================================
# ANA ARAYÜZ BÖLÜMÜ
# ==========================================

def arayuz_baslat():
    global secilen_dil_kodu
    
    secilen_dil_kodu = ozel_dil_secim_penceresi()

    pencere = tk.Tk()
    pencere.title("Küresel Isınma ve Çevre Asistanı")
    
    pencere.attributes('-fullscreen', True)
    pencere.bind("<Escape>", lambda event: pencere.attributes('-fullscreen', False))

    ekran_genislik = pencere.winfo_screenwidth()
    ekran_yukseklik = pencere.winfo_screenheight()

    bg_label = tk.Label(pencere)
    bg_label.place(relwidth=1, relheight=1)

    #  art.png ve art2.png arasında geçiş yapacak tıklama fonksiyonu
    def arka_plani_degistir(event=None):
        global arkaplan_durumu
        try:
            if arkaplan_durumu == 1:
                dosya_adi = "art2.png"
                arkaplan_durumu = 2
            else:
                dosya_adi = "art.png"
                arkaplan_durumu = 1

            pil_image = Image.open(dosya_adi)
            pil_image = pil_image.resize((ekran_genislik, ekran_yukseklik), Image.Resampling.LANCZOS)
            bg_image = ImageTk.PhotoImage(pil_image)
            
            bg_label.config(image=bg_image)
            bg_label.image = bg_image
        except Exception as e:
            print(f"Görsel değiştirilirken hata oluştu: {e}")

    try:
        pil_image = Image.open("art.png")
        pil_image = pil_image.resize((ekran_genislik, ekran_yukseklik), Image.Resampling.LANCZOS)
        bg_image = ImageTk.PhotoImage(pil_image)
        
        bg_label.config(image=bg_image)
        bg_label.image = bg_image
    except Exception as e:
        print(f"Resim yüklenirken hata oluştu: {e}")
        bg_label.config(bg="#e0f2f1")

    # Arka plana (karaktere) tıklandığında görseli değiştirme bağlayıcısı
    bg_label.bind("<Button-1>", arka_plani_degistir)

    # Dil Sözlüğü
    metinler = {
        "en": {
            "kod": "en-US", "tts": "en",
            "hosgeldin": "Hello! I am your climate change and environment assistant.",
            "konus": "🎙️ Speak", "yaz": "⌨️ Type", "durdur": "🛑 Stop", "gecmis": "📜 History", "dil": "🌐 Language", "cikis": "❌ Exit",
            "dinleniyor": "Listening, please speak...",
            "yaz_baslik": "Text Input", "yaz_soru": "Type your question about climate or environment:",
            "gecmis_baslik": "Chat History",
            "durdu": "🛑 Operation stopped. You can ask a new question.",
            "iptal_mesaji": "❌ İşlem iptal edildi."
        },
        "ja": {
            "kod": "ja-JP", "tts": "ja",
            "hosgeldin": "こんにちは！地球温暖化と環境のアシスタントです。",
            "konus": "🎙️ 話す", "yaz": "⌨️ 入力", "durdur": "🛑 停止", "gecmis": "📜 履歴", "dil": "🌐 言語切替", "cikis": "❌ 終了",
            "dinleniyor": "聞いています、どうぞお話ください...",
            "yaz_baslik": "テキスト入力", "yaz_soru": "気候や環境に関する質問を入力してください:",
            "gecmis_baslik": "チャット履歴",
            "durdu": "🛑 操作が停止しました。新しい質問をどうぞ。",
            "iptal_mesaji": "❌ 操作がキャンセルされました。"
        },
        "nl": {
            "kod": "nl-NL", "tts": "nl",
            "hosgeldin": "Hallo! Ik ben je assistent voor klimaatverandering en milieu.",
            "konus": "🎙️ Spreken", "yaz": "⌨️ Typen", "durdur": "🛑 Stop", "gecmis": "📜 Geschiedenis", "dil": "🌐 Taal", "cikis": "❌ Afsluiten",
            "dinleniyor": "Luisteren, praat alstublieft...",
            "yaz_baslik": "Tekstinvoer", "yaz_soru": "Typ je vraag over klimaat of milieu:",
            "gecmis_baslik": "Chatgeschiedenis",
            "durdu": "🛑 Bewerking gestopt. Je kunt een nieuwe vraag stellen.",
            "iptal_mesaji": "❌ Bewerking geannuleerd."
        },
        "ru": {
            "kod": "ru-RU", "tts": "ru",
            "hosgeldin": "Здравствуйте! Я ваш помощник по вопросам изменения климата.",
            "konus": "🎙️ Говорить", "yaz": "⌨️ Написать", "durdur": "🛑 Стоп", "gecmis": "📜 История", "dil": "🌐 Язык", "cikis": "❌ Выход",
            "dinleniyor": "Слушаю вас, говорите...",
            "yaz_baslik": "Текстовый ввод", "yaz_soru": "Введите ваш вопрос об экологии или климате:",
            "gecmis_baslik": "История чата",
            "durdu": "🛑 Операция остановлена. Вы можете задать новый вопрос.",
            "iptal_mesaji": "❌ Операция отменена."
        },
        "tr": {
            "kod": "tr-TR", "tts": "tr",
            "hosgeldin": "Merhaba! Ben küresel ısınma ve çevre asistanınızım.",
            "konus": "🎙️ Konuş", "yaz": "⌨️ Yazarak Sor", "durdur": "🛑 Durdur", "gecmis": "📜 Geçmiş", "dil": "🌐 Dil Değiştir", "cikis": "❌ Çıkış",
            "dinleniyor": "Dinleniyor, konuşabilirsiniz...",
            "yaz_baslik": "Yazılı Soru Sor", "yaz_soru": "İklim krizi veya çevre ile ilgili sorunuzu yazın:",
            "gecmis_baslik": "Sohbet Geçmişi",
            "durdu": "🛑 İşlem durduruldu. Yeni bir soru sormak için butonları kullanabilirsiniz.",
            "iptal_mesaji": "❌ İşlem iptal edildi."
        }
    }

    secilen_dil = metinler.get(secilen_dil_kodu, metinler["tr"])

    durum_etiketi = tk.Label(
        pencere, 
        text=secilen_dil["hosgeldin"], 
        font=("Arial", 14, "bold"), 
        bg="#eaf4f4",           
        fg="#1b5e20",           
        padx=15, pady=8,
        wraplength=ekran_genislik - 150,  
        justify="center"
    )
    durum_etiketi.pack(pady=30)

    def konus_tikla():
        secilen_sure = sure_secim_penceresi(secilen_dil_kodu)
        
        if secilen_sure is None:
            durum_etiketi.config(text=secilen_dil["iptal_mesaji"])
            pencere.update()
            return
        
        durum_etiketi.config(text=f"🎤 {secilen_dil['dinleniyor']} ({secilen_sure} sn)")
        pencere.update()
        
        soru = sesli_soru_al(secilen_dil["kod"], sure=secilen_sure)
        if soru:
            durum_etiketi.config(text=f"Siz / You: {soru}")
            pencere.update()
            cevap = yapay_zekaya_sor(soru)
            gecmise_kaydet(soru, cevap)
            durum_etiketi.config(text=f"Asistan / Assistant: {cevap}")
            pencere.update()
            sesli_soyle(cevap, lang=secilen_dil["tts"])
        else:
            durum_etiketi.config(text="⚠️ Ses algılanamadı veya işlem sürdürülmedi.")

    def yazarak_sor_tikla():
        soru = ozel_yazi_penceresi(secilen_dil["yaz_baslik"], secilen_dil["yaz_soru"])
        if soru:
            durum_etiketi.config(text=f"Siz (Yazılı) / You: {soru}")
            pencere.update()
            cevap = yapay_zekaya_sor(soru)
            gecmise_kaydet(soru, cevap)
            durum_etiketi.config(text=f"Asistan / Assistant: {cevap}")
            pencere.update()
            sesli_soyle(cevap, lang=secilen_dil["tts"])

    def gecmisi_goster():
        gecmis_penceresi_ac(secilen_dil["gecmis_baslik"])

    def durdur_veya_sifirla():
        durum_etiketi.config(text=secilen_dil["durdu"])
        pencere.update()

    def dil_degistir():
        pencere.destroy()
        arayuz_baslat()

    def uygulamadan_cikis():
        pencere.destroy()
        exit()

    # Buton çerçevesi
    buton_cercevesi = tk.Frame(pencere, bg="")
    buton_cercevesi.pack(side=tk.BOTTOM, pady=40)

    btn_konus = tk.Button(buton_cercevesi, text=secilen_dil["konus"], font=("Arial", 11, "bold"), bg="#2e7d32", fg="white", padx=12, pady=6, bd=0, command=konus_tikla)
    btn_konus.pack(side=tk.LEFT, padx=5)

    btn_yaz = tk.Button(buton_cercevesi, text=secilen_dil["yaz"], font=("Arial", 11, "bold"), bg="#0277bd", fg="white", padx=12, pady=6, bd=0, command=yazarak_sor_tikla)
    btn_yaz.pack(side=tk.LEFT, padx=5)

    btn_gecmis = tk.Button(buton_cercevesi, text=secilen_dil["gecmis"], font=("Arial", 11, "bold"), bg="#d35400", fg="white", padx=12, pady=6, bd=0, command=gecmisi_goster)
    btn_gecmis.pack(side=tk.LEFT, padx=5)

    btn_durdur = tk.Button(buton_cercevesi, text=secilen_dil["durdur"], font=("Arial", 11, "bold"), bg="#c62828", fg="white", padx=12, pady=6, bd=0, command=durdur_veya_sifirla)
    btn_durdur.pack(side=tk.LEFT, padx=5)

    btn_dil = tk.Button(buton_cercevesi, text=secilen_dil["dil"], font=("Arial", 11, "bold"), bg="#6d4c41", fg="white", padx=12, pady=6, bd=0, command=dil_degistir)
    btn_dil.pack(side=tk.LEFT, padx=5)

    btn_cikis = tk.Button(buton_cercevesi, text=secilen_dil["cikis"], font=("Arial", 11, "bold"), bg="#c0392b", fg="white", padx=12, pady=6, bd=0, command=uygulamadan_cikis)
    btn_cikis.pack(side=tk.LEFT, padx=5)

    sesli_soyle(secilen_dil["hosgeldin"], lang=secilen_dil["tts"])

    pencere.mainloop()


if __name__ == "__main__":
    arayuz_baslat()