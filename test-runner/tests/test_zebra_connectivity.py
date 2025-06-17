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

        logger.info(f"""📊 Wygenerowano raport zdrowia: {health_percentage:.1f}% komponentów zdrowych""")

    except Exception as e:
        logger.error(f"Błąd podczas generowania raportu zdrowia: {e}")

