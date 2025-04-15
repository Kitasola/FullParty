from .recruitment import set_channel, create_event

def register_commands(client):
    print("Registering commands...")
    client.tree.add_command(set_channel)
    print(f"Registered command: {set_channel.name}")
    client.tree.add_command(create_event)
    print(f"Registered command: {create_event.name}")

__all__ = ["register_commands"]