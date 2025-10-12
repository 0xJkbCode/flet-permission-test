import flet as ft
import os

# التحقق من أننا على Android
try:
    from jnius import autoclass, cast
    IS_ANDROID = True
except ImportError:
    print("Pyjnius not found, native Android functions will not be available.")
    autoclass = None
    IS_ANDROID = False

# --- Android Native Functions ---
def get_activity():
    """الحصول على Activity بالطريقة الصحيحة لـ Flet"""
    if not autoclass:
        return None
    
    try:
        # الطريقة الصحيحة للحصول على Activity في Flet
        activity_host_class = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")
        if not activity_host_class:
            print("MAIN_ACTIVITY_HOST_CLASS_NAME not found")
            return None
        
        activity_host = autoclass(activity_host_class)
        activity = activity_host.mActivity
        return activity
    except Exception as e:
        print(f"Error getting activity: {e}")
        return None

def request_contact_permissions() -> bool:
    """
    طلب صلاحيات جهات الاتصال باستخدام pyjnius
    """
    if not autoclass:
        print("Cannot request permissions, pyjnius is not available.")
        return False
    
    try:
        # الحصول على Activity
        current_activity = get_activity()
        if not current_activity:
            return False
        
        # استيراد الكلاسات الضرورية
        ActivityCompat = autoclass('androidx.core.app.ActivityCompat')
        Manifest = autoclass('android.Manifest$permission')
        PackageManager = autoclass('android.content.pm.PackageManager')
        
        # التحقق من الصلاحية
        if ActivityCompat.checkSelfPermission(current_activity, Manifest.WRITE_CONTACTS) == PackageManager.PERMISSION_GRANTED:
            print("WRITE_CONTACTS permission is already granted.")
            return True
        
        # طلب الصلاحية
        print("Requesting WRITE_CONTACTS permission...")
        ActivityCompat.requestPermissions(
            current_activity,
            [Manifest.WRITE_CONTACTS, Manifest.READ_CONTACTS],
            0
        )
        
        print("Permission request dialog should be shown.")
        return True
    except Exception as e:
        print(f"Error requesting permissions via pyjnius: {e}")
        return False

def add_contact(name: str, phone: str) -> bool:
    """
    إضافة جهة اتصال باستخدام pyjnius
    """
    if not autoclass:
        print("Cannot add contact, pyjnius is not available.")
        return False
    
    if not name or not phone:
        print("Name and phone are required")
        return False
    
    try:
        # الحصول على Activity
        current_activity = get_activity()
        if not current_activity:
            return False
        
        # استيراد الكلاسات الضرورية
        ContentValues = autoclass('android.content.ContentValues')
        ContactsContract = autoclass('android.provider.ContactsContract')
        Data = autoclass('android.provider.ContactsContract$Data')
        RawContacts = autoclass('android.provider.ContactsContract$RawContacts')
        StructuredName = autoclass('android.provider.ContactsContract$CommonDataKinds$StructuredName')
        Phone = autoclass('android.provider.ContactsContract$CommonDataKinds$Phone')
        
        # الحصول على ContentResolver
        context = current_activity.getApplicationContext()
        content_resolver = context.getContentResolver()
        
        # إنشاء جهة اتصال جديدة
        values = ContentValues()
        values.put(RawContacts.ACCOUNT_TYPE, None)
        values.put(RawContacts.ACCOUNT_NAME, None)
        
        raw_contact_uri = content_resolver.insert(RawContacts.CONTENT_URI, values)
        if not raw_contact_uri:
            print("Failed to create raw contact")
            return False
            
        raw_contact_id = int(raw_contact_uri.getLastPathSegment())
        
        # إضافة الاسم
        name_values = ContentValues()
        name_values.put(Data.RAW_CONTACT_ID, raw_contact_id)
        name_values.put(Data.MIMETYPE, StructuredName.CONTENT_ITEM_TYPE)
        name_values.put(StructuredName.DISPLAY_NAME, name)
        content_resolver.insert(Data.CONTENT_URI, name_values)
        
        # إضافة رقم الهاتف
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
