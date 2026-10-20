import math
import threading
import time
import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports

# --- GLOBALNE VARIJABLE ZA SERIJSKU VEZU ---
arduino = None
connected = False


def get_available_ports():
  ports = serial.tools.list_ports.comports()
  return [port.device for port in ports]


# --- GLAVNI PROZOR ---
root = tk.Tk()
root.title('ASMC 1-3 (Advanced StackMatch Controller)')
root.geometry('500x235')
root.configure(bg='#1a1a1a')
root.resizable(True, True)

PANEL_BG = '#282828'
TEXT_COLOR = '#ffffff'

# Stanja sustava
top_rx = tk.BooleanVar(value=True)
mid_rx = tk.BooleanVar(value=False)
bot_rx = tk.BooleanVar(value=False)

top_tx = tk.BooleanVar(value=True)
mid_tx = tk.BooleanVar(value=True)
bot_tx = tk.BooleanVar(value=True)

ptt_active = tk.BooleanVar(value=False)
remote_active = tk.BooleanVar(value=False)
flex_mode = tk.BooleanVar(value=False)  # False = EXCL, True = FLEX

# Varijabla za Fade animaciju
fade_angle = 0.0

# --- GORNJA TRAKA (COM PORT SKENER & STATUS) ---
top_bar = tk.Frame(root, bg='#121212', height=40)
top_bar.pack(fill=tk.X, side=tk.TOP, padx=10, pady=5)

lbl_port = tk.Label(
    top_bar,
    text='COM Port:',
    font=('Arial', 9, 'bold'),
    fg='#ffffff',
    bg='#121212',
)
lbl_port.pack(side=tk.LEFT, padx=5)

port_combobox = ttk.Combobox(
    top_bar, values=get_available_ports(), width=12, state='readonly'
)
port_combobox.pack(side=tk.LEFT, padx=5)
if port_combobox['values']:
  port_combobox.current(0)


def refresh_ports():
  ports = get_available_ports()
  port_combobox['values'] = ports
  if ports:
    port_combobox.current(0)


btn_scan = tk.Button(
    top_bar,
    text='Scan',
    font=('Arial', 8, 'bold'),
    bg='#444444',
    fg='#ffffff',
    command=refresh_ports,
)
btn_scan.pack(side=tk.LEFT, padx=2)


def toggle_connection():
  global arduino, connected
  if not connected:
    selected_port = port_combobox.get()
    if selected_port:
      try:
        arduino = serial.Serial(selected_port, 9600, timeout=0.1)
        connected = True
        btn_connect.config(text='Disconnect', bg='#c0392b')
        remote_active.set(True)
        print(f'Spojeno na {selected_port}')
      except Exception as e:
        print(f'Greška spajanja: {e}')
  else:
    try:
      if arduino and arduino.is_open:
        arduino.close()
    except:
      pass
    connected = False
    btn_connect.config(text='Connect', bg='#27ae60')
    remote_active.set(False)
    print('Odspojeno.')


btn_connect = tk.Button(
    top_bar,
    text='Connect',
    font=('Arial', 8, 'bold'),
    bg='#27ae60',
    fg='#ffffff',
    command=toggle_connection,
    width=10,
)
btn_connect.pack(side=tk.LEFT, padx=10)

# Status MODOVA u gornjoj traci
lbl_rx_mode_status = tk.Label(
    top_bar,
    text='RX MOD: EXCL',
    font=('Arial', 9, 'bold'),
    fg='#f1c40f',
    bg='#121212',
)
lbl_rx_mode_status.pack(side=tk.RIGHT, padx=15)

# --- GLAVNI OKVIR PREDNJE PLOČE ---
main_frame = tk.Frame(
    root, bg=PANEL_BG, bd=3, relief=tk.RAISED, highlightbackground='#000000'
)
main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 0))

# LIJEVI DIO: LOGO & GUMB ZA RX MOD
left_frame = tk.Frame(main_frame, bg=PANEL_BG)
left_frame.pack(side=tk.LEFT, padx=15, pady=10)

lbl_title = tk.Label(
    left_frame,
    text='ASMC 1-3',
    font=('Arial', 18, 'bold'),
    fg=TEXT_COLOR,
    bg=PANEL_BG,
)
lbl_title.pack(anchor='w')

lbl_sub = tk.Label(
    left_frame,
    text='ADVANCED STACKMATCH',
    font=('Arial', 7, 'bold'),
    fg='#aaaaaa',
    bg=PANEL_BG,
)
lbl_sub.pack(anchor='w', pady=(0, 15))

