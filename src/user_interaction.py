from typing import Optional

from src.db_manager import DBManager


def user_interaction(database_name: str, params: dict) -> None:
    """Функция для взаимодействия с пользователем через консоль"""

    # Создаем экземпляр DBManager для работы с БД
    db_manager = DBManager(database_name, params)

    print("ПРОГРАММА ДЛЯ ПОЛУЧЕНИЯ ИНФОРМАЦИИ О КОМПАНИЯХ И ВАКАНСИЯХ")

    while True:
        print("\nМеню:")
        print("1. Получить список всех компаний и количество вакансий")
        print("2. Получить список всех вакансий с указанием названия компании")
        print("3. Получить среднюю зарплату по вакансиям")
        print("4. Получить список всех вакансий с зарплатой выше средней")
        print("5. Получить список всех вакансий по переданным словам")
        print("0. Выход")

        choice = input("\nВыберите действие (0-5): ").strip()

        if choice == "1":
            # Получение списка всех компаний и количество вакансий
            get_companies_and_vacancies_count(db_manager)

        elif choice == "2":
            # Получение списка всех вакансий с указанием названия компании
            get_all_vacancies(db_manager)

        elif choice == "3":
            # Получение средней зарплаты по вакансиям
            get_avg_salary(db_manager)

        elif choice == "4":
            # Получение списка всех вакансий с зарплатой выше средней
            get_vacancies_with_higher_salary(db_manager)

        elif choice == "5":
            # Получение списка всех вакансий по переданным словам
            get_vacancies_with_keyword(db_manager)

        elif choice == "0":
            print("\nСпасибо за использование программы! До свидания!")
            break

        else:
            print("\nНеверный выбор. Пожалуйста, выберите действие от 0 до 5.")


def get_companies_and_vacancies_count(db_manager: DBManager) -> None:
    """
    Получает и выводит список всех компаний и количество вакансий

    Args:
        db_manager: Экземпляр класса DBManager
    """
    print("СПИСОК КОМПАНИЙ И КОЛИЧЕСТВО ВАКАНСИЙ")
    results = db_manager.get_companies_and_vacancies_count()

    if results:
        for company_name, count in results:
            print(f"• {company_name}: {count} вакансий")
        print(f"\nВсего компаний: {len(results)}")
    else:
        print("Данные о компаниях не найдены")


def get_all_vacancies(db_manager: DBManager, limit: Optional[int] = None) -> None:
    """
    Получает и выводит список всех вакансий с указанием названия компании

    Args:
        db_manager: Экземпляр класса DBManager
        limit: Ограничение на количество выводимых вакансий
    """
    print("СПИСОК ВСЕХ ВАКАНСИЙ")

    results = db_manager.get_all_vacancies()

    if results:
        display_vacancies = results if limit is None else results[:limit]

        for i, vac in enumerate(display_vacancies, 1):
            company_name, vac_name, salary_from, salary_to, url = vac

            # Форматируем зарплату
            if salary_from and salary_to:
                salary = f"{salary_from} - {salary_to} руб."
            elif salary_from:
                salary = f"от {salary_from} руб."
            elif salary_to:
                salary = f"до {salary_to} руб."
            else:
                salary = "зарплата не указана"

            print(f"\n{i}. {company_name}")
            print(f"   Вакансия: {vac_name}")
            print(f"   Зарплата: {salary}")
            print(f"   Ссылка: {url}")

        if limit and len(results) > limit:
            print(f"\n... и еще {len(results) - limit} вакансий")
        print(f"\nВсего вакансий: {len(results)}")
    else:
        print("Вакансии не найдены")


