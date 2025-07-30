import requests
import time



class Message:
    def __init__(self, data, bot_instance):
        self.data = data
        self.text = data.get("text", "")
        self.chat = type('Chat', (), {'id': data["chat"]["id"]})
        self.from_user = type('User', (), data.get("from", {}))
        self.message_id = data.get("message_id")
        self._bot = bot_instance
    
    def reply(self, text, parse_mode=None, reply_markup=None):
        return self._bot.send_message(
            chat_id=self.chat.id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=self.message_id
        )
    
    def reply_photo(self, photo_url, caption=None):
        return self._bot.send_photo(
            chat_id=self.chat.id,
            photo_url=photo_url,
            caption=caption,
            reply_to_message_id=self.message_id
        )


class Bot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://tapi.bale.ai/bot{token}/"
        self.message_handlers = []
        self.command_handlers = {}

    def _send_request(self, method, data):
        return requests.post(f"{self.base_url}{method}", json=data)

    def send_message(self, chat_id, text, parse_mode=None, reply_markup=None, reply_to_message_id=None):
        data = {"chat_id": chat_id, "text": text}
        if parse_mode:
            data["parse_mode"] = parse_mode
        if reply_markup:
            data["reply_markup"] = reply_markup
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        return self._send_request("sendMessage", data)

    def send_photo(self, chat_id, photo_url, caption=None, reply_to_message_id=None):
        data = {"chat_id": chat_id, "photo": photo_url}
        if caption:
            data["caption"] = caption
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        return self._send_request("sendPhoto", data)

    def send_voice(self, chat_id, voice_url, caption=None, reply_to_message_id=None):
        data = {"chat_id": chat_id, "voice": voice_url}
        if caption:
            data["caption"] = caption
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        return self._send_request("sendVoice", data)

    def send_audio(self, chat_id, audio_url, caption=None, reply_to_message_id=None):
        data = {"chat_id": chat_id, "audio": audio_url}
        if caption:
            data["caption"] = caption
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        return self._send_request("sendAudio", data)

    def send_video(self, chat_id, video_url, caption=None, reply_to_message_id=None):
        data = {"chat_id": chat_id, "video": video_url}
        if caption:
            data["caption"] = caption
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        return self._send_request("sendVideo", data)

    def send_document(self, chat_id, file_url, caption=None, reply_to_message_id=None):
        data = {"chat_id": chat_id, "document": file_url}
        if caption:
            data["caption"] = caption
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        return self._send_request("sendDocument", data)

    def forward_message(self, chat_id, from_chat_id, message_id):
        data = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id
        }
        return self._send_request("forwardMessage", data)

    def send_contact(self, chat_id, phone_number, first_name, last_name=None):
        data = {
            "chat_id": chat_id,
            "phone_number": phone_number,
            "first_name": first_name
        }
        if last_name:
            data["last_name"] = last_name
        return self._send_request("sendContact", data)

    def on_message(self, func=None, commands=None):
        def decorator(f):
            if commands:
                for cmd in commands:
                    self.command_handlers[cmd] = f
            else:
                self.message_handlers.append(f)
            return f

        if func:
            return decorator(func)
        return decorator

    def create_inline_keyboard(self, buttons):
        return {"inline_keyboard": buttons}

    def create_reply_keyboard(self, buttons, resize=True, one_time=False):
        return {
            "keyboard": buttons,
            "resize_keyboard": resize,
            "one_time_keyboard": one_time
        }

    def process_message(self, m):
        if m.text and m.text.startswith('/'):
            cmd = m.text.split()[0][1:].split('@')[0]
            if cmd in self.command_handlers:
                self.command_handlers[cmd](m)
                return
        for handler in self.message_handlers:
            handler(m)

    def run(self):
        print("Hello , welcom to parsbale...")
        print("bot started...")
        update_id = None
        while True:
            try:
                params = {"offset": update_id} if update_id else {}
                response = requests.post(f"{self.base_url}getUpdates", json=params)
                updates = response.json()

                if updates.get("result"):
                    for update in updates["result"]:
                        update_id = update["update_id"] + 1
                        if "message" not in update:
                            continue

                        message = Message(update["message"], self)
                        self.process_message(message)

                time.sleep(0.1)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
                print("Hello , welcom to parsbale...")
                print("bot started...")