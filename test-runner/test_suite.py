# test-runner/test_suite.py
import sys
import os
import pytest
import json
import yaml
from datetime import datetime
import logging
from pathlib import Path

# Konfiguracja loggingu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_suite.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class TestSuiteRunner:
    def __init__(self):
        self.config = self.load_config()
        self.results_dir = Path('reports')
        self.results_dir.mkdir(exist_ok=True)

    def load_config(self):
        """Ładuje konfigurację testów"""
        config_file = Path('config/test_config.yaml')
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)

        # Domyślna konfiguracja
        return {
            'environment': os.getenv('TEST_ENVIRONMENT', 'docker'),
            'endpoints': {
                'rpi_server': 'http://rpi-server:8081',
                'mssql_wapromag': 'mssql-wapromag:1433',
                'zebra_printer_1': 'zebra-printer-1:9100',
                'zebra_printer_2': 'zebra-printer-2:9100'
            },
            'database': {
                'host': 'mssql-wapromag',
                'port': 1433,
                'database': 'WAPROMAG_TEST',
                'username': 'sa',
                'password': 'WapromagPass123!'
            },
            'timeouts': {
                'connection': 10,
                'response': 30,
                'long_operation': 60
            },
            'test_data': {
                'test_product_code': 'TEST001',
                'test_contractor_code': 'TESTK001',
                'test_document_number': 'TEST/001/2025'
            }
        }

    def run_tests(self):
        """Uruchamia wszystkie testy i generuje raporty"""
        logger.info("🧪 Rozpoczynanie testów WAPRO Network Mock")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Argumenty dla pytest
        pytest_args = [
            'tests/',
            '-v',
            '--tb=short',
            f'--html=reports/test_report_{timestamp}.html',
            '--self-contained-html',
            f'--json-report=reports/test_results_{timestamp}.json',
            '--json-report-summary'
        ]

        # Dodatkowe opcje w zależności od środowiska
        if self.config.get('environment') == 'ci':
            pytest_args.extend(['--maxfail=5', '--strict-markers'])

        try:
            # Uruchomienie testów
            exit_code = pytest.main(pytest_args)

            # Generowanie dodatkowych raportów
            self.generate_summary_report(timestamp)
            self.generate_health_report()

            if exit_code == 0:
                logger.info("✅ Wszystkie testy zakończone pomyślnie")
            else:
                logger.warning(f"⚠️ Testy zakończone z błędami (kod: {exit_code})")

            return exit_code

        except Exception as e:
            logger.error(f"❌ Błąd podczas uruchamiania testów: {e}")
            return 1

    def generate_summary_report(self, timestamp):
        """Generuje podsumowanie wyników testów"""
        try:
            json_report_path = f'reports/test_results_{timestamp}.json'
            if not os.path.exists(json_report_path):
                return

            with open(json_report_path, 'r') as f:
                results = json.load(f)

            summary = {
                'timestamp': timestamp,
                'environment': self.config.get('environment'),
                'total_tests': results['summary']['total'],
                'passed': results['summary'].get('passed', 0),
                'failed': results['summary'].get('failed', 0),
                'skipped': results['summary'].get('skipped', 0),
                'errors': results['summary'].get('errors', 0),
                'duration': results['summary']['duration'],
                'success_rate': 0
            }

            if summary['total_tests'] > 0:
                summary['success_rate'] = (summary['passed'] / summary['total_tests']) * 100

            # Grupowanie wyników po kategoriach
            categories = {
                'database': [],
                'printers': [],
                'integration': [],
                'performance': []
            }

            for test in results['tests']:
                test_name = test['nodeid']
                if 'test_rpi_sql' in test_name or 'database' in test_name:
                    categories['database'].append(test)
                elif 'zebra' in test_name or 'printer' in test_name:
                    categories['printers'].append(test)
                elif 'integration' in test_name:
                    categories['integration'].append(test)
                elif 'performance' in test_name:
                    categories['performance'].append(test)

            summary['categories'] = {}
            for category, tests in categories.items():
                passed = len([t for t in tests if t['outcome'] == 'passed'])
                total = len(tests)
                summary['categories'][category] = {
                    'total': total,
                    'passed': passed,
                    'success_rate': (passed / total * 100) if total > 0 else 0
                }

            # Zapisanie podsumowania
            with open(f'reports/summary_{timestamp}.json', 'w') as f:
                json.dump(summary, f, indent=2)

            logger.info(
                f"🏥 Stan zdrowia systemu: {health_percentage:.1f}% ({healthy_components}/{total_components} komponentów)")

        except Exception as e:
            logger.error(f"Błąd podczas generowania raportu zdrowia: {e}")


def main():
    """Główna funkcja uruchamiająca testy"""
    runner = TestSuiteRunner()
    exit_code = runner.run_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

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


