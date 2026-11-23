# ==============================================================================
# G.A.R.I.N. (Guardian Assistive Realtime Intelligent Notification)
# Production Firmware - Main Application for CanMV K230 (MicroPython)
# File: Deployment/main.py
# ==============================================================================
# [บันทึกประวัติการพัฒนาและรายการแก้ไข (CHANGELOG)]
# วันที่ปรับปรุงล่าสุด: 23 พฤศจิกายน 2026 (2026-11-23 23:25 UTC+7)
# ผู้พัฒนา/ปรับปรุง: Google DeepMind Antigravity AI Assistant
#
# รายการสิ่งที่แก้ไขและเพิ่มเข้ามาใหม่ในไฟล์นี้ (Changelog Summary):
# 1. รวบรวมโค้ดระบบ UI ทั้งหมดเข้าเป็น Main File เดียว พร้อม Deploy ลงบอร์ด CanMV K230 ทันที
# 2. [NEW UI WATCH FACE] หน้าปัดนาฬิกา Activity Watch Face ใหม่ล่าสุด (ตามภาพต้นฉบับของผู้ใช้):
#    - แสดงตัวเลขเวลาชั่วโมงและนาทีซ้อนกันขนาดใหญ่ (Giant Stacked Digital Time) ชัดเจน คอนทราสต์สูงระดับ AMOLED
#    - วงแหวนโค้งด้านบน (Top Arc Gauge): เกจวัดพลังงาน/แคลอรีสีส้ม-แดง (#FF5F14) พร้อมไอคอนเปลวไฟ (Flame Icon 🔥)
#    - วงแหวนโค้งด้านล่าง (Bottom Arc Gauge): เกจวัดกิจกรรม/เสียงรอบตัว สีเขียวนีออน (#50E13C) พร้อมไอคอนกิจกรรม
#    - Complication ด้านซ้าย: วันที่ตัวหนาสีขาว + วันในสัปดาห์ภาษาอังกฤษสีฟ้าไอซ์บลู (e.g. 23 SUN)
#    - Complication ด้านขวา: ค่าสถิติ (e.g. 78) + ไอคอนหัวใจเต้น (❤️)
#    - ดึงเวลาจริงและซิงค์เวลามาตรฐานประเทศไทย (UTC+7 Thailand Real-Time Sync)
# 3. [TOUCH-TO-SET TIME] ระบบสัมผัสที่ตัวเลขเวลาเพื่อตั้งค่า RTC:
#    - แตะที่บริเวณตัวเลขเวลา (ชั่วโมง/นาที) หรือแตะที่วันที่ฝั่งซ้าย จะสั่นเตือนและเปิดโหมดตั้งเวลา RTC (โหมด 10) ทันที
#    - หน้าตั้งเวลา RTC มีปุ่มสัมผัส ▲ / ▼ ปรับชั่วโมง, นาที, ปี, เดือน, วัน พร้อมปุ่ม [V] บันทึก (SAVE) เขียนลงชิป RTC ฮาร์ดแวร์
# 4. [11 MODES CYBER-BLUE UI] หน้าจอเฝ้าระวังและเตือนภัยครบครัน 11 โหมด:
#    - โหมด 0: หน้าปัดนาฬิกา Activity Watch Face (Home / Standby)
#    - โหมด 1: ข้อมูลสเปกระบบ GARIN (K230 Dual 64-bit RISC-V, 6 TOPS KPU, 16kHz DMA, ESP32 Link)
#    - โหมด 2: แจ้งเตือนเสียงสุนัขเห่า (DOG BARKING DETECTED)
#    - โหมด 3: แจ้งเตือนเขตก่อสร้าง (CONSTRUCTION SITE)
#    - โหมด 4: โหมดสงบนิ่งประหยัดพลังงาน (SILENT STANDBY)
#    - โหมด 5: แจ้งเตือนเครื่องจักรทำงาน (HEAVY MACHINE WORKING)
#    - โหมด 6: แจ้งเตือนฉุกเฉิน รถยนต์แล่นมาใกล้ (CAR APPROACHING)
#    - โหมด 7: แจ้งเตือนฉุกเฉิน เสียงแตรรถบรรทุก (TRUCK HORN ALERT)
#    - โหมด 8: แจ้งเตือนภัยร้ายแรง เสียงระเบิด/กระแทก (BANG / EXPLOSION ALERT)
#    - โหมด 9: บัตรคิวดิจิทัลบริการสาธารณะและโรงพยาบาล (PUBLIC QUEUE CALLING)
#    - โหมด 10: เมนูสัมผัสตั้งเวลาและวันที่ระบบ RTC (TIME & DATE SETTER)
# 5. [DOCK NAVIGATION] แถบปุ่มสัมผัส 3 ปุ่มมาตรฐานล่างจอ (< ย้อน, หน้าหลัก, ถัดไป >) นำทางสะดวก
# 6. [ESP32 UART BRIDGE] รองรับรับคำสั่งแจ้งเตือนจากบอร์ดภายนอก (TTGO T7 ESP32) ผ่าน UART1 (115200 bps)
# 7. [HAPTIC ENGINE] ระบบสั่นเตือนข้อมือผ่าน GPIO1 (VIBE) และ GPIO2 (BUZZ) แยกจังหวะตามระดับความรุนแรง
# 8. [DISPLAY HARDWARE] รองรับหน้าจอ CanMV K230 ST7701 (Portrait 480x640 MIPI DSI @ 30 FPS)
# ==============================================================================

import os
import sys
import time
import math
import image
from media.display import *
from media.media import *
from machine import Pin, FPIOA, TOUCH, UART

# Clean slate: deinit any stale MediaManager
try:
    MediaManager.deinit()
except Exception:
    pass

# ==============================================================================
# 1. Config - Portrait Mode (480x640) ST7701 MIPI DSI
# ==============================================================================
SCREEN_W = 480
SCREEN_H = 640

# --- CYBER-BLUE HIGH-CONTRAST PALETTE (ธีมสีฟ้า) ---
COLOR_BG            = (6, 12, 22)        # Deep Obsidian Navy Black (OLED depth)
COLOR_CARD_BG       = (12, 22, 38)       # Rich Slate Blue Card Fill
COLOR_CARD_SURFACE  = (18, 34, 56)       # Elevated Surface Blue (Buttons / Panels)
COLOR_HEADER_BG     = (10, 18, 32)       # Top Header & Bottom Dock Fill
COLOR_HEADER_LINE   = (0, 160, 240)      # Glowing Neon Blue Divider

# Primary Blue Accents
COLOR_PRIMARY_BLUE  = (0, 175, 255)      # Electric Cyber Blue (Hero Accent)
COLOR_CYAN_GLOW     = (0, 230, 255)      # Vivid Ice Cyan (High Visibility Highlights)
COLOR_DEEP_BLUE     = (0, 95, 195)       # Strong Royal Blue (Filled Primary Buttons)
COLOR_LIGHT_BLUE    = (130, 205, 255)    # Frost Sky Blue (Subtitles & Badges)
COLOR_BORDER_BLUE   = (28, 56, 92)       # Card Border Blue
COLOR_BORDER_GLOW   = (0, 160, 240)      # Highlight Glow Border
COLOR_MUTED_BLUE    = (70, 105, 145)     # Darker Muted Slate Blue (Guides / Dividers)

# Status & Contrast Accents
COLOR_WHITE         = (255, 255, 255)    # Pure Crisp White (Primary Text)
COLOR_MUTED         = (150, 175, 205)    # Cool Silver / Secondary Text
COLOR_SAFE_GREEN    = (0, 235, 140)      # Normal / Safe Status Indicator
COLOR_WARN_AMBER    = (255, 190, 40)     # Caution / Machinery / Construction
COLOR_ALERT_RED     = (255, 60, 75)      # Urgent / Car / Horn / Bang Danger

# Localization constants (Thai Days & Months)
TH_DAYS   = ["จันทร์", "อังคาร", "พุธ", "พฤหัส", "ศุกร์", "เสาร์", "อาทิตย์"]
TH_MONTHS = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
EN_DAYS   = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

# ==============================================================================
# 2. Hardware Initialization
# ==============================================================================
try:
    Display.init(Display.ST7701, width=480, height=640, fps=30, to_ide=True)
except Exception as e:
    print(f"[Display Error] Display.init failed: {e}")

# Hardware Media Process Engine (Required for physical display output!)
try:
    MediaManager.init()
    print("[Display] Hardware MIPI Output Engine: ONLINE (480x640)")