def get_avg_salary(db_manager: DBManager) -> None:
    """
    Получает и выводит среднюю зарплату по вакансиям

    Args:
        db_manager: Экземпляр класса DBManager
    """
    print("СРЕДНЯЯ ЗАРПЛАТА ПО ВАКАНСИЯМ")

    avg_salary = db_manager.get_avg_salary()

    if avg_salary > 0:
        print(f"Средняя зарплата по всем вакансиям: {avg_salary:,.2f} руб.")
    else:
        print("Не удалось рассчитать среднюю зарплату (нет данных о зарплатах)")


def get_vacancies_with_higher_salary(db_manager: DBManager, limit: Optional[int] = None) -> None:
    """
    Получает и выводит список всех вакансий с зарплатой выше средней

    Args:
        db_manager: Экземпляр класса DBManager
        limit: Ограничение на количество выводимых вакансий
    """
    print("ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ")

    # Сначала покажем среднюю зарплату для контекста
    avg_salary = db_manager.get_avg_salary()
    if avg_salary > 0:
        print(f"Средняя зарплата: {avg_salary:,.2f} руб.\n")

    results = db_manager.get_vacancies_with_higher_salary()

    if results:
        display_vacancies = results if limit is None else results[:limit]

        for i, vac in enumerate(display_vacancies, 1):
            company_name, vac_name, salary_from, salary_to, currency, url = vac

            # Форматируем зарплату
            if salary_from and salary_to:
                salary = f"{salary_from} - {salary_to}"
            elif salary_from:
                salary = f"от {salary_from}"
            elif salary_to:
                salary = f"до {salary_to}"
            else:
                salary = "зарплата не указана"

            currency_str = f" {currency}" if currency else " руб."

            print(f"\n{i}. {company_name}")
            print(f"   Вакансия: {vac_name}")
            print(f"   Зарплата: {salary}{currency_str}")
            print(f"   Ссылка: {url}")

        if limit and len(results) > limit:
            print(f"\n... и еще {len(results) - limit} вакансий")
        print(f"\nВсего вакансий с зарплатой выше средней: {len(results)}")
    else:
        print("Вакансии с зарплатой выше средней не найдены")


def get_vacancies_with_keyword(db_manager: DBManager) -> None:
    """
    Получает и выводит список всех вакансий по переданным словам

    Args:
        db_manager: Экземпляр класса DBManager
    """
    print("ПОИСК ВАКАНСИЙ ПО КЛЮЧЕВЫМ СЛОВАМ")

    keyword = input("Введите ключевое слово для поиска: ").strip()

    if not keyword:
        print("Ключевое слово не может быть пустым")
        return

    print(f"\nПоиск вакансий по слову '{keyword}'...")

    results = db_manager.get_vacancies_with_keyword(keyword)

    if results:
        # Спросим пользователя, сколько вакансий показать
        show_all = input(f"\nНайдено {len(results)} вакансий. Показать все? (д/н): ").strip().lower()

        if show_all in ["д", "да", "yes", "y"]:
            display_vacancies = results
        else:
            try:
                limit = int(input("Сколько вакансий показать? (введите число): ").strip())
                display_vacancies = results[:limit]
            except ValueError:
                print("Введено некорректное число. Покажем первые 10 вакансий.")
                display_vacancies = results[:10]

        for i, vac in enumerate(display_vacancies, 1):
            company_name, vac_name, salary_from, salary_to, currency, url = vac

            # Форматируем зарплату
            if salary_from and salary_to:
                salary = f"{salary_from} - {salary_to}"
            elif salary_from:
                salary = f"от {salary_from}"
            elif salary_to:
                salary = f"до {salary_to}"
            else:
                salary = "зарплата не указана"

            currency_str = f" {currency}" if currency else " руб."

            print(f"\n{i}. {company_name}")
            print(f"   Вакансия: {vac_name}")
            print(f"   Зарплата: {salary}{currency_str}")
            print(f"   Ссылка: {url}")

        if len(display_vacancies) < len(results):
            print(f"\n... и еще {len(results) - len(display_vacancies)} вакансий")
    else:
        print(f"Вакансии по запросу '{keyword}' не найдены")
