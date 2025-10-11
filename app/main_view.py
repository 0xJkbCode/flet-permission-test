import flet as ft
from app.contacts_manager import request_contact_permissions , add_contact

def main_view(page : ft.Page):
    page.title = "اضافه جهات اتصال"
    page.appbar = ft.AppBar(title=ft.Text("POC - إضافه صامته"))
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE


    name_field = ft.TextField(label="اسم جهة الاتصال",width=300)
    phone_field = ft.TextField(label="رقم الهاتف" , width=300)

    def on_request_click(e):
        if request_contact_permissions():
            page.add(ft.Text("تم الحصول على الصلاحية بنجاح", color=ft.Colors.GREEN))
        else:
            page.add(ft.Text("فشل الحصول على الصلاحية",color=ft.Colors.RED))
        page.update()
    
    def on_add_click(e):
        if add_contact(name_field.value , phone_field.value):
            page.add(ft.Text(f"تمت اضافة {name_field.value} بنجاح" ,color=ft.Colors.GREEN))

            name_field.value = ""
            phone_field.value = ""
        else:
            page.add(ft.Text("فشل اضافة جهة اتصال",color=ft.Colors.RED))
        page.update()

    page.add(ft.Text("الخطوه 1 : طلب صلاحية جهات الاتصال",size=18,weight=ft.FontWeight.BOLD),ft.ElevatedButton("Reques Permissions", on_click=on_request_click),
             ft.Divider(),
             ft.Text("الخطوه 2: إضافة جهة اتصال جديدة",size=18,weight=ft.FontWeight.BOLD),
             name_field,
             phone_field,
             ft.ElevatedButton("Add Contact Silently",on_click=on_add_click)
             )