btn_toggle_mode = tk.Button(
    left_frame,
    text='TOGGLE RX MODE',
    font=('Arial', 8, 'bold'),
    bg='#f39c12',
    fg='#000000',
    padx=8,
    pady=4,
    command=lambda: send_custom_cmd('TOGGLE_MODE'),
)
btn_toggle_mode.pack(pady=5)

# SREDNJI DIO: ANTENE (TOP, MID, BOT)
center_frame = tk.Frame(main_frame, bg=PANEL_BG)
center_frame.pack(side=tk.LEFT, padx=10, pady=10)


def create_antenna_row(parent, label_text, rx_cmd, tx_cmd):
    row_frame = tk.Frame(parent, bg=PANEL_BG)
    row_frame.pack(fill=tk.X, pady=4)

    lbl = tk.Label(
        row_frame,
        text=label_text,
        font=('Arial', 10, 'bold'),
        fg=TEXT_COLOR,
        bg=PANEL_BG,
        width=6,        # Povećano s 4 na 6 kako bi stali nazivi poput TOP-A
        anchor='w',     # Poravnanje ulijevo
    )
    lbl.pack(side=tk.LEFT, padx=2)

    # RX LED
    c_rx = tk.Canvas(
        row_frame, width=15, height=15, bg=PANEL_BG, highlightthickness=0
    )
    c_rx.pack(side=tk.LEFT, padx=2)
    led_rx_id = c_rx.create_oval(1, 1, 14, 14, fill='#1e5128', outline='')

    # RX Tipka
    btn_rx = tk.Button(
        row_frame,
        text='RX',
        font=('Arial', 8, 'bold'),
        bg='#3498db',
        fg='#ffffff',
        width=4,
        command=rx_cmd,
    )
    btn_rx.pack(side=tk.LEFT, padx=3)

    # TX LED
    c_tx = tk.Canvas(
        row_frame, width=15, height=15, bg=PANEL_BG, highlightthickness=0
    )
    c_tx.pack(side=tk.LEFT, padx=2)
    led_tx_id = c_tx.create_oval(1, 1, 14, 14, fill='#53310e', outline='')

    # TX Tipka
    btn_tx = tk.Button(
        row_frame,
        text='TX',
        font=('Arial', 8, 'bold'),
        bg='#e74c3c',
        fg='#ffffff',
        width=4,
        command=tx_cmd,
    )
    btn_tx.pack(side=tk.LEFT, padx=3)

    return c_rx, led_rx_id, c_tx, led_tx_id


def toggle_top_tx():
  top_tx.set(not top_tx.get())
  send_tx_command()


def toggle_mid_tx():
  mid_tx.set(not mid_tx.get())
  send_tx_command()


def toggle_bot_tx():
  bot_tx.set(not bot_tx.get())
  send_tx_command()


def send_tx_command():
  if connected and arduino and arduino.is_open:
    t_t = '1' if top_tx.get() else '0'
    t_m = '1' if mid_tx.get() else '0'
    t_b = '1' if bot_tx.get() else '0'
    cmd = f'SETTX:{t_t}{t_m}{t_b}\n'
    try:
      arduino.write(cmd.encode('utf-8'))
    except Exception as e:
      print(f'Greška slanja: {e}')
  update_indicators()


def toggle_top_rx():
  if flex_mode.get():
    top_rx.set(not top_rx.get())
  else:
    top_rx.set(True)
    mid_rx.set(False)
    bot_rx.set(False)
  send_rx_command()


def toggle_mid_rx():
  if flex_mode.get():
    mid_rx.set(not mid_rx.get())
  else:
    top_rx.set(False)
    mid_rx.set(True)
    bot_rx.set(False)
  send_rx_command()


def toggle_bot_rx():
  if flex_mode.get():
    bot_rx.set(not bot_rx.get())
  else:
    top_rx.set(False)
    mid_rx.set(False)
    bot_rx.set(True)
  send_rx_command()


c_top_rx, led_top_rx, c_top_tx, led_top_tx = create_antenna_row(
    center_frame, 'TOP-A', toggle_top_rx, toggle_top_tx
)
c_mid_rx, led_mid_rx, c_mid_tx, led_mid_tx = create_antenna_row(
    center_frame, 'MID-B', toggle_mid_rx, toggle_mid_tx
)
c_bot_rx, led_bot_rx, c_bot_tx, led_bot_tx = create_antenna_row(
    center_frame, 'BOT-C', toggle_bot_rx, toggle_bot_tx
)