# test-runner/tests/test_zebra_connectivity.py
import pytest
import socket
import requests
import time
from concurrent.futures import ThreadPoolExecutor


class TestZebraConnectivity:
    """Testy łączności z drukarkami ZEBRA"""

    @pytest.fixture(scope="class")
    def zebra_printers(self):
        return {
            'zebra-1': {
                'host': 'zebra-printer-1',
                'socket_port': 9100,
                'web_port': 8080,
                'name': 'ZEBRA-001',
                'model': 'ZT230'
            },
            'zebra-2': {
                'host': 'zebra-printer-2',
                'socket_port': 9100,
                'web_port': 8080,
                'name': 'ZEBRA-002',
                'model': 'ZT410'
            }
        }

    @pytest.fixture(scope="class")
    def rpi_base_url(self):
        return "http://rpi-server:8081/api"

    @pytest.mark.parametrize("printer_id", ['zebra-1', 'zebra-2'])
    def test_direct_socket_connection(self, zebra_printers, printer_id):
        """Test bezpośredniego połączenia socket z drukarką"""
        printer = zebra_printers[printer_id]

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)

        try:
            result = sock.connect_ex((printer['host'], printer['socket_port']))
            assert result == 0, f"Nie można połączyć się z {printer_id} na porcie {printer['socket_port']}"
        finally:
            sock.close()

    @pytest.mark.parametrize("printer_id", ['zebra-1', 'zebra-2'])
    def test_web_interface_accessibility(self, zebra_printers, printer_id):
        """Test dostępności interfejsu web drukarki"""
        printer = zebra_printers[printer_id]

        response = requests.get(
            f"http://{printer['host']}:{printer['web_port']}/api/status",
            timeout=10
        )
        assert response.status_code == 200

        status_data = response.json()
        assert 'name' in status_data
        assert status_data['name'] == printer['name']

    @pytest.mark.parametrize("printer_id", ['zebra-1', 'zebra-2'])
    def test_rpi_printer_connection_test(self, rpi_base_url, printer_id):
        """Test połączenia z drukarką przez RPI Server"""
        response = requests.get(f"{rpi_base_url}/zebra/test/{printer_id}", timeout=15)
        assert response.status_code == 200

        result = response.json()
        assert result['success'] is True

    @pytest.mark.parametrize("printer_id", ['zebra-1', 'zebra-2'])
    def test_rpi_printer_status(self, rpi_base_url, printer_id):
        """Test pobierania statusu drukarki przez RPI Server"""
        response = requests.get(f"{rpi_base_url}/zebra/status/{printer_id}", timeout=15)
        assert response.status_code == 200

        result = response.json()
        assert result['success'] is True
        assert 'status' in result

    def test_rpi_all_printers_status(self, rpi_base_url):
        """Test pobierania statusu wszystkich drukarek"""
        response = requests.get(f"{rpi_base_url}/zebra/status", timeout=20)
        assert response.status_code == 200

        result = response.json()
        assert 'zebra-1' in result
        assert 'zebra-2' in result

    @pytest.mark.parametrize("printer_id,command", [
        ('zebra-1', '~HI'),  # Host Identification
        ('zebra-1', '~HS'),  # Host Status
        ('zebra-1', 'PING'),  # Ping
        ('zebra-2', '~HI'),
        ('zebra-2', '~HS'),
        ('zebra-2', 'PING'),
    ])
    def test_basic_zpl_commands(self, rpi_base_url, printer_id, command):
        """Test podstawowych komend ZPL"""
        command_data = {
            'printerId': printer_id,
            'command': command
        }

        response = requests.post(
            f"{rpi_base_url}/zebra/command",
            json=command_data,
            timeout=15
        )
        assert response.status_code == 200

        result = response.json()
        assert result['success'] is True

    @pytest.mark.parametrize("printer_id", ['zebra-1', 'zebra-2'])
    def test_direct_zpl_communication(self, zebra_printers, printer_id):
        """Test bezpośredniej komunikacji ZPL"""
        printer = zebra_printers[printer_id]

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)

        try:
            sock.connect((printer['host'], printer['socket_port']))

            # Wyślij komendę Host Identification
            sock.send(b'~HI\n')

            # Odbierz odpowiedź
            response = sock.recv(1024).decode('utf-8', errors='ignore')
            assert len(response) > 0
            assert printer['name'] in response or 'ZEBRA' in response.upper()

        finally:
            sock.close()

    def test_parallel_printer_access(self, zebra_printers):
        """Test równoczesnego dostępu do drukarek"""

        def test_printer_connection(printer_data):
            printer_id, printer = printer_data
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)

            try:
                result = sock.connect_ex((printer['host'], printer['socket_port']))
                return printer_id, result == 0
            except:
                return printer_id, False
            finally:
                sock.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(test_printer_connection, item) for item in zebra_printers.items()]
            results = [future.result() for future in futures]

        for printer_id, success in results:
            assert success, f"Połączenie z {printer_id} nieudane podczas testu równoczesnego dostępu"

    @pytest.mark.parametrize("printer_id", ['zebra-1', 'zebra-2'])
    def test_printer_response_time(self, zebra_printers, printer_id):
        """Test czasu odpowiedzi drukarki"""
        printer = zebra_printers[printer_id]

        start_time = time.time()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        try:
            sock.connect((printer['host'], printer['socket_port']))
            sock.send(b'PING\n')
            response = sock.recv(1024)

            response_time = time.time() - start_time
            assert response_time < 2.0, f"Czas odpowiedzi {printer_id} zbyt długi: {response_time:.2f}s"
            assert len(response) > 0

        finally:
            sock.close()

    @pytest.mark.parametrize("printer_id", ['zebra-1', 'zebra-2'])
    def test_test_label_printing(self, rpi_base_url, printer_id):
        """Test drukowania etykiety testowej"""
        response = requests.post(
            f"{rpi_base_url}/zebra/test-print/{printer_id}",
            timeout=20
        )
        assert response.status_code == 200

        result = response.json()
        assert result['success'] is True

    def test_printer_commands_list(self, rpi_base_url):
        """Test pobierania listy dostępnych komend"""
        response = requests.get(f"{rpi_base_url}/zebra/commands", timeout=10)
        assert response.status_code == 200

        commands = response.json()
        assert 'host_identification' in commands
        assert 'host_status' in commands
        assert 'ping' in commands

    @pytest.mark.parametrize("printer_id", ['zebra-1', 'zebra-2'])
    def test_complex_zpl_label(self, rpi_base_url, printer_id):
        """Test złożonej etykiety ZPL"""
        zpl_command = """
^XA
^FO50,50^A0N,50,50^FDTest Complex Label^FS
^FO50,120^A0N,30,30^FDPrinter: """ + printer_id + """^FS
^FO50,170^A0N,30,30^FDTime: """ + str(int(time.time())) + """^FS
^FO50,220^BY3
^BCN,100,Y,N,N
^FD123456789^FS
^XZ
        """.strip()

        command_data = {
            'printerId': printer_id,
            'command': zpl_command
        }

        response = requests.post(
            f"{rpi_base_url}/zebra/command",
            json=command_data,
            timeout=20
        )
        assert response.status_code == 200

        result = response.json()
        assert result['success'] is True
        "📊 Wygenerowano podsumowanie: {summary['success_rate']:.1f}% testów zakończonych sukcesem")

        except Exception as e:
        logger.error(f"Błąd podczas generowania podsumowania: {e}")


