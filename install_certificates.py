import ssl
import certifi
import os

def install_certificates():
    # Get the path to the certifi certificate bundle
    certifi_path = certifi.where()
    
    # Set the SSL_CERT_FILE environment variable
    os.environ['SSL_CERT_FILE'] = certifi_path
    
    # Set the default SSL context to use these certificates
    ssl._create_default_https_context = ssl.create_default_context

if __name__ == "__main__":
    install_certificates()
    print("Certificates installed successfully!") 