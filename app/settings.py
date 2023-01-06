import environs

env = environs.Env()
env.read_env()

ADMIN_TELEGRAM_USER_ID = env.int("ADMIN_TELEGRAM_USER_ID")
BOT_TOKEN = env.str("BOT_TOKEN")
