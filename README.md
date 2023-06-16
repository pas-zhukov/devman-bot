# Devman Notifications Bot

---

Бот для отправки уведомлений о проверке работ на сайте Devman.

## Установка зависимостей
Первым делом, скачайте код:
``` 
git clone https://github.com/pas-zhukov/wine.git
```
Для работы скрипта понадобятся библиотеки, перечисленные в `reqirements.txt`.
Их можно установить при помощи pip:
```
pip install -r requirements.txt
```
Проверить, что все необходимые библиотеки на месте:
``` 
pip list
```

## Данные для работы бота

Для работы бота необходимо указать свой id в Telegram. Чтобы его узнать, напишите [этому боту](https://t.me/userinfobot).

## Запуск

1. Чтобы бот мог писать Вам сообщения, напшите ему любое сообщение от своего имени. [ссылка](https://t.me/dvmn_ntfy_bot)

2. Для запуска бота необходимо прописать следующую команду, в качестве аргумента указав свой id:
```
python main.py <Ваш id>
```
например:
```
python main.py 5563781
```

3. Если всё было сделано правильно, при проверки задания преподавателем, Вы получите следующего вида сообщение:

![img](notification_example.png)

## Цели проекта

Код написан в учебных целях — это урок на курсе по Python и веб-разработке на сайте Devman.