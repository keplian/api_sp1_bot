# Telegram-бот для проверки статуса задания в ЯндексПрактикум

## Описание

Бот с определенной периодичностью обращается с через API ЯндексПрактикум, запрашивает текущий статус задания, отправленного на ревью, и отправляет сообщение о статусе текстовым сообщением в telegram.



## Технологии
python-telegram-bot 12.7


## Установка
Бот развертывается на любом сервере. В данном примере на базе Heroku:

1. Зарегистрируйтесь на **Heroku**.
2. После успешной регистрации и подтверждения почты вы окажетесь на странице https://dashboard.heroku.com/apps
3. Создайте приложение (кнопка **New → Create new app**)
4. Теперь привяжите аккаунт на **GitHub**: зайдите в раздел **Deploy**, выберите **GitHub** в разделе **Development method** и нажмите на кнопку **Connect to GitHub**.
   
   Имейте в виду: чтобы всё завелось, нужно поместить в репозиторий два служебных файла:
    * **requirements.txt** со списком зависимостей, чтобы Heroku знал, какие пакеты ему нужно установить;
    * файл **Procfile**, в котором должна быть указана «точка входа» — файл, который должен быть запущен.

Не забудьте передать переменные окружения:

_Откройте вкладку Settings и найдите пункт Config Vars. Нажмите **Reveal Config Vars** и добавьте поочерёдно ключ и значение для каждой переменной: `PRAKTIKUM_TOKEN`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`_

## Логгирование
Бот пишет лог в консоль Heroku, а также внутрь файла `bot.log`