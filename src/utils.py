from typing import Any

import psycopg2
import requests


def get_employers(employer_ids: list[int]) -> list[dict[str, Any]]:
    """
    Получение информации о работодателях по их ID

    Args:
        employer_ids: Список ID работодателей

    Returns:
        Список информации о работодателях
    """
    employers = []
    session = requests.Session()
    session.headers.update({"User-Agent": "HH-User-Agent", "Content-Type": "application/json"})

    for employer_id in employer_ids:
        try:
            response = session.get(f"https://api.hh.ru/employers/{employer_id}")
            response.raise_for_status()
            employers.append(response.json())
            print(f"Получены данные о компании ID {employer_id}")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении работодателя {employer_id}: {e}")

    session.close()
    return employers


def get_vacancies(employer_id: list[int], per_page: int = 50) -> list[dict[str, Any]]:
    """
    Получение вакансий для конкретного работодателя

    Args:
        employer_id: ID работодателя
        per_page: Количество вакансий на странице

    Returns:
        Список вакансий
    """
    vacancies = []
    page = 0
    pages = 1
    session = requests.Session()
    session.headers.update({"User-Agent": "HH-User-Agent", "Content-Type": "application/json"})

    try:
        for emp_id in employer_id:
            while page < pages:
                params = {"employer_id": emp_id, "per_page": per_page, "page": page}
                response = session.get("https://api.hh.ru/vacancies", params=params)
                response.raise_for_status()
                data = response.json()

                vacancies.extend(data.get("items", []))
                pages = data.get("pages", 1)
                page += 1

        print(f"Получено {len(vacancies)} вакансий для компании ID {employer_id}")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении вакансий для работодателя {employer_id}: {e}")

    session.close()
    return vacancies


def create_database(database_name: str, params: dict) -> None:
    """Создание базы данных и таблиц для сохранения данных о работодателях и вакансиях"""
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"DROP DATABASE {database_name}")
    cur.execute(f"CREATE DATABASE {database_name}")
    cur.close()
    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE companies (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        site_url VARCHAR(255),
                        area VARCHAR(100),
                        accredited_it_employer BOOLEAN DEFAULT FALSE
                        )
                    """)

    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE vacancies (
                        id INTEGER PRIMARY KEY,
                        company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        salary_from INTEGER,
                        salary_to INTEGER,
                        salary_currency VARCHAR(10),
                        url VARCHAR(255),
                        area VARCHAR(100),
                        published_at TIMESTAMP
                        )
                    """)

    conn.commit()
    conn.close()


def insert_companies(db_name: str, params: dict[str, Any], companies_data: list) -> None:
    """
    Вставка данных о компаниях в базу данных

    Args:
        db_name: Имя базы данных
        params: Параметры подключения
        companies_data: Список данных о компаниях
    """
    conn = None
    try:
        conn = psycopg2.connect(dbname=db_name, **params)
        cur = conn.cursor()

        for company in companies_data:
            cur.execute(
                """
                INSERT INTO companies (id, name, description, site_url, area, accredited_it_employer)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    site_url = EXCLUDED.site_url,
                    area = EXCLUDED.area,
                    accredited_it_employer = EXCLUDED.accredited_it_employer
            """,
                (
                    company["id"],
                    company["name"],
                    company.get("description"),
                    company.get("site_url"),
                    company.get("area", {}).get("name") if company.get("area") else None,
                    company.get("accredited_it_employer", False),
                ),
            )

        conn.commit()
        print(f"Успешно добавлено/обновлено {len(companies_data)} компаний")

        cur.close()
    except psycopg2.Error as e:
        print(f"Ошибка при вставке компаний: {e}")
    finally:
        if conn:
            conn.close()


def insert_vacancies(db_name: str, params: dict[str, Any], vacancies_data: list) -> None:
    """
    Вставка данных о вакансиях в базу данных

    Args:
        db_name: Имя базы данных
        params: Параметры подключения
        vacancies_data: Список данных о вакансиях
    """
    conn = None
    try:
        conn = psycopg2.connect(dbname=db_name, **params)
        cur = conn.cursor()

        for vacancy in vacancies_data:
            # Извлекаем данные о зарплате
            salary = vacancy.get("salary")
            salary_from = None
            salary_to = None
            salary_currency = None

            if salary:
                salary_from = salary.get("from")
                salary_to = salary.get("to")
                salary_currency = salary.get("currency")

            cur.execute(
                """
                INSERT INTO vacancies (
                    id, company_id, name, description, 
                    salary_from, salary_to, salary_currency, 
                    url, area, published_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    salary_from = EXCLUDED.salary_from,
                    salary_to = EXCLUDED.salary_to,
                    salary_currency = EXCLUDED.salary_currency,
                    url = EXCLUDED.url,
                    area = EXCLUDED.area,
                    published_at = EXCLUDED.published_at
            """,
                (
                    vacancy["id"],
                    vacancy["employer"]["id"],
                    vacancy["name"],
                    vacancy.get("snippet", {}).get("responsibility"),
                    salary_from,
                    salary_to,
                    salary_currency,
                    vacancy.get("alternate_url"),
                    vacancy.get("area", {}).get("name") if vacancy.get("area") else None,
                    vacancy.get("published_at"),
                ),
            )

        conn.commit()
        print(f"Успешно добавлено/обновлено {len(vacancies_data)} вакансий")

        cur.close()
    except psycopg2.Error as e:
        print(f"Ошибка при вставке вакансий: {e}")
    finally:
        if conn:
            conn.close()
