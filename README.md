# ASMC 1-3 (Advanced StackMatch Controller)

ASMC 1-3 je napredni mikrokontrolerski sustav za upravljanje i preklapanje triju visokofrekventnih (HF) antena u StackMatch konfiguraciji (TOP-A, MID-B, BOT-C). Sustav se sastoji od **Arduino Nano** mikrokontrolera koji izvršava logiku preklapanja u realnom vremenu te **Python (Tkinter) GUI** aplikacije za daljinsko upravljanje i nadzor putem serijske (USB) veze.

---

## 🚀 Glavne Značajke

- **Standardna BCC Matrix Logika:** Podrška za rad s pojedinačnim antenama (A, B, C), kombinacijama po dvije (A+B, A+C, B+C) ili svim tri antene istovremeno (A+B+C).
- **Invertirani NC Relejni Izlazi:** Zbog zaštite i specifičnog ožičenja, releji u unpowered (NC) stanju po defaultu spajaju sve antene zajedno.
- **Dual PTT Optokaplerski Ulaz (PC817):** Podrška za HIGH i LOW PTT okidanje s ugrađenim PTT Interlockom i tail-delay zaštitom.
- **Fleksibilni RX/TX Načini Rada:** Podrška za ekskluzivni (EXCL) i fleksibilni (FLEX) RX način preklapanja.
- **Dvosmjerna Serial Komunikacija:** Automatsko usklađivanje stanja između fizičkih tipki na uređaju i Python GUI sučelja.
- **Watchdog Timer (WDT):** Automatsko resetiranje kontrolera u slučaju zastoja.

---

## 📌 Popis Arduino Nano Pinova

| Pin na Arduinu | Tip Pina | Funkcija / Opis |
| :--- | :--- | :--- |
| **D2** | Izlaz | `RELAY_1` (Upravljanje relejem 1) |
| **D3** | Izlaz | `RELAY_2` (Upravljanje relejem 2) |
| **D4** | Izlaz | `RELAY_3` (Upravljanje relejem 3) |
| **A5** | Izlaz | `RELAY_4` (Upravljanje relejem transformatora / fazora) |
| **D5** | Ulaz (Pull-up) | `BTN_RX_A` (RX Antena TOP-A tipkalo) |
| **D6** | Ulaz (Pull-up) | `BTN_RX_B` (RX Antena MID-B tipkalo) |
| **D7** | Ulaz (Pull-up) | `BTN_RX_C` (RX Antena BOT-C tipkalo) |
| **D12** | Ulaz (Pull-up) | `BTN_RX_ALL` (Aktivacija svih RX antena) |
| **A4** | Ulaz (Pull-up) | `BTN_RX_MODE` (Prebacivanje EXCL / FLEX moda) |
| **D8** | Ulaz (Pull-up) | `BTN_TX_A` (TX Antena TOP-A tipkalo) |
| **D9** | Ulaz (Pull-up) | `BTN_TX_B` (TX Antena MID-B tipkalo) |
| **D10** | Ulaz (Pull-up) | `BTN_TX_C` (TX Antena BOT-C tipkalo) |
| **D13** | Ulaz (Pull-up) | `BTN_TX_ALL` (Aktivacija svih TX antena) |
| **D11** | Ulaz (Pull-up) | `PTT_PIN` (Ulaz s PC817 optokaplera) |
| **A0** | Izlaz (PWM/Digital) | `LED_RX_A` (Indikator RX Antena A) |
| **A1** | Izlaz (PWM/Digital) | `LED_RX_B` (Indikator RX Antena B) |
| **A2** | Izlaz (PWM/Digital) | `LED_RX_C` (Indikator RX Antena C) |
| **A3** | Izlaz (PWM/Analog) | `LED_TX_A` (Indikator TX Antena A + Fade efekt) |
| **A6** | Izlaz (PWM/Analog) | `LED_TX_B` (Indikator TX Antena B + Fade efekt) |
| **A7** | Izlaz (PWM/Analog) | `LED_TX_C` (Indikator TX Antena C + Fade efekt) |

---

## ⚡ Tablica Stanja Releja (BCC Matrica & NC Logika)

*(Napomena: Zbog upotrebe `!r` inverzije u kodu i Normally Closed releja, `HIGH` signal s Arduina označava ugašeni relej, dok `LOW` signal označava aktivirani/uključeni relej).*

| Kombinacija Antena | RELAY_1 (D2) | RELAY_2 (D3) | RELAY_3 (D4) | RELAY_4 (A5) |
| :--- | :--- | :--- | :--- | :--- |
| **TOP (A)** | HIGH (Ugašen) | LOW (Uključen) | LOW (Uključen) | LOW (Uključen) |
| **MID (B)** | LOW (Uključen) | HIGH (Ugašen) | LOW (Uključen) | LOW (Uključen) |
| **BOT (C)** | LOW (Uključen) | LOW (Uključen) | HIGH (Ugašen) | LOW (Uključen) |
| **TOP + MID (A+B)** | HIGH (Ugašen) | HIGH (Ugašen) | LOW (Uključen) | HIGH (Ugašen) |
| **TOP + BOT (A+C)** | HIGH (Ugašen) | LOW (Uključen) | HIGH (Ugašen) | HIGH (Ugašen) |
| **MID + BOT (B+C)** | LOW (Uključen) | HIGH (Ugašen) | HIGH (Ugašen) | HIGH (Ugašen) |
| **ALL (A+B+C)** | HIGH (Ugašen) | HIGH (Ugašen) | HIGH (Ugašen) | HIGH (Ugašen) |
| **STANDBY (Nijedna)**| LOW (Uključen) | LOW (Uključen) | LOW (Uključen) | LOW (Uključen) |

---

## 🐍 Upute za Python GUI Aplikaciju

Python sučelje omogućava vizualni nadzor i upravljanje preklapanjem direktno s vašeg računala.

### 1. Preduvjeti

Potrebno je imati instaliran Python 3.x i biblioteku `pyserial`:

```bash
pip install pyserial
```

### 2. Pokretanje Aplikacije

Pokrenite skriptu iz naredbenog retka ili terminala:

```bash
python asm_controller.py
```

### 3. Korištenje Aplikacije

1. **Odabir COM Porta:** U gornjoj traci kliknite na gumb **Scan**, odaberite odgovarajući COM port na koji je spojen Arduino Nano te kliknite **Connect**.
2. **Upravljanje RX Antenama:**
   - Kliknite na gumb **RX** pokraj željene antene (TOP-A, MID-B, BOT-C).
   - Za brzi odabir svih antena odjednom koristite gumb **ALL RX**.
3. **Upravljanje TX Antenama:**
   - Prebacite željene antene za predaju pomoću **TX** gumba ili gumba **ALL TX**.
4. **Izmjena RX Moda:**
   - Klikom na gumb **MODE: EXCL / MODE: FLEX** prebacujete između ekskluzivnog načina (samo jedna antena aktivna na prijemu) i fleksibilnog načina (proizvoljna kombinacija antena na prijemu).
5. **Indikator Stanja:**
   - Donja traka i led indikatori na sučelju u realnom vremenu prikazuju PTT status (STANDBY ili ENGAGED) i trenutno aktivnu kombinaciju antena.
