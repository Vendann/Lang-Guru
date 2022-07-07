import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtWidgets import QLabel, QInputDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from gtts import gTTS
from googletrans import Translator
from design import Ui_MainWindow


class Example(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect('words.db')
        self.searchWord_widget.hide()
        self.translate_widget.hide()
        self.setWindowIcon(QIcon('icon.png'))

        # Логотип
        self.pixmap = QPixmap('logo.png')
        self.label_image = QLabel(self)
        self.label_image.setPixmap(self.pixmap)
        self.label_image.resize(180, 49)
        self.label_image.show()

        # Меню
        self.newWord_btn.clicked.connect(self.newWordMenu)
        self.searchWord_btn.clicked.connect(self.searchWordMenu)
        self.translateMenu_btn.clicked.connect(self.translateMenu)

        self.newWord_button.clicked.connect(self.newWord)
        self.search_btn.clicked.connect(self.searchWord)
        self.allWords_btn.clicked.connect(self.allWords)
        self.translate_btn.clicked.connect(self.translate)
        self.tts_btn.clicked.connect(self.textToSpeech)
        self.tts_btn.setIcon(QIcon('zvuk2.png'))
        self.tts_btn.setIconSize(QSize(20, 20))

        self.player = QMediaPlayer()

        self.count = 0

    def newWord(self):
        '''Получение запроса из поля ввода, добавление нового элемента в БД'''
        cur = self.con.cursor()
        cur.execute('''INSERT INTO words (russian, english) VALUES (?, ?)''',
                    (self.writeRussian.text(), self.writeEnglish.text(),))
        self.con.commit()
        self.writeRussian.clear()
        self.writeEnglish.clear()    

    def searchWord(self):
        '''Загрузка введенного слова из БД в таблицу'''
        cur = self.con.cursor()
        if self.search_line.text() != '':
            # Запрос из поля ввода, проверка выбранного языка
            if self.ru_check.isChecked():
                result = cur.execute('SELECT * FROM Words WHERE russian=?',
                                     (self.search_line.text(),)).fetchall()
            elif self.en_check.isChecked():
                result = cur.execute('SELECT * FROM Words WHERE english=?',
                                     (self.search_line.text(),)).fetchall()
            if len(result) > 0:
                # Заполнение размеров таблицы
                self.wordList.setRowCount(len(result))
                self.wordList.setColumnCount(len(result[0]))
                self.titles = [description[0] for description in cur.description]
                # Заполнение таблицы элементами
                for i, elem in enumerate(result):
                    for j, val in enumerate(elem):
                        self.wordList.setItem(i, j, QTableWidgetItem(str(val)))
                self.modified = {}
                self.search_line.clear()
            else: self.search_line.clear()

    def allWords(self):
        '''Загрузка всех слов из БД в таблицу'''
        cur = self.con.cursor()
        result = cur.execute('SELECT * FROM Words').fetchall()
        # Заполнение размеров таблицы
        self.wordList.setRowCount(len(result))
        self.wordList.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        # Заполнение таблицы элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.wordList.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def translate(self):
        '''Перевод текста'''
        translator = Translator()
        self.result_label.clear()
        if self.trans_to_ru.isChecked():
            result = translator.translate(self.lineEdit.text(), dest='ru')
            self.result_label.setText(result.text)
        elif self.trans_to_en.isChecked():
            result = translator.translate(self.lineEdit.text(), dest='en')
            self.result_label.setText(result.text)

    def textToSpeech(self):
        '''Преобразует текст в звуковой файл и запускает его'''
        if self.trans_to_ru.isChecked():
            language = 'ru'
        elif self.trans_to_en.isChecked():
            language = 'en'
        tts = gTTS(self.result_label.text(), lang = language)        
        tts.save(f'text{self.count}.mp3')
        self.player.pause()
        self.player.setMedia(QMediaContent(QUrl(f'text{self.count}.mp3')))
        self.player.play()
        self.count += 1

    def newWordMenu(self):
        '''Открывает окно добавления слова в словарь'''
        self.searchWord_widget.hide()
        self.translate_widget.hide()
        self.newWord_widget.show()

    def searchWordMenu(self):
        '''Открывает окно просмотра словаря'''
        self.newWord_widget.hide()
        self.translate_widget.hide()
        self.searchWord_widget.show()

    def translateMenu(self):
        '''Открывает переводчик'''
        self.newWord_widget.hide()
        self.searchWord_widget.hide()
        self.translate_widget.show()


if __name__=='__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())
