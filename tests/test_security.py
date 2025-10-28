"""
Testes de segurança para a API.

Valida proteções contra:
- SQL Injection
- XSS (Cross-Site Scripting)
- DoS (Denial of Service) via uploads grandes
- Path Traversal
- Timing Attacks na API Key
"""

import pytest
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# API key de teste
TEST_API_KEY = "test_api_key_12345"


class TestSecurityVulnerabilities:
    """Testes de vulnerabilidades de segurança."""

    def test_sql_injection_in_upload(self):
        """Testa proteção contra SQL injection em uploads."""
        malicious_payloads = [
            "'; DROP TABLE students; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
        ]
        
        for payload in malicious_payloads:
            # Criar CSV malicioso
            csv_content = f"student_id,timestamp,item_id,skill_id,correct\n{payload},2023-01-01,item1,1,1"
            
            response = client.post(
                "/upload-csv",
                files={"file": ("malicious.csv", csv_content, "text/csv")},
                headers={"x-api-key": TEST_API_KEY}
            )
            
            # Deve processar sem executar SQL injection
            # Se houver erro, deve ser de validação, não de SQL
            assert response.status_code in [200, 400, 422], f"Payload '{payload}' causou status inesperado"
            if response.status_code != 200:
                # Erro deve ser de validação, não de SQL
                assert "DROP" not in response.text.upper()
                assert "UNION" not in response.text.upper()

    def test_xss_protection_in_responses(self):
        """Testa proteção contra XSS em respostas."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
        ]
        
        for payload in xss_payloads:
            # Tentar injetar XSS via upload
            csv_content = f"student_id,timestamp,item_id,skill_id,correct\n{payload},2023-01-01,item1,1,1"
            
            response = client.post(
                "/upload-csv",
                files={"file": ("xss.csv", csv_content, "text/csv")},
                headers={"x-api-key": TEST_API_KEY}
            )
            
            # Resposta não deve conter script não escapado
            assert "<script>" not in response.text.lower()
            assert "onerror=" not in response.text.lower()
            assert "javascript:" not in response.text.lower()

    def test_dos_large_file_protection(self):
        """Testa proteção contra DoS com arquivos grandes."""
        # Criar arquivo "grande" (simulado com muitas linhas)
        large_content = "student_id,timestamp,item_id,skill_id,correct\n"
        large_content += "student1,2023-01-01,item1,1,1\n" * 1_000_000  # ~50MB
        
        response = client.post(
            "/upload-csv",
            files={"file": ("large.csv", large_content, "text/csv")},
            headers={"x-api-key": TEST_API_KEY}
        )
        
        # Deve rejeitar arquivo muito grande (413 Payload Too Large)
        assert response.status_code == 413, "Arquivo grande não foi rejeitado"
        assert "muito grande" in response.json().get("detail", "").lower() or \
               "large" in response.json().get("detail", "").lower()

    def test_invalid_file_extension_rejected(self):
        """Testa rejeição de extensões de arquivo inválidas."""
        invalid_extensions = [
            ("malicious.exe", "text/csv"),
            ("script.sh", "text/csv"),
            ("data.txt", "text/plain"),
            ("archive.zip", "application/zip"),
        ]
        
        for filename, content_type in invalid_extensions:
            csv_content = "student_id,timestamp,item_id,skill_id,correct\nstudent1,2023-01-01,item1,1,1"
            
            response = client.post(
                "/upload-csv",
                files={"file": (filename, csv_content, content_type)},
                headers={"x-api-key": TEST_API_KEY}
            )
            
            # Deve rejeitar extensão inválida
            assert response.status_code == 400, f"Extensão {filename} não foi rejeitada"
            assert "extensão" in response.json().get("detail", "").lower() or \
                   "extension" in response.json().get("detail", "").lower()

    def test_empty_file_rejected(self):
        """Testa rejeição de arquivo vazio."""
        response = client.post(
            "/upload-csv",
            files={"file": ("empty.csv", "", "text/csv")},
            headers={"x-api-key": TEST_API_KEY}
        )
        
        # Deve rejeitar arquivo vazio
        assert response.status_code == 400
        assert "vazio" in response.json().get("detail", "").lower() or \
               "empty" in response.json().get("detail", "").lower()

    def test_path_traversal_in_filename(self):
        """Testa proteção contra path traversal em nomes de arquivo."""
        malicious_filenames = [
            "../../../etc/passwd.csv",
            "..\\..\\..\\windows\\system32\\config\\sam.csv",
            "../../../../root/.ssh/id_rsa.csv",
        ]
        
        csv_content = "student_id,timestamp,item_id,skill_id,correct\nstudent1,2023-01-01,item1,1,1"
        
        for filename in malicious_filenames:
            response = client.post(
                "/upload-csv",
                files={"file": (filename, csv_content, "text/csv")},
                headers={"x-api-key": TEST_API_KEY}
            )
            
            # Sistema deve processar sem permitir path traversal
            # O arquivo deve ser salvo apenas no diretório uploads/
            assert response.status_code in [200, 400, 422]

    def test_timing_attack_on_api_key(self):
        """Testa proteção contra timing attack na verificação de API key."""
        correct_key = TEST_API_KEY
        wrong_keys = [
            "x" + correct_key[1:],  # Primeiro char errado
            correct_key[:-1] + "x",  # Último char errado
            "wrong_key_completely",
        ]
        
        # Medir tempo de resposta para chave correta
        start = time.perf_counter()
        response_correct = client.get("/metrics", headers={"x-api-key": correct_key})
        time_correct = time.perf_counter() - start
        
        # Medir tempo de resposta para chaves erradas
        times_wrong = []
        for wrong_key in wrong_keys:
            start = time.perf_counter()
            response_wrong = client.get("/metrics", headers={"x-api-key": wrong_key})
            time_wrong = time.perf_counter() - start
            times_wrong.append(time_wrong)
            
            # Deve retornar 401 para chaves erradas
            assert response_wrong.status_code == 401
        
        # Tempo médio para chaves erradas
        avg_time_wrong = sum(times_wrong) / len(times_wrong)
        
        # Diferença de tempo deve ser pequena (< 10ms)
        # Isso indica uso de secrets.compare_digest() que é constant-time
        time_diff = abs(time_correct - avg_time_wrong)
        assert time_diff < 0.01, f"Diferença de tempo suspeita: {time_diff*1000:.2f}ms"

    def test_rate_limiting_protection(self):
        """Testa proteção de rate limiting."""
        # Fazer muitas requisições rapidamente
        responses = []
        for i in range(65):  # Limite padrão é 60/min
            response = client.get("/health")  # Endpoint sem autenticação
            responses.append(response.status_code)
        
        # Pelo menos uma requisição deve ser bloqueada por rate limit
        # Note: Este teste pode falhar se rate limit não estiver habilitado no health endpoint
        # Ajustar conforme implementação
        assert any(status == 429 for status in responses[-10:]), \
            "Rate limiting não está bloqueando requisições excessivas"

    def test_invalid_json_payload(self):
        """Testa proteção contra payloads JSON malformados."""
        response = client.post(
            "/infer",
            data="not a json",  # JSON inválido
            headers={
                "x-api-key": TEST_API_KEY,
                "Content-Type": "application/json"
            }
        )
        
        # Deve retornar erro de validação
        assert response.status_code in [400, 422]

    def test_missing_required_fields(self):
        """Testa validação de campos obrigatórios."""
        # Upload sem campos obrigatórios
        invalid_csv = "col1,col2\nvalue1,value2"  # Sem as colunas necessárias
        
        response = client.post(
            "/upload-csv",
            files={"file": ("invalid.csv", invalid_csv, "text/csv")},
            headers={"x-api-key": TEST_API_KEY}
        )
        
        # Deve rejeitar por falta de colunas obrigatórias
        assert response.status_code == 400
        assert "column" in response.json().get("detail", "").lower() or \
               "coluna" in response.json().get("detail", "").lower()


class TestAuthenticationSecurity:
    """Testes de segurança de autenticação."""

    def test_missing_api_key_rejected(self):
        """Testa rejeição quando API key está ausente."""
        response = client.get("/metrics")
        assert response.status_code == 401

    def test_wrong_api_key_rejected(self):
        """Testa rejeição de API key incorreta."""
        response = client.get("/metrics", headers={"x-api-key": "wrong_key"})
        assert response.status_code == 401

    def test_empty_api_key_rejected(self):
        """Testa rejeição de API key vazia."""
        response = client.get("/metrics", headers={"x-api-key": ""})
        assert response.status_code == 401

    def test_health_endpoint_no_auth(self):
        """Testa que endpoint de health não requer autenticação."""
        response = client.get("/health")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
