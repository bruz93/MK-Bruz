import telebot
from telebot import types
import math
import re
from config import TELEGRAM_TOKEN
from menu import get_menu
from interface_list import get_interface_list
from pppoe_list import get_pppoe_list
from ip_address_list import get_ip_list
from dns import get_dns
from neighbor_list import get_neighbor_list
from route_list import get_route_list
from interface_management import disable_interface, enable_interface, change_interface_name
from pppoe_management import add_pppoe_user, disable_pppoe, enable_pppoe, change_pppoe_name, remove_pppoe
from ip_address_management import add_ip_address, disable_ip, enable_ip, change_ip_interface, remove_ip
from route_management import add_route, disable_route, enable_route, change_route_distance, remove_route
from interface_status import get_interface_status
from hotspot_user import get_hotspot_user_data
from hotspot_find_user import find_hotspot_user
from hotspot_detail_user import get_hotspot_user_details
from hotspot_delete_user import delete_hotspot_user
from hotspot_delete_active import hotspot_delete_active
from hotspot_profile_list import get_hotspot_profile_list
from hotspot_ip_binding import get_hotspot_ip_binding
from hotspot_gen_vc import get_profile_list, generate_vouchers
from queue_list import get_queue_list
from queue_management import disable_queue, enable_queue, change_queue_limit
from netwatch_list import get_netwatch_list
from netwatch_management import add_netwatch, disable_netwatch, enable_netwatch, change_netwatch_host, remove_netwatch
from netwatch_id import get_netwatch_id
from logger import logger
import threading

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Dictionary to keep track of interface rename states
interface_rename_state = {}
pppoe_rename_state = {}
ip_set_state = {}
dns_set_state = {}
route_set_state = {}
queue_pages = {}
queue_set_state = {}
netwatch_set_state = {}
voucher_generation_state = {}
hotspot_state = {}

# Event to stop the monitoring thread
monitoring_stop_event = threading.Event()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info(f"Received /start command from {message.chat.id}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Interface"))
    markup.add(types.KeyboardButton("PPPOE"))
    markup.add(types.KeyboardButton("IP"))
    markup.add(types.KeyboardButton("Hotspot"))
    markup.add(types.KeyboardButton("Queue"))
    markup.add(types.KeyboardButton("Netwatch"))
    bot.reply_to(message, "Selamat datang di Bot MikroTik! Silakan pilih menu:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Interface")
