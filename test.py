import flet as ft
# We don't need os import anymore

def main(page: ft.Page):
    page.title = "Flet Environment Inspector v2"
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.appbar = ft.AppBar(title=ft.Text("Android Environment Inspector"))

    results_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=10)

    def run_inspection(e):
        # [THE FIX]: Check the platform from the page object at the moment of the click
        if page.platform != ft.PagePlatform.ANDROID:
            results_column.controls.append(ft.Text("This test must be run on an Android device.", color=ft.Colors.RED))
            page.update()
            return
        
        # Clear previous results
        results_column.controls.clear()
        results_column.controls.append(ft.Text("Starting inspection...", weight=ft.FontWeight.BOLD))
        page.update()

        try:
            from jnius import autoclass

            # --- The One True Test ---
            # We will now test the official and correct way to get the Activity
            try:
                # This is the main class of the Flet Android app
                FletMainActivity = autoclass("io.flet.flet.MainActivity")
                
                # It has a static method to get the current instance
                current_activity = FletMainActivity.getInstance()
                
                if current_activity:
                    context = current_activity.getApplicationContext()
                    results_column.controls.append(ft.Text("SUCCESS: Found 'io.flet.flet.MainActivity'!", color=ft.Colors.GREEN))
                    results_column.controls.append(ft.Text(f"Activity object: {current_activity}"))
                    results_column.controls.append(ft.Text(f"Context object: {context}"))
                else:
                    results_column.controls.append(ft.Text("FAILED: getInstance() returned None.", color=ft.Colors.RED))

            except Exception as e:
                results_column.controls.append(ft.Text("FAILED: Could not find or use 'io.flet.flet.MainActivity'.", color=ft.Colors.RED))
                results_column.controls.append(ft.Text(f"Error: {e}", selectable=True))

            page.update()

        except ImportError:
            results_column.controls.append(ft.Text("CRITICAL: pyjnius is not installed!", color=ft.Colors.RED))
            page.update()
        except Exception as e:
            results_column.controls.append(ft.Text(f"An unexpected pyjnius error occurred: {e}", color=ft.Colors.RED, selectable=True))
            page.update()


    page.add(
        ft.ElevatedButton("Run Android Inspection", on_click=run_inspection, width=300),
        ft.Text("Results will appear below:"),
        ft.Divider(),
        results_column
    )

ft.app(main)