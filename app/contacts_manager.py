import flet as ft
from flet_permission_handler import PermissionHandler, PermissionStatus, PermissionType

try:
    from jnius import autoclass

    # دالة طلب الصلاحيات
    def request_permissions(page: ft.Page) -> bool:
        if page.platform != ft.PagePlatform.ANDROID:
            print("Permission requests are only supported on Android.")
            return False
        
        ph = PermissionHandler()
        page.overlay.append(ph)
        page.update()

        result = ph.request_permission(PermissionType.CONTACTS)
        
        # [الإصلاح رقم 1]: المقارنة بالحالة الصحيحة
        return result == PermissionStatus.GRANTED

    # دالة الإضافة الصامتة
    def add_contact(name: str, phone: str) -> bool:
        if not autoclass:
            print("Cannot add contact, pyjnius is not available.")
            return False
        
        # استدعاء كلاسات أندرويد
        # [الإصلاح رقم 2]: تصحيح org.kivy
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        ContentValues = autoclass("android.content.ContentValues")
        Data = autoclass("android.provider.ContactsContract$Data")
        RawContacts = autoclass("android.provider.ContactsContract$RawContacts")
        StructuredName = autoclass("android.provider.ContactsContract$CommonDataKinds$StructuredName")
        Phone = autoclass("android.provider.ContactsContract$CommonDataKinds$Phone")

        try:
            current_activity = PythonActivity.mActivity
            content_resolver = current_activity.getContentResolver()

            # إنشاء جهة اتصال خام
            values = ContentValues()
            raw_contact_uri = content_resolver.insert(RawContacts.CONTENT_URI, values)
            raw_contact_id = int(raw_contact_uri.getLastPathSegment())
            
            # إضافة الاسم
            values.clear()
            values.put(Data.RAW_CONTACT_ID, raw_contact_id)
            # [الإصلاح رقم 3]: تصحيح MIMETYPE
            values.put(Data.MIMETYPE, StructuredName.CONTENT_ITEM_TYPE)
            values.put(StructuredName.DISPLAY_NAME, name)
            content_resolver.insert(Data.CONTENT_URI, values)

            # إضافة الرقم
            values.clear()
            values.put(Data.RAW_CONTACT_ID, raw_contact_id)
            # [الإصلاح رقم 4]: تصحيح MIMETYPE
            values.put(Data.MIMETYPE, Phone.CONTENT_ITEM_TYPE)
            values.put(Phone.NUMBER, phone)
            values.put(Phone.TYPE, Phone.TYPE_MOBILE)
            content_resolver.insert(Data.CONTENT_URI, values)

            print(f"Contact '{name}' added successfully.")
            return True

        except Exception as e:
            print(f"Error creating raw contact: {e}")
            return False

except Exception as e:
    print(f"Pyjnius not found or failed to initialize: {e}")
    autoclass = None
    # بنعمل دوال "وهمية" عشان البرنامج ميكسرش لو pyjnius مش موجود
    def request_permissions(page: ft.Page) -> bool:
        print("Cannot request permissions, pyjnius/Android API not available.")
        return False
    def add_contact(name: str, phone: str) -> bool:
        print("Cannot add contact, pyjnius/Android API not available.")
        return False