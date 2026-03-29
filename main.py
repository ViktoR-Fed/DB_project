from config import config
from src.user_interaction import user_interaction
from src.utils import create_database, get_employers, get_vacancies, insert_companies, insert_vacancies

DBNAME = "employers"


def main():
    employer_ids = [
        1740,  # Яндекс
        15478,  # VK
        3529,  # Сбер
        3776,  # Тинькофф
        78638,  # Ozon
        2180,  # 2ГИС
        87021,  # Wildberries
        1101,  # Avito
        3127,  # MTC
        4181,  # Билайн
    ]

    params = config()  # Параметры для подключения к базе данных
    # Получение данных о компаниях с API запроса
    data_companies = get_employers(employer_ids)

    # Получение данных о вакансиях с API запроса
    data_vacancies = get_vacancies(employer_ids, 50)

    # Создание базы данных и таблиц о компаниях и вакансиях
    create_database(DBNAME, params)

    # Вставка данных о компаниях в базу данных
    insert_companies(DBNAME, params, data_companies)

    # Вставка данных о вакансиях в базу данных
    insert_vacancies(DBNAME, params, data_vacancies)
    # Работа программы
    user_interaction(DBNAME, params)


if __name__ == "__main__":
    main()
