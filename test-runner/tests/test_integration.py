# test-runner/tests/test_integration.py
import pytest
import requests
import time
import json
from datetime import datetime


class TestWaproIntegration:
    """Testy integracyjne całego systemu WAPRO"""

    @pytest.fixture(scope="class")
    def rpi_base_url(self):
        return "http://rpi-server:8081/api"

    @pytest.fixture(scope="class")
    def test_data(self):
        return {
            'product_code': f'TEST_{int(time.time())}',
            'contractor_code': f'TESTK_{int(time.time())}',
            'document_number': f'TEST/{int(time.time())}/2025'
        }

    def test_full_system_health(self, rpi_base_url):
        """Test kompletnego stanu zdrowia systemu"""
        response = requests.get(f"{rpi_base_url}/health/detailed", timeout=30)
        assert response.status_code == 200

        health_report = response.json()
        assert 'summary' in health_report
        assert health_report['summary']['overall_status'] in ['HEALTHY', 'DEGRADED']

    def test_database_to_printer_workflow(self, rpi_base_url, test_data):
        """Test przepływu danych od bazy danych do drukarki"""

        # 1. Pobierz produkt z bazy danych
        query_data = {
            'database': 'wapromag',
            'query': 'SELECT TOP 1 ID, Kod, Nazwa, KodKreskowy FROM Produkty WHERE CzyAktywny = 1'
        }

        response = requests.post(f"{rpi_base_url}/sql/query", json=query_data, timeout=15)
        assert response.status_code == 200

        sql_result = response.json()
        assert sql_result['success'] is True
        assert len(sql_result['recordset']) > 0

        product = sql_result['recordset'][0]

        # 2. Wygeneruj etykietę na podstawie danych produktu
        zpl_label = f"""
^XA
^FO50,50^A0N,40,40^FD{product[2]}^FS
^FO50,100^A0N,30,30^FDKod: {product[1]}^FS
^FO50,150^BY3
^BCN,80,Y,N,N
^FD{product[3] or product[1]}^FS
^FO50,250^A0N,25,25^FDData: {datetime.now().strftime('%Y-%m-%d %H:%M')}^FS
^XZ
        """.strip()

        # 3. Wyślij etykietę do drukarki
        print_data = {
            'printerId': 'zebra-1',
            'command': zpl_label
        }

        response = requests.post(f"{rpi_base_url}/zebra/command", json=print_data, timeout=20)
        assert response.status_code == 200

        print_result = response.json()
        assert print_result['success'] is True

    def test_printer_configuration_from_database(self, rpi_base_url):
        """Test konfiguracji drukarek z bazy danych"""

        # Pobierz konfigurację drukarek z bazy
        query_data = {
            'database': 'wapromag',
            'query': 'SELECT NazwaDrukarki, AdresIP, Port, ModelDrukarki FROM KonfiguracjaDrukarek WHERE CzyAktywna = 1'
        }

        response = requests.post(f"{rpi_base_url}/sql/query", json=query_data, timeout=15)
        assert response.status_code == 200

        config_result = response.json()
        assert config_result['success'] is True
        assert len(config_result['recordset']) > 0

        # Sprawdź czy drukarki z konfiguracji są dostępne
        for printer_config in config_result['recordset']:
            printer_name = printer_config[0]
            # Mapowanie nazw drukarek z bazy na ID używane w API
            if 'ZEBRA-001' in printer_name:
                printer_id = 'zebra-1'
            elif 'ZEBRA-002' in printer_name:
                printer_id = 'zebra-2'
            else:
                continue

            response = requests.get(f"{rpi_base_url}/zebra/test/{printer_id}", timeout=10)
            assert response.status_code == 200

            test_result = response.json()
            assert test_result['success'] is True

    def test_document_creation_and_labeling(self, rpi_base_url, test_data):
        """Test tworzenia dokumentu i generowania etykiet"""

        # 1. Pobierz produkty do dokumentu
        query_data = {
            'database': 'wapromag',
            'query': '''
                SELECT TOP 3 p.ID, p.Kod, p.Nazwa, p.KodKreskowy, sm.Stan
                FROM Produkty p 
                LEFT JOIN StanyMagazynowe sm ON p.ID = sm.ProduktID
                WHERE p.CzyAktywny = 1 AND sm.Stan > 0
            '''
        }

        response = requests.post(f"{rpi_base_url}/sql/query", json=query_data, timeout=15)
        assert response.status_code == 200

        products_result = response.json()
        assert products_result['success'] is True
        assert len(products_result['recordset']) > 0

        # 2. Wygeneruj etykiety dla wszystkich produktów
        for product in products_result['recordset'][:2]:  # Testuj tylko 2 produkty
            label_zpl = f"""
^XA
^FO30,30^A0N,35,35^FD{product[2][:20]}^FS
^FO30,80^A0N,25,25^FDKod: {product[1]}^FS
^FO30,110^A0N,25,25^FDStan: {product[4]}^FS
^FO30,150^BY2
^BCN,60,Y,N,N
^FD{product[3] or product[1]}^FS
^XZ
            """.strip()

            # Wyślij do pierwszej drukarki
            print_data = {
                'printerId': 'zebra-1',
                'command': label_zpl
            }

            response = requests.post(f"{rpi_base_url}/zebra/command", json=print_data, timeout=15)
            assert response.status_code == 200

            result = response.json()
            assert result['success'] is True

            # Krótka pauza między etykietami
            time.sleep(1)

    def test_multi_printer_load_balancing(self, rpi_base_url):
        """Test rozłożenia obciążenia między drukarkami"""

        # Test równoczesnego drukowania na obu drukarkach
        test_commands = [
            ('zebra-1', '^XA^FO50,50^A0N,40,40^FDTest Printer 1^FS^XZ'),
            ('zebra-2', '^XA^FO50,50^A0N,40,40^FDTest Printer 2^FS^XZ')
        ]

        import concurrent.futures

        def send_print_command(printer_id, command):
            print_data = {
                'printerId': printer_id,
                'command': command
            }
            response = requests.post(f"{rpi_base_url}/zebra/command", json=print_data, timeout=15)
            return printer_id, response.status_code == 200, response.json().get('success', False)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(send_print_command, printer_id, command)
                for printer_id, command in test_commands
            ]

            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Sprawdź czy wszystkie zadania się powiodły
        for printer_id, status_ok, success in results:
            assert status_ok, f"Błąd HTTP dla drukarki {printer_id}"
            assert success, f"Błąd drukowania dla drukarki {printer_id}"

    def test_error_handling_and_recovery(self, rpi_base_url):
        """Test obsługi błędów i odzyskiwania"""

        # Test nieprawidłowego zapytania SQL
        invalid_query = {
            'database': 'wapromag',
            'query': 'SELECT * FROM NonExistentTable'
        }

        response = requests.post(f"{rpi_base_url}/sql/query", json=invalid_query, timeout=10)
        assert response.status_code == 500

        # Test nieprawidłowej komendy drukarki
        invalid_print = {
            'printerId': 'zebra-1',
            'command': ''  # Pusta komenda
        }

        response = requests.post(f"{rpi_base_url}/zebra/command", json=invalid_print, timeout=10)
        assert response.status_code == 400 or response.json().get('success') is False

        # Test że system nadal działa po błędach
        response = requests.get(f"{rpi_base_url}/health", timeout=10)
        assert response.status_code == 200

    def test_performance_under_load(self, rpi_base_url):
        """Test wydajności pod obciążeniem"""

        import concurrent.futures
        import time

        def execute_quick_test():
            start_time = time.time()

            # Test bazy danych
            query_data = {
                'database': 'wapromag',
                'query': 'SELECT COUNT(*) FROM Produkty'
            }
            response = requests.post(f"{rpi_base_url}/sql/query", json=query_data, timeout=5)
            db_success = response.status_code == 200

            # Test drukarki
            response = requests.get(f"{rpi_base_url}/zebra/test/zebra-1", timeout=5)
            printer_success = response.status_code == 200

            execution_time = time.time() - start_time
            return db_success, printer_success, execution_time

        # Wykonaj 10 równoczesnych testów
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(execute_quick_test) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Analiza wyników
        db_success_count = sum(1 for db_ok, _, _ in results if db_ok)
        printer_success_count = sum(1 for _, printer_ok, _ in results if printer_ok)
        avg_execution_time = sum(exec_time for _, _, exec_time in results) / len(results)

        assert db_success_count >= 8, f"Zbyt mało udanych testów bazy danych: {db_success_count}/10"
        assert printer_success_count >= 8, f"Zbyt mało udanych testów drukarek: {printer_success_count}/10"
        assert avg_execution_time < 3.0, f"Średni czas wykonania zbyt długi: {avg_execution_time:.2f}s"

    def test_data_consistency_check(self, rpi_base_url):
        """Test spójności danych w systemie"""

        # Sprawdź spójność stanów magazynowych
        query_data = {
            'database': 'wapromag',
            'query': '''
                SELECT p.Kod, p.StanMagazynowy, sm.Stan, sm.StanDostepny
                FROM Produkty p
                LEFT JOIN StanyMagazynowe sm ON p.ID = sm.ProduktID
                WHERE p.CzyAktywny = 1
            '''
        }

        response = requests.post(f"{rpi_base_url}/sql/query", json=query_data, timeout=15)
        assert response.status_code == 200

        result = response.json()
        assert result['success'] is True

        # Sprawdź czy stany się zgadzają
        for row in result['recordset']:
            product_code, product_stock, warehouse_stock, available_stock = row
            if warehouse_stock is not None:
                # Tolerancja różnic w stanach (może być aktualizowane)
                assert abs(float(product_stock or 0) - float(warehouse_stock)) < 0.001, \
                    f"Niezgodność stanów dla produktu {product_code}"

    def test_system_monitoring_integration(self, rpi_base_url):
        """Test integracji systemu monitorowania"""

        # Test diagnostyki
        response = requests.get(f"{rpi_base_url}/diagnostic/full", timeout=30)
        assert response.status_code == 200

        diagnostics = response.json()
        assert 'database' in diagnostics
        assert 'printers' in diagnostics
        assert 'network' in diagnostics

        # Test generowania raportu
        response = requests.get(f"{rpi_base_url}/diagnostic/report", timeout=30)
        assert response.status_code == 200

        report = response.json()
        assert 'summary' in report
        assert 'recommendations' in report