# Brze tipke za odabir svih antena
all_frame = tk.Frame(center_frame, bg=PANEL_BG)
all_frame.pack(fill=tk.X, pady=6)

btn_rx_all = tk.Button(
    all_frame,
    text='ALL RX',
    font=('Arial', 8, 'bold'),
    bg='#2980b9',
    fg='#ffffff',
    width=7,
    command=lambda: set_all_rx(True),
)
btn_rx_all.pack(side=tk.LEFT, padx=3)

btn_tx_all = tk.Button(
    all_frame,
    text='ALL TX',
    font=('Arial', 8, 'bold'),
    bg='#c0392b',
    fg='#ffffff',
    width=7,
    command=lambda: set_all_tx(True),
)
btn_tx_all.pack(side=tk.LEFT, padx=3)


def set_all_rx(val):
  top_rx.set(val)
  mid_rx.set(val)
  bot_rx.set(val)
  send_rx_command()


def set_all_tx(val):
  top_tx.set(val)
  mid_tx.set(val)
  bot_tx.set(val)
  send_tx_command()


# DESNI DIO: PTT I REMOTE STATUS
right_frame = tk.Frame(main_frame, bg=PANEL_BG)
right_frame.pack(side=tk.RIGHT, padx=15, pady=10)


def create_status_indicator(parent, label_text):
  f = tk.Frame(parent, bg=PANEL_BG)
  f.pack(pady=10, anchor='e')

  lbl = tk.Label(
      f, text=label_text, font=('Arial', 9, 'bold'), fg=TEXT_COLOR, bg=PANEL_BG
  )
  lbl.pack(side=tk.RIGHT, padx=4)

  c = tk.Canvas(f, width=16, height=16, bg=PANEL_BG, highlightthickness=0)
  c.pack(side=tk.RIGHT)
  circle = c.create_oval(1, 1, 15, 15, fill='#555555', outline='')
  return c, circle


c_ptt, led_ptt = create_status_indicator(right_frame, 'PTT')
c_remote, led_remote = create_status_indicator(right_frame, 'REMOTE')

# --- STATUS BAR NA DNU PROZORA ---
status_bar = tk.Frame(root, bg='#0a0a0a', height=26, bd=1, relief=tk.SUNKEN)
status_bar.pack(fill=tk.X, side=tk.BOTTOM)

lbl_status_ptt = tk.Label(
    status_bar,
    text='PTT: STANDBY',
    font=('Arial', 9, 'bold'),
    fg='#00ff00',
    bg='#0a0a0a',
    padx=10,
)
lbl_status_ptt.pack(side=tk.LEFT)

lbl_status_antennas = tk.Label(
    status_bar,
    text='RX: NONE | TX: NONE',
    font=('Arial', 9, 'bold'),
    fg='#ffffff',
    bg='#0a0a0a',
    padx=10,
)
lbl_status_antennas.pack(side=tk.RIGHT)


# --- FADE / DIMMING EFEKT I OSVJEŽAVANJE ---
def animate_tx_fade():
  global fade_angle
  if ptt_active.get():
    fade_angle += 0.15
    brightness = int((math.sin(fade_angle) + 1) / 2 * 215 + 40)
    hex_color = f'#{brightness:02x}{int(brightness*0.5):02x}00'

    if top_tx.get():
      c_top_tx.itemconfig(led_top_tx, fill=hex_color)
    else:
      c_top_tx.itemconfig(led_top_tx, fill='#53310e')

    if mid_tx.get():
      c_mid_tx.itemconfig(led_mid_tx, fill=hex_color)
    else:
      c_mid_tx.itemconfig(led_mid_tx, fill='#53310e')

    if bot_tx.get():
      c_bot_tx.itemconfig(led_bot_tx, fill=hex_color)
    else:
      c_bot_tx.itemconfig(led_bot_tx, fill='#53310e')
  else:
    c_top_tx.itemconfig(
        led_top_tx, fill='#e67e22' if top_tx.get() else '#53310e'
    )
    c_mid_tx.itemconfig(
        led_mid_tx, fill='#e67e22' if mid_tx.get() else '#53310e'
    )
    c_bot_tx.itemconfig(
        led_bot_tx, fill='#e67e22' if bot_tx.get() else '#53310e'
    )

  root.after(40, animate_tx_fade)


