import flet as ft
import os

# We only try to import pyjnius if we are on Android
# Flet sets this environment variable during the build process
IS_ANDROID = os.environ.get("FLET_PLATFORM") == "android"

if IS_ANDROID:
    try:
        from jnius import autoclass, cast
    except ImportError:
        print("Pyjnius not found, native Android functions will not be available.")
        autoclass = None
else:
    autoclass = None


# --- Android Native Functions ---

def request_contact_permissions() -> bool:
    """
    Uses pyjnius to directly request CONTACTS permissions from the Android OS.
    This is the most reliable method.
    """
    if not autoclass:
        print("Cannot request permissions, pyjnius is not available.")
        return False

    try:
        # Import necessary Android classes
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        ActivityCompat = autoclass('androidx.core.app.ActivityCompat')
        Manifest = autoclass('android.Manifest$permission')
        PackageManager = autoclass('android.content.pm.PackageManager')

        current_activity = PythonActivity.mActivity
        
        # Check if permission is already granted
        if ActivityCompat.checkSelfPermission(current_activity, Manifest.WRITE_CONTACTS) == PackageManager.PERMISSION_GRANTED:
            print("WRITE_CONTACTS permission is already granted.")
            return True

        # If not granted, request it
        print("Requesting WRITE_CONTACTS permission...")
        ActivityCompat.requestPermissions(
            current_activity,
            [Manifest.WRITE_CONTACTS, Manifest.READ_CONTACTS],
            0  # requestCode, can be any integer
        )
        
        # Note: This is an asynchronous operation. We can't immediately know the result here.
        # For a POC, we will assume the user grants it. A production app would handle the result in the activity.
        # For now, we just trigger the request.
        print("Permission request dialog should be shown.")
        return True # We return True to indicate the request was sent

    except Exception as e:
        print(f"Error requesting permissions via pyjnius: {e}")
        return False

def add_contact(name: str, phone: str) -> bool:
    """
    Uses pyjnius to silently add a contact to the Android phonebook.
    This uses the more robust method of getting the context.
    """
    if not autoclass:
        print("Cannot add contact, pyjnius is not available.")
        return False
        
    try:
        # Import necessary Android classes
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        ContentValues = autoclass('android.content.ContentValues')
        ContactsContract = autoclass('android.provider.ContactsContract')
        Data = autoclass('android.provider.ContactsContract$Data')
        RawContacts = autoclass('android.provider.ContactsContract$RawContacts')
        StructuredName = autoclass('android.provider.ContactsContract$CommonDataKinds$StructuredName')
        Phone = autoclass('android.provider.ContactsContract$CommonDataKinds$Phone')

        # [THE FIX]: Get context and content resolver correctly
        current_activity = PythonActivity.mActivity
        context = current_activity.getApplicationContext()
        content_resolver = context.getContentResolver()

        # Step 1: Create a new raw contact entry
        values = ContentValues()
        # [THE FIX]: Specify account type as null for local contacts
        values.put(RawContacts.ACCOUNT_TYPE, None)
        values.put(RawContacts.ACCOUNT_NAME, None)
        raw_contact_uri = content_resolver.insert(RawContacts.CONTENT_URI, values)
        raw_contact_id = int(raw_contact_uri.getLastPathSegment())

        # Step 2: Add the display name
        name_values = ContentValues()
        name_values.put(Data.RAW_CONTACT_ID, raw_contact_id)
        name_values.put(Data.MIMETYPE, StructuredName.CONTENT_ITEM_TYPE)
        name_values.put(StructuredName.DISPLAY_NAME, name)
        content_resolver.insert(Data.CONTENT_URI, name_values)

        # Step 3: Add the phone number
        phone_values = ContentValues()
        phone_values.put(Data.RAW_CONTACT_ID, raw_contact_id)
        phone_values.put(Data.MIMETYPE, Phone.CONTENT_ITEM_TYPE)
        phone_values.put(Phone.NUMBER, phone)
        phone_values.put(Phone.TYPE, Phone.TYPE_MOBILE)
        content_resolver.insert(Data.CONTENT_URI, phone_values)

        print(f"Contact '{name}' added successfully via pyjnius.")
        return True

    except Exception as e:
        print(f"Error adding contact via pyjnius: {e}")
        return False