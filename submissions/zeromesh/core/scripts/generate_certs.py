"""
Script to generate SSL certificates for ZeroMesh
"""

import logging
import argparse
from pathlib import Path
from core.utils.ssl_utils import (
    generate_ca_certificate,
    generate_server_certificate,
    generate_client_certificate
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate SSL certificates for ZeroMesh")
    parser.add_argument(
        "--cert-dir",
        type=str,
        default="certs",
        help="Directory to store certificates"
    )
    parser.add_argument(
        "--dns-names",
        type=str,
        nargs="+",
        default=["localhost"],
        help="DNS names for server certificate"
    )
    parser.add_argument(
        "--agent-ids",
        type=str,
        nargs="+",
        default=[],
        help="Agent IDs to generate client certificates for"
    )
    
    args = parser.parse_args()
    cert_dir = Path(args.cert_dir)
    
    # Generate CA certificate
    logger.info("Generating CA certificate...")
    ca_cert_path, ca_key_path = generate_ca_certificate(cert_dir)
    
    # Generate server certificate
    logger.info("Generating server certificate...")
    server_cert_path, server_key_path = generate_server_certificate(
        cert_dir,
        ca_cert_path,
        ca_key_path,
        dns_names=args.dns_names
    )
    
    # Generate client certificates
    for agent_id in args.agent_ids:
        logger.info(f"Generating client certificate for {agent_id}...")
        client_cert_path, client_key_path = generate_client_certificate(
            cert_dir,
            ca_cert_path,
            ca_key_path,
            agent_id
        )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main() 