def interface_menu(message):
    logger.info(f"Interface menu selected by {message.chat.id}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("List"))
    markup.add(types.KeyboardButton("Disable"))
    markup.add(types.KeyboardButton("Enable"))
    markup.add(types.KeyboardButton("Monitor"))
    markup.add(types.KeyboardButton("Rename"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih perintah interface:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "PPPOE")
def pppoe_menu(message):
    logger.info(f"PPPOE menu selected by {message.chat.id}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("List-PPPOE"))
    markup.add(types.KeyboardButton("Add-PPPOE"))
    markup.add(types.KeyboardButton("Disable-PPPOE"))
    markup.add(types.KeyboardButton("Enable-PPPOE"))
    markup.add(types.KeyboardButton("Rename-PPPOE"))
    markup.add(types.KeyboardButton("Remove-PPPOE"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih perintah pppoe:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "IP")
def ip_menu(message):
    logger.info(f"IP menu selected by {message.chat.id}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("List-IP"))
    markup.add(types.KeyboardButton("Add-IP"))
    markup.add(types.KeyboardButton("Disable-IP"))
    markup.add(types.KeyboardButton("Enable-IP"))
    markup.add(types.KeyboardButton("Set-IP-Interface"))
    markup.add(types.KeyboardButton("Remove-IP"))
    markup.add(types.KeyboardButton("Dns-IP"))
    markup.add(types.KeyboardButton("Neighbor-IP"))
    markup.add(types.KeyboardButton("Route-IP"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih perintah IP:", reply_markup=markup)
    
@bot.message_handler(func=lambda message: message.text == "Dns-IP")
def dns_menu(message):
    logger.info(f"Dns menu selected by {message.chat.id}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("List-Dns"))
    # markup.add(types.KeyboardButton("Set-Dns"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih perintah dns:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Hotspot")
def hotspot_menu(message):
    logger.info(f"Hotspot menu selected by {message.chat.id}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Total"))
    markup.add(types.KeyboardButton("Cari"))
    markup.add(types.KeyboardButton("Detail"))
    markup.add(types.KeyboardButton("Hapus"))
    markup.add(types.KeyboardButton("Kick"))
    markup.add(types.KeyboardButton("Profile"))
    markup.add(types.KeyboardButton("Binding"))
    markup.add(types.KeyboardButton("Generate"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih perintah hotspot:", reply_markup=markup)
    
@bot.message_handler(func=lambda message: message.text == "Route-IP")
def route_menu(message):
    logger.info(f"Route menu selected by {message.chat.id}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("List-Route"))
    markup.add(types.KeyboardButton("Add-Route"))
    markup.add(types.KeyboardButton("Disable-Route"))
    markup.add(types.KeyboardButton("Enable-Route"))
    markup.add(types.KeyboardButton("Set-Route-Distance"))
    markup.add(types.KeyboardButton("Remove-Route"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih perintah route:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Queue")
def queue_menu(message):
    logger.info(f"Queue menu selected by {message.chat.id}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("List-Queue"))
    markup.add(types.KeyboardButton("Add-Queue"))
    markup.add(types.KeyboardButton("Disable-Queue"))
    markup.add(types.KeyboardButton("Enable-Queue"))
    markup.add(types.KeyboardButton("Limit"))
    markup.add(types.KeyboardButton("Remove-Queue"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih perintah Queue:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Netwatch")
def netwatch_menu(message):
    logger.info(f"IP menu selected by {message.chat.id}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("List-Netwatch"))
    markup.add(types.KeyboardButton("Add-Netwatch"))
    markup.add(types.KeyboardButton("Disable-Netwatch"))
    markup.add(types.KeyboardButton("Enable-Netwatch"))
    markup.add(types.KeyboardButton("Set-Netwatch-Host"))
    markup.add(types.KeyboardButton("Remove-Netwatch"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih perintah netwatch:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Kembali")
def main_menu(message):
    logger.info(f"Main menu selected by {message.chat.id}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Interface"))
    markup.add(types.KeyboardButton("PPPOE"))
    markup.add(types.KeyboardButton("IP"))
    markup.add(types.KeyboardButton("Hotspot"))
    markup.add(types.KeyboardButton("Queue"))
    markup.add(types.KeyboardButton("Netwatch"))
    bot.reply_to(message, "Silakan pilih menu:", reply_markup=markup)

# Interface Handlers
@bot.message_handler(func=lambda message: message.text == "List")
def send_interface_list(message):
    logger.info(f"Received List command from {message.chat.id}")
    interfaces = get_interface_list()
    interface_info = "\n".join([f"⏹️ {interface['name']} \n{interface['comment']} \n{interface['type']} {'✅' if interface['status'] == 'enabled' else '❌'}\n\n" for interface in interfaces])
    bot.reply_to(message, interface_info)

@bot.message_handler(func=lambda message: message.text == "Disable")
def disable_interface_menu(message):
    logger.info(f"Disable menu selected by {message.chat.id}")
    interfaces = get_interface_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for interface in interfaces:
        markup.add(types.KeyboardButton(f"Disable {interface['name']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih interface yang akan di-disable:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Disable "))
def handle_disable_interface(message):
    interface_name = message.text.split("Disable ")[1]
    logger.info(f"Received /interface_disable command for {interface_name} from {message.chat.id}")
    result = disable_interface(interface_name)
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text == "Enable")
def enable_interface_menu(message):
    logger.info(f"Enable menu selected by {message.chat.id}")
    interfaces = get_interface_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for interface in interfaces:
        markup.add(types.KeyboardButton(f"Enable {interface['name']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih interface yang akan di-enable:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Enable "))
def handle_enable_interface(message):
    interface_name = message.text.split("Enable ")[1]
    logger.info(f"Received /interface_enable command for {interface_name} from {message.chat.id}")
    result = enable_interface(interface_name)
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text == "Monitor")
def monitor_interface_menu(message):
    logger.info(f"Monitor menu selected by {message.chat.id}")
    interfaces = get_interface_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for interface in interfaces:
        markup.add(types.KeyboardButton(f"Monitor {interface['name']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih interface yang akan dimonitor:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Monitor "))
def handle_monitor_interface(message):
    interface_name = message.text.split("Monitor ")[1]
    logger.info(f"Received /interface_status command for {interface_name} from {message.chat.id}")
    monitoring_stop_event.clear()
    status = get_interface_status(interface_name)
    
    if isinstance(status, str) and status.startswith("Error"):
        bot.reply_to(message, status)
    else:
        formatted_status = (
            f"Monitoring Traffic {interface_name}\n\n"
            f"Upload: {int(status[0]['tx-bits-per-second']) / 1_000_000:.2f} Mbps ⬆️\n"
            f"Download: {int(status[0]['rx-bits-per-second']) / 1_000_000:.2f} Mbps ⬇️\n\n"
            "Tekan tombol ini untuk menghentikan proses monitoring."
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Stop", callback_data="stop_monitoring"))
        sent_message = bot.reply_to(message, formatted_status, reply_markup=markup)
        
        # Start monitoring in a new thread
        monitoring_thread = threading.Thread(target=monitor_interface_status, args=(message.chat.id, sent_message.message_id, interface_name))
        monitoring_thread.start()

@bot.callback_query_handler(func=lambda call: call.data == "stop_monitoring")
def stop_monitoring_callback(call):
    logger.info(f"Received stop monitoring command from {call.message.chat.id}")
    monitoring_stop_event.set()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Monitoring dihentikan.")

@bot.message_handler(func=lambda message: message.text == "Rename")
def rename_interface_menu(message):
    logger.info(f"Rename menu selected by {message.chat.id}")
    interfaces = get_interface_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for interface in interfaces:
        markup.add(types.KeyboardButton(f"Rename {interface['name']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih interface yang akan di-rename:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Rename "))
def handle_rename_interface(message):
    interface_name = message.text.split("Rename ")[1]
    logger.info(f"Received /interface_c_name command for {interface_name} from {message.chat.id}")
    interface_rename_state[message.chat.id] = interface_name
    bot.reply_to(message, f"Masukkan nama baru untuk interface {interface_name}:")

@bot.message_handler(func=lambda message: message.chat.id in interface_rename_state)
def handle_new_interface_name(message):
    old_name = interface_rename_state.pop(message.chat.id, None)
    if old_name:
        new_name = message.text.strip()
        logger.info(f"Renaming interface {old_name} to {new_name}")
        result = change_interface_name(old_name, new_name)
        bot.reply_to(message, result)
        bot.reply_to(message, "Gunakan perintah List untuk mengecek apakah nama interface sudah berhasil di ganti.")
    else:
        bot.reply_to(message, "Tidak ada permintaan perubahan nama interface yang aktif.")

def monitor_interface_status(chat_id, message_id, interface_name):
    import time
    previous_status = ""
    while not monitoring_stop_event.is_set():
        status = get_interface_status(interface_name)
        if isinstance(status, str) and status.startswith("Error"):
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=status)
            break
        else:
            formatted_status = (
                f"Monitoring Traffic {interface_name}\n\n"
                f"Upload: {int(status[0]['tx-bits-per-second']) / 1_000_000:.2f} Mbps ⬆️\n"
                f"Download: {int(status[0]['rx-bits-per-second']) / 1_000_000:.2f} Mbps ⬇️\n\n"
                "Tekan tombol ini untuk menghentikan proses monitoring."
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Stop", callback_data="stop_monitoring"))
            if formatted_status != previous_status:
                try:
                    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=formatted_status, reply_markup=markup)
                    previous_status = formatted_status
                except telebot.apihelper.ApiTelegramException as e:
                    if "message is not modified" in str(e):
                        continue
                    else:
                        raise e
        time.sleep(3)
        
# PPPOE Handler
@bot.message_handler(func=lambda message: message.text == "List-PPPOE")
def send_pppoe_list(message):
    logger.info(f"Received List command from {message.chat.id}")  # Pastikan logger terinisialisasi
    interfaces = get_pppoe_list()  # Fungsi ini mengembalikan pppoe_list seperti yang dicontohkan
    if not interfaces:
        bot.reply_to(message, "Tidak ada PPPoE interface yang ditemukan.")
        return
    # Membuat string informasi PPPoE untuk setiap interface, termasuk status, flags, comment, dan dynamic
    interface_info = "\n".join([  # Membuat format string untuk setiap interface
        f"⏹️ {interface['name']} (Interface: {interface['interface']}) # (Service-Name: {interface['service-name']}); (Default-Distance: {interface['default-route-distance']}); {interface['profile']} \n"
        f"# {'🔛 Enable' if interface['status'] == 'enabled' else '❌ Disable'} - {'✅ Running' if interface['flags'] == 'Running' else '❗ Not Running'} "
        f"- {'🔃 Dynamic' if interface['dynamic'] == 'Dynamic' else '🔒Static'}#\n Comment: {interface['comment']} ;\n\n"
        for interface in interfaces
    ])
    # Kirim balasan ke bot dengan informasi PPPoE
    bot.reply_to(message, interface_info)

@bot.message_handler(func=lambda message: message.text == "Add-PPPOE")
def add_pppoe_menu(message):
    logger.info(f"Add PPPoE menu selected by {message.chat.id}")
    bot.reply_to(
        message,
        "Masukkan detail PPPoE dalam format berikut:\n\n`name interface service_name user password profile`\n\nContoh:\n`pppoe-out ether service-name user password default`",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: " " in message.text and len(message.text.split()) == 6)
def handle_add_pppoe(message):
    try:
        # Parsing input
        name, interface, service_name, user, password, profile = map(str.strip, message.text.split())
        logger.info(f"Received Add PPPoE request: name={name}, interface={interface}, service_name={service_name}, user={user}, profile={profile}")
        # Panggil fungsi add_pppoe_user
        result = add_pppoe_user(name=name, interface=interface, service_name=service_name, user=user, password=password, profile=profile)
        # Balas dengan hasil
        bot.reply_to(message, result)
    except ValueError:
        bot.reply_to(
            message,
            "Format input tidak valid. Pastikan menggunakan format:\n`name interface service_name user password profile`",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to add PPPoE user: {e}")
        bot.reply_to(message, f"Gagal menambahkan PPPoE user. Error: {e}")
    
@bot.message_handler(func=lambda message: message.text == "Disable-PPPOE")
def disable_pppoe_menu(message):
    logger.info(f"Disable menu selected by {message.chat.id}")
    interfaces = get_pppoe_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for interface in interfaces:
        markup.add(types.KeyboardButton(f"Disable {interface['name']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih pppoe yang akan di-disable:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Disable-PPPOE "))
def handle_disable_pppoe(message):
    interface_name = message.text.split("Disable ")[1]
    logger.info(f"Received /pppoe_disable command for {interface_name} from {message.chat.id}")
    result = disable_pppoe(interface_name)
    bot.reply_to(message, result)
    
@bot.message_handler(func=lambda message: message.text == "Enable-PPPOE")
def enable_pppoe_menu(message):
    logger.info(f"Enable menu selected by {message.chat.id}")
    interfaces = get_pppoe_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for interface in interfaces:
        markup.add(types.KeyboardButton(f"Enable {interface['name']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih pppoe yang akan di-enable:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Enable-PPPOE "))
def handle_enable_pppoe(message):
    interface_name = message.text.split("Enable ")[1]
    logger.info(f"Received /pppoe_enable command for {interface_name} from {message.chat.id}")
    result = enable_pppoe(interface_name)
    bot.reply_to(message, result)
    
@bot.message_handler(func=lambda message: message.text == "Rename-PPPOE")
def rename_pppoe_menu(message):
    logger.info(f"Rename menu selected by {message.chat.id}")
    interfaces = get_pppoe_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for interface in interfaces:
        markup.add(types.KeyboardButton(f"Rename {interface['name']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih pppoe yang akan di-rename:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Rename-PPPOE "))
def handle_rename_pppoe(message):
    interface_name = message.text.split("Rename ")[1]
    logger.info(f"Received /pppoe_c_name command for {interface_name} from {message.chat.id}")
    pppoe_rename_state[message.chat.id] = interface_name
    bot.reply_to(message, f"Masukkan nama baru untuk interface {interface_name}:")

@bot.message_handler(func=lambda message: message.chat.id in pppoe_rename_state)
def handle_new_pppoe_name(message):
    old_name = pppoe_rename_state.pop(message.chat.id, None)
    if old_name:
        new_name = message.text.strip()
        logger.info(f"Renaming pppoe {old_name} to {new_name}")
        result = change_pppoe_name(old_name, new_name)
        bot.reply_to(message, result)
        bot.reply_to(message, "Gunakan perintah List untuk mengecek apakah nama interface sudah berhasil di ganti.")
    else:
        bot.reply_to(message, "Tidak ada permintaan perubahan nama interface yang aktif.")

@bot.message_handler(func=lambda message: message.text == "Remove-PPPOE")
def remove_pppoe_menu(message):
    logger.info(f"Remove menu selected by {message.chat.id}")
    interfaces = get_pppoe_list()
    if not interfaces:
        bot.reply_to(message, "Tidak ada PPPoE interface yang ditemukan.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for interface in interfaces:
        markup.add(types.KeyboardButton(f"Remove {interface['name']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih PPPoE interface yang akan dihapus:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Remove "))
def handle_remove_pppoe(message):
    interface_name = message.text.split("Remove ")[1]
    logger.info(f"Received /pppoe_remove command for {interface_name} from {message.chat.id}")
    result = remove_pppoe(interface_name)
    bot.reply_to(message, result)

# Handle Ip Address
@bot.message_handler(func=lambda message: message.text == "List-IP")
def send_ip_list(message):
    logger.info(f"Received List command from {message.chat.id}")  # Pastikan logger terinisialisasi
    ips = get_ip_list()  # Fungsi ini mengembalikan pppoe_list seperti yang dicontohkan
    if not ips:
        bot.reply_to(message, "Tidak ada PPPoE interface yang ditemukan.")
        return
    # Membuat string informasi PPPoE untuk setiap interface, termasuk status, flags, comment, dan dynamic
    ip_info = "\n".join([  # Membuat format string untuk setiap interface
        f"🏠 {ip['address']} (Actual-Interface: {ip['actual-interface']}) (Interface: {ip['interface']}) (Network: {ip['network']})"
        f"\n# {'🔛 Enable' if ip['status'] == 'enabled' else '❌ Disable'} - {'✅ Valid' if ip['invalid'] == 'valid' else '❗ Invalid'} "
        f"- {'🔃 Dynamic' if ip['dynamic'] == 'Dynamic' else '🔒Static'}# \nComment: {ip['comment']} ;\n\n"
        for ip in ips
    ])
    # Kirim balasan ke bot dengan informasi PPPoE
    bot.reply_to(message, ip_info)

@bot.message_handler(func=lambda message: message.text == "Add-IP")
def add_ip_menu(message):
    logger.info(f"Add IP menu selected by {message.chat.id}")
    bot.reply_to(
        message,
        "Masukkan detail IP dalam format berikut:\n\n`address interface comment`\n\nContoh:\n`192.168.1.1 ether1 test`",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: " " in message.text and len(message.text.split()) == 3)
def handle_add_ip(message):
    try:
        # Parsing input
        address, interface, comment = map(str.strip, message.text.split())
        logger.info(f"Received Add IP request: address={address}, interface={interface}, comment={comment}")
        # Panggil fungsi add_ip_address
        result = add_ip_address(address=address, interface=interface, comment=comment)
        # Balas dengan hasil
        bot.reply_to(message, result)
    except ValueError:
        bot.reply_to(
            message,
            "Format input tidak valid. Pastikan menggunakan format:\n`address interface comment`",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to add IP address: {e}")
        bot.reply_to(message, f"Gagal menambahkan IP address. Error: {e}")
    
@bot.message_handler(func=lambda message: message.text == "Disable-IP")
def disable_ip_menu(message):
    logger.info(f"Disable menu selected by {message.chat.id}")
    ips = get_ip_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for ip in ips:
        markup.add(types.KeyboardButton(f"Disable-IP {ip['address']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih ip yang akan di-disable:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Disable-IP "))
def handle_disable_ip(message):
    address = message.text.split("Disable-IP ")[1]
    logger.info(f"Received /ip_disable command for {address} from {message.chat.id}")
    result = disable_ip(address)
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text == "Enable-IP")
def enable_ip_menu(message):
    logger.info(f"Enable menu selected by {message.chat.id}")
    ips = get_ip_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for ip in ips:
        markup.add(types.KeyboardButton(f"Enable-IP {ip['address']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih ip yang akan di-enable:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Enable-IP "))
def handle_enable_ip(message):
    address = message.text.split("Enable-IP ")[1]
    logger.info(f"Received /ip_enable command for {address} from {message.chat.id}")
    result = enable_ip(address)
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text == "Set-IP-Interface")
def set_ip_menu(message):
    logger.info(f"Set-IP-Interface menu selected by {message.chat.id}")
    ips = get_ip_list()  # Mendapatkan daftar IP
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    # Membuat tombol untuk setiap IP yang ada
    for ip in ips:
        markup.add(types.KeyboardButton(f"Change {ip['address']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih IP yang akan di-set:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Change"))
def handle_set_ip(message):
    # Mengambil alamat IP dari pesan yang dikirimkan (setelah 'Change ')
    address = message.text.split("Change ")[1].strip()
    logger.info(f"Received command to change interface for IP {address} from {message.chat.id}")
    # Menyimpan alamat IP yang dipilih ke dalam state untuk pengguna
    ip_set_state[message.chat.id] = address
    bot.reply_to(message, f"Set interface baru untuk IP {address}: Silakan kirimkan nama interface baru dengan tipe pilihan berikut:\n\n- `ether`\n- `bridge`\n- `pppoe-out`\n- `vlan`\n\nContoh:\n`ether7`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in ip_set_state)
def handle_new_ip_interface(message):
    old_address = ip_set_state.pop(message.chat.id, None)
    if old_address:
        new_interface = message.text.strip()
        logger.info(f"Changing interface for IP {old_address} to {new_interface}")
        # Panggil fungsi untuk mengubah interface
        result = change_ip_interface(old_address, new_interface)
        # Kirimkan hasilnya ke pengguna
        bot.reply_to(message, result)
        bot.reply_to(message, "Gunakan perintah 'List' untuk mengecek apakah IP interface sudah berhasil diganti.")
    else:
        bot.reply_to(message, "Tidak ada permintaan perubahan IP interface yang aktif.")

@bot.message_handler(func=lambda message: message.text == "Remove-IP")
def remove_ip_menu(message):
    logger.info(f"Remove menu selected by {message.chat.id}")
    ips = get_ip_list()
    if not ips:
        bot.reply_to(message, "Tidak ada ip address yang ditemukan.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for ip in ips:
        markup.add(types.KeyboardButton(f"Remove-IP {ip['address']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih IP address yang akan dihapus:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Remove-IP "))
def handle_remove_ip(message):
    address = message.text.split("Remove-IP ")[1]
    logger.info(f"Received /ip_remove command for {address} from {message.chat.id}")
    result = remove_ip(address)
    bot.reply_to(message, result)
    
# handler Route
@bot.message_handler(func=lambda message: message.text == "List-Route")
def send_route_list(message):
    logger.info(f"Received List command from {message.chat.id}")  
    routes = get_route_list()  
    if not routes:
        bot.reply_to(message, "Tidak ada route yang ditemukan.")
        return
    route_info = "\n".join([  
        f"number: {route['.id']} \ndst-address: {route['dst-address']} \n(gateway: {route['gateway']}) \n(distance: {route['distance']}) \n(local-address: {route['local-address']}) \n(immediate-gw: {route['immediate-gw']}) \n(routing-table: {route['routing-table']}) \n(scope: {route['scope']}) \n(target-scope: {route['target-scope']}) \n(vrf-interface: {route['vrf-interface']})"
        f"\n# {'❌ Disable' if route['status'] == 'disabled' else '✅ Enabled'} - {'✅ active' if route['inactive'] == 'active' else '❌inactive'} - {'✅ ecmp' if route['ecmp'] == 'ecmp' else '❌ecmp'} - {'✅ hw-offloaded' if route['hw-offloaded'] == 'hw-offloaded' else '❌ hw-offloaded'} - {'✅ vpn' if route['vpn'] == 'vpn' else '❌vpn'}"
        f"- {'🔃 Dynamic' if route['dynamic'] == 'Dynamic' else '🔒Static'} - {'✅ connect' if route['connect'] == 'connect' else '❌disconnect'} \nComment: {route['comment']} ;\n\n"
        for route in routes
    ])
    # Kirim balasan ke bot dengan informasi 
    max_length = 4096
    for i in range(0, len(route_info), max_length):
        bot.reply_to(message, route_info[i:i + max_length])

@bot.message_handler(func=lambda message: message.text == "Add-Route")
def add_route_menu(message):
    logger.info(f"Add route menu selected by {message.chat.id}")
    bot.reply_to(
        message,
        "Masukkan detail route dalam format berikut:\n\n`dst-address gateway distance comment`\n\nContoh:\n`0.0.0.0/0 pppoe-out2 2 srouteFiberstar`",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: " " in message.text and len(message.text.split()) == 4)
def handle_add_route(message):
    try:
        # Parsing input
        dst_address, gateway, distance, comment = map(str.strip, message.text.split())
        logger.info(f"Received Add Route request: dst_address={dst_address}, gateway={gateway}, distance={distance}, comment={comment}")
        # Panggil fungsi add_ip_address
        result = add_route(dst_address=dst_address, gateway=gateway, distance=distance, comment=comment)
        # Balas dengan hasil
        bot.reply_to(message, result)
    except ValueError:
        bot.reply_to(
            message,
            "Format input tidak valid. Pastikan menggunakan format:\n`dst-address gateway distance comment`",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to add Route address: {e}")
        bot.reply_to(message, f"Gagal menambahkan IP Route. Error: {e}")
        
@bot.message_handler(func=lambda message: message.text == "Disable-Route")
def disable_route_menu(message):
    logger.info(f"Disable menu selected by {message.chat.id}")
    routes = get_route_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for route in routes:
        markup.add(types.KeyboardButton(f"Disable-Route {route['.id']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih route yang akan di-disable:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Disable-Route "))
def handle_disable_route(message):
    route_id = message.text.split("Disable-Route ")[1]
    logger.info(f"Received /route_disable command for {route_id} from {message.chat.id}")
    result = disable_route(route_id)
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text == "Enable-Route")
def enable_route_menu(message):
    logger.info(f"Enable menu selected by {message.chat.id}")
    routes = get_route_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for route in routes:
        markup.add(types.KeyboardButton(f"Enable-Route {route['.id']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih route yang akan di-enable:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Enable-Route "))
def handle_enable_route(message):
    route_id = message.text.split("Enable-Route ")[1]
    logger.info(f"Received /route_enable command for {route_id} from {message.chat.id}")
    result = enable_route(route_id)
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text == "Set-Route-Distance")
def distance_route_menu(message):
    logger.info(f"Distance menu selected by {message.chat.id}")
    routes = get_route_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for route in routes:
        markup.add(types.KeyboardButton(f"Distance {route['.id']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih route yang akan di-distance:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Distance "))
def handle_distance_route(message):
    try:
        route_id = message.text.split("Distance ")[1].strip()
        if not route_id:
            raise ValueError("Route ID kosong.")
        logger.info(f"Received /route_c_distance command for {route_id} from {message.chat.id}")
        route_set_state[message.chat.id] = route_id
        bot.reply_to(message, f"Masukkan distance baru untuk route {route_id}:")
    except IndexError:
        bot.reply_to(message, "Format pesan tidak valid. Gunakan 'Set-Route-Distance Distance <route_id>'.")

@bot.message_handler(func=lambda message: message.chat.id in route_set_state)
def handle_new_route_distance(message):
    old_distance = route_set_state.pop(message.chat.id, None)
    if old_distance:
        new_distance = message.text.strip()
        if not new_distance.isdigit() or int(new_distance) <= 0:
            bot.reply_to(message, "Distance harus berupa angka positif.")
            return
        logger.info(f"Distancing route {old_distance} to {new_distance}")
        result = change_route_distance(old_distance, new_distance)
        bot.reply_to(message, f"Hasil: {result}\nGunakan perintah List-Route untuk mengecek apakah distance route sudah berhasil di ganti.")
    else:
        bot.reply_to(message, "Tidak ada permintaan perubahan distance route yang aktif.")

@bot.message_handler(func=lambda message: message.text == "Remove-Route")
def remove_route_menu(message):
    logger.info(f"Remove menu selected by {message.chat.id}")
    routes = get_route_list()  
    if not routes:
        bot.reply_to(message, "Tidak ada route yang ditemukan.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for route in routes:
        markup.add(types.KeyboardButton(f"Remove-Route {route['.id']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih route yang akan dihapus:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Remove-Route "))
def handle_remove_route(message):
    route_id = message.text.split("Remove-Route ")[1].strip()
    logger.info(f"Received /route_remove command for {route_id} from {message.chat.id}")
    routes = get_route_list()
    if any(route['.id'] == route_id for route in routes): 
        result = remove_route(route_id)
        bot.reply_to(message, result)
    else:
        bot.reply_to(message, f"Route dengan id {route_id} tidak ditemukan.")

# handler neigbor
@bot.message_handler(func=lambda message: message.text == "Neighbor-IP")
def send_neighbor_list(message):
    logger.info(f"Received List command from {message.chat.id}")
    neighbors = get_neighbor_list()
    if not neighbors:
        bot.reply_to(message, "Neighbor list is empty.")
        return
    neighbor_info = "\n".join([
        f"Identity: {n.get('identity')}; \nInterface: {n.get('interface')}; \nBoard: {n.get('board')}; \n"
        f"Interface-Name: {n.get('interface-name')}; \nPlatform: {n.get('platform')}; \n"
        f"Mac-Address: {n.get('mac-address')}; \nSystem-Caps: {n.get('system-caps')}; \nCaps-Enabled: {n.get('system-caps-enabled')};\n"
        f"System-Description: {n.get('system-description')}; \nDiscovered by: {n.get('discovered-by')}; \n"
        f"{'✅ ipv6' if n.get('ipv6') == 'ipv6' else '❌ ipv6'}; \nVersion: {n.get('version')}; \n"
        f"Software-ID: {n.get('software-id')}; \nAddress: {n.get('address')}; \nAddress4: {n.get('address4')}; \n"
        f"Age: {n.get('age')}; \nUptime: {n.get('uptime')} ;\n\n"
        for n in neighbors
    ])
    max_length = 4096
    for i in range(0, len(neighbor_info), max_length):
        bot.reply_to(message, neighbor_info[i:i + max_length])

# handle dns
@bot.message_handler(func=lambda message: message.text == "List-Dns")
def send_dns_list(message):
    logger.info(f"Received List command from {message.chat.id}")
    dns = get_dns()
    dns_info = (
        f"Servers: {dns['servers']}\n"
        f"Dynamic Servers: {dns['dynamic-servers']}\n"
        f"{'allow-remote-requests✅' if dns['allow-remote-requests'] == 'checked' else 'allow-remote-requests❌'}\n"
    )
    bot.reply_to(message, dns_info)


# Hotspot Handlers
@bot.message_handler(func=lambda message: message.text == "Total")
def handle_hotspot_user(message):
    logger.info(f"Received /hotspot_user command from {message.chat.id}")
    result = get_hotspot_user_data()
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text == "Cari")
def handle_hotspot_find_user_prompt(message):
    hotspot_state[message.chat.id] = 'find_user'
    bot.reply_to(message, "Masukkan nama user yang akan dicari:")

@bot.message_handler(func=lambda message: message.text == "Detail")
def handle_hotspot_detail_user_prompt(message):
    hotspot_state[message.chat.id] = 'detail_user'
    bot.reply_to(message, "Masukkan nama user yang akan diperiksa secara detail:")

@bot.message_handler(func=lambda message: message.text == "Hapus")
def handle_hotspot_delete_user_prompt(message):
    hotspot_state[message.chat.id] = 'delete_user'
    bot.reply_to(message, "Masukkan nama user yang akan dihapus:")

@bot.message_handler(func=lambda message: message.text == "Kick")
def handle_hotspot_delete_active_user_prompt(message):
    hotspot_state[message.chat.id] = 'kick_user'
    bot.reply_to(message, "Masukkan nama user yang akan di-kick:")

@bot.message_handler(func=lambda message: message.chat.id in hotspot_state)
def handle_hotspot_actions(message):
    action = hotspot_state.pop(message.chat.id)
    user_name = message.text.strip()
    if action == 'find_user':
        result = find_hotspot_user(user_name)
        bot.reply_to(message, result)
    elif action == 'detail_user':
        result = get_hotspot_user_details(user_name)
        bot.reply_to(message, result)
    elif action == 'delete_user':
        result = delete_hotspot_user(user_name)
        bot.reply_to(message, result)
    elif action == 'kick_user':
        result = hotspot_delete_active(user_name)
        bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text == "Profile")
def handle_hotspot_profile_list(message):
    logger.info(f"Received /hotspot_profile_list command from {message.chat.id}")
    profiles, profile_info = get_profile_list()
    bot.reply_to(message, "\n".join(profile_info))

@bot.message_handler(func=lambda message: message.text == "Binding")
def handle_hotspot_ip_binding(message):
    logger.info(f"Received /hotspot_ip_binding command from {message.chat.id}")
    results = get_hotspot_ip_binding()
    for result in results:
        bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text == "Generate")
def hotspot_gen_vc(message):
    logger.info(f"Received /hotspot_gen_vc command from {message.chat.id}")
    profiles, profile_info = get_profile_list()
    if profiles:
        voucher_generation_state[message.chat.id] = {"step": "choose_profile", "profiles": profiles}
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, input_field_placeholder="Pilih profile")
        for profile in profile_info:
            markup.add(types.KeyboardButton(profile.split(' 🔀 ')[0].replace("📋", "")))
        bot.reply_to(message, "Silahkan pilih profile:", reply_markup=markup)
    else:
        bot.reply_to(message, "\n".join(profile_info))

@bot.message_handler(func=lambda message: voucher_generation_state.get(message.chat.id, {}).get("step") == "choose_profile")
def choose_profile(message):
    profile_name = message.text.strip()
    profiles = voucher_generation_state[message.chat.id]["profiles"]
    profile_names = [profile["name"] for profile in profiles]
    if profile_name in profile_names:
        voucher_generation_state[message.chat.id]["profile"] = profile_name
        voucher_generation_state[message.chat.id]["step"] = "enter_count"
        bot.reply_to(message, f"Profile {profile_name} dipilih. Berapa voucher yang akan di-generate?")
    else:
        bot.reply_to(message, f"Profile {profile_name} tidak ditemukan. Silahkan pilih profile yang benar.")

@bot.message_handler(func=lambda message: voucher_generation_state.get(message.chat.id, {}).get("step") == "enter_count")
def enter_count(message):
    try:
        voucher_count = int(message.text.strip())
        if voucher_count <= 0:
            raise ValueError("Voucher count must be positive.")
        voucher_generation_state[message.chat.id]["voucher_count"] = voucher_count
        voucher_generation_state[message.chat.id]["step"] = "enter_length"
        bot.reply_to(message, f"{voucher_count} voucher akan di-generate. Berapa digit format voucher?")
    except ValueError:
        bot.reply_to(message, "Silahkan masukkan jumlah voucher yang valid.")

@bot.message_handler(func=lambda message: voucher_generation_state.get(message.chat.id, {}).get("step") == "enter_length")
def enter_length(message):
    try:
        digit_length = int(message.text.strip())
        if digit_length <= 0:
            raise ValueError("Digit length must be positive.")
        profile_name = voucher_generation_state[message.chat.id]["profile"]
        voucher_count = voucher_generation_state[message.chat.id]["voucher_count"]
        generated_users = generate_vouchers(profile_name, voucher_count, digit_length)
        voucher_generation_state.pop(message.chat.id, None)
        bot.reply_to(message, f"{voucher_count} voucher telah di-generate:\n\n" + "\n".join(generated_users))
    except ValueError:
        bot.reply_to(message, "Silahkan masukkan panjang digit yang valid.")
        
# handle queue
ITEMS_PER_PAGE = 10  
@bot.message_handler(func=lambda message: message.text.startswith("List-Queue"))
def send_queue_list_paginated(message):
    user_id = message.chat.id
    queues = get_queue_list()
    if not queues:
        bot.reply_to(message, "Tidak ada Queue yang ditemukan.")
        return
    # Inisialisasi halaman pertama untuk pengguna
    if user_id not in queue_pages:
        queue_pages[user_id] = 0  # Halaman awal
    page = queue_pages[user_id]
    # Hitung indeks awal dan akhir
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    paginated_queues = queues[start_idx:end_idx]
    # Jika data kosong untuk halaman ini
    if not paginated_queues:
        bot.reply_to(message, "Tidak ada lebih banyak Queue untuk ditampilkan.")
        return
    # Format informasi Queue
    queue_info = "\n".join([
        f"name: {queue['name']} \ntarget: {queue['target']} \n(max-limit: {int(queue['max-limit'].split('/')[0]) / 1_000_000:.2f} Mbps / {int(queue['max-limit'].split('/')[1]) / 1_000_000:.2f} Mbps) \n"
        f"(burst-limit: {queue['burst-limit']}) \n(burst-time: {queue['burst-time']}) \n(limit-at: {queue['limit-at']}) \n(priority: {queue['priority']})"
        f"\n# {'❌ Disable' if queue['status'] == 'disabled' else '✅ Enabled'}"
        f"- {'🔃 Dynamic' if queue['dynamic'] == 'Dynamic' else '🔒Static'} - \nComment: {queue['comment']}\n\n"
        for queue in paginated_queues
    ])
    # Kirim informasi Queue
    bot.reply_to(message, queue_info)
    total_pages = math.ceil(len(queues) / ITEMS_PER_PAGE)
    bot.reply_to(message, f"Halaman {page + 1} dari {total_pages}")
    # Tambahkan tombol navigasi
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if page > 0:
        markup.add(types.KeyboardButton("Prev"))
    if page < total_pages - 1:
        markup.add(types.KeyboardButton("Next"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.send_message(user_id, "Gunakan tombol untuk navigasi halaman.", reply_markup=markup)

# Fungsi untuk navigasi halaman
@bot.message_handler(func=lambda message: message.text == "Next")
def next_page(message):
    user_id = message.chat.id
    if user_id in queue_pages:
        queue_pages[user_id] += 1  
        send_queue_list_paginated(message)

@bot.message_handler(func=lambda message: message.text == "Prev")
def prev_page(message):
    user_id = message.chat.id
    if user_id in queue_pages and queue_pages[user_id] > 0:
        queue_pages[user_id] -= 1  
        send_queue_list_paginated(message)

@bot.message_handler(func=lambda message: message.text == "Disable-Queue")
def disable_queue_menu(message):
    logger.info(f"Disable menu selected by {message.chat.id}")
    queues = get_queue_list()
    queue_pages[message.chat.id] = 0  # Set halaman awal
    send_queue_menu(message.chat.id, queues, 0)

def send_queue_menu(chat_id, queues, page):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    sliced_queues = queues[start:end]
    for queue in sliced_queues:
        markup.add(types.KeyboardButton(f"Disable-Queue {queue['name']}"))
    # Tambahkan tombol navigasi halaman
    if page > 0:
        markup.add(types.KeyboardButton("Prev Page"))
    if end < len(queues):
        markup.add(types.KeyboardButton("Next Page"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.send_message(chat_id, "Silakan pilih queue yang akan di-disable:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Next Page", "Prev Page"])
def handle_page_navigation(message):
    chat_id = message.chat.id
    queues = get_queue_list()
    if message.text == "Next Page":
        queue_pages[chat_id] += 1
    elif message.text == "Prev Page":
        queue_pages[chat_id] -= 1
    
    send_queue_menu(chat_id, queues, queue_pages[chat_id])

@bot.message_handler(func=lambda message: message.text.startswith("Disable-Queue "))
def handle_disable_queue(message):
    queue_name = message.text.split("Disable-Queue ")[1]
    logger.info(f"Received /queue_disable command for {queue_name} from {message.chat.id}")
    result = disable_queue(queue_name)
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text == "Enable-Queue")
def enable_queue_menu(message):
    logger.info(f"Enable menu selected by {message.chat.id}")
    queues = get_queue_list()
    queue_pages[message.chat.id] = 0  
    send_queuenable_menu(message.chat.id, queues, 0)

def send_queuenable_menu(chat_id, queues, page):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    sliced_queues = queues[start:end]
    for queue in sliced_queues:
        markup.add(types.KeyboardButton(f"Enable-Queue {queue['name']}"))
    # Tambahkan tombol navigasi halaman
    if page > 0:
        markup.add(types.KeyboardButton("Prev Page"))
    if end < len(queues):
        markup.add(types.KeyboardButton("Next Page"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.send_message(chat_id, "Silakan pilih queue yang akan di-Enable:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Next Page", "Prev Page"])
def handle_page_navigation(message):
    chat_id = message.chat.id
    queues = get_queue_list()
    if message.text == "Next Page":
        queue_pages[chat_id] += 1
    elif message.text == "Prev Page":
        queue_pages[chat_id] -= 1
    send_queuenable_menu(chat_id, queues, queue_pages[chat_id])

@bot.message_handler(func=lambda message: message.text.startswith("Enable-Queue "))
def handle_enable_queue(message):
    queue_name = message.text.split("Enable-Queue ")[1]
    logger.info(f"Received /queue_enable command for {queue_name} from {message.chat.id}")
    result = enable_queue(queue_name)
    bot.reply_to(message, result)
    
@bot.message_handler(func=lambda message: message.text == "Limit")
def limit_queue_menu(message):
    try:
        logger.info(f"Limit menu selected by {message.chat.id}")
        queues = get_queue_list()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for queue in queues:
            markup.add(types.KeyboardButton(f"Limit {queue['name']}"))
        markup.add(types.KeyboardButton("Kembali"))
        bot.reply_to(message, "Silakan pilih Queue yang akan di-limit:", reply_markup=markup)
    except Exception as e:
        logger.error(f"Failed to fetch queue list: {e}")
        bot.reply_to(message, "Gagal mengambil daftar Queue. Silakan coba lagi.")

@bot.message_handler(func=lambda message: message.text.startswith("Limit "))
def handle_limit_queue(message):
    queue_name = message.text.split("Limit ")[1]
    logger.info(f"Received /queue_c_limit command for {queue_name} from {message.chat.id}")
    queue_set_state[message.chat.id] = queue_name
    bot.reply_to(message, f"Masukkan limit baru untuk Queue {queue_name} :\n\n Contoh: 1M/1M.")

@bot.message_handler(func=lambda message: message.chat.id in queue_set_state)
def handle_new_queue_limit(message):
    queue_name = queue_set_state.pop(message.chat.id, None)
    if queue_name:
        queue_limit = message.text.strip()
        if not re.match(r"^\d+[KMG]?/\d+[KMG]?$", queue_limit):
            bot.reply_to(message, "Format limit tidak valid. Contoh: 1M/1M.")
            return
        logger.info(f"Limiting Queue {queue_name} to {queue_limit}")
        result = change_queue_limit(queue_name, queue_limit)
        bot.reply_to(message, result, reply_markup=types.ReplyKeyboardRemove())
        bot.reply_to(message, "Gunakan perintah `List-Queue` untuk memeriksa perubahan.")
    else:
        bot.reply_to(message, "Tidak ada permintaan perubahan limit Queue yang aktif.")

# Handle Netwatch
@bot.message_handler(func=lambda message: message.text == "List-Netwatch")
def send_netwatch_list(message):
    logger.info(f"Received List command from {message.chat.id}")
    
    netwatchs = get_netwatch_list()
    if not netwatchs:
        bot.reply_to(message, "Tidak ada netwatch yang ditemukan.")
        return
    # Format informasi netwatch
    netwatch_info = "\n".join([
        f"🏠 Host: {n.get('host', 'Unknown')} "
        f"(Interval: {n.get('interval', '-')}) "
        f"(Done Tests: {n.get('done-tests', '0')}) "
        f"(Failed Tests: {n.get('failed-tests', '0')}) "
        f"(Since: {n.get('since', '-')})\n"
        f"Status: {'🔛 Enable' if n.get('disabled') == 'enabled' else '❌ Disable'} - {'✅ UP' if n.get('status') == 'up' else '❗ DOWN'}\n"
        f"Comment: {n.get('comment', 'No comment')}\n\n"
        for n in netwatchs
    ])
    # Bagi pesan jika terlalu panjang
    max_length = 4096
    for i in range(0, len(netwatch_info), max_length):
        bot.reply_to(message, netwatch_info[i:i + max_length])

@bot.message_handler(func=lambda message: message.text.startswith("Add-Netwatch"))
def add_netwatch_menu(message):
    logger.info(f"Add Netwatch menu selected by {message.chat.id}")
    bot.reply_to(
        message,
        "Masukkan detail netwatch dalam format berikut:\n\n`host comment`\n\nContoh:\n`8.8.4.4 SecondaryGoogle`",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: " " in message.text and len(message.text.split()) == 2 and not message.text.startswith(("Disable-Netwatch", "Disable-Queue", "Remove-Netwatch", "Enable-Netwatch", "Set-Netwatch-Host", "Edit", "Distance")))
def handle_add_netwatch(message):
    try:
        # Mengambil host dan comment dari input
        parts = message.text.split(" ", 1)  # Pisahkan hanya pada spasi pertama
        host = parts[0].strip()
        comment = parts[1].strip() if len(parts) > 1 else ""
        logger.info(f"Received Add Netwatch request: host={host}, comment={comment}")
        # Panggil fungsi untuk menambah netwatch
        result = add_netwatch(host=host, comment=comment)
        # Kirimkan hasil ke pengguna
        bot.reply_to(message, result)
    except ValueError:
        bot.reply_to(
            message,
            "Format input tidak valid. Pastikan menggunakan format:\n`host comment`",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to add Netwatch Host: {e}")
        bot.reply_to(message, f"Gagal menambahkan netwatch Host. Error: {e}")


@bot.message_handler(func=lambda message: message.text == "Disable-Netwatch")
def disable_netwatch_menu(message):
    logger.info(f"Disable-Netwatch menu selected by {message.chat.id}")
    netwatch_list = get_netwatch_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for n in netwatch_list:
        markup.add(types.KeyboardButton(f"Disable-Netwatch {n['host']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih NetWatch yang akan dinonaktifkan:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Disable-Netwatch "))
def handle_disable_netwatch(message):
    host = message.text.split("Disable-Netwatch ")[1]
    logger.info(f"Received /netwatch_disable command for {host} from {message.chat.id}")
    # Dapatkan ID Netwatch berdasarkan hostname
    netwatch_id = get_netwatch_id(host)
    # Jika tidak menemukan ID, beri tahu pengguna
    if not netwatch_id:
        result = f"Netwatch untuk host {host} tidak ditemukan."
    else:
        # Jika ID ditemukan, lanjutkan untuk menonaktifkan Netwatch
        result = disable_netwatch(host)
    # Kirimkan hasilnya kepada pengguna
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text == "Enable-Netwatch")
def enable_netwatch_menu(message):
    logger.info(f"Enable menu selected by {message.chat.id}")
    netwatchs = get_netwatch_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for n in netwatchs:
        markup.add(types.KeyboardButton(f"Enable-Netwatch {n['host']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih netwatch yang akan di-enable:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Enable-Netwatch "))
def handle_enable_netwatch(message):
    host = message.text.split("Enable-Netwatch ")[1]
    logger.info(f"Received /host_enable command for {host} from {message.chat.id}")
    result = enable_netwatch(host)
    bot.reply_to(message, result)

@bot.message_handler(func=lambda message: message.text == "Set-Netwatch-Host")
def set_netwatch_menu(message):
    logger.info(f"Set-Netwatch-Host menu selected by {message.chat.id}")
    netwatchs = get_netwatch_list()  # Mendapatkan daftar IP
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    # Membuat tombol untuk setiap netwatch yang ada
    for n in netwatchs:
        markup.add(types.KeyboardButton(f"Edit {n['host']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih netwatch host yang akan di-set:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Edit"))
def handle_set_netwatch(message):
    host = message.text.split("Edit ")[1].strip()
    logger.info(f"Received command to change host for netwatch {host} from {message.chat.id}")
    netwatch_set_state[message.chat.id] = host
    bot.reply_to(message, f"Set host baru untuk netwatch {host}: ")

@bot.message_handler(func=lambda message: message.chat.id in netwatch_set_state)
def handle_new_netwatch_host(message):
    old_host = netwatch_set_state.pop(message.chat.id, None)
    if old_host:
        new_host = message.text.strip()
        logger.info(f"Changing host for netwatch {old_host} to {new_host}")
        result = change_netwatch_host(old_host, new_host)
        # Kirimkan hasilnya ke pengguna
        bot.reply_to(message, result)
        bot.reply_to(message, "Gunakan perintah 'List-Netwatch' untuk mengecek apakah host netwatch sudah berhasil diganti.")
    else:
        bot.reply_to(message, "Tidak ada permintaan perubahan netwatch yang aktif.")

@bot.message_handler(func=lambda message: message.text == "Remove-Netwatch")
def remove_netwatch_menu(message):
    logger.info(f"Remove menu selected by {message.chat.id}")
    netwatchs = get_netwatch_list()  # Ambil daftar netwatch
    if not netwatchs:
        bot.reply_to(message, "Tidak ada netwatch yang ditemukan.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for n in netwatchs:
        markup.add(types.KeyboardButton(f"Remove-Netwatch {n['host']}"))
    markup.add(types.KeyboardButton("Kembali"))
    bot.reply_to(message, "Silakan pilih netwatch yang akan dihapus:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.startswith("Remove-Netwatch "))
def handle_remove_netwatch(message):
    host = message.text.split("Remove-Netwatch ")[1].strip()  # Ambil nama host dan pastikan tidak ada spasi ekstra
    logger.info(f"Received /netwatch_remove command for {host} from {message.chat.id}")
    # Periksa apakah host valid dalam daftar netwatch
    netwatchs = get_netwatch_list()
    if any(n['host'] == host for n in netwatchs):  # Pastikan host ada dalam daftar
        result = remove_netwatch(host)
        bot.reply_to(message, result)
    else:
        bot.reply_to(message, f"Netwatch dengan host {host} tidak ditemukan.")

bot.polling(timeout=60, long_polling_timeout=60)