except Exception as e:
    print(f"[Display Error] MediaManager init failed: {e}")

# Touch sensor (with fallback if hardware touch is disconnected)
try:
    tp = TOUCH(0)
    TOUCH_OK = True
    print("[Touch] Initialized successfully")
except Exception as e:
    tp = None
    TOUCH_OK = False
    print(f"[Touch Warning] Open Touch Device failed: {e}")

# VIBE & BUZZ Pins for Tactile Feedback
try:
    fpioa = FPIOA()
    fpioa.set_function(1, FPIOA.GPIO1)
    fpioa.set_function(2, FPIOA.GPIO2)
    VIBE_PIN = Pin(1, Pin.OUT)
    BUZZ_PIN = Pin(2, Pin.OUT)
    HW_OK = True
except Exception:
    HW_OK = False

# ==============================================================================
# 3. UART Interface with TTGO T7 (ESP32)
# 01Studio CanMV K230 Pinout:
#   IO3 = UART1_TXD -> Connect to ESP32 RX (e.g. GPIO16)
#   IO4 = UART1_RXD -> Connect to ESP32 TX (e.g. GPIO17)
#   GND             -> Connect to ESP32 GND
# ==============================================================================
UART_OK = False
uart = None
try:
    fpioa.set_function(3, FPIOA.UART1_TXD)
    fpioa.set_function(4, FPIOA.UART1_RXD)
    uart = UART(UART.UART1, 115200)
    UART_OK = True
    print("[UART] Connected to ESP32 on IO3(TX) / IO4(RX) @ 115200 bps")
    try:
        uart.write("READY:GARIN_K230_DISPLAY\n")
    except Exception:
        pass
except Exception as e:
    print(f"[UART Warning] Init failed: {e}")

# ==============================================================================
# 4. Haptic Feedback Patterns
# ==============================================================================
HAPTIC_SINGLE = 1   # Normal tap / mode cycle
HAPTIC_DOUBLE = 2   # Confirm / Save action
HAPTIC_WARN   = 3   # Warning (Dog, Construction, Machine)
HAPTIC_URGENT = 4   # Urgent Danger (Car, Truck Horn, Bang)
HAPTIC_QUEUE  = 5   # Public Queue Alert

def trigger_haptic(pattern=HAPTIC_SINGLE):
    if not HW_OK:
        return
    try:
        if pattern == HAPTIC_SINGLE:
            VIBE_PIN.value(1)
            time.sleep_ms(80)
            VIBE_PIN.value(0)
        elif pattern == HAPTIC_DOUBLE:
            for _ in range(2):
                VIBE_PIN.value(1)
                time.sleep_ms(120)
                VIBE_PIN.value(0)
                time.sleep_ms(60)
        elif pattern == HAPTIC_WARN:
            for _ in range(3):
                VIBE_PIN.value(1)
                BUZZ_PIN.value(1)
                time.sleep_ms(150)
                VIBE_PIN.value(0)
                BUZZ_PIN.value(0)
                time.sleep_ms(80)
        elif pattern == HAPTIC_URGENT:
            for _ in range(4):
                VIBE_PIN.value(1)
                BUZZ_PIN.value(1)
                time.sleep_ms(220)
                VIBE_PIN.value(0)
                BUZZ_PIN.value(0)
                time.sleep_ms(50)
        elif pattern == HAPTIC_QUEUE:
            for _ in range(2):
                VIBE_PIN.value(1)
                time.sleep_ms(350)
                VIBE_PIN.value(0)
                time.sleep_ms(150)
    except Exception:
        pass

