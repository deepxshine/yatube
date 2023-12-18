# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)


*YATUBE - блог для авторов с возмодностью публикации, удаления и редактирования записей, а также возможностью подписки на авторов и добавлению постов в избранное*
* Список используемых технологий:
  * Django 2.2
  * Python 3.8
  * Django Unittest
  * Django debug toolbar
  * PostgreSQL
  * Django ORM

 * Развернуть проект у себя:
 * Клонирование проекта:
 * `git clone git@github.com:deepxshine/yatube.git`
  * Установка зависимостей:
    * `pip install -r requirements.txt`
  * Миграции:
    * `python manage.py makemigrations`
    * `python manage.py migrate`
  * Создание суперпользователя:
    * `python manage.py createsuperuser`
  * Запуск проекта:
    * `python manage.py runserver`
