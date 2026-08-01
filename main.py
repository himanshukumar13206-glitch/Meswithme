import asyncio
import importlib
import pkgutil

from clients import bot, assistant, call_py
from keepalive import run_keepalive_server
import plugins  # noqa: F401  (package init just needs to exist)


def load_plugins():
    """Import every module in plugins/ so their @bot.on_message
    decorators register themselves."""
    import plugins as plugins_pkg
    for _, name, _ in pkgutil.iter_modules(plugins_pkg.__path__):
        importlib.import_module(f"plugins.{name}")
        print(f"[plugins] loaded plugins.{name}")


async def main():
    load_plugins()
    await run_keepalive_server()
    await bot.start()
    await assistant.start()
    await call_py.start()
    print("✅ Meow Music is up. Bot, assistant, and PyTgCalls are all running.")
    await asyncio.Event().wait()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
