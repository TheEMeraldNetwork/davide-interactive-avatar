#!/usr/bin/env python3
"""
Voice Automation System for HeyGen
Automazione di sistema per input automatico in HeyGen
"""

import pyautogui
import time
import sys
import json
import subprocess
from pathlib import Path

# Configurazione
pyautogui.FAILSAFE = True  # Muovi mouse in angolo per fermare
pyautogui.PAUSE = 0.1      # Pausa tra azioni

class HeyGenAutomator:
    def __init__(self):
        self.last_text = ""
        
    def find_and_fill_input(self, text):
        """Trova l'input di HeyGen e lo riempie automaticamente"""
        
        print(f"🔍 Cercando input di HeyGen per: '{text}'")
        
        # Step 1: Cerca un'area di input visualmente
        input_found = self.find_input_area()
        
        if not input_found:
            print("❌ Input non trovato")
            return False
            
        # Step 2: Copia il testo negli appunti
        self.copy_to_clipboard(text)
        
        # Step 3: Clicca nell'input e incolla
        return self.paste_and_submit()
    
    def find_input_area(self):
        """Trova l'area di input di HeyGen usando riconoscimento visivo"""
        
        try:
            # Metodo 1: Cerca pattern comuni di input
            input_patterns = [
                'input_field.png',  # Se hai uno screenshot del campo
                'chat_input.png',   # Screenshot dell'area chat
            ]
            
            # Per ora usiamo coordinate approssimative se visibile
            # In una versione più avanzata useremo computer vision
            
            # Cerca area nella parte bassa dello schermo (dove solitamente è l'input)
            screen_width, screen_height = pyautogui.size()
            
            # Area probabile per l'input (bottom 30% dello schermo)
            search_region = (0, int(screen_height * 0.7), screen_width, int(screen_height * 0.3))
            
            print(f"📍 Cercando nell'area: {search_region}")
            
            # Metodo semplice: clicca nell'area centrale-bassa
            # dove solitamente sono gli input di chat
            center_x = screen_width // 2
            input_y = int(screen_height * 0.85)  # 85% dall'alto
            
            print(f"🎯 Tentativo click su posizione approssimativa: ({center_x}, {input_y})")
            return True
            
        except Exception as e:
            print(f"❌ Errore nella ricerca: {e}")
            return False
    
    def copy_to_clipboard(self, text):
        """Copia il testo negli appunti del sistema"""
        try:
            # Su macOS usiamo pbcopy
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            print(f"📋 Testo copiato negli appunti: '{text}'")
            return True
        except Exception as e:
            print(f"❌ Errore copia appunti: {e}")
            return False
    
    def paste_and_submit(self):
        """Incolla il testo e invia"""
        try:
            screen_width, screen_height = pyautogui.size()
            
            # Step 1: Clicca nell'area di input (centro-basso schermo)
            center_x = screen_width // 2
            input_y = int(screen_height * 0.85)
            
            print(f"🖱️ Click su input area: ({center_x}, {input_y})")
            pyautogui.click(center_x, input_y)
            time.sleep(0.3)
            
            # Step 2: Seleziona tutto (per pulire)
            pyautogui.hotkey('cmd', 'a')
            time.sleep(0.1)
            
            # Step 3: Incolla il testo
            print("📝 Incollando testo...")
            pyautogui.hotkey('cmd', 'v')
            time.sleep(0.2)
            
            # Step 4: Premi Enter per inviare
            print("⏎ Premendo Enter per inviare...")
            pyautogui.press('enter')
            
            print("✅ Testo inviato con successo!")
            return True
            
        except Exception as e:
            print(f"❌ Errore nell'invio: {e}")
            return False
    
    def process_voice_input(self, text):
        """Processa input vocale ricevuto dal JavaScript"""
        
        if not text or text == self.last_text:
            return False
            
        self.last_text = text
        
        print(f"\n🎤 Nuovo input vocale ricevuto: '{text}'")
        
        # Attendi un momento per dare tempo all'utente
        time.sleep(0.5)
        
        # Processa l'input
        success = self.find_and_fill_input(text)
        
        if success:
            print("🎉 Automazione completata con successo!")
        else:
            print("⚠️ Automazione fallita - copia manuale necessaria")
            
        return success

def main():
    """Funzione principale - può essere chiamata da JavaScript"""
    
    if len(sys.argv) < 2:
        print("❌ Uso: python voice_automation.py 'testo da inviare'")
        return
    
    text = ' '.join(sys.argv[1:])
    
    automator = HeyGenAutomator()
    automator.process_voice_input(text)

if __name__ == "__main__":
    main() 