def update_indicators():
  # RX diode
  c_top_rx.itemconfig(
      led_top_rx, fill='#2ecc71' if top_rx.get() else '#1e5128'
  )
  c_mid_rx.itemconfig(
      led_mid_rx, fill='#2ecc71' if mid_rx.get() else '#1e5128'
  )
  c_bot_rx.itemconfig(
      led_bot_rx, fill='#2ecc71' if bot_rx.get() else '#1e5128'
  )

  # PTT indikator
  c_ptt.itemconfig(led_ptt, fill='#ff0000' if ptt_active.get() else '#441111')

  # REMOTE indikator
  c_remote.itemconfig(
      led_remote, fill='#2ecc71' if remote_active.get() else '#555555'
  )

  # Prikaz modova
  lbl_rx_mode_status.config(
      text='RX MOD: FLEX' if flex_mode.get() else 'RX MOD: EXCL'
  
  )
   # Ažuriranje teksta na gumbu ovisno o aktivnom modu
  btn_toggle_mode.config(
      text='MODE: FLEX' if flex_mode.get() else 'MODE: EXCL'
  )
  
  # --- OSVJEŽAVANJE STATUS BARA ---
  if ptt_active.get():
    lbl_status_ptt.config(text=' PTT ENGAGED ', fg='#ffffff', bg='#ff0000')
  else:
    lbl_status_ptt.config(text=' PTT: STANDBY ', fg='#00ff00', bg='#0a0a0a')

  rx_list = []
  if top_rx.get():
    rx_list.append('TOP')
  if mid_rx.get():
    rx_list.append('MID')
  if bot_rx.get():
    rx_list.append('BOT')
  rx_str = ', '.join(rx_list) if rx_list else 'NONE'

  tx_list = []
  if top_tx.get():
    tx_list.append('TOP')
  if mid_tx.get():
    tx_list.append('MID')
  if bot_tx.get():
    tx_list.append('BOT')
  tx_str = ', '.join(tx_list) if tx_list else 'NONE'

  lbl_status_antennas.config(text=f'RX: {rx_str}  |  TX: {tx_str}')


def send_rx_command():
  if connected and arduino and arduino.is_open:
    r_t = '1' if top_rx.get() else '0'
    r_m = '1' if mid_rx.get() else '0'
    r_b = '1' if bot_rx.get() else '0'
    cmd = f'SET:{r_t}{r_m}{r_b}\n'
    try:
      arduino.write(cmd.encode('utf-8'))
    except Exception as e:
      print(f'Greška slanja: {e}')
  update_indicators()


def send_tx_command():
  if connected and arduino and arduino.is_open:
    t_t = '1' if top_tx.get() else '0'
    t_m = '1' if mid_tx.get() else '0'
    t_b = '1' if bot_tx.get() else '0'
    cmd = f'SETTX:{t_t}{t_m}{t_b}\n'
    try:
      arduino.write(cmd.encode('utf-8'))
    except Exception as e:
      print(f'Greška slanja: {e}')
  update_indicators()


def send_custom_cmd(command):
  if connected and arduino and arduino.is_open:
    try:
      arduino.write(f'{command}\n'.encode('utf-8'))
    except Exception as e:
      print(f'Greška slanja: {e}')


def read_from_arduino():
  global connected, arduino
  while True:
    if connected and arduino:
      try:
        if arduino.in_waiting > 0:
          line = arduino.readline().decode('utf-8').strip()
          if line.startswith('RX:'):
            parts = line.split(' ')
            rx_part = parts[0].split(':')[1]
            # tx_part privremeno ne diramo da Arduino ne gazi vaš odabir u GUI-ju
            ptt_part = parts[2].split(':')[1]
            mod_part = parts[3].split(':')[1]

            top_rx.set(rx_part[0] == '1')
            mid_rx.set(rx_part[1] == '1')
            bot_rx.set(rx_part[2] == '1')

            # Ostavljamo da Python sam pamti TX stanje koje ste kliknuli
            # top_tx.set(tx_part[0] == '1')
            # mid_tx.set(tx_part[1] == '1')
            # bot_tx.set(tx_part[2] == '1')

            ptt_active.set(ptt_part == 'TX')
            flex_mode.set(mod_part == 'FLEX')
            remote_active.set(True)

            root.after(0, update_indicators)
      except Exception as e:
        connected = False
        remote_active.set(False)
        root.after(0, update_indicators)
    time.sleep(0.04)


# Pokretanje dretvi i animacija
threading.Thread(target=read_from_arduino, daemon=True).start()
root.after(100, animate_tx_fade)

root.mainloop()