def generate_health_report(self):
    """Generuje raport zdrowia systemu"""
    try:
        import requests

        health_data = {
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }

        # Test RPI Server
        try:
            response = requests.get(
                f"{self.config['endpoints']['rpi_server']}/api/health",
                timeout=self.config['timeouts']['connection']
            )
            health_data['components']['rpi_server'] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response.elapsed.total_seconds(),
                'details': response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            health_data['components']['rpi_server'] = {
                'status': 'unhealthy',
                'error': str(e)
            }

        # Test bazy danych
        try:
            import pymssql
            conn = pymssql.connect(
                server=self.config['database']['host'],
                user=self.config['database']['username'],
                password=self.config['database']['password'],
                database=self.config['database']['database'],
                timeout=self.config['timeouts']['connection']
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()

            health_data['components']['database'] = {
                'status': 'healthy',
                'database': self.config['database']['database']
            }
        except Exception as e:
            health_data['components']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }

        # Test drukarek
        for printer_name in ['zebra_printer_1', 'zebra_printer_2']:
            try:
                import socket
                host, port = self.config['endpoints'][printer_name].split(':')
                port = int(port)

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.config['timeouts']['connection'])
                result = sock.connect_ex((host, port))
                sock.close()

                health_data['components'][printer_name] = {
                    'status': 'healthy' if result == 0 else 'unhealthy',
                    'endpoint': f"{host}:{port}"
                }
            except Exception as e:
                health_data['components'][printer_name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }

        # Zapisanie raportu zdrowia
        with open('reports/health_report.json', 'w') as f:
            json.dump(health_data, f, indent=2)

        # Obliczenie ogólnego stanu zdrowia
        healthy_components = len([c for c in health_data['components'].values() if c['status'] == 'healthy'])
        total_components = len(health_data['components'])
        health_percentage = (healthy_components / total_components * 100) if total_components > 0 else 0

        logger.info(f