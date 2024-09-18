import telebot
from telebot import types
from telebot.async_telebot import AsyncTeleBot
import os, sys
import pathlib
import re
import telebot.async_telebot
import asyncio

bot = AsyncTeleBot("7453825153:AAGeD-4sNZXlPUzTHyAI3f5cgq4CmeyFOiA", parse_mode = None)
CHAT_ID_ADMIN = 5395483001
user_id = None

game_mode_text= """El día de hoy La modalidad es: inviertes 20bs te otorgamos 2 cartones y participas por un premio de 10$.  🤑🥳🫰🏻
 """

pending_payments = {}
@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
	await bot.reply_to(message, "Bienvenido soy tu asistente virtual, es un placer atenderte el día de hoy. ¿En que puedo ayudarte?")
	markup = types.ReplyKeyboardMarkup(row_width=2)
	item1 = types.KeyboardButton('Cartones Disponibles')
	item2 = types.KeyboardButton('Modo de juego')
	item3 = types.KeyboardButton('Hora de inicio del juego')
	item4 = types.KeyboardButton('Quiero jugar')
	markup.add(item1, item2, item3, item4)
	await bot.send_message(message.chat.id, 'Escoja una opcion', reply_markup=markup)
	


@bot.message_handler(content_types=['text'])
async def cartones_disponibles(message):
	print(message.chat.id)
	if message.text.lower() == 'cartones disponibles': 
		await bot.reply_to(message, 'Buscando Cartones disponibles')
		await buscar_cartones(message)
	elif message.text.lower() == 'modo de juego':
		await bot.reply_to(message, game_mode_text)
	elif message.text.lower() == 'hora de inicio del juego':
		await bot.reply_to(message, 'Hora de inicio 8:00pm hora de Venezuela. \nUnete a nuestro grupo de whatsapp ')
	elif message.text.lower() == 'quiero jugar':
		await bot.reply_to(message, """\nDatos de pago🥳\nTLF:04140698835\nCI:26.914.488\n0105 MERCANTIL\nEn caso de que no haya visto los numeros disponibles lo invitamos presionar el boton 'Cartones Disponibles'. """)							
		await bot.reply_to(message, 'Por favor, una vez realizado el pago envie el comprobante en formato de imagen y asi validar la información, con la descripcion de los numeros a solicitar')
		#bot.send_photo(CHAT_ID_ADMIN, 'HOLA')
	elif message.text.lower() in ['si', 'no'] and message.chat.id == CHAT_ID_ADMIN:
		print(pending_payments)
		await handle_admin_response(message)
		print(pending_payments)
		

	#	bot.send_message(user_id, 'Aprobado')		
	#	bot.answer_callback_query()



@bot.message_handler(content_types=['photo'])
async def handle_photo(message):
	user_id = message.chat.id
	photo = message.photo[-1]  # Obtiene la mejor resolución de la imagen
	caption = f"Usuario {user_id} ha enviado un comprobante. ¿Aprobar el pago? Responde con SI o NO."
	nro_carton = message.caption
	
	# Envía la foto al administrador
	await bot.send_photo(CHAT_ID_ADMIN, photo.file_id, caption=caption)
	await bot.send_message(user_id, 'Nos encontramos validando su pago, por favor sea paciente')
	# Guarda la referencia del comprobante en el diccionario
	pending_payments[CHAT_ID_ADMIN] = (user_id, photo.file_id, nro_carton)
	print(pending_payments)

#@bot.message_handler(func=lambda message: message.chat.id == int(CHAT_ID_ADMIN) and message.text.lower() in ['si', 'no'])
async def handle_admin_response(message):
	admin_id = message.chat.id
	response = message.text.lower()
	
	if admin_id in pending_payments:
		user_id, photo_file_id, nro_carton = pending_payments.pop(admin_id)
		
		if response == 'si':
			await bot.send_message(user_id, "Tu pago ha sido Aprobado.")
			await enviar_numero(nro_carton, user_id)
			await bot.send_message(admin_id, "Has aprobado el pago.")
		else:
			await bot.send_message(user_id, "Tu pago ha sido Rechazado.")
			await bot.send_message(admin_id, "Has rechazado el pago.")
	else:
		await bot.send_message(admin_id, "No hay pagos pendientes para aprobar.")

async def enviar_numero(nro_carton: str, user_id):
	nro_cartones_user = re.findall(r'\d+', nro_carton)
	nro_cartones_user_Set = {carton for carton in nro_cartones_user }#Set contiene numero de cartones seleccionado por los usuarios sin repetir numero
	for carton in nro_cartones_user_Set:
		if len(carton) == 1:
			carton = '00' + carton
			photo=await buscar_cartones_disponibles(carton)
			await bot.send_photo(user_id, photo)
		elif len(carton) == 2:
			carton = '0' + carton
			photo=await buscar_cartones_disponibles(carton)
			await bot.send_photo(user_id, photo)
		else:
			photo = await buscar_cartones_disponibles(carton)	
			await bot.send_photo(user_id, photo)
			
				
			

async def buscar_cartones_disponibles(nro_carton):
	if os.path.isfile(f'cartones/CARTON-{nro_carton}.png'):
		print(nro_carton, 'impresion')
		with open(f'cartones/CARTON-{nro_carton}.png', 'rb') as carton_buffer:
			photo = carton_buffer.read()
		# #move = await move_carton(file)	
		# if move:
		# 	return photo

async def move_carton(file):
	pass

		


async def buscar_cartones(message):
	elementos = os.listdir(f'{pathlib.Path().absolute()}/cartones')
	numeros = [" "+ str(x) for x in range(1, len(elementos))]
	mensaje = ",".join(numeros)
	await bot.reply_to(message, mensaje)





try:
	asyncio.run(bot.infinity_polling())
except Exception as e:
	print(e)
		