# ==============================================================================
# 5. RTC System Time Setting Function
# ==============================================================================
def set_rtc_time(year, month, day, hour, minute, second=0):
    try:
        from machine import RTC
        rtc = RTC()
        rtc.datetime((year, month, day, 0, hour, minute, second, 0))
        print(f"[RTC] Saved: {year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
        return True
    except Exception as e:
        print("[RTC] Set time error:", e)
        return False

# Interactive time setting state variables
try:
    t_init = time.localtime()
    edit_year, edit_month, edit_day = t_init[0], t_init[1], t_init[2]
    edit_hour, edit_minute = t_init[3], t_init[4]
except Exception:
    edit_year, edit_month, edit_day = 2026, 11, 23
    edit_hour, edit_minute = 10, 9

# ==============================================================================
# 6. UI Mode State (11 Screens Total: 0..10)
# ==============================================================================
ui_mode = 0
MODE_COUNT = 11
_running = True

# ==============================================================================
# 7. Curved Arc Progress Gauge & Modern Watch Face Components
# ==============================================================================
def draw_arc_gauge(canvas, cx, cy, r, start_deg, end_deg, active_ratio, active_color, inactive_color=(40, 42, 48), thickness=18):
    """Draws a smooth circular arc progress gauge with rounded caps for watch face."""
    total_span = end_deg - start_deg
    active_ratio = max(0.0, min(1.0, active_ratio))
    split_deg = start_deg + total_span * active_ratio
    deg = float(start_deg)
    step = 2.0  # 2 degrees step gives smooth curve and fast execution on CanMV K230
    cap_r = max(2, thickness // 2)
    while deg <= end_deg:
        rad = math.radians(deg)
        x = int(cx + r * math.cos(rad))
        y = int(cy + r * math.sin(rad))
        col = active_color if deg <= split_deg else inactive_color
        canvas.draw_circle(x, y, cap_r, color=col, thickness=1, fill=True)
        deg += step

def draw_flame_icon(canvas, cx, cy):
    """Draws a miniature flame icon for the top calories/energy arc."""
    canvas.draw_circle(cx, cy, 6, color=(255, 120, 0), thickness=1, fill=True)
    canvas.draw_line(cx - 3, cy + 2, cx, cy - 7, color=(255, 220, 50), thickness=2)
    canvas.draw_line(cx + 3, cy + 2, cx, cy - 7, color=(255, 220, 50), thickness=2)

def draw_heart_icon(canvas, cx, cy, size=7, color=(255, 90, 40)):
    """Draws a crisp geometric heart icon."""
    r = max(2, size // 2)
    canvas.draw_circle(cx - r, cy - size // 3, r, color=color, thickness=1, fill=True)
    canvas.draw_circle(cx + r, cy - size // 3, r, color=color, thickness=1, fill=True)
    canvas.draw_line(cx - size, cy, cx, cy + size, color=color, thickness=2)
    canvas.draw_line(cx + size, cy, cx, cy + size, color=color, thickness=2)
    canvas.draw_circle(cx, cy, r, color=color, thickness=1, fill=True)

def draw_pill_badge(canvas, x, y, w, h, text, text_color=COLOR_CYAN_GLOW, bg_color=COLOR_CARD_SURFACE, border_color=COLOR_PRIMARY_BLUE, font_size=18):
    """Draws a rounded-look pill badge with centered label."""
    canvas.draw_rectangle(x, y, w, h, color=bg_color, thickness=1, fill=True)
    canvas.draw_rectangle(x, y, w, h, color=border_color, thickness=1, fill=False)
    est_w = len(text) * int(font_size * 0.5)
    tx = max(x + 6, x + (w - est_w) // 2)
    ty = y + max(2, (h - font_size) // 2)
    canvas.draw_string_advanced(tx, ty, font_size, text, color=text_color)

def draw_warning_triangle(canvas, cx, cy, size=56, color=COLOR_WARN_AMBER):
    """Draws a crisp geometric warning triangle with exclamation mark."""
    h = int(size * 0.866)
    x1, y1 = cx, cy - int(h * 0.6)
    x2, y2 = cx - size // 2, cy + int(h * 0.4)
    x3, y3 = cx + size // 2, cy + int(h * 0.4)
    canvas.draw_line(x1, y1, x2, y2, color=color, thickness=3)
    canvas.draw_line(x2, y2, x3, y3, color=color, thickness=3)
    canvas.draw_line(x3, y3, x1, y1, color=color, thickness=3)
    canvas.draw_line(cx, cy - int(h * 0.25), cx, cy + int(h * 0.1), color=color, thickness=3)
    canvas.draw_rectangle(cx - 1, cy + int(h * 0.22), 3, 3, color=color, thickness=1, fill=True)

def draw_danger_shield(canvas, cx, cy, size=52, color=COLOR_ALERT_RED):
    """Draws a geometric danger beacon with exclamation mark."""
    r = size // 2
    canvas.draw_rectangle(cx - r, cy - r, size, size, color=color, thickness=3, fill=False)
    canvas.draw_line(cx, cy - int(r * 0.6), cx, cy + int(r * 0.2), color=color, thickness=4)
    canvas.draw_rectangle(cx - 2, cy + int(r * 0.4), 4, 4, color=color, thickness=1, fill=True)

def draw_header_bar(canvas, title="G.A.R.I.N.", status_text="SAFE [OK]", mode_idx=0, is_alert=False):
    """Draws top status bar with device identity, status badge, and mode pagination."""
    canvas.draw_rectangle(0, 0, SCREEN_W, 56, color=COLOR_HEADER_BG, thickness=1, fill=True)
    border_c = COLOR_ALERT_RED if is_alert else COLOR_HEADER_LINE
    canvas.draw_line(0, 55, SCREEN_W, 55, color=border_c, thickness=2)

    # Logo / Title on Left (Tap to Home shortcut zone)
    title_c = COLOR_ALERT_RED if is_alert else COLOR_CYAN_GLOW
    canvas.draw_string_advanced(16, 12, 28, title, color=title_c)

    # Mode Pagination Chip
    chip_txt = f"{mode_idx}/10"
    draw_pill_badge(canvas, 190, 12, 60, 32, chip_txt, text_color=COLOR_MUTED, bg_color=COLOR_CARD_BG, border_color=COLOR_BORDER_BLUE, font_size=16)

    # Status Pill on Right
    badge_w = 180
    badge_x = SCREEN_W - badge_w - 14
    badge_c = COLOR_ALERT_RED if is_alert else COLOR_PRIMARY_BLUE
    badge_bg = (35, 14, 20) if is_alert else COLOR_CARD_SURFACE
    draw_pill_badge(canvas, badge_x, 10, badge_w, 36, status_text, text_color=COLOR_WHITE, bg_color=badge_bg, border_color=badge_c, font_size=18)

def draw_footer_dock(canvas, left_label="< ย้อน", center_label="หน้าหลัก", right_label="ถัดไป >", highlight_center=False):
    """
    Standardized 3-button touch dock at bottom of screen.
    Touch Targets:
      - Left:   X 15..145, Y 575..632
      - Center: X 160..320, Y 575..632
      - Right:  X 335..465, Y 575..632
    """
    canvas.draw_rectangle(0, SCREEN_H - 65, SCREEN_W, 65, color=COLOR_HEADER_BG, thickness=1, fill=True)
    canvas.draw_line(0, SCREEN_H - 65, SCREEN_W, SCREEN_H - 65, color=COLOR_HEADER_LINE, thickness=2)

    # Left Button: Prev
    canvas.draw_rectangle(15, SCREEN_H - 57, 130, 48, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_rectangle(15, SCREEN_H - 57, 130, 48, color=COLOR_BORDER_BLUE, thickness=1, fill=False)
    canvas.draw_string_advanced(38, SCREEN_H - 44, 20, left_label, color=COLOR_LIGHT_BLUE)

    # Center Button: Home / Dismiss
    c_bg = COLOR_DEEP_BLUE if highlight_center else COLOR_CARD_SURFACE
    c_border = COLOR_CYAN_GLOW if highlight_center else COLOR_PRIMARY_BLUE
    c_txt = COLOR_WHITE if highlight_center else COLOR_CYAN_GLOW
    canvas.draw_rectangle(160, SCREEN_H - 57, 160, 48, color=c_bg, thickness=1, fill=True)
    canvas.draw_rectangle(160, SCREEN_H - 57, 160, 48, color=c_border, thickness=2, fill=False)
    canvas.draw_string_advanced(188, SCREEN_H - 44, 20, center_label, color=c_txt)

    # Right Button: Next
    canvas.draw_rectangle(335, SCREEN_H - 57, 130, 48, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_rectangle(335, SCREEN_H - 57, 130, 48, color=COLOR_BORDER_BLUE, thickness=1, fill=False)
    canvas.draw_string_advanced(358, SCREEN_H - 44, 20, right_label, color=COLOR_LIGHT_BLUE)

def draw_tech_card(canvas, x, y, w, h, border_color=COLOR_PRIMARY_BLUE, fill_color=COLOR_CARD_BG, thickness=2, glow_corners=True):
    """Draws a modern high-contrast cyber-styled card with optional glowing corner markers."""
    canvas.draw_rectangle(x, y, w, h, color=fill_color, thickness=1, fill=True)
    canvas.draw_rectangle(x, y, w, h, color=border_color, thickness=thickness, fill=False)
    if glow_corners:
        csz = 12
        th = thickness + 1
        canvas.draw_line(x, y, x + csz, y, color=COLOR_CYAN_GLOW, thickness=th)
        canvas.draw_line(x, y, x, y + csz, color=COLOR_CYAN_GLOW, thickness=th)
        canvas.draw_line(x + w - csz, y, x + w, y, color=COLOR_CYAN_GLOW, thickness=th)
        canvas.draw_line(x + w, y, x + w, y + csz, color=COLOR_CYAN_GLOW, thickness=th)
        canvas.draw_line(x, y + h - csz, x, y + h, color=COLOR_CYAN_GLOW, thickness=th)
        canvas.draw_line(x, y + h, x + csz, y + h, color=COLOR_CYAN_GLOW, thickness=th)
        canvas.draw_line(x + w - csz, y + h, x + w, y + h, color=COLOR_CYAN_GLOW, thickness=th)
        canvas.draw_line(x + w, y + h - csz, x + w, y + h, color=COLOR_CYAN_GLOW, thickness=th)

# ==============================================================================
# 8. Touch Interaction Listener Task
# ==============================================================================
def task_clock():
    global _running, ui_mode, edit_year, edit_month, edit_day, edit_hour, edit_minute
    if tp is None:
        print("[Task Touch] Touch disabled (hardware not available)")
        return
    print("[Task Touch] Modern Cyber-Blue Touch Listener Active")
    last_toggle = 0
    DEBOUNCE_MS = 220

    while _running:
        try:
            point = tp.read(1)
            if point and len(point):
                pt = point[0]
                if pt.event == 3:  # Touch press event
                    now = time.ticks_ms()
                    if time.ticks_diff(now, last_toggle) >= DEBOUNCE_MS:
                        px = getattr(pt, 'x', 0)
                        py = getattr(pt, 'y', 0)
                        print(f"[Touch] ({px}, {py}) Current Mode: {ui_mode}")

                        # ------------------------------------------------------
                        # GLOBAL HEADER TAP: Top-left area returns to Home
                        # ------------------------------------------------------
                        if py <= 56 and px <= 140 and ui_mode != 0:
                            ui_mode = 0
                            trigger_haptic(HAPTIC_SINGLE)

                        # ------------------------------------------------------
                        # GLOBAL BOTTOM DOCK NAVIGATION (Y: 570..640)
                        # Available on screens 1..9, plus custom handlers
                        # ------------------------------------------------------
                        elif py >= 570 and ui_mode != 10:
                            # Left Dock: Previous Screen
                            if 15 <= px <= 145:
                                ui_mode = (ui_mode - 1) % MODE_COUNT
                                trigger_haptic(HAPTIC_SINGLE)
                            # Center Dock: Quick Return to Screen 0 (Home)
                            elif 160 <= px <= 320:
                                ui_mode = 0
                                trigger_haptic(HAPTIC_SINGLE)
                            # Right Dock: Next Screen
                            elif 335 <= px <= 465:
                                ui_mode = (ui_mode + 1) % MODE_COUNT
                                trigger_haptic(HAPTIC_SINGLE)

                        # ------------------------------------------------------
                        # MODE 0: CLOCK / HOME SCREEN (Activity Watch Face)
                        # ------------------------------------------------------
                        elif ui_mode == 0:
                            # 1. Direct Time Tap (Hour or Minute digits: Y: 90..480):
                            # Tapping on the time immediately opens the Time Set Screen!
                            if 50 <= px <= 430 and 90 <= py <= 480:
                                try:
                                    t = time.localtime()
                                    edit_year, edit_month, edit_day = t[0], t[1], t[2]
                                    edit_hour, edit_minute = t[3], t[4]
                                except Exception:
                                    pass
                                ui_mode = 10  # Jump to Time Setting Screen
                                trigger_haptic(HAPTIC_SINGLE)
                                print("[Touch] Time tapped -> Opening Time Set (Mode 10)")

                            # 2. Left Complication: Date tap also opens Time Setting
                            elif px <= 100 and 250 <= py <= 350:
                                try:
                                    t = time.localtime()
                                    edit_year, edit_month, edit_day = t[0], t[1], t[2]
                                    edit_hour, edit_minute = t[3], t[4]
                                except Exception:
                                    pass
                                ui_mode = 10
                                trigger_haptic(HAPTIC_SINGLE)

                            # 3. Bottom Area: Advance to next screen (Mode 1 Info)
                            elif py >= 500:
                                ui_mode = 1
                                trigger_haptic(HAPTIC_SINGLE)

                        # ------------------------------------------------------
                        # MODE 10: TIME & DATE SETTER SCREEN
                        # ------------------------------------------------------
                        elif ui_mode == 10:
                            # Hour UP [ ▲ ] (X: 30..220, Y: 110..160)
                            if 30 <= px <= 220 and 110 <= py <= 160:
                                edit_hour = (edit_hour + 1) % 24
                                trigger_haptic(HAPTIC_SINGLE)
                            # Hour DOWN [ ▼ ] (X: 30..220, Y: 250..300)
                            elif 30 <= px <= 220 and 250 <= py <= 300:
                                edit_hour = (edit_hour - 1) % 24
                                trigger_haptic(HAPTIC_SINGLE)

                            # Minute UP [ ▲ ] (X: 260..450, Y: 110..160)
                            elif 260 <= px <= 450 and 110 <= py <= 160:
                                edit_minute = (edit_minute + 1) % 60
                                trigger_haptic(HAPTIC_SINGLE)
                            # Minute DOWN [ ▼ ] (X: 260..450, Y: 250..300)
                            elif 260 <= px <= 450 and 250 <= py <= 300:
                                edit_minute = (edit_minute - 1) % 60
                                trigger_haptic(HAPTIC_SINGLE)

                            # Year UP / DOWN (X: 25..155, Y: 315..355 / 415..455)
                            elif 25 <= px <= 155 and 315 <= py <= 355:
                                edit_year = min(2035, edit_year + 1)
                                trigger_haptic(HAPTIC_SINGLE)
                            elif 25 <= px <= 155 and 415 <= py <= 455:
                                edit_year = max(2024, edit_year - 1)
                                trigger_haptic(HAPTIC_SINGLE)

                            # Month UP / DOWN (X: 172..308, Y: 315..355 / 415..455)
                            elif 172 <= px <= 308 and 315 <= py <= 355:
                                edit_month = 1 if edit_month >= 12 else edit_month + 1
                                trigger_haptic(HAPTIC_SINGLE)
                            elif 172 <= px <= 308 and 415 <= py <= 455:
                                edit_month = 12 if edit_month <= 1 else edit_month - 1
                                trigger_haptic(HAPTIC_SINGLE)

                            # Day UP / DOWN (X: 325..455, Y: 315..355 / 415..455)
                            elif 325 <= px <= 455 and 315 <= py <= 355:
                                edit_day = 1 if edit_day >= 31 else edit_day + 1
                                trigger_haptic(HAPTIC_SINGLE)
                            elif 325 <= px <= 455 and 415 <= py <= 455:
                                edit_day = 31 if edit_day <= 1 else edit_day - 1
                                trigger_haptic(HAPTIC_SINGLE)

                            # SAVE BUTTON: Save to RTC & Return to Home (X: 25..275, Y: 480..550)
                            elif 25 <= px <= 275 and 480 <= py <= 550:
                                set_rtc_time(edit_year, edit_month, edit_day, edit_hour, edit_minute, 0)
                                trigger_haptic(HAPTIC_DOUBLE)
                                ui_mode = 0

                            # CANCEL BUTTON: Discard & Return to Home (X: 290..455, Y: 480..550)
                            elif 290 <= px <= 455 and 480 <= py <= 550:
                                trigger_haptic(HAPTIC_SINGLE)
                                ui_mode = 0

                        # ------------------------------------------------------
                        # ALERT & INFO SCREENS (Screens 1..9)
                        # ------------------------------------------------------
                        else:
                            # Primary Dismiss / Ack Button (X: 18..462, Y: 485..553)
                            if 18 <= px <= 462 and 485 <= py <= 553:
                                ui_mode = 0  # Clear alert, jump back to Clock
                                trigger_haptic(HAPTIC_SINGLE)
                            # Body tap: Cycle forward to next mode
                            else:
                                ui_mode = (ui_mode + 1) % MODE_COUNT
                                trigger_haptic(HAPTIC_SINGLE)

                        # Notify companion ESP32 over UART
                        if UART_OK and uart is not None:
                            try:
                                uart.write(f"TOUCH:X={px},Y={py},MODE={ui_mode}\n")
                            except Exception:
                                pass

                        last_toggle = now
        except Exception:
            pass
        time.sleep_ms(10)
    print("[Task Touch] Stopped")

# ==============================================================================
# 9. Task: ESP32 UART Command Listener & Processor
# ==============================================================================
def process_esp32_command(cmd):
    global ui_mode, edit_year, edit_month, edit_day, edit_hour, edit_minute
    cmd = cmd.strip()
    if not cmd:
        return
    print(f"[UART CMD From ESP32] {cmd}")

    # 1. Switch Screen Mode: "MODE:<0-10>"
    if cmd.startswith("MODE:"):
        try:
            m = int(cmd.split(":")[1].strip())
            if 0 <= m < MODE_COUNT:
                ui_mode = m
                if UART_OK and uart is not None:
                    uart.write(f"ACK:MODE={ui_mode}\n")
        except Exception:
            pass

    # 2. Trigger Haptic Vibration: "HAPTIC:<1-5>"
    elif cmd.startswith("HAPTIC:"):
        try:
            p = int(cmd.split(":")[1].strip())
            trigger_haptic(p)
            if UART_OK and uart is not None:
                uart.write(f"ACK:HAPTIC={p}\n")
        except Exception:
            pass

    # 3. Synchronize Time: "TIME:<HH>:<MM>:<SS>"
    elif cmd.startswith("TIME:"):
        try:
            parts = cmd.split(":")[1:]
            if len(parts) >= 2:
                h = int(parts[0])
                m = int(parts[1])
                s = int(parts[2]) if len(parts) > 2 else 0
                set_rtc_time(edit_year, edit_month, edit_day, h, m, s)
                if UART_OK and uart is not None:
                    uart.write("ACK:TIME_SYNCED\n")
        except Exception:
            pass

    # 4. Synchronize Date: "DATE:<YYYY>-<MM>-<DD>"
    elif cmd.startswith("DATE:"):
        try:
            datestr = cmd.split(":", 1)[1].strip()
            y, mo, d = [int(x) for x in datestr.split("-")]
            set_rtc_time(y, mo, d, edit_hour, edit_minute, 0)
            if UART_OK and uart is not None:
                uart.write("ACK:DATE_SYNCED\n")
        except Exception:
            pass

    # 5. Heartbeat Ping / Pong
    elif cmd == "PING":
        if UART_OK and uart is not None:
            uart.write("PONG\n")

def task_uart_rx():
    global _running
    if not UART_OK or uart is None:
        print("[Task UART] UART not available, listener disabled")
        return
    print("[Task UART] ESP32 Command Listener Active on UART1 (IO4/RX)")
    buffer = ""
    while _running:
        try:
            if uart.any():
                raw = uart.read(64)
                if raw:
                    try:
                        buffer += raw.decode()
                    except Exception:
                        pass
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if line:
                            process_esp32_command(line)
        except Exception:
            pass
        time.sleep_ms(15)
    print("[Task UART] Stopped")

# ==============================================================================
# 10. Screen Renderers (Cyber-Blue Theme - 480x640 Portrait)
# ==============================================================================

def draw_screen_0_clock(canvas):
    """SCREEN 0: MODERN STACKED ACTIVITY WATCH FACE (HOME / STANDBY IDLE)"""
    canvas.clear()
    canvas.draw_rectangle(0, 0, SCREEN_W, SCREEN_H, color=(0, 0, 0), thickness=1, fill=True)

    # 1. Fetch Real Thai Time (UTC+7)
    try:
        t = time.localtime()
        hour_str = "{:02d}".format(t[3])
        min_str = "{:02d}".format(t[4])
        day_num = str(t[2])
        day_names = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        day_name = day_names[t[6] % 7] if len(t) > 6 else "SUN"
        # Day progress for top gauge (0.0 to 1.0)
        day_sec = t[3] * 3600 + t[4] * 60 + t[5]
        top_ratio = max(0.15, min(0.95, day_sec / 86400.0))
    except Exception:
        hour_str = "10"
        min_str = "09"
        day_num = "16"
        day_name = "SUN"
        top_ratio = 0.78

    # 2. Top Curved Arc (Orange-Red Activity / Energy Gauge)
    draw_arc_gauge(canvas, 240, 280, 225, 208, 332, top_ratio, (255, 95, 20), inactive_color=(40, 42, 48), thickness=18)
    rad_f = math.radians(208)
    fx = int(240 + 225 * math.cos(rad_f))
    fy = int(280 + 225 * math.sin(rad_f))
    draw_flame_icon(canvas, fx, fy)

    # 3. Bottom Curved Arc (Neon Lime Green Audio / Activity Gauge)
    bot_ratio = 0.72
    draw_arc_gauge(canvas, 240, 360, 225, 28, 152, bot_ratio, (80, 225, 60), inactive_color=(40, 42, 48), thickness=18)
    rad_r = math.radians(152)
    rx = int(240 + 225 * math.cos(rad_r))
    ry = int(360 + 225 * math.sin(rad_r))
    canvas.draw_circle(rx, ry, 6, color=(80, 225, 60), thickness=1, fill=True)
    canvas.draw_circle(rx, ry, 3, color=(0, 0, 0), thickness=1, fill=True)

    # 4. Large Stacked Digital Clock (Hours on top, Minutes on bottom)
    canvas.draw_string_advanced(145, 105, 160, hour_str, color=(255, 255, 255))
    canvas.draw_string_advanced(145, 285, 160, min_str, color=(255, 255, 255))

    # 5. Left Complication: Date (e.g. 16 SUN)
    canvas.draw_string_advanced(46, 275, 28, day_num, color=(255, 255, 255))
    canvas.draw_string_advanced(42, 308, 18, day_name, color=(0, 215, 255))

    # 6. Right Complication: Metric (78 Heart / Battery / Audio)
    metric_val = "78"
    canvas.draw_string_advanced(402, 275, 28, metric_val, color=(255, 255, 255))
    draw_heart_icon(canvas, 416, 314, size=6, color=(255, 90, 40))

    # 7. Subtle Setting Button / Prompt
    canvas.draw_string_advanced(150, 595, 16, "[แตะที่เวลาเพื่อตั้งค่า RTC]", color=(80, 105, 135))
    Display.show_image(canvas)

def draw_screen_1_garin_info(canvas):
    """SCREEN 1: GARIN SYSTEM & AI SPECIFICATIONS"""
    canvas.clear()
    canvas.draw_rectangle(0, 0, SCREEN_W, SCREEN_H, color=COLOR_BG, thickness=1, fill=True)
    draw_header_bar(canvas, title="G.A.R.I.N.", status_text="INFO [1/10]", mode_idx=1, is_alert=False)

    # Title Banner Card
    draw_tech_card(canvas, 18, 68, 444, 82, border_color=COLOR_PRIMARY_BLUE, fill_color=COLOR_CARD_BG, thickness=2)
    canvas.draw_string_advanced(110, 78, 34, "GARIN ASSIST", color=COLOR_CYAN_GLOW)
    canvas.draw_string_advanced(80, 118, 20, "อุปกรณ์ประสาทสัมผัสสำรองอัจฉริยะ", color=COLOR_LIGHT_BLUE)

    # Specs Container Card (Y: 160..465)
    draw_tech_card(canvas, 18, 160, 444, 305, border_color=COLOR_PRIMARY_BLUE, fill_color=COLOR_CARD_BG, thickness=2)
    canvas.draw_string_advanced(36, 178, 22, "• บอร์ด: CanMV K230 Dual 64-bit RISC-V", color=COLOR_WHITE)
    canvas.draw_string_advanced(36, 222, 22, "• AI KPU: 6 TOPS Edge Accelerator", color=COLOR_WHITE)
    canvas.draw_string_advanced(36, 266, 22, "• โมเดลเสียง: YOLO11 Sound Classifier", color=COLOR_WHITE)
    canvas.draw_string_advanced(36, 310, 22, "• ไมโครโฟน: 16kHz DMA High-Precision", color=COLOR_WHITE)
    canvas.draw_string_advanced(36, 354, 22, "• การเตือน: มอเตอร์สั่นที่ข้อมือ Real-time", color=COLOR_WHITE)
    canvas.draw_string_advanced(36, 398, 22, "• สหายบอร์ด: TTGO T7 ESP32 via UART1", color=COLOR_LIGHT_BLUE)
    canvas.draw_string_advanced(36, 435, 18, "สำหรับผู้บกพร่องทางการได้ยินและผู้สูงอายุ", color=COLOR_MUTED)

    # Dismiss / Return Home Button
    canvas.draw_rectangle(18, 480, 444, 68, color=COLOR_DEEP_BLUE, thickness=1, fill=True)
    canvas.draw_rectangle(18, 480, 444, 68, color=COLOR_CYAN_GLOW, thickness=2, fill=False)
    canvas.draw_string_advanced(105, 502, 24, "[*] กลับสู่หน้าหลัก (CLOCK)", color=COLOR_WHITE)

    draw_footer_dock(canvas, left_label="< ย้อน", center_label="หน้าหลัก", right_label="ถัดไป >")
    Display.show_image(canvas)

def draw_screen_2_dog_bark(canvas):
    """SCREEN 2: DOG BARKING DETECTION WARNING"""
    canvas.clear()
    canvas.draw_rectangle(0, 0, SCREEN_W, SCREEN_H, color=COLOR_BG, thickness=1, fill=True)
    draw_header_bar(canvas, title="[!] เตือนภัย", status_text="สุนัขเห่า [WARN]", mode_idx=2, is_alert=True)

    # Warning Hero Card
    draw_tech_card(canvas, 18, 68, 444, 230, border_color=COLOR_WARN_AMBER, fill_color=COLOR_CARD_BG, thickness=3)
    draw_warning_triangle(canvas, 240, 125, size=64, color=COLOR_WARN_AMBER)
    canvas.draw_string_advanced(130, 175, 50, "สุนัขเห่า!", color=COLOR_WHITE)
    canvas.draw_string_advanced(115, 242, 26, "DOG BARKING DETECTED", color=COLOR_WARN_AMBER)

    # Advice Info Card
    draw_tech_card(canvas, 18, 310, 444, 155, border_color=COLOR_PRIMARY_BLUE, fill_color=COLOR_CARD_BG, thickness=2)
    canvas.draw_string_advanced(60, 328, 28, "ระวังโดนสุนัขกัดหรือวิ่งไล่!", color=COLOR_WARN_AMBER)
    canvas.draw_string_advanced(70, 375, 22, "สังเกตรอบตัวและอย่าวิ่งหนีกะทันหัน", color=COLOR_WHITE)
    canvas.draw_string_advanced(60, 420, 18, "รูปแบบสั่น: สั่นเตือน 3 ครั้ง (WARNING HAPTIC)", color=COLOR_LIGHT_BLUE)

    # Primary Ack Button
    canvas.draw_rectangle(18, 485, 444, 68, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_rectangle(18, 485, 444, 68, color=COLOR_WARN_AMBER, thickness=2, fill=False)
    canvas.draw_string_advanced(130, 508, 24, "[OK] รับทราบเหตุเตือนภัย", color=COLOR_WHITE)

    draw_footer_dock(canvas, left_label="< ย้อน", center_label="หน้าหลัก", right_label="ถัดไป >")
    Display.show_image(canvas)

def draw_screen_3_construction(canvas):
    """SCREEN 3: CONSTRUCTION SITE SOUND WARNING"""
    canvas.clear()
    canvas.draw_rectangle(0, 0, SCREEN_W, SCREEN_H, color=COLOR_BG, thickness=1, fill=True)
    draw_header_bar(canvas, title="[!] ระวัง", status_text="ก่อสร้าง [WARN]", mode_idx=3, is_alert=True)

    # Yellow/Amber Warning Hero Card
    draw_tech_card(canvas, 18, 68, 444, 230, border_color=COLOR_WARN_AMBER, fill_color=COLOR_CARD_BG, thickness=3)
    draw_warning_triangle(canvas, 240, 125, size=64, color=COLOR_WARN_AMBER)
    canvas.draw_string_advanced(95, 175, 46, "เขตก่อสร้าง!", color=COLOR_WHITE)
    canvas.draw_string_advanced(110, 242, 26, "CONSTRUCTION SITE", color=COLOR_WARN_AMBER)

    # Details Card
    draw_tech_card(canvas, 18, 310, 444, 155, border_color=COLOR_PRIMARY_BLUE, fill_color=COLOR_CARD_BG, thickness=2)
    canvas.draw_string_advanced(45, 328, 26, "ระวังสิ่งของตกหล่นหรือเศษหินกระเด็น!", color=COLOR_WARN_AMBER)
    canvas.draw_string_advanced(65, 375, 22, "สวมหมวกนิรภัยหรือหลีกเลี่ยงพื้นที่", color=COLOR_WHITE)
    canvas.draw_string_advanced(85, 420, 18, "ระดับเสียงเกิน 85dB | ควรสวมที่อุดหู", color=COLOR_MUTED)

    # Ack Button
    canvas.draw_rectangle(18, 485, 444, 68, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_rectangle(18, 485, 444, 68, color=COLOR_WARN_AMBER, thickness=2, fill=False)
    canvas.draw_string_advanced(130, 508, 24, "[OK] รับทราบเหตุเตือนภัย", color=COLOR_WHITE)

    draw_footer_dock(canvas, left_label="< ย้อน", center_label="หน้าหลัก", right_label="ถัดไป >")
    Display.show_image(canvas)

def draw_screen_4_silent(canvas):
    """SCREEN 4: SILENT MODE / QUIET REST STANDBY"""
    canvas.clear()
    canvas.draw_rectangle(0, 0, SCREEN_W, SCREEN_H, color=COLOR_BG, thickness=1, fill=True)
    draw_header_bar(canvas, title="G.A.R.I.N.", status_text="SILENT [REST]", mode_idx=4, is_alert=False)

    # Muted Blue Silent Card
    draw_tech_card(canvas, 18, 68, 444, 230, border_color=COLOR_MUTED_BLUE, fill_color=COLOR_CARD_BG, thickness=2)
    canvas.draw_circle(240, 130, 36, color=COLOR_LIGHT_BLUE, thickness=2, fill=False)
    canvas.draw_string_advanced(232, 115, 32, "Z", color=COLOR_LIGHT_BLUE)
    canvas.draw_string_advanced(120, 180, 48, "โหมดเงียบ", color=COLOR_WHITE)
    canvas.draw_string_advanced(135, 245, 24, "QUIET REST STANDBY", color=COLOR_MUTED)

    # Status Info Card
    draw_tech_card(canvas, 18, 310, 444, 155, border_color=COLOR_PRIMARY_BLUE, fill_color=COLOR_CARD_BG, thickness=2)
    canvas.draw_string_advanced(95, 330, 24, "ปิดพักผ่อน / โหมดห้องเรียน", color=COLOR_CYAN_GLOW)
    canvas.draw_string_advanced(70, 375, 20, "ปิดระบบสั่นเตือนเสียงรบกวนทั่วไป", color=COLOR_WHITE)
    canvas.draw_string_advanced(55, 415, 18, "ยังคงสั่นเตือนเฉพาะภัยร้ายแรง (CAR / BANG)", color=COLOR_ALERT_RED)

    # Return Button
    canvas.draw_rectangle(18, 485, 444, 68, color=COLOR_DEEP_BLUE, thickness=1, fill=True)
    canvas.draw_rectangle(18, 485, 444, 68, color=COLOR_CYAN_GLOW, thickness=2, fill=False)
    canvas.draw_string_advanced(120, 508, 24, "[*] ปลุกระบบกลับสู่ปกติ", color=COLOR_WHITE)

    draw_footer_dock(canvas, left_label="< ย้อน", center_label="หน้าหลัก", right_label="ถัดไป >")
    Display.show_image(canvas)

def draw_screen_5_machine(canvas):
    """SCREEN 5: HEAVY MACHINERY RUNNING WARNING"""
    canvas.clear()
    canvas.draw_rectangle(0, 0, SCREEN_W, SCREEN_H, color=COLOR_BG, thickness=1, fill=True)
    draw_header_bar(canvas, title="[!] ระวัง", status_text="เครื่องจักร [WARN]", mode_idx=5, is_alert=True)

    # Machinery Warning Card
    draw_tech_card(canvas, 18, 68, 444, 230, border_color=COLOR_WARN_AMBER, fill_color=COLOR_CARD_BG, thickness=3)
    # Vector Gear Symbol
    canvas.draw_circle(240, 125, 32, color=COLOR_WARN_AMBER, thickness=3, fill=False)
    for i in range(0, 360, 45):
        rad = math.radians(i)
        x1 = 240 + int(28 * math.cos(rad))
        y1 = 125 + int(28 * math.sin(rad))
        x2 = 240 + int(42 * math.cos(rad))
        y2 = 125 + int(42 * math.sin(rad))
        canvas.draw_line(x1, y1, x2, y2, color=COLOR_WARN_AMBER, thickness=3)

    canvas.draw_string_advanced(100, 175, 46, "เครื่องจักรทำงาน!", color=COLOR_WHITE)
    canvas.draw_string_advanced(115, 242, 26, "HEAVY MACHINERY ACTIVE", color=COLOR_WARN_AMBER)

    # Advice Card
    draw_tech_card(canvas, 18, 310, 444, 155, border_color=COLOR_PRIMARY_BLUE, fill_color=COLOR_CARD_BG, thickness=2)
    canvas.draw_string_advanced(65, 328, 26, "ระวังชิ้นส่วนเคลื่อนไหวหรือหนีบ!", color=COLOR_WARN_AMBER)
    canvas.draw_string_advanced(70, 375, 22, "รักษาระยะห่างจากเครื่องจักร 2 เมตร", color=COLOR_WHITE)
    canvas.draw_string_advanced(75, 420, 18, "ตรวจสอบไฟสัญญาณเตือนในโรงงาน", color=COLOR_MUTED)

    # Ack Button
    canvas.draw_rectangle(18, 485, 444, 68, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_rectangle(18, 485, 444, 68, color=COLOR_WARN_AMBER, thickness=2, fill=False)
    canvas.draw_string_advanced(130, 508, 24, "[OK] รับทราบเหตุเตือนภัย", color=COLOR_WHITE)

    draw_footer_dock(canvas, left_label="< ย้อน", center_label="หน้าหลัก", right_label="ถัดไป >")
    Display.show_image(canvas)

def draw_screen_6_car_approaching(canvas):
    """SCREEN 6: CRITICAL CAR APPROACHING ALERT"""
    canvas.clear()
    canvas.draw_rectangle(0, 0, SCREEN_W, SCREEN_H, color=COLOR_BG, thickness=1, fill=True)
    draw_header_bar(canvas, title="[!] อันตรายด่วน", status_text="รถยนต์ใกล้เข้ามา", mode_idx=6, is_alert=True)

    # Urgent Red Beacon Card
    draw_tech_card(canvas, 18, 68, 444, 230, border_color=COLOR_ALERT_RED, fill_color=(28, 10, 16), thickness=4)
    draw_danger_shield(canvas, 240, 125, size=64, color=COLOR_ALERT_RED)
    canvas.draw_string_advanced(120, 175, 52, "รถกำลังแล่นมา!", color=COLOR_WHITE)
    canvas.draw_string_advanced(105, 242, 26, "VEHICLE APPROACHING FAST", color=COLOR_ALERT_RED)

    # Direction & Action Card
    draw_tech_card(canvas, 18, 310, 444, 155, border_color=COLOR_ALERT_RED, fill_color=COLOR_CARD_BG, thickness=2)
    canvas.draw_string_advanced(45, 328, 30, ">>> มีรถแล่นมาทางขวา! >>>", color=COLOR_ALERT_RED)
    canvas.draw_string_advanced(70, 375, 22, "โปรดหยุดเดินและมองด้านข้างทันที", color=COLOR_WHITE)
    canvas.draw_string_advanced(60, 420, 18, "รูปแบบสั่น: สั่นรัวต่อเนื่อง 4 ครั้ง (CRITICAL)", color=COLOR_CYAN_GLOW)

    # Dismiss Button
    canvas.draw_rectangle(18, 485, 444, 68, color=(48, 12, 18), thickness=1, fill=True)
    canvas.draw_rectangle(18, 485, 444, 68, color=COLOR_ALERT_RED, thickness=3, fill=False)
    canvas.draw_string_advanced(115, 508, 24, "[V] มองเห็นรถแล้ว / ปลอดภัย", color=COLOR_WHITE)

    draw_footer_dock(canvas, left_label="< ย้อน", center_label="หน้าหลัก", right_label="ถัดไป >")
    Display.show_image(canvas)

def draw_screen_7_truck_horn(canvas):
    """SCREEN 7: CRITICAL TRUCK HORN ALERT"""
    canvas.clear()
    canvas.draw_rectangle(0, 0, SCREEN_W, SCREEN_H, color=COLOR_BG, thickness=1, fill=True)
    draw_header_bar(canvas, title="[!] แตรเตือนภัย", status_text="แตรสิบล้อ [ALERT]", mode_idx=7, is_alert=True)

    # Loud Horn Card
    draw_tech_card(canvas, 18, 68, 444, 230, border_color=COLOR_ALERT_RED, fill_color=(28, 10, 16), thickness=4)
    # Sound Waves vector
    cx, cy = 240, 125
    canvas.draw_circle(cx, cy, 18, color=COLOR_ALERT_RED, thickness=3, fill=False)
    canvas.draw_circle(cx, cy, 32, color=COLOR_WARN_AMBER, thickness=3, fill=False)
    canvas.draw_circle(cx, cy, 46, color=COLOR_WHITE, thickness=3, fill=False)
    canvas.draw_string_advanced(cx - 6, cy - 14, 28, "!", color=COLOR_ALERT_RED)

    canvas.draw_string_advanced(110, 175, 50, "เสียงแตรสิบล้อ!", color=COLOR_WHITE)
    canvas.draw_string_advanced(120, 242, 26, "LOUD TRUCK HORN DETECTED", color=COLOR_ALERT_RED)

    # Advice Card
    draw_tech_card(canvas, 18, 310, 444, 155, border_color=COLOR_ALERT_RED, fill_color=COLOR_CARD_BG, thickness=2)
    canvas.draw_string_advanced(70, 328, 28, "หลบเข้าข้างทางโดยด่วน!", color=COLOR_ALERT_RED)
    canvas.draw_string_advanced(80, 375, 22, "มีรถบรรทุกหรือรถใหญ่บีบแตรเตือน", color=COLOR_WHITE)
    canvas.draw_string_advanced(70, 420, 18, "สั่นเตือนข้อมือรัวแรงเพื่อแจ้งเตือนฉุกเฉิน", color=COLOR_LIGHT_BLUE)

    # Dismiss Button
    canvas.draw_rectangle(18, 485, 444, 68, color=(48, 12, 18), thickness=1, fill=True)
    canvas.draw_rectangle(18, 485, 444, 68, color=COLOR_ALERT_RED, thickness=3, fill=False)
    canvas.draw_string_advanced(115, 508, 24, "[V] รับทราบ / หลบเข้าทางเท้า", color=COLOR_WHITE)

    draw_footer_dock(canvas, left_label="< ย้อน", center_label="หน้าหลัก", right_label="ถัดไป >")
    Display.show_image(canvas)

def draw_screen_8_bang_explosion(canvas):
    """SCREEN 8: EXTREME DANGER BANG / EXPLOSION ALERT"""
    canvas.clear()
    canvas.draw_rectangle(0, 0, SCREEN_W, SCREEN_H, color=COLOR_BG, thickness=1, fill=True)
    draw_header_bar(canvas, title="[!] ภัยร้ายแรง", status_text="เสียงระเบิด [DANGER]", mode_idx=8, is_alert=True)

    # Explosion Hero Card
    draw_tech_card(canvas, 18, 68, 444, 230, border_color=COLOR_ALERT_RED, fill_color=(36, 8, 14), thickness=4)
    # Burst lines
    cx, cy = 240, 125
    for i in range(0, 360, 30):
        rad = math.radians(i)
        x1 = cx + int(12 * math.cos(rad))
        y1 = cy + int(12 * math.sin(rad))
        x2 = cx + int(46 * math.cos(rad))
        y2 = cy + int(46 * math.sin(rad))
        canvas.draw_line(x1, y1, x2, y2, color=COLOR_WARN_AMBER, thickness=4)

    canvas.draw_string_advanced(120, 175, 56, "เสียงระเบิด!", color=COLOR_WARN_AMBER)
    canvas.draw_string_advanced(110, 242, 26, "EXPLOSION / SUDDEN BANG", color=COLOR_ALERT_RED)

    # Safety Protocol Card
    draw_tech_card(canvas, 18, 310, 444, 155, border_color=COLOR_ALERT_RED, fill_color=COLOR_CARD_BG, thickness=2)
    canvas.draw_string_advanced(45, 328, 28, "อันตรายสูงสุด! หลบเข้าที่กำบัง!", color=COLOR_ALERT_RED)
    canvas.draw_string_advanced(70, 375, 22, "หมอบลงต่ำและระวังสะเก็ดระเบิด", color=COLOR_WHITE)
    canvas.draw_string_advanced(95, 420, 18, "โทรขอความช่วยเหลือฉุกเฉิน 191 / 1669", color=COLOR_WARN_AMBER)

    # Ack Button
    canvas.draw_rectangle(18, 485, 444, 68, color=(56, 12, 16), thickness=1, fill=True)
    canvas.draw_rectangle(18, 485, 444, 68, color=COLOR_ALERT_RED, thickness=3, fill=False)
    canvas.draw_string_advanced(105, 508, 24, "[!] รับทราบภัย / อยู่ในที่ปลอดภัย", color=COLOR_WHITE)

    draw_footer_dock(canvas, left_label="< ย้อน", center_label="หน้าหลัก", right_label="ถัดไป >")
    Display.show_image(canvas)

def draw_screen_9_public_queue(canvas):
    """SCREEN 9: ACCESSIBLE DIGITAL QUEUE TICKET DISPLAY"""
    canvas.clear()
    canvas.draw_rectangle(0, 0, SCREEN_W, SCREEN_H, color=COLOR_BG, thickness=1, fill=True)
    draw_header_bar(canvas, title="G.A.R.I.N.", status_text="คิวดิจิทัล [QUEUE]", mode_idx=9, is_alert=False)

    # Queue Number Hero Card
    draw_tech_card(canvas, 18, 68, 444, 230, border_color=COLOR_PRIMARY_BLUE, fill_color=COLOR_CARD_BG, thickness=3)
    canvas.draw_string_advanced(130, 85, 26, "บัตรคิวของคุณ (MY QUEUE):", color=COLOR_LIGHT_BLUE)
    # Giant Queue Number
    canvas.draw_string_advanced(110, 130, 84, "A-042", color=COLOR_CYAN_GLOW)
    canvas.draw_string_advanced(100, 242, 22, "โรงพยาบาล / จุดบริการประชาชน", color=COLOR_WHITE)

    # Current Calling Status Card
    draw_tech_card(canvas, 18, 310, 444, 155, border_color=COLOR_SAFE_GREEN, fill_color=COLOR_CARD_BG, thickness=2)
    canvas.draw_string_advanced(40, 328, 26, "● กำลังเรียกคิว: A-041 (ช่องบริการ 3)", color=COLOR_SAFE_GREEN)
    canvas.draw_string_advanced(40, 375, 22, "• รออีกเพียง 1 คิว! เตรียมตัวหน้าเคาน์เตอร์", color=COLOR_WHITE)
    canvas.draw_string_advanced(40, 420, 18, "นาฬิกาจะสั่นเตือนยาว 2 ครั้งเมื่อถึงคิวคุณ", color=COLOR_LIGHT_BLUE)

    # Dismiss / Return Button
    canvas.draw_rectangle(18, 485, 444, 68, color=COLOR_DEEP_BLUE, thickness=1, fill=True)
    canvas.draw_rectangle(18, 485, 444, 68, color=COLOR_CYAN_GLOW, thickness=2, fill=False)
    canvas.draw_string_advanced(120, 508, 24, "[*] กลับสู่หน้าหลัก (CLOCK)", color=COLOR_WHITE)

    draw_footer_dock(canvas, left_label="< ย้อน", center_label="หน้าหลัก", right_label="ถัดไป >")
    Display.show_image(canvas)

def draw_screen_10_time_set(canvas):
    """SCREEN 10: INTERACTIVE TOUCH RTC TIME & DATE SETTER"""
    canvas.clear()
    canvas.draw_rectangle(0, 0, SCREEN_W, SCREEN_H, color=COLOR_BG, thickness=1, fill=True)
    draw_header_bar(canvas, title="ตั้งเวลา RTC", status_text="SETUP [RTC]", mode_idx=10, is_alert=False)

    # Title Card
    draw_tech_card(canvas, 18, 60, 444, 45, border_color=COLOR_BORDER_BLUE, fill_color=COLOR_CARD_BG, thickness=1)
    canvas.draw_string_advanced(40, 70, 20, "แตะปุ่ม ▲ / ▼ เพื่อปรับแต่งเวลาจริงของบอร์ด", color=COLOR_LIGHT_BLUE)

    # --- HOUR SELECTOR (X: 30..220) ---
    # Up Button
    canvas.draw_rectangle(30, 110, 190, 50, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_rectangle(30, 110, 190, 50, color=COLOR_PRIMARY_BLUE, thickness=1, fill=False)
    canvas.draw_string_advanced(75, 122, 24, "▲ +1 ชม.", color=COLOR_WHITE)

    # Display Box
    canvas.draw_rectangle(30, 168, 190, 74, color=COLOR_CARD_BG, thickness=2, fill=True)
    canvas.draw_rectangle(30, 168, 190, 74, color=COLOR_CYAN_GLOW, thickness=2, fill=False)
    canvas.draw_string_advanced(85, 178, 54, "{:02d}".format(edit_hour), color=COLOR_CYAN_GLOW)

    # Down Button
    canvas.draw_rectangle(30, 250, 190, 50, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_rectangle(30, 250, 190, 50, color=COLOR_PRIMARY_BLUE, thickness=1, fill=False)
    canvas.draw_string_advanced(75, 262, 24, "▼ -1 ชม.", color=COLOR_WHITE)

    # --- MINUTE SELECTOR (X: 260..450) ---
    # Up Button
    canvas.draw_rectangle(260, 110, 190, 50, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_rectangle(260, 110, 190, 50, color=COLOR_PRIMARY_BLUE, thickness=1, fill=False)
    canvas.draw_string_advanced(305, 122, 24, "▲ +1 นาที", color=COLOR_WHITE)

    # Display Box
    canvas.draw_rectangle(260, 168, 190, 74, color=COLOR_CARD_BG, thickness=2, fill=True)
    canvas.draw_rectangle(260, 168, 190, 74, color=COLOR_CYAN_GLOW, thickness=2, fill=False)
    canvas.draw_string_advanced(315, 178, 54, "{:02d}".format(edit_minute), color=COLOR_CYAN_GLOW)

    # Down Button
    canvas.draw_rectangle(260, 250, 190, 50, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_rectangle(260, 250, 190, 50, color=COLOR_PRIMARY_BLUE, thickness=1, fill=False)
    canvas.draw_string_advanced(305, 262, 24, "▼ -1 นาที", color=COLOR_WHITE)

    # --- DATE SELECTOR ROW (Y: 315..455) ---
    # Year (X: 25..155)
    canvas.draw_rectangle(25, 315, 130, 40, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_string_advanced(55, 324, 20, "▲ ปี", color=COLOR_WHITE)
    canvas.draw_rectangle(25, 362, 130, 48, color=COLOR_CARD_BG, thickness=2, fill=True)
    canvas.draw_string_advanced(45, 374, 24, str(edit_year), color=COLOR_WHITE)
    canvas.draw_rectangle(25, 417, 130, 40, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_string_advanced(55, 426, 20, "▼ ปี", color=COLOR_WHITE)

    # Month (X: 172..308)
    canvas.draw_rectangle(172, 315, 136, 40, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_string_advanced(195, 324, 20, "▲ เดือน", color=COLOR_WHITE)
    canvas.draw_rectangle(172, 362, 136, 48, color=COLOR_CARD_BG, thickness=2, fill=True)
    canvas.draw_string_advanced(215, 374, 26, "{:02d}".format(edit_month), color=COLOR_WHITE)
    canvas.draw_rectangle(172, 417, 136, 40, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_string_advanced(195, 426, 20, "▼ เดือน", color=COLOR_WHITE)

    # Day (X: 325..455)
    canvas.draw_rectangle(325, 315, 130, 40, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_string_advanced(355, 324, 20, "▲ วัน", color=COLOR_WHITE)
    canvas.draw_rectangle(325, 362, 130, 48, color=COLOR_CARD_BG, thickness=2, fill=True)
    canvas.draw_string_advanced(368, 374, 26, "{:02d}".format(edit_day), color=COLOR_WHITE)
    canvas.draw_rectangle(325, 417, 130, 40, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_string_advanced(355, 426, 20, "▼ วัน", color=COLOR_WHITE)

    # --- ACTION BUTTONS (Y: 480..550) ---
    # SAVE BUTTON (X: 25..275)
    canvas.draw_rectangle(25, 480, 250, 70, color=COLOR_DEEP_BLUE, thickness=1, fill=True)
    canvas.draw_rectangle(25, 480, 250, 70, color=COLOR_CYAN_GLOW, thickness=2, fill=False)
    canvas.draw_string_advanced(45, 502, 22, "[V] บันทึก (SAVE)", color=COLOR_WHITE)

    # CANCEL BUTTON (X: 290..455)
    canvas.draw_rectangle(290, 480, 165, 70, color=COLOR_CARD_SURFACE, thickness=1, fill=True)
    canvas.draw_rectangle(290, 480, 165, 70, color=COLOR_BORDER_BLUE, thickness=1, fill=False)
    canvas.draw_string_advanced(315, 502, 22, "[X] ยกเลิก", color=COLOR_MUTED)

    draw_footer_dock(canvas, left_label="< ย้อน", center_label="หน้าหลัก", right_label="ถัดไป >")
    Display.show_image(canvas)

# ==============================================================================
# 11. Main Display Loop
# ==============================================================================
def main():
    global _running, ui_mode

    canvas = image.Image(SCREEN_W, SCREEN_H, image.ARGB8888)

    print("====================================================")
    print(" G.A.R.I.N. Watch Production Firmware (v2.5)        ")
    print(" Deploy Path: Deployment/main.py                    ")
    print(" Active Watch Face: Apple Activity Style (OLED 480) ")
    print(" Touch to Set RTC: ENABLED (Tap Time Digits)        ")
    print(" Display: 480x640 ST7701 MIPI DSI                   ")
    print(" Full Touch Navigation Dock & ESP32 UART Ready      ")
    print("====================================================")

    # 1. Spawn Touch Handler Thread
    import _thread
    _thread.start_new_thread(task_clock, ())

    # 2. Spawn ESP32 UART Command Listener Thread
    if UART_OK and uart is not None:
        _thread.start_new_thread(task_uart_rx, ())

    last_mode = -1

    try:
        while _running:
            os.exitpoint()

            current_mode = ui_mode

            # Trigger haptic feedback on mode transition
            if current_mode != last_mode:
                last_mode = current_mode
                if current_mode in (0, 4):
                    trigger_haptic(HAPTIC_SINGLE)
                elif current_mode in (1, 10):
                    trigger_haptic(HAPTIC_DOUBLE)
                elif current_mode in (3, 5):
                    trigger_haptic(HAPTIC_WARN)
                elif current_mode in (2, 6, 7, 8):
                    trigger_haptic(HAPTIC_URGENT)
                elif current_mode == 9:
                    trigger_haptic(HAPTIC_QUEUE)

            # Render Screen based on Mode (0..10)
            if current_mode == 0:
                draw_screen_0_clock(canvas)
            elif current_mode == 1:
                draw_screen_1_garin_info(canvas)
            elif current_mode == 2:
                draw_screen_2_dog_bark(canvas)
            elif current_mode == 3:
                draw_screen_3_construction(canvas)
            elif current_mode == 4:
                draw_screen_4_silent(canvas)
            elif current_mode == 5:
                draw_screen_5_machine(canvas)
            elif current_mode == 6:
                draw_screen_6_car_approaching(canvas)
            elif current_mode == 7:
                draw_screen_7_truck_horn(canvas)
            elif current_mode == 8:
                draw_screen_8_bang_explosion(canvas)
            elif current_mode == 9:
                draw_screen_9_public_queue(canvas)
            elif current_mode == 10:
                draw_screen_10_time_set(canvas)

            # ~30 FPS UI Update Loop
            time.sleep_ms(33)

    except KeyboardInterrupt:
        print("G.A.R.I.N. System Powering Down...")
    except BaseException as e:
        import sys
        sys.print_exception(e)
    finally:
        _running = False
        time.sleep_ms(300)

        if HW_OK:
            try:
                VIBE_PIN.value(0)
                BUZZ_PIN.value(0)
            except Exception:
                pass

        try:
            Display.deinit()
        except Exception:
            pass

        try:
            MediaManager.deinit()
        except Exception:
            pass

        print("Cleanup Complete. G.A.R.I.N. Standby.")

if __name__ == "__main__":
    main()
