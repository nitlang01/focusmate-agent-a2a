from minio import Minio
from minio.error import S3Error

def test_minio_connection():
    try:
        # Initialize MinIO client
        client = Minio(
            "localhost:9000",          # MinIO endpoint
            access_key="minioadmin",   # Default user
            secret_key="minioadmin",   # Default password
            secure=False               # Because we're running HTTP, not HTTPS
        )

        bucket_name = "focusmate"      # Bucket you created in console

        # Chec
        # k if bucket exists
        if not client.bucket_exists(bucket_name):
            print(f"Bucket '{bucket_name}' not found. Creating it...")
            client.make_bucket(bucket_name)
        else:
            print(f"✅ Bucket '{bucket_name}' exists.")

        # Create a test file
        with open("test.txt", "w") as f:
            f.write("Hello MinIO from FocusMate!")

        # Upload file to MinIO
        client.fput_object(bucket_name, "test.txt", "test.txt")
        print("✅ File uploaded successfully!")

        # Download the same file
        client.fget_object(bucket_name, "test.txt", "downloaded_test.txt")
        print("📥 File downloaded successfully!")

    except S3Error as e:
        print("❌ MinIO Error:", e)
    except Exception as ex:
        print("⚠️ General Error:", ex)

if __name__ == "__main__":
    test_minio_connection()
