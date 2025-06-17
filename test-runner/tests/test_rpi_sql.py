# test-runner/tests/test_rpi_sql.py
import pytest
import requests
import pymssql
import time
from datetime import datetime


class TestRPISQLConnection:
    """Testy połączenia RPI Server z bazą danych WAPROMAG"""

    @pytest.fixture(scope="class")
    def rpi_base_url(self):
        return "http://rpi-server:8081/api"

    @pytest.fixture(scope="class")
    def db_config(self):
        return {
            'host': 'mssql-wapromag',
            'port': 1433,
            'database': 'WAPROMAG_TEST',
            'username': 'sa',
            'password': 'WapromagPass123!'
        }

    def test_rpi_server_health(self, rpi_base_url):
        """Test czy RPI Server odpowiada"""
        response = requests.get(f"{rpi_base_url}/health", timeout=10)
        assert response.status_code == 200

        health_data = response.json()
        assert 'status' in health_data
        assert health_data['status'] in ['HEALTHY', 'DEGRADED']

    def test_direct_database_connection(self, db_config):
        """Test bezpośredniego połączenia z bazą danych"""
        conn = pymssql.connect(
            server=db_config['host'],
            user=db_config['username'],
            password=db_config['password'],
            database=db_config['database'],
            timeout=10
        )

        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        assert version is not None

        cursor.close()
        conn.close()

    def test_rpi_database_connection_test(self, rpi_base_url):
        """Test połączenia z bazą przez RPI Server"""
        response = requests.get(f"{rpi_base_url}/sql/test/wapromag", timeout=10)
        assert response.status_code == 200

        result = response.json()
        assert result['success'] is True
        assert 'message' in result

    def test_rpi_database_query_tables(self, rpi_base_url):
        """Test zapytania o listę tabel przez RPI Server"""
        response = requests.get(f"{rpi_base_url}/sql/tables/wapromag", timeout=15)
        assert response.status_code == 200

        result = response.json()
        assert result['success'] is True
        assert 'recordset' in result

        # Sprawdź czy są wymagane tabele
        table_names = [row[1] for row in result['recordset']]  # TABLE_NAME
        required_tables = ['Kontrahenci', 'Produkty', 'DokumentyMagazynowe', 'KonfiguracjaDrukarek']

        for table in required_tables:
            assert table in table_names, f"Brak wymaganej tabeli: {table}"

    def test_rpi_database_query_products(self, rpi_base_url):
        """Test zapytania o produkty przez RPI Server"""
        query_data = {
            'database': 'wapromag',
            'query': 'SELECT TOP 5 ID, Kod, Nazwa, StanMagazynowy FROM Produkty WHERE CzyAktywny = 1'
        }

        response = requests.post(
            f"{rpi_base_url}/sql/query",
            json=query_data,
            timeout=15
        )
        assert response.status_code == 200

        result = response.json()
        assert result['success'] is True
        assert 'recordset' in result
        assert len(result['recordset']) > 0

    def test_rpi_database_query_contractors(self, rpi_base_url):
        """Test zapytania o kontrahentów przez RPI Server"""
        query_data = {
            'database': 'wapromag',
            'query': 'SELECT TOP 5 ID, Kod, Nazwa, NIP FROM Kontrahenci WHERE CzyAktywny = 1'
        }

        response = requests.post(
            f"{rpi_base_url}/sql/query",
            json=query_data,
            timeout=15
        )
        assert response.status_code == 200

        result = response.json()
        assert result['success'] is True
        assert 'recordset' in result
        assert len(result['recordset']) > 0

    def test_rpi_database_query_documents(self, rpi_base_url):
        """Test zapytania o dokumenty przez RPI Server"""
        query_data = {
            'database': 'wapromag',
            'query': '''
                SELECT TOP 5 d.ID, d.Numer, d.TypDokumentu, d.DataWystawienia, k.Nazwa as Kontrahent
                FROM DokumentyMagazynowe d
                LEFT JOIN Kontrahenci k ON d.KontrahentID = k.ID
                ORDER BY d.DataWystawienia DESC
            '''
        }

        response = requests.post(
            f"{rpi_base_url}/sql/query",
            json=query_data,
            timeout=15
        )
        assert response.status_code == 200

        result = response.json()
        assert result['success'] is True
        assert 'recordset' in result

    def test_rpi_database_invalid_query(self, rpi_base_url):
        """Test nieprawidłowego zapytania SQL"""
        query_data = {
            'database': 'wapromag',
            'query': 'SELECT * FROM NonExistentTable'
        }

        response = requests.post(
            f"{rpi_base_url}/sql/query",
            json=query_data,
            timeout=15
        )
        assert response.status_code == 500

        result = response.json()
        assert 'error' in result

    def test_database_performance_simple_query(self, db_config):
        """Test wydajności prostego zapytania"""
        start_time = time.time()

        conn = pymssql.connect(
            server=db_config['host'],
            user=db_config['username'],
            password=db_config['password'],
            database=db_config['database']
        )

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Produkty")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        execution_time = time.time() - start_time
        assert execution_time < 5.0, f"Zapytanie trwało zbyt długo: {execution_time:.2f}s"
        assert result[0] > 0, "Brak produktów w bazie danych"

    @pytest.mark.parametrize("table_name", [
        "Kontrahenci", "Produkty", "DokumentyMagazynowe",
        "PozycjeDokumentowMagazynowych", "StanyMagazynowe", "KonfiguracjaDrukarek"
    ])
    def test_table_accessibility(self, rpi_base_url, table_name):
        """Test dostępności wszystkich głównych tabel"""
        query_data = {
            'database': 'wapromag',
            'query': f'SELECT COUNT(*) as cnt FROM {table_name}'
        }

        response = requests.post(
            f"{rpi_base_url}/sql/query",
            json=query_data,
            timeout=10
        )
        assert response.status_code == 200

        result = response.json()
        assert result['success'] is True
        assert len(result['recordset']) == 1


