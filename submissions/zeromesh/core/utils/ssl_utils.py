"""
SSL certificate generation utilities for ZeroMesh
"""

import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger(__name__)

def generate_key_pair(key_size: int = 2048) -> rsa.RSAPrivateKey:
    """Generate an RSA key pair"""
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )

def create_certificate_authority(
    private_key: rsa.RSAPrivateKey,
    common_name: str = "ZeroMesh CA",
    organization: str = "ZeroMesh",
    country: str = "US",
    validity_days: int = 365
) -> x509.Certificate:
    """Create a CA certificate"""
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.COUNTRY_NAME, country)
    ])
    
    now = datetime.utcnow()
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        now
    ).not_valid_after(
        now + timedelta(days=validity_days)
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None),
        critical=True
    ).add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_cert_sign=True,
            crl_sign=True,
            content_commitment=False,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False
        ),
        critical=True
    ).sign(private_key, hashes.SHA256())
    
    return cert

def create_server_certificate(
    private_key: rsa.RSAPrivateKey,
    ca_cert: x509.Certificate,
    ca_key: rsa.RSAPrivateKey,
    common_name: str = "localhost",
    organization: str = "ZeroMesh",
    country: str = "US",
    validity_days: int = 365,
    dns_names: Optional[list[str]] = None
) -> x509.Certificate:
    """Create a server certificate"""
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.COUNTRY_NAME, country)
    ])
    
    now = datetime.utcnow()
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        now
    ).not_valid_after(
        now + timedelta(days=validity_days)
    )
    
    # Add DNS names if provided
    if dns_names:
        cert = cert.add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(name) for name in dns_names
            ]),
            critical=False
        )
    
    # Add key usage
    cert = cert.add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False
        ),
        critical=True
    ).add_extension(
        x509.ExtendedKeyUsage([
            x509.oid.ExtendedKeyUsageOID.SERVER_AUTH
        ]),
        critical=True
    )
    
    return cert.sign(ca_key, hashes.SHA256())

def create_client_certificate(
    private_key: rsa.RSAPrivateKey,
    ca_cert: x509.Certificate,
    ca_key: rsa.RSAPrivateKey,
    agent_id: str,
    organization: str = "ZeroMesh",
    country: str = "US",
    validity_days: int = 365
) -> x509.Certificate:
    """Create a client certificate"""
    # Ensure agent_id has the proper prefix
    if not agent_id.startswith("agent:"):
        agent_id = f"agent:{agent_id}"
        
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, agent_id),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.COUNTRY_NAME, country)
    ])
    
    now = datetime.utcnow()
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        now
    ).not_valid_after(
        now + timedelta(days=validity_days)
    ).add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False
        ),
        critical=True
    ).add_extension(
        x509.ExtendedKeyUsage([
            x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH
        ]),
        critical=True
    )
    
    return cert.sign(ca_key, hashes.SHA256())

def generate_ca_certificate(cert_dir: Path) -> Tuple[Path, Path]:
    """Generate a CA certificate and key"""
    cert_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate CA key pair
    ca_key = generate_key_pair()
    
    # Create CA certificate
    ca_cert = create_certificate_authority(ca_key)
    
    # Save CA certificate and key
    ca_cert_path = cert_dir / "ca.crt"
    ca_key_path = cert_dir / "ca.key"
    
    ca_cert_path.write_bytes(
        ca_cert.public_bytes(serialization.Encoding.PEM)
    )
    ca_key_path.write_bytes(
        ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    )
    
    return ca_cert_path, ca_key_path

def generate_server_certificate(
    cert_dir: Path,
    ca_cert_path: Path,
    ca_key_path: Path,
    dns_names: Optional[list[str]] = None
) -> Tuple[Path, Path]:
    """Generate a server certificate signed by the CA"""
    cert_dir.mkdir(parents=True, exist_ok=True)
    
    # Load CA certificate and key
    ca_cert = x509.load_pem_x509_certificate(ca_cert_path.read_bytes())
    ca_key = serialization.load_pem_private_key(
        ca_key_path.read_bytes(),
        password=None
    )
    
    # Generate server key pair
    server_key = generate_key_pair()
    
    # Create server certificate
    server_cert = create_server_certificate(
        server_key,
        ca_cert,
        ca_key,
        dns_names=dns_names
    )
    
    # Save server certificate and key
    server_cert_path = cert_dir / "server.crt"
    server_key_path = cert_dir / "server.key"
    
    server_cert_path.write_bytes(
        server_cert.public_bytes(serialization.Encoding.PEM)
    )
    server_key_path.write_bytes(
        server_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    )
    
    return server_cert_path, server_key_path

def generate_client_certificate(
    cert_dir: Path,
    ca_cert_path: Path,
    ca_key_path: Path,
    agent_id: str
) -> Tuple[Path, Path]:
    """Generate a client certificate signed by the CA"""
    cert_dir.mkdir(parents=True, exist_ok=True)
    
    # Load CA certificate and key
    ca_cert = x509.load_pem_x509_certificate(ca_cert_path.read_bytes())
    ca_key = serialization.load_pem_private_key(
        ca_key_path.read_bytes(),
        password=None
    )
    
    # Generate client key pair
    client_key = generate_key_pair()
    
    # Create client certificate
    client_cert = create_client_certificate(
        client_key,
        ca_cert,
        ca_key,
        agent_id
    )
    
    # Save client certificate and key
    client_cert_path = cert_dir / f"{agent_id.replace(':', '_')}.crt"
    client_key_path = cert_dir / f"{agent_id.replace(':', '_')}.key"
    
    client_cert_path.write_bytes(
        client_cert.public_bytes(serialization.Encoding.PEM)
    )
    client_key_path.write_bytes(
        client_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    )
    
    return client_cert_path, client_key_path 