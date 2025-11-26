try:
    from app.config.settings import Settings
    print("Settings imported successfully")
except Exception as e:
    import traceback
    traceback.print_exc()
