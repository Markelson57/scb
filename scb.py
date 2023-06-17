import os
import json
import subprocess
from google.oauth2 import service_account
import googleapiclient.discovery
import mimetypes

def clear_console():
    # Función para limpiar la consola
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')

def create_credentials_file():
    clear_console()
    print("=== SCB - Creación de Credenciales ===")
    project_id = input("Ingrese el ID del proyecto de Google Cloud: ")
    client_email = input("Ingrese el correo electrónico de la cuenta de servicio: ")
    private_key = input("Ingrese la clave privada de la cuenta de servicio: ")

    credentials = {
        "type": "service_account",
        "project_id": project_id,
        "private_key_id": "your-private-key-id",
        "private_key": private_key,
        "client_email": client_email,
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}"
    }

    try:
        file_path = input("Ingrese la ruta completa donde desea guardar el archivo de credenciales JSON: ")
        with open(file_path, 'w') as file:
            json.dump(credentials, file, indent=4)
        print("El archivo de credenciales JSON se ha creado exitosamente en:", file_path)
    except Exception as e:
        print("Error al crear el archivo de credenciales JSON:", str(e))

def get_service_credentials(credentials_file):
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=["https://www.googleapis.com/auth/androidpublisher"]
    )
    return credentials

def install_required_packages():
    clear_console()
    print("=== SCB - Instalación de Paquetes ===")
    print("Se requieren paquetes adicionales para ejecutar esta acción.")
    install_confirmation = input("¿Desea instalar los paquetes necesarios? (s/n): ")
    if install_confirmation.lower() == 's':
        try:
            subprocess.check_call(['pip', 'install', 'google-auth', 'google-auth-oauthlib', 'google-auth-httplib2', 'google-api-python-client'])
            print("La instalación de paquetes se ha completado.")
        except Exception as e:
            print("Error al instalar los paquetes:", str(e))
    else:
        print("La instalación de paquetes ha sido cancelada.")

def upload_apk(credentials_file, package_name, apk_file_path):
    credentials = get_service_credentials(credentials_file)

    # Crea un cliente para la API de Google Play Developer
    android_publisher = googleapiclient.discovery.build('androidpublisher', 'v3', credentials=credentials)

    # ID del paquete de la aplicación
    package_name = 'com.tuapp'

    # Crea un nuevo borrador de edición (versionCode único requerido)
    edit_request = android_publisher.edits().insert(body={}, packageName=package_name)
    edit_response = edit_request.execute()
    edit_id = edit_response['id']

    try:
        # Crea una nueva versión de la aplicación
        version_code = 1  # Cambia esto al número de versión deseado
        new_version_request = android_publisher.edits().tracks().update(
            editId=edit_id,
            packageName=package_name,
            track='production',
            body={'releases': [{'versionCodes': [str(version_code)], 'status': 'draft'}]}
        )
        new_version_response = new_version_request.execute()

        # Sube el archivo de aplicación (APK)
        apk_file_name = os.path.basename(apk_file_path)
        apk_file_type, _ = mimetypes.guess_type(apk_file_path)
        apk_upload_request = android_publisher.edits().bundles().upload(
            editId=edit_id,
            packageName=package_name,
            media_body=apk_file_path,
            media_mime_type=apk_file_type
        )
        apk_upload_response = apk_upload_request.execute()
        apk_version_code = apk_upload_response['versionCode']

        # Configura los detalles del lanzamiento
        release_notes = {
            'en-US': 'Release notes for version {}'.format(version_code)
        }
        track_release_request = android_publisher.edits().tracks().update(
            editId=edit_id,
            packageName=package_name,
            track='production',
            body={'releases': [{'versionCodes': [str(apk_version_code)], 'releaseNotes': release_notes}]}
        )
        track_release_response = track_release_request.execute()

        # Realiza la validación de la edición
        validate_request = android_publisher.edits().validate(editId=edit_id, packageName=package_name)
        validate_response = validate_request.execute()

        # Imprime la respuesta
        print("Se creó una nueva versión de la aplicación en Google Play Console.")
        print("ID de la edición:", edit_id)
        print("Código de versión:", version_code)
        print("Respuesta:", track_release_response)

    except Exception as e:
        print("Error al crear una nueva versión de la aplicación:", str(e))

    finally:
        # Cierra la edición
        android_publisher.edits().commit(editId=edit_id, packageName=package_name).execute()

def main():
    clear_console()
    print("""
██████╗ ██╗   ██╗ ██████╗ ██████╗  ██████╗ 
██╔══██╗██║   ██║██╔═══██╗██╔══██╗██╔═══██╗
██████╔╝██║   ██║██║   ██║██║  ██║██║   ██║
██╔═══╝ ██║   ██║██║   ██║██║  ██║██║   ██║
██║     ╚██████╔╝╚██████╔╝██████╔╝╚██████╔╝
╚═╝      ╚═════╝  ╚═════╝ ╚═════╝  ╚═════╝                                             
    """)

    credentials_file = "ruta/a/tu/archivo-de-credenciales.json"
    package_name = "com.tuapp"
    apk_file_path = "ruta/al/archivo.apk"

    if not os.path.exists(credentials_file):
        create_credentials_file()

    if os.path.exists(credentials_file):
        install_required_packages()
        upload_apk(credentials_file, package_name, apk_file_path)
    else:
        print("El archivo de credenciales no existe. Ejecute nuevamente el programa y cree el archivo de credenciales primero.")

if __name__ == '__main__':
    main()

