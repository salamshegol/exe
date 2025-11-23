import sys
import os
from pathlib import Path
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QTextEdit, QPushButton, QComboBox, QLabel, 
                              QDialog, QLineEdit, QTabWidget, QListWidget, QListWidgetItem,
                              QMessageBox, QFileDialog, QScrollArea)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
import json
from datetime import datetime

class WebhookSender(QMainWindow):
    def __init__(self):
        super().__init__()
        self.webhook_dir = Path.home() / "AppData" / "Local" / "hook"
        self.webhook_dir.mkdir(parents=True, exist_ok=True)
        self.attached_files = []
        self.settings = self.load_settings()
        self.current_theme = self.settings.get("theme", "light").lower()
        self.current_language = self.settings.get("language", "english").lower()
        self.translations = self.get_translations()
        self.init_ui()
        self.apply_saved_theme()
        self.load_webhooks()
        self.load_current_messages()
    
    def load_settings(self):
        settings_file = self.webhook_dir / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"theme": "light", "language": "english"}
    
    def save_settings(self):
        settings_file = self.webhook_dir / "settings.json"
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_language(self):
        language_file = self.webhook_dir / "language.txt"
        if language_file.exists():
            try:
                with open(language_file, 'r', encoding='utf-8') as f:
                    lang = f.read().strip().lower()
                    if lang in ["english", "russian"]:
                        return lang
            except:
                pass
        return "english"
    
    def save_language(self):
        language_file = self.webhook_dir / "language.txt"
        try:
            with open(language_file, 'w', encoding='utf-8') as f:
                f.write(self.current_language)
        except Exception as e:
            print(f"Error saving language: {e}")
    
    def get_translations(self):
        return {
            "english": {
                "theme": "Theme:",
                "light": "Light",
                "dark": "Dark",
                "language": "Language:",
                "select_webhook": "Select Webhook:",
                "add": "+ Add",
                "edit": "Edit",
                "delete": "- Delete",
                "format": "Format:",
                "message": "Message:",
                "attach_file": "Attach File",
                "send": "Send",
                "message_history": "Message History:",
                "clear_all": "Clear All",
                "add_webhook_title": "Add Webhook",
                "webhook_name": "Webhook Name:",
                "webhook_url": "Webhook URL:",
                "save": "Save",
                "cancel": "Cancel",
                "error": "Error",
                "success": "Success",
                "no_webhooks": "No webhooks found",
                "name_url_empty": "Name and URL cannot be empty",
                "invalid_url": "Invalid URL",
                "webhook_saved": "Webhook saved!",
                "file_large": "is larger than 10MB",
                "select_files": "Select Files",
                "no_webhooks_found": "No webhooks found",
                "invalid_webhook": "Invalid webhook selected",
                "message_empty": "Message is empty",
                "files_empty": "Message and files are empty",
                "message_sent": "Message sent!",
                "select_message": "Select a message to edit",
                "cannot_edit": "Cannot edit this message",
                "message_edited": "Message edited!",
                "delete_confirm": "Delete this message from Discord?",
                "cannot_delete": "Cannot delete this message (invalid data)",
                "message_deleted": "Message deleted!",
                "delete_all_confirm": "Delete ALL messages from Discord?",
                "no_messages": "No messages to delete",
                "done": "Done",
                "delete_webhook_confirm": "Delete webhook",
                "webhook_deleted": "Webhook deleted!",
                "edit_webhook_title": "Edit Webhook",
                "webhook_updated": "Webhook updated!",
                "nothing_send": "Nothing to send",
            },
            "russian": {
                "theme": "Тема:",
                "light": "Светлая",
                "dark": "Тёмная",
                "language": "Язык:",
                "select_webhook": "Выбрать Webhook:",
                "add": "+ Добавить",
                "edit": "Изменить",
                "delete": "- Удалить",
                "format": "Форматирование:",
                "message": "Сообщение:",
                "attach_file": "Прикрепить файл",
                "send": "Отправить",
                "message_history": "История сообщений:",
                "clear_all": "Очистить всё",
                "add_webhook_title": "Добавить Webhook",
                "webhook_name": "Имя Webhook:",
                "webhook_url": "URL Webhook:",
                "save": "Сохранить",
                "cancel": "Отмена",
                "error": "Ошибка",
                "success": "Успешно",
                "no_webhooks": "Webhook'и не найдены",
                "name_url_empty": "Имя и URL не могут быть пустыми",
                "invalid_url": "Неверный URL",
                "webhook_saved": "Webhook сохранён!",
                "file_large": "больше чем 10MB",
                "select_files": "Выбрать файлы",
                "no_webhooks_found": "Webhook'и не найдены",
                "invalid_webhook": "Неверный webhook выбран",
                "message_empty": "Сообщение пусто",
                "files_empty": "Сообщение и файлы пусты",
                "message_sent": "Сообщение отправлено!",
                "select_message": "Выбрать сообщение для изменения",
                "cannot_edit": "Невозможно изменить это сообщение",
                "message_edited": "Сообщение изменено!",
                "delete_confirm": "Удалить это сообщение из Discord?",
                "cannot_delete": "Невозможно удалить это сообщение (неверные данные)",
                "message_deleted": "Сообщение удалено!",
                "delete_all_confirm": "Удалить ВСЕ сообщения из Discord?",
                "no_messages": "Нет сообщений для удаления",
                "done": "Готово",
                "delete_webhook_confirm": "Удалить webhook",
                "webhook_deleted": "Webhook удалён!",
                "edit_webhook_title": "Изменить Webhook",
                "webhook_updated": "Webhook обновлён!",
                "nothing_send": "Нечего отправлять",
            }
        }
    
    def t(self, key):
        return self.translations[self.current_language].get(key, key)
    
    def init_ui(self):
        self.setWindowTitle("Discord Webhook Sender")
        self.setGeometry(100, 100, 610, 450)
        self.setFixedSize(610, 450)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(self.t("theme")))
        theme_combo = QComboBox()
        theme_combo.addItems([self.t("light"), self.t("dark")])
        theme_combo.setCurrentText(self.t("light") if self.current_theme == "light" else self.t("dark"))
        theme_combo.currentTextChanged.connect(self.change_theme)
        top_layout.addWidget(theme_combo)
        
        top_layout.addWidget(QLabel(self.t("language")))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Русский"])
        self.lang_combo.setCurrentText("Русский" if self.current_language == "russian" else "English")
        self.lang_combo.currentTextChanged.connect(self.change_language)
        top_layout.addWidget(self.lang_combo)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)
        
        tabs = QTabWidget()
        
        sender_widget = QWidget()
        sender_layout = QVBoxLayout()
        
        webhook_layout = QHBoxLayout()
        webhook_layout.addWidget(QLabel(self.t("select_webhook")))
        self.webhook_combo = QComboBox()
        self.webhook_combo.currentTextChanged.connect(self.on_webhook_changed)
        webhook_layout.addWidget(self.webhook_combo)
        add_webhook_btn = QPushButton(self.t("add"))
        add_webhook_btn.setMaximumWidth(60)
        add_webhook_btn.setToolTip("Add new webhook")
        add_webhook_btn.clicked.connect(self.add_webhook_dialog)
        webhook_layout.addWidget(add_webhook_btn)
        edit_webhook_btn = QPushButton(self.t("edit"))
        edit_webhook_btn.setMaximumWidth(50)
        edit_webhook_btn.setToolTip("Edit selected webhook")
        edit_webhook_btn.clicked.connect(self.edit_webhook_dialog)
        webhook_layout.addWidget(edit_webhook_btn)
        delete_webhook_btn = QPushButton(self.t("delete"))
        delete_webhook_btn.setMaximumWidth(80)
        delete_webhook_btn.setToolTip("Delete selected webhook")
        delete_webhook_btn.clicked.connect(self.delete_webhook)
        webhook_layout.addWidget(delete_webhook_btn)
        sender_layout.addLayout(webhook_layout)
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel(self.t("format")))
        
        bold_btn = QPushButton("B")
        bold_btn.setMaximumWidth(35)
        bold_btn.setToolTip("Bold: **text**")
        bold_btn.clicked.connect(lambda: self.apply_format("**", "**"))
        format_layout.addWidget(bold_btn)
        
        italic_btn = QPushButton("I")
        italic_btn.setMaximumWidth(35)
        italic_btn.setToolTip("Italic: *text*")
        italic_btn.clicked.connect(lambda: self.apply_format("*", "*"))
        format_layout.addWidget(italic_btn)
        
        bold_italic_btn = QPushButton("BI")
        bold_italic_btn.setMaximumWidth(35)
        bold_italic_btn.setToolTip("Bold Italic: ***text***")
        bold_italic_btn.clicked.connect(lambda: self.apply_format("***", "***"))
        format_layout.addWidget(bold_italic_btn)
        
        underline_btn = QPushButton("U")
        underline_btn.setMaximumWidth(35)
        underline_btn.setToolTip("Underline: __text__")
        underline_btn.clicked.connect(lambda: self.apply_format("__", "__"))
        format_layout.addWidget(underline_btn)
        
        strikethrough_btn = QPushButton("S")
        strikethrough_btn.setMaximumWidth(35)
        strikethrough_btn.setToolTip("Strikethrough: ~~text~~")
        strikethrough_btn.clicked.connect(lambda: self.apply_format("~~", "~~"))
        format_layout.addWidget(strikethrough_btn)
        
        code_btn = QPushButton("Code")
        code_btn.setMaximumWidth(50)
        code_btn.setToolTip("Inline code: `text`")
        code_btn.clicked.connect(lambda: self.apply_format("`", "`"))
        format_layout.addWidget(code_btn)
        
        codeblock_btn = QPushButton("Block")
        codeblock_btn.setMaximumWidth(50)
        codeblock_btn.setToolTip("Code block: ```text```")
        codeblock_btn.clicked.connect(lambda: self.apply_format("```\n", "\n```"))
        format_layout.addWidget(codeblock_btn)
        
        heading_btn = QPushButton("H")
        heading_btn.setMaximumWidth(35)
        heading_btn.setToolTip("Heading: # text")
        heading_btn.clicked.connect(self.apply_heading)
        format_layout.addWidget(heading_btn)
        
        quote_btn = QPushButton("Quote")
        quote_btn.setMaximumWidth(50)
        quote_btn.setToolTip("Quote: > text")
        quote_btn.clicked.connect(self.apply_quote)
        format_layout.addWidget(quote_btn)
        
        spoiler_btn = QPushButton("Spoiler")
        spoiler_btn.setMaximumWidth(60)
        spoiler_btn.setToolTip("Spoiler: ||text||")
        spoiler_btn.clicked.connect(lambda: self.apply_format("||", "||"))
        format_layout.addWidget(spoiler_btn)
        
        format_layout.addStretch()
        sender_layout.addLayout(format_layout)
        
        sender_layout.addWidget(QLabel(self.t("message")))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(self.t("message"))
        sender_layout.addWidget(self.text_edit)
        
        file_layout = QHBoxLayout()
        attach_btn = QPushButton(self.t("attach_file"))
        attach_btn.setMaximumWidth(100)
        attach_btn.setToolTip("Attach file (max 10MB)")
        attach_btn.clicked.connect(self.attach_file)
        file_layout.addWidget(attach_btn)
        file_layout.addStretch()
        sender_layout.addLayout(file_layout)
        
        self.attached_files = []
        self.file_list_scroll = QScrollArea()
        self.file_list_scroll.setWidgetResizable(True)
        self.file_list_scroll.setMaximumHeight(100)
        self.file_list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.file_list_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.file_list_container = QWidget()
        self.file_list_layout = QHBoxLayout()
        self.file_list_layout.setContentsMargins(0, 0, 0, 0)
        self.file_list_container.setLayout(self.file_list_layout)
        self.file_list_scroll.setWidget(self.file_list_container)
        
        sender_layout.addWidget(self.file_list_scroll)
        
        self.send_button = QPushButton(self.t("send"))
        self.send_button.setToolTip("Send message and files to Discord")
        self.send_button.clicked.connect(self.send_message)
        sender_layout.addWidget(self.send_button)
        
        sender_widget.setLayout(sender_layout)
        tabs.addTab(sender_widget, self.t("send") if self.current_language == "russian" else "Send")
        
        history_widget = QWidget()
        history_layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        history_layout.addWidget(QLabel(self.t("message_history")))
        history_layout.addWidget(self.history_list)
        
        history_buttons = QHBoxLayout()
        edit_btn = QPushButton(self.t("edit"))
        edit_btn.setToolTip("Edit selected message")
        edit_btn.clicked.connect(self.edit_message)
        
        delete_btn = QPushButton(self.t("delete"))
        delete_btn.setToolTip("Delete selected message from Discord")
        delete_btn.clicked.connect(self.delete_message)
        
        clear_btn = QPushButton(self.t("clear_all"))
        clear_btn.setToolTip("Delete all messages from Discord")
        clear_btn.clicked.connect(self.clear_history)
        
        history_buttons.addWidget(edit_btn)
        history_buttons.addWidget(delete_btn)
        history_buttons.addWidget(clear_btn)
        history_layout.addLayout(history_buttons)
        
        history_widget.setLayout(history_layout)
        tabs.addTab(history_widget, self.t("message_history") if self.current_language == "russian" else "History")
        
        main_layout.addWidget(tabs)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def change_theme(self, theme_name):
        new_theme = "dark" if self.t("dark") in theme_name else "light"
        self.current_theme = new_theme
        self.settings["theme"] = new_theme
        self.save_settings()
        
        if self.current_theme == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
    def apply_light_theme(self):
        self.setStyleSheet("")
    
    def apply_dark_theme(self):
        dark_stylesheet = """
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTextEdit, QLineEdit, QListWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
            }
            QPushButton {
                background-color: #0d47a1;
                color: #ffffff;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 5px 20px;
            }
            QTabBar::tab:selected {
                background-color: #0d47a1;
            }
            QLabel {
                color: #ffffff;
            }
            QScrollArea {
                background-color: #1e1e1e;
            }
        """
        self.setStyleSheet(dark_stylesheet)
    
    def load_webhooks(self):
        self.webhooks = {}
        self.webhook_combo.clear()
        
        for webhook_folder in self.webhook_dir.iterdir():
            if webhook_folder.is_dir():
                deleted_file = webhook_folder / "deleted.txt"
                url_file = webhook_folder / "URL.txt"
                
                if deleted_file.exists():
                    try:
                        with open(deleted_file, 'r') as f:
                            if f.read().strip().lower() == "true":
                                continue
                    except:
                        pass
                
                if url_file.exists():
                    try:
                        with open(url_file, 'r') as f:
                            url = f.read().strip()
                            if url.startswith("http"):
                                name = webhook_folder.name
                                self.webhooks[name] = url
                                self.webhook_combo.addItem(name)
                    except Exception as e:
                        print(f"Error reading {url_file}: {e}")
        
        if not self.webhooks:
            self.webhook_combo.addItem("No webhooks found")
    
    def get_messages_file(self, webhook_name):
        messages_dir = self.webhook_dir / webhook_name / "messages"
        messages_dir.mkdir(parents=True, exist_ok=True)
        return messages_dir / "messages.json"
    
    def load_current_messages(self):
        if not self.webhooks:
            self.history = []
            return
        
        current_name = self.webhook_combo.currentText()
        if current_name not in self.webhooks:
            self.history = []
            return
        
        messages_file = self.get_messages_file(current_name)
        self.history = []
        
        if messages_file.exists():
            try:
                with open(messages_file, 'r') as f:
                    self.history = json.load(f)
                self.update_history_list()
            except Exception as e:
                print(f"Error loading messages: {e}")
    
    def save_messages(self):
        current_name = self.webhook_combo.currentText()
        if current_name not in self.webhooks:
            return
        
        messages_file = self.get_messages_file(current_name)
        try:
            with open(messages_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving messages: {e}")
    
    def update_history_list(self):
        self.history_list.clear()
        for idx, msg in enumerate(self.history):
            item_text = f"[{msg['webhook']}] {msg['text'][:50]}..."
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.history_list.addItem(item)
    
    def add_webhook_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.t("add_webhook_title"))
        dialog.setGeometry(200, 200, 400, 150)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(self.t("webhook_name")))
        name_input = QLineEdit()
        layout.addWidget(name_input)
        
        layout.addWidget(QLabel(self.t("webhook_url")))
        url_input = QLineEdit()
        url_input.setPlaceholderText("https://discordapp.com/api/webhooks/...")
        layout.addWidget(url_input)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton(self.t("save"))
        cancel_btn = QPushButton(self.t("cancel"))
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def save_webhook():
            name = name_input.text().strip()
            url = url_input.text().strip()
            
            if not name or not url:
                QMessageBox.warning(self, self.t("error"), self.t("name_url_empty"))
                return
            
            if not url.startswith("http"):
                QMessageBox.warning(self, self.t("error"), self.t("invalid_url"))
                return
            
            webhook_folder = self.webhook_dir / name
            webhook_folder.mkdir(parents=True, exist_ok=True)
            
            url_file = webhook_folder / "URL.txt"
            try:
                with open(url_file, 'w') as f:
                    f.write(url)
                QMessageBox.information(self, self.t("success"), self.t("webhook_saved"))
                dialog.close()
                self.load_webhooks()
            except Exception as e:
                QMessageBox.warning(self, self.t("error"), f"Error saving webhook: {e}")
        
        save_btn.clicked.connect(save_webhook)
        cancel_btn.clicked.connect(dialog.close)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def attach_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, self.t("select_files"), "", "All Files (*)")
        if not file_paths:
            return
        
        for file_path in file_paths:
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            
            if file_size > 10:
                QMessageBox.warning(self, self.t("error"), f"{os.path.basename(file_path)} {self.t('file_large')}")
                continue
            
            if file_path not in self.attached_files:
                self.attached_files.append(file_path)
        
        self.update_file_list()
    
    def update_file_list(self):
        while self.file_list_layout.count() > 0:
            item = self.file_list_layout.takeAt(0)
            if item is not None and item.widget() is not None:
                item.widget().deleteLater()
        
        if not self.attached_files:
            self.file_list_layout.addStretch()
            return
        
        for file_path in self.attached_files:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            
            file_widget = QWidget()
            file_widget.setMaximumHeight(50)
            file_widget.setMinimumWidth(300)
            file_widget_layout = QHBoxLayout()
            file_widget_layout.setContentsMargins(5, 5, 5, 5)
            file_widget_layout.setSpacing(10)
            
            label = QLabel(f"{file_name}\n{file_size:.2f}MB")
            label.setWordWrap(True)
            file_widget_layout.addWidget(label)
            
            remove_btn = QPushButton("X")
            remove_btn.setMaximumWidth(30)
            remove_btn.setMaximumHeight(30)
            remove_btn.clicked.connect(lambda checked, fp=file_path: self.remove_file(fp))
            file_widget_layout.addWidget(remove_btn)
            
            file_widget.setLayout(file_widget_layout)
            self.file_list_layout.addWidget(file_widget)
        
        self.file_list_layout.addStretch()
    
    def remove_file(self, file_path):
        if file_path in self.attached_files:
            self.attached_files.remove(file_path)
            self.update_file_list()
    
    def send_message(self):
        if not self.webhooks:
            QMessageBox.warning(self, self.t("error"), "No webhooks found")
            return
        
        current_name = self.webhook_combo.currentText()
        if current_name not in self.webhooks:
            print("Invalid webhook selected")
            return
        
        message = self.text_edit.toPlainText().strip()
        webhook_url = self.webhooks[current_name]
        
        if not message and not self.attached_files:
            print("Message and files are empty")
            return
        
        try:
            if message:
                response = requests.post(f"{webhook_url}?wait=true", json={"content": message})
                
                if response.status_code == 200:
                    msg_data = response.json()
                    message_id = msg_data.get('id')
                    
                    self.history.append({
                        "webhook": current_name,
                        "text": message,
                        "webhook_url": webhook_url,
                        "message_id": message_id,
                        "files": [],
                        "timestamp": datetime.now().isoformat()
                    })
            
            for file_path in self.attached_files:
                if os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    with open(file_path, 'rb') as file_obj:
                        files = {'file': (file_name, file_obj)}
                        response = requests.post(f"{webhook_url}?wait=true", files=files)
                    
                    if response.status_code == 200:
                        msg_data = response.json()
                        message_id = msg_data.get('id')
                        
                        self.history.append({
                            "webhook": current_name,
                            "text": "",
                            "webhook_url": webhook_url,
                            "message_id": message_id,
                            "files": [file_name],
                            "timestamp": datetime.now().isoformat()
                        })
            
            if message or self.attached_files:
                self.save_messages()
                self.update_history_list()
                self.text_edit.clear()
                self.attached_files = []
                self.update_file_list()
                QMessageBox.information(self, self.t("success"), self.t("message_sent"))
            else:
                QMessageBox.warning(self, self.t("error"), self.t("nothing_send"))
        except Exception as e:
            QMessageBox.warning(self, self.t("error"), f"Error sending message: {e}")
    
    def edit_message(self):
        current_item = self.history_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, self.t("error"), self.t("select_message"))
            return
        
        idx = current_item.data(Qt.ItemDataRole.UserRole)
        msg = self.history[idx]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Message")
        dialog.setGeometry(200, 200, 400, 200)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Webhook:"))
        webhook_input = QLineEdit(msg['webhook'])
        webhook_input.setReadOnly(True)
        layout.addWidget(webhook_input)
        
        layout.addWidget(QLabel("Message:"))
        text_input = QTextEdit(msg['text'])
        layout.addWidget(text_input)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def save_edit():
            new_text = text_input.toPlainText()
            webhook_url = msg.get('webhook_url')
            message_id = msg.get('message_id')
            
            if not webhook_url or not message_id:
                QMessageBox.warning(self, self.t("error"), self.t("cannot_edit"))
                return
            
            try:
                edit_url = f"{webhook_url}/messages/{message_id}"
                response = requests.patch(edit_url, json={"content": new_text})
                
                if response.status_code == 200:
                    self.history[idx]['text'] = new_text
                    self.save_messages()
                    self.update_history_list()
                    QMessageBox.information(self, self.t("success"), self.t("message_edited"))
                    dialog.close()
                else:
                    QMessageBox.warning(self, self.t("error"), f"Failed: {response.status_code}")
            except Exception as e:
                QMessageBox.warning(self, self.t("error"), f"Error: {e}")
        
        save_btn.clicked.connect(save_edit)
        cancel_btn.clicked.connect(dialog.close)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def delete_message(self):
        current_item = self.history_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, self.t("error"), "Select a message to delete")
            return
        
        idx = current_item.data(Qt.ItemDataRole.UserRole)
        
        if idx < 0 or idx >= len(self.history):
            QMessageBox.warning(self, self.t("error"), "Invalid message selected")
            self.update_history_list()
            return
        
        msg = self.history[idx]
        
        webhook_url = msg.get('webhook_url')
        message_id = msg.get('message_id')
        
        if not webhook_url or not message_id:
            QMessageBox.warning(self, self.t("error"), "Cannot delete this message (invalid data)")
            del self.history[idx]
            self.save_messages()
            self.update_history_list()
            return
        
        reply = QMessageBox.question(self, "Confirm", self.t("delete_confirm"))
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            delete_url = f"{webhook_url}/messages/{message_id}"
            response = requests.delete(delete_url)
            
            if response.status_code == 204:
                del self.history[idx]
                self.save_messages()
                self.update_history_list()
                QMessageBox.information(self, self.t("success"), self.t("message_deleted"))
            else:
                QMessageBox.warning(self, self.t("error"), f"Failed: {response.status_code}")
                del self.history[idx]
                self.save_messages()
                self.update_history_list()
        except Exception as e:
            QMessageBox.warning(self, self.t("error"), f"Error: {e}")
            del self.history[idx]
            self.save_messages()
            self.update_history_list()
    
    def clear_history(self):
        reply = QMessageBox.question(self, "Confirm", self.t("delete_all_confirm"))
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        if not self.history:
            QMessageBox.information(self, "Info", self.t("no_messages"))
            return
        
        deleted_count = 0
        failed_count = 0
        
        for msg in self.history:
            webhook_url = msg.get('webhook_url')
            message_id = msg.get('message_id')
            
            if not webhook_url or not message_id:
                failed_count += 1
                continue
            
            try:
                delete_url = f"{webhook_url}/messages/{message_id}"
                response = requests.delete(delete_url)
                
                if response.status_code == 204:
                    deleted_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"Error deleting message: {e}")
                failed_count += 1
        
        self.history = []
        self.save_messages()
        self.update_history_list()
        
        QMessageBox.information(self, "Done", f"Deleted: {deleted_count}, Failed: {failed_count}")

    def delete_webhook(self):
        if not self.webhooks:
            QMessageBox.warning(self, self.t("error"), "No webhooks to delete")
            return
        
        current_name = self.webhook_combo.currentText()
        if current_name not in self.webhooks:
            QMessageBox.warning(self, self.t("error"), "Select a webhook to delete")
            return
        
        reply = QMessageBox.question(self, self.t("delete_webhook_confirm", current_name))
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            webhook_folder = self.webhook_dir / current_name
            deleted_file = webhook_folder / "deleted.txt"
            
            with open(deleted_file, 'w') as f:
                f.write("true")
            
            QMessageBox.information(self, self.t("success"), self.t("webhook_deleted"))
            self.load_webhooks()
            self.load_current_messages()
        except Exception as e:
            QMessageBox.warning(self, self.t("error"), f"Error deleting webhook: {e}")
    
    def edit_webhook_dialog(self):
        if not self.webhooks:
            QMessageBox.warning(self, self.t("error"), "No webhooks to edit")
            return
        
        current_name = self.webhook_combo.currentText()
        if current_name not in self.webhooks:
            QMessageBox.warning(self, self.t("error"), "Select a webhook to edit")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(self.t("edit_webhook_title"))
        dialog.setGeometry(200, 200, 400, 150)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(self.t("webhook_name")))
        name_input = QLineEdit(current_name)
        layout.addWidget(name_input)
        
        layout.addWidget(QLabel(self.t("webhook_url")))
        url_input = QLineEdit(self.webhooks[current_name])
        layout.addWidget(url_input)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton(self.t("save"))
        cancel_btn = QPushButton(self.t("cancel"))
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def save_webhook_edit():
            new_name = name_input.text().strip()
            new_url = url_input.text().strip()
            
            if not new_name or not new_url:
                QMessageBox.warning(self, self.t("error"), self.t("name_url_empty"))
                return
            
            if not new_url.startswith("http"):
                QMessageBox.warning(self, self.t("error"), self.t("invalid_url"))
                return
            
            try:
                old_folder = self.webhook_dir / current_name
                new_folder = self.webhook_dir / new_name
                
                if current_name != new_name:
                    old_folder.rename(new_folder)
                    new_folder = self.webhook_dir / new_name
                
                url_file = new_folder / "URL.txt"
                with open(url_file, 'w') as f:
                    f.write(new_url)
                
                QMessageBox.information(self, self.t("success"), self.t("webhook_updated"))
                dialog.close()
                self.load_webhooks()
                self.load_current_messages()
            except Exception as e:
                QMessageBox.warning(self, self.t("error"), f"Error updating webhook: {e}")
        
        save_btn.clicked.connect(save_webhook_edit)
        cancel_btn.clicked.connect(dialog.close)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def apply_format(self, prefix, suffix):
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            cursor.insertText(f"{prefix}{suffix}")
            self.text_edit.setTextCursor(cursor)
            return
        
        start_pos = cursor.selectionStart()
        end_pos = cursor.selectionEnd()
        
        cursor.setPosition(start_pos)
        cursor.insertText(prefix)
        
        cursor.setPosition(end_pos + len(prefix))
        cursor.insertText(suffix)
        
        self.text_edit.setTextCursor(cursor)
    
    def apply_heading(self):
        cursor = self.text_edit.textCursor()
        block = cursor.block()
        block_text = block.text()
        
        if block_text.startswith("# "):
            new_text = block_text[2:]
        else:
            new_text = f"# {block_text}"
        
        block_start = block.position()
        cursor.setPosition(block_start)
        cursor.movePosition(cursor.MoveOperation.EndOfBlock, cursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(new_text)
        
        self.text_edit.setTextCursor(cursor)
    
    def apply_quote(self):
        cursor = self.text_edit.textCursor()
        block = cursor.block()
        block_text = block.text()
        
        if block_text.startswith("> "):
            new_text = block_text[2:]
        else:
            new_text = f"> {block_text}"
        
        block_start = block.position()
        cursor.setPosition(block_start)
        cursor.movePosition(cursor.MoveOperation.EndOfBlock, cursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(new_text)
        
        self.text_edit.setTextCursor(cursor)
    
    def on_webhook_changed(self):
        self.load_current_messages()
    
    def change_language(self, lang_name):
        new_language = "russian" if lang_name == "Русский" else "english"
        
        if new_language == self.current_language:
            return
        
        self.current_language = new_language
        self.settings["language"] = new_language
        self.save_settings()
        QMessageBox.information(self, self.t("success"), "Language changed! Please restart the application.")
    
    def retranslate_ui(self):
        self.setWindowTitle("Discord Webhook Sender")
        
        self.lang_combo.blockSignals(True)
        self.lang_combo.clear()
        self.lang_combo.addItems(["English", "Русский"])
        self.lang_combo.setCurrentText("Русский" if self.current_language == "russian" else "English")
        self.lang_combo.blockSignals(False)
    
    def apply_saved_theme(self):
        if self.current_theme == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebhookSender()
    window.show()
    sys.exit(app.exec())
