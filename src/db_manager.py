from typing import Any, Dict, List, Optional, Tuple

import psycopg2


class DBManager:
    """
    Класс для работы с данными в базе данных.
    Предоставляет методы для получения различной информации о компаниях и вакансиях.
    """

    def __init__(self, db_name: str, params: Dict[str, Any]):
        """
        Инициализация менеджера базы данных

        Args:
            db_name: Имя базы данных
            params: Параметры подключения (хост, пользователь, пароль, порт)
        """
        self.db_name = db_name
        self.params = params

    def _execute_query(self, query: str, params: Optional[tuple] = None) -> List[Tuple]:
        """
        Выполнение SQL запроса и возврат результатов

        Args:
            query: SQL запрос
            params: Параметры запроса

        Returns:
            Результаты запроса
        """
        conn = None
        try:
            conn = psycopg2.connect(dbname=self.db_name, **self.params)
            cur = conn.cursor()
            cur.execute(query, params)
            results = cur.fetchall()
            cur.close()
            return results
        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании

        Returns:
            Список кортежей (название компании, количество вакансий)
        """
        query = """
            SELECT c.name, COUNT(v.id) as vacancies_count
            FROM companies c
            LEFT JOIN vacancies v ON c.id = v.company_id
            GROUP BY c.id, c.name
            ORDER BY vacancies_count DESC
        """
        return self._execute_query(query)

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию

        Returns:
            Список кортежей (название компании, название вакансии, зарплата от, зарплата до, ссылка)
        """
        query = """
            SELECT 
                c.name as company_name,
                v.name as vacancy_name,
                v.salary_from,
                v.salary_to,
                v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
            ORDER BY c.name, v.name
        """
        return self._execute_query(query)

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям
        (учитываются вакансии с указанной зарплатой)

        Returns:
            Средняя зарплата
        """
        query = """
            SELECT AVG(avg_salary) as avg_salary
            FROM (
                SELECT 
                    CASE 
                        WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL 
                            THEN (salary_from + salary_to) / 2.0
                        WHEN salary_from IS NOT NULL 
                            THEN salary_from
                        WHEN salary_to IS NOT NULL 
                            THEN salary_to
                        ELSE NULL
                    END as avg_salary
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            ) as calculated_salaries
        """
        result = self._execute_query(query)
        return result[0][0] if result and result[0][0] else 0

    def get_vacancies_with_higher_salary(self) -> List[Tuple]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям

        Returns:
            Список вакансий с зарплатой выше средней
        """
        query = """
            WITH avg_salary_calc AS (
                SELECT AVG(
                    CASE 
                        WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL 
                            THEN (salary_from + salary_to) / 2.0
                        WHEN salary_from IS NOT NULL 
                            THEN salary_from
                        WHEN salary_to IS NOT NULL 
                            THEN salary_to
                    END
                ) as avg_salary
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            )
            SELECT 
                c.name as company_name,
                v.name as vacancy_name,
                v.salary_from,
                v.salary_to,
                v.salary_currency,
                v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
            CROSS JOIN avg_salary_calc avg_calc
            WHERE 
                CASE 
                    WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL 
                        THEN (v.salary_from + v.salary_to) / 2.0
                    WHEN v.salary_from IS NOT NULL 
                        THEN v.salary_from
                    WHEN v.salary_to IS NOT NULL 
                        THEN v.salary_to
                END > avg_calc.avg_salary
            ORDER BY company_name, vacancy_name
        """
        return self._execute_query(query)

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple]:
        """
        Получает список всех вакансий, в названии которых содержатся переданные слова

        Args:
            keyword: Ключевое слово для поиска

        Returns:
            Список вакансий, содержащих ключевое слово в названии
        """
        query = """
            SELECT 
                c.name as company_name,
                v.name as vacancy_name,
                v.salary_from,
                v.salary_to,
                v.salary_currency,
                v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
            WHERE LOWER(v.name) LIKE LOWER(%s)
            ORDER BY company_name, vacancy_name
        """
        return self._execute_query(query, (f"%{keyword}